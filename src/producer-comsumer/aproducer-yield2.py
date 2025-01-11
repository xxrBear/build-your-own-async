"""
生产者-消费者 yield 调度器示例
"""
import time
import heapq
from collections import deque


class Scheduler:
    def __init__(self):
        self.ready = deque()
        self.current = None
        self.sequence = 0
        self.sleeping = []

    def new_task(self, coro):
        self.ready.append(coro)

    def call_soon(self, func):
        self.ready.append(func)

    def call_later(self, delay, func):
        self.sequence += 1
        deadline = time.time() + delay
        heapq.heappush(self.sleeping, (deadline, self.sequence, func))

    async def sleep(self, delay):
        deadline = time.time() + delay
        self.sequence += 1
        heapq.heappush(self.sleeping, (deadline, self.sequence, self.current))
        self.current = None  # "消失"
        await switch()  # 任务切换

    def run(self):
        while self.ready or self.sleeping:
            if not self.ready:
                deadline, _, self.current = heapq.heappop(self.sleeping)
                delay = deadline - time.time()
                if delay > 0:
                    time.sleep(delay)
                self.ready.append(self.current)

            self.current = self.ready.popleft()
            try:
                # next(self.current)
                self.current.send(None)  # 如果 send(None)，其行为等同于调用 next()，即不会传递任何值到生成器
                if self.current:
                    self.ready.append(self.current)
            except StopIteration:
                pass


class Awaitable:
    def __await__(self):  # await 关键词调用的 特殊方法
        yield


# 任务切换函数
def switch():
    return Awaitable()


sched = Scheduler()


class QueueClosed(Exception):
    pass


class AsyncQueue:
    def __init__(self):
        self.items = deque()
        self.waiting = deque()
        self._closed = False

    def close(self):
        self._closed = True
        if self.waiting and not self.items:
            sched.ready.append(self.waiting.popleft())

    async def put(self, item):
        if self._closed:
            raise QueueClosed()

        self.items.append(item)
        if self.waiting:
            sched.ready.append(self.waiting.popleft())

    async def get(self):
        while not self.items:
            if self._closed:
                raise QueueClosed()

            self.waiting.append(sched.current)  # 推送自己到等待队列
            sched.current = None  # 消失
            await switch()  # 切换到另一个任务
        return self.items.popleft()


async def producer(q, count):
    for n in range(count):
        print('Producing', n)
        await q.put(n)
        await sched.sleep(1)
    print('Producer done')
    q.close()


async def consumer(q):
    try:
        while True:
            item = await q.get()  # 线程安全的方法
            print('Consuming', item)
    except QueueClosed:
        print('Consumer done')


q = AsyncQueue()
sched.new_task(producer(q, 10))
sched.new_task(consumer(q))
sched.run()
