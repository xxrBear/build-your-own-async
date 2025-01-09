"""
实现与 生产者-消费者-线程安全 示例一样的功能，而不是用线程

难点：实现自己的任务队列
"""
import heapq
import time
from collections import deque


class Scheduler:
    def __init__(self):
        self.ready = deque()  # 双端队列
        self.sleeping = []
        self.sequence = 0

    def call_soon(self, func):
        self.ready.append(func)

    def call_later(self, delay, func):
        deadline = time.time() + delay
        heapq.heappush(self.sleeping, (deadline, self.sequence + 1, func))

    def run(self):
        while self.ready or self.sleeping:
            if not self.ready:
                deadline, _, func = heapq.heappop(self.sleeping)
                delta = deadline - time.time()
                if delta > 0:
                    time.sleep(delta)
                self.ready.append(func)

            while self.ready:
                func = self.ready.popleft()
                func()


sched = Scheduler()


class AsyncQueue:
    """
    自定义任务队列
    """

    def __init__(self):
        self.items = deque()
        self.waiting = deque()

    def put(self, item):
        self.items.append(item)
        if self.waiting:
            func = self.waiting.popleft()
            # func()  ==> 不直接调用函数，防止深度递归
            sched.call_soon(func)

    def get(self, callback):
        # 等待直到有项目可用，然后返回它
        if self.items:
            callback(self.items.popleft())
        else:
            self.waiting.append(lambda: self.get(callback))  # 一直等???


def producer(q, count):
    for n in range(count):
        print('Producing', n)
        q.put(n)
        time.sleep(1)

    print('Producer done')
    q.put(None)


def consumer(q):
    while True:
        item = q.get()  # 线程安全的方法
        if item is None:
            break

        print('Consuming', item)
    print('Consumer done')