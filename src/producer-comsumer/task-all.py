"""
生产者-消费者 yield 调度器示例
"""
import time
import heapq
from collections import deque


# 基于回调的调度器（来自之前的内容）
class Scheduler:
    def __init__(self):
        self.ready = deque()
        self.current = None
        self.sequence = 0
        self.sleeping = []

    def call_soon(self, func):
        self.ready.append(func)

    def call_later(self, delay, func):
        self.sequence += 1
        deadline = time.time() + delay
        heapq.heappush(self.sleeping, (deadline, self.sequence, func))

    def run(self):
        while self.ready or self.sleeping:
            if not self.ready:
                # Find the nearest deadline
                deadline, _, func = heapq.heappop(self.sleeping)
                delta = deadline - time.time()
                if delta > 0:
                    time.sleep(delta)
                self.ready.append(func)

            while self.ready:
                func = self.ready.popleft()
                func()

    def new_task(self, coro):
        self.ready.append(Task(coro))

    async def sleep(self, delay):
        self.call_later(delay, self.current)
        self.current = None
        await switch()


# 封装协程的类 —— 使其看起来像一个回调函数
class Task:
    def __init__(self, coro):
        self.coro = coro

    def __call__(self):
        try:
            # 像之前一样驱动协程
            sched.current = self
            self.coro.send(None)
            if sched.current:
                sched.ready.append(self)
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


# sched.run()

# Call-back based tasks
def countdown(n):
    if n > 0:
        print('Down', n)
        # time.sleep(4)    # Blocking call (nothing else can run)
        sched.call_later(4, lambda: countdown(n - 1))


def countup(stop):
    def _run(x):
        if x < stop:
            print('Up', x)
            # time.sleep(1)
            sched.call_later(1, lambda: _run(x + 1))

    _run(0)


sched.call_soon(lambda: countdown(5))
sched.call_soon(lambda: countup(20))
sched.run()
