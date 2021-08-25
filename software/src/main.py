from serial.serialutil import EIGHTBITS, PARITY_NONE, STOPBITS_ONE
from asyncio.events import get_event_loop
from signal import SIGINT, SIGTERM
from nats.aio.client import Client
import argparse
import asyncio
import logging
import serial
import sys

from event_queue import EventQueue

# TODO: 
# - Generic read/write with something else.
# - Logging colors

COMMAND_LEFT = 0
COMMAND_RIGHT = 1
COMMAND_FORWARD = 2
COMMAND_BACKWARD = 3
COMMAND_STOP = 4
COMMAND_RUN = 5

PRIORITY_CRITICAL = 0
PRIORITY_MANUAL = 1
PRIORITY_AUTONOMOUS = 2

class Command:
    def __init__(self, command, priority):
        self.command = command
        self.priority = priority

UART_ADDR = '/tmp/uart'

def handle_uart(event_queue, uart):
    data = uart.read_all()
    event_queue.insert('UART_EVENT_IN', data)

async def periodic(event_queue, interval=1):
    while True:
        await event_queue.insert('PERIODIC_EVENT', 'hi!')
        await asyncio.sleep(interval)

async def transmission(commands, event_queue):
    last_was_left = False
    l = logging.getLogger('transmission')

    while True:
        command = await commands.get()
        
        if command.command == COMMAND_RIGHT:
            l.debug('COMMAND_RIGHT')

            if last_was_left:
                l.debug('Queueing UART_EVENT_OUT')
                await event_queue.insert_async('UART_EVENT_OUT', 'left -> right')

        if command.command == COMMAND_LEFT:
            l.debug('COMMAND_LEFT')
            last_was_left = True
        else:
            last_was_left = False

async def main():
    loop = asyncio.get_event_loop()
    eq = EventQueue()
    commands = asyncio.Queue()

    uart = serial.Serial(
        port=UART_ADDR,
        baudrate=115200,
        bytesize=EIGHTBITS,
        parity=PARITY_NONE,
        stopbits=STOPBITS_ONE
    )

    nats = Client()
    await nats.connect('localhost:4222')

    async def uart_event_in(event_queue, data, user_data):
        await event_queue.insert_async('NATS_EVENT_OUT', data)

    async def uart_event_out(event_queue, data, user_data):
        uart.write(data.encode())

    async def nats_event_in(event_queue, data, commands):
        subject = data.subject
        message = data.data

        if subject == 'transmission.in.left':
            await commands.put(Command(COMMAND_LEFT, PRIORITY_MANUAL))
        elif subject == 'transmission.in.right':
            await commands.put(Command(COMMAND_RIGHT, PRIORITY_MANUAL))

    async def nats_event_out(event_queue, data, user_data):
        await nats.publish('thingy.out', data)

    async def periodic_event(event_queue, data, user_data):
        print(data)

    eq.register('UART_EVENT_IN', uart_event_in)
    eq.register('UART_EVENT_OUT', uart_event_out, uart)
    eq.register('NATS_EVENT_IN', nats_event_in, commands)
    eq.register('NATS_EVENT_OUT', nats_event_out, nats)
    eq.register('PERIODIC_EVENT', periodic_event, None)

    loop.add_reader(uart.fileno(), handle_uart, eq, uart)

    async def nats_cb(msg):
        await eq.insert_async('NATS_EVENT_IN', msg)

    await nats.subscribe('transmission.in.>', 'workers', nats_cb)

    #asyncio.create_task(periodic(eq, interval=5))
    asyncio.create_task(transmission(commands, eq))

    await eq.run()

def cancel():
    for t in asyncio.all_tasks():
        t.cancel()

# https://stackoverflow.com/questions/29475007/python-asyncio-reader-callback-and-coroutine-communication

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true')

    args = parser.parse_args()
    format = '%(asctime)s [%(name)s]: %(message)s'
    datefmt = '%Y-%m-%d %H:%M:%S'

    if args.debug:
        logging.basicConfig(
            stream=sys.stdout,
            format=format,
            datefmt=datefmt,
            level=logging.DEBUG)
    else:
        logging.basicConfig(
            stream=sys.stdout,
            format=format,
            datefmt=datefmt,
            level=logging.INFO)

    loop = asyncio.get_event_loop()
    
    for s in [SIGINT, SIGTERM]:
        loop.add_signal_handler(s, cancel)

    try:
       loop.run_until_complete(main())
    except asyncio.exceptions.CancelledError:
        pass
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
