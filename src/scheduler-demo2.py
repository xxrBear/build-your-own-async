"""
并发实现任务调度，并且不使用线程


deque: 快速创建双端队列
参考： https://blog.csdn.net/weixin_43790276/article/details/107749745

任务调度器实现2

1.自定义过期时间
2.增加 call_later 函数
3.增加 sleeping 休眠函数列表
"""

import time
from collections import deque


class Scheduler:
    def __init__(self):
        self.ready = deque()  # 双端队列
        self.sleeping = []

    def call_soon(self, func):
        self.ready.append(func)

    def call_later(self, delay, func):
        deadline = time.time() + delay
        self.sleeping.append((deadline, func))
        self.sleeping.sort()

    def run(self):
        while self.ready or self.sleeping:
            if not self.ready:
                deadline, func = self.sleeping.pop(0)
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
