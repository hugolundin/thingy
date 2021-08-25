from serial.serialutil import EIGHTBITS, PARITY_NONE, STOPBITS_ONE
from asyncio.events import get_event_loop
from signal import SIGINT, SIGTERM
from nats.aio.client import Client
import argparse
import asyncio
import logging
import serial
import sys

# TODO: 
# - Generic read/write with something else.
# - Logging colors

UART_EVENT_IN = 0
UART_EVENT_OUT = 1
NATS_EVENT_IN = 2
NATS_EVENT_OUT = 3
PERIODIC_EVENT = 4

class Event:
    def __init__(self, category, data):
        self.category = category
        self.data = data

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

UART_ADDR = 'uart'

def handle_uart(queue, uart):
    data = uart.read_all()
    asyncio.create_task(queue.put(Event(UART_EVENT_IN, data)))

async def periodic(queue, interval=1):
    while True:
        await queue.put(Event(PERIODIC_EVENT, 'hi!'))
        await asyncio.sleep(interval)

async def transmission(commands, queue):
    last_was_left = False
    l = logging.getLogger('transmission')

    while True:
        command = await commands.get()
        
        if command.command == COMMAND_RIGHT:
            l.debug('COMMAND_RIGHT')

            if last_was_left:
                l.debug('Queueing UART_EVENT_OUT')
                await queue.put(Event(UART_EVENT_OUT, 'left -> right'))

        if command.command == COMMAND_LEFT:
            l.debug('COMMAND_LEFT')
            last_was_left = True
        else:
            last_was_left = False

async def main():
    loop = asyncio.get_event_loop()
    queue = asyncio.Queue()
    commands = asyncio.Queue()

    uart = serial.Serial(
        port=UART_ADDR,
        baudrate=115200,
        bytesize=EIGHTBITS,
        parity=PARITY_NONE,
        stopbits=STOPBITS_ONE
    )
    loop.add_reader(uart.fileno(), handle_uart, queue, uart)

    nats = Client()
    await nats.connect('localhost:4222', loop=get_event_loop())

    async def nats_cb(msg):
        await queue.put(Event(NATS_EVENT_IN, msg))

    await nats.subscribe('transmission.in.>', 'workers', nats_cb)

    # asyncio.create_task(periodic(queue, interval=5))
    asyncio.create_task(transmission(commands, queue))

    l = logging.getLogger('main')

    while True:
        event = await queue.get()

        if event.category == UART_EVENT_OUT:
            l.debug(f'UART_EVENT_OUT: {event.data}')
            uart.write(event.data.encode())

        if event.category == UART_EVENT_IN:
            # Incoming sensor reading
            pass

        if event.category == NATS_EVENT_OUT:
            l.debug(f'NATS_EVENT_OUT: {event.data}')
            nats.publish('thingy.out', event.data)

        if event.category == NATS_EVENT_IN:
            subject = event.data.subject
            l.debug(f'NATS_EVENT_IN: {subject}: {event.data.data}')

            if subject == 'transmission.in.left':
                await commands.put(Command(COMMAND_LEFT, PRIORITY_MANUAL))
            elif subject == 'transmission.in.right':
                await commands.put(Command(COMMAND_RIGHT, PRIORITY_MANUAL))

        if event.category == PERIODIC_EVENT:
            print(event.data)

def cancel():
    for t in asyncio.all_tasks():
        t.cancel()

# https://stackoverflow.com/questions/29475007/python-asyncio-reader-callback-and-coroutine-communication

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true')

    args = parser.parse_args()
    format = '[%(asctime)s] [%(name)s]: %(message)s'
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
