import asyncio
import logging

class EventQueue:
    def __init__(self):
        self.queue = asyncio.Queue()
        self.events = {}
        self.logger = logging.getLogger('EventQueue')

    def register(self, event, callback, user_data=None):
        self.events[event] = (callback, user_data)

    def insert(self, event, data):
        asyncio.create_task(self.queue.put((event, data)))
    
    async def insert_async(self, event, data):
        await self.queue.put((event, data))

    async def run(self):
        while True:
            event, data = await self.queue.get()

            try:
                callback, user_data = self.events[event]
                await callback(self, data, user_data)
            except KeyError:
                self.logger.info(f'No callback registered for {event}')
    
