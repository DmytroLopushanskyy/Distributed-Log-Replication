import asyncio


class CountDownLatch:
    def __init__(self, count=1):
        self.count = count
        self.lock = asyncio.Condition()

    async def count_down(self):
        await self.lock.acquire()
        self.count -= 1
        if self.count <= 0:
            self.lock.notify_all()
        self.lock.release()

    async def wait(self):
        await self.lock.acquire()
        while self.count > 0:
            await self.lock.wait()
        self.lock.release()
