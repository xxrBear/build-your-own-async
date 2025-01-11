# Build Your Own Async
#
# David Beazley (@dabeaz)
# https://www.dabeaz.com
#
# Originally presented at PyCon India, Chennai, October 14, 2019

# 使用 yield 关键字，完成任务

# 在示例1，我们已经完成了任务，现在让我们隐藏 yield，并理解新版本的 python 特性

import time
from collections import deque


class Scheduler:
    def __init__(self):
        self.ready = deque()
        self.current = None

    def new_task(self, coro):
        self.ready.append(coro)

    def run(self):
        while self.ready:
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
        time.sleep(1)
        await switch()
        n -= 1


async def countup(stop):
    x = 0
    while x < stop:
        print('Up', x)
        time.sleep(1)
        await switch()
        x += 1


# Example of sequential execution

sched = Scheduler()
sched.new_task(countdown(5))
sched.new_task(countup(5))
sched.run()
