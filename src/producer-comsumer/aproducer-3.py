"""
实现与 生产者-消费者-线程安全 示例一样的功能，而不是用线程

示例2已经完成了 任务队列 的基本使用

现在让我们解决如下问题

1.当 生产者 不生产消息时，如何保证任务继续运行
2.
"""
import heapq
import time
from collections import deque


class Result:
    def __init__(self, value=None, exc=None):
        self.value = value
        self.exc = exc

    def result(self):
        if self.exc:
            raise self.exc
        else:
            return self.value


class Scheduler:
    def __init__(self):
        self.ready = deque()  # 双端队列
        self.sleeping = []
        self.sequence = 0

    def call_soon(self, func):
        self.ready.append(func)

    def call_later(self, delay, func):
        self.sequence += 1
        deadline = time.time() + delay
        heapq.heappush(self.sleeping, (deadline, self.sequence, func))

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


class QueueClosed(Exception):
    pass


class AsyncQueue:
    """
    自定义任务队列
    """

    def __init__(self):
        self.items = deque()
        self.waiting = deque()
        self._closed = False

    def close(self):
        self._closed = True
        if self.waiting and not self.items:
            for func in self.waiting:
                sched.call_soon(func)

    def put(self, item):
        if self._closed:
            raise QueueClosed()

        self.items.append(item)
        if self.waiting:
            func = self.waiting.popleft()
            # func()  ==> 不直接调用函数，防止深度递归

            sched.call_soon(func)

    def get(self, callback):
        # 等待直到有项目可用，然后返回它
        if self.items:
            callback(Result(value=self.items.popleft()))  # 好的结果
        else:
            # 没有项目可用（必须等待）
            if self._closed:
                callback(Result(exc=QueueClosed()))
            else:
                self.waiting.append(lambda: self.get(callback))


def producer(q, count):
    def _run(n):
        if n < count:
            print('Producing', n)
            q.put(n)
            sched.call_later(1, lambda: _run(n + 1))
        else:
            print('Producer done')
            q.close()

    _run(0)


def consumer(q):
    def _consume(result):
        try:
            item = result.result()
            print('Consuming', item)
            sched.call_soon(lambda: consumer(q))
        except QueueClosed:
            print('Consumer done')

    q.get(callback=_consume)


q = AsyncQueue()
sched.call_soon(lambda: producer(q, 10))
sched.call_soon(lambda: consumer(q, ))
sched.run()
