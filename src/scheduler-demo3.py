"""
并发实现任务调度，并且不使用线程


deque: 快速创建双端队列
参考： https://blog.csdn.net/weixin_43790276/article/details/107749745

heapq: python 实现 堆
参考：https://blog.csdn.net/weixin_43790276/article/details/107741332

任务调度器实现3

1.heapq 替换 sleeping 列表
2.增加 sequence 解决相同日期排序可能出现的 bug
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


def countdown(n):
    if n > 0:
        # time.sleep(1)
        print('Down', n)
        s.call_later(4, lambda: countdown(n - 1))


def countup(stop):
    def _run(x=0):
        if x < stop:
            # time.sleep(1)
            print('Up', x)
            s.call_later(1, lambda: _run(x + 1))

    _run(0)


s = Scheduler()
s.call_soon(lambda: countdown(5))
s.call_soon(lambda: countup(20))
s.run()
