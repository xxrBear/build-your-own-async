# Build Your Own Async
#
# David Beazley (@dabeaz)
# https://www.dabeaz.com
#
# Originally presented at PyCon India, Chennai, October 14, 2019

# 使用 yield 关键字，完成任务

import time
from collections import deque


class Scheduler:
    def __init__(self):
        self.ready = deque()
        self.current = None

    def new_task(self, gen):
        self.ready.append(gen)

    def run(self):
        while self.ready:
            self.current = self.ready.popleft()
            try:
                next(self.current)  # 调用一个 生成器
                if self.current:
                    self.ready.append(self.current)
            except StopIteration:
                pass


def countdown(n):
    while n > 0:
        print('Down', n)
        time.sleep(1)
        yield
        n -= 1


def countup(stop):
    x = 0
    while x < stop:
        print('Up', x)
        time.sleep(1)
        yield
        x += 1


# Example of sequential execution

sched = Scheduler()
sched.new_task(countdown(5))
sched.new_task(countup(5))
sched.run()
