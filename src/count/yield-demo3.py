# Build Your Own Async
#
# David Beazley (@dabeaz)
# https://www.dabeaz.com
#
# Originally presented at PyCon India, Chennai, October 14, 2019
# 使用 yield 关键字，完成任务

# 在这个示例中，我们要完成如何使调度函数 支持任务休眠时，自动切换函数（就像调度器示例那样）

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


async def countdown(n):
    while n > 0:
        print('Down', n)
        # time.sleep(1)
        await sched.sleep(4)
        n -= 1


async def countup(stop):
    x = 0
    while x < stop:
        print('Up', x)
        # time.sleep(1)
        await sched.sleep(1)
        x += 1


# Example of sequential execution

sched = Scheduler()
sched.new_task(countdown(5))
sched.new_task(countup(20))
sched.run()
