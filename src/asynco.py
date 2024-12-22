# asynco.py
#
# 基本的异步调度器，支持时间管理

import time
from collections import deque
import heapq


class Scheduler:
    def __init__(self):
        self.ready = deque()  # 准备好执行的函数
        self.sleeping = []  # 睡眠函数
        self.sequence = 0  # 用于打破优先队列中的平局

    def call_soon(self, func):
        self.ready.append(func)

    def call_later(self, delay, func):
        self.sequence += 1
        deadline = time.time() + delay  # Expiration time
        heapq.heappush(self.sleeping, (deadline, self.sequence, func))

    def run(self):
        while self.ready or self.sleeping:
            if not self.ready:
                # 查找最近的截止日期
                deadline, _, func = heapq.heappop(self.sleeping)
                delta = deadline - time.time()
                if delta > 0:
                    time.sleep(delta)
                self.ready.append(func)

            while self.ready:
                func = self.ready.popleft()
                func()


sched = Scheduler()  # Behind scenes scheduler object


def countdown(n):
    if n > 0:
        print('Down', n)
        # time.sleep(4)
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
