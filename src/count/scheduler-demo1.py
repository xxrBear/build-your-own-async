"""
并发实现任务调度，并且不使用线程

任务调度器实现

deque: 快速创建双端队列
参考： https://blog.csdn.net/weixin_43790276/article/details/107749745
"""

import time
from collections import deque


class Scheduler:
    def __init__(self):
        self.ready = deque()  # 双端队列

    def call_soon(self, func):
        self.ready.append(func)

    def run(self):
        while self.ready:
            func = self.ready.popleft()
            func()


def countdown(n):
    if n > 0:
        time.sleep(1)
        print('Down', n)
        s.call_soon(lambda: countdown(n - 1))


def countup(stop):
    def _run(x=0):
        if x < stop:
            time.sleep(1)
            print('Up', x)
            s.call_soon(lambda: _run(x + 1))

    _run(0)


s = Scheduler()
s.call_soon(lambda: countdown(5))
s.call_soon(lambda: countup(5))
s.run()
