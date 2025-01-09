"""
生产者-消费者 线程安全的示例
"""
import time
import queue
import threading


def producer(q, count):
    for n in range(count):
        print('Producing', n)
        q.put(n)

        time.sleep(1)
    print('Producer done')
    q.put(None)  # 哨兵值，表示生产者停止生产消息


def consumer(q):
    while True:
        item = q.get()  # 线程安全的方法

        if item is None:
            break
        print('Consuming', item)

    print('Consumer done')


q = queue.Queue()
threading.Thread(target=producer, args=(q, 10)).start()
threading.Thread(target=consumer, args=(q,)).start()
