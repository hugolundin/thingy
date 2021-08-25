from os import putenv
from serial.serialutil import EIGHTBITS, PARITY_NONE, STOPBITS_ONE
import serial
import asyncio

# TODO: 
# - Argument passing (we don't want uart to be a global)
# - Add readers where? Is this OK? 
# - Integrate with NATS/MQTT/other things.
# - Generic read/write with something else.

UART_EVENT = 0

class Event:
    def __init__(self, category, data):
        self.category = category
        self.data = data

# Run in the same folder as this file:
# socat PTY,link=test,raw,echo=0 -
UART_ADDR = 'test'

uart = serial.Serial(
    port=UART_ADDR,
    baudrate=115200,
    bytesize=EIGHTBITS,
    parity=PARITY_NONE,
    stopbits=STOPBITS_ONE)

queue = asyncio.Queue()

def handle_uart():
    data = uart.read_all()
    queue.put_nowait(Event(UART_EVENT, data))

async def periodic():
    while True:
        await asyncio.sleep(0.5)
        print('Periodic!')

async def event_dispatch():
    while True:
        event = await queue.get()

        if (event.category == UART_EVENT):
            print(f'Received: {event.data}')

            uart.write(b'pong\n')

async def main():
    tasks = [
        event_dispatch(),
        periodic()
    ]

    await asyncio.gather(*tasks)

# https://stackoverflow.com/questions/29475007/python-asyncio-reader-callback-and-coroutine-communication
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.add_reader(uart.fileno(), handle_uart)

    try:
       loop.run_until_complete(main())
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
