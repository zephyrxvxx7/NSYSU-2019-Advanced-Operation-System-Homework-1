import random
import matplotlib.pyplot as plt
from queue import Queue
from collections import deque
import time

plt.style.use('ggplot')

MAX_STRING = 500
MEMORY_REFERENCE_TIMES = 100000
FRAME_list = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]


def random_reference():
    return [random.randint(1, MAX_STRING) for _ in range(MEMORY_REFERENCE_TIMES)]

def locality_reference():
    pass

def random_dirty_bits():
    return [random.randint(0, 1) for _ in range(MEMORY_REFERENCE_TIMES)]


def FIFO(process_table, dirty_bits, frame_size):
    page_fault = 0
    interrupt = 0
    write_back = 0

    frame_queue = Queue(maxsize=frame_size)

    for frame_iter, frame_id in enumerate(process_table):
        if frame_id in frame_queue.queue:
            continue
        
        if frame_queue.full():
            frame_queue.get()
        
        frame_queue.put(frame_id)

        page_fault += 1
        interrupt += 1

        if dirty_bits[frame_iter] == 1:
            write_back += 1
            interrupt += 1
    
    return page_fault, interrupt, write_back


def Optimal(process_table, dirty_bits, frame_size):
    page_fault = 0
    interrupt = 0
    write_back = 0

    frame_list = []

    for frame_iter, frame_id in enumerate(process_table):
        if frame_id in frame_list:
            continue

        if len(frame_list) == frame_size:
            victim_list = list([0] * frame_size)
            victim_index = 0

            counter = 0
            for index, frame in enumerate(process_table[frame_iter:]):
                if frame in frame_list:
                    victim_list[frame_list.index(frame)] = index
                    counter += 1

                if counter == frame_size - 1:
                    break
            
            for index, _ in enumerate(victim_list):
                if victim_list[index] == 0:
                    victim_list[index] = MEMORY_REFERENCE_TIMES
            
            victim_index = victim_list.index(max(victim_list))
            frame_list[victim_index] = frame_id
        else:
            frame_list.append(frame_id)
        

        page_fault += 1
        interrupt += 1

        if dirty_bits[frame_iter] == 1:
            write_back += 1
            interrupt += 1

    return page_fault, interrupt, write_back


def enhance_second_chance(process_table, dirty_bits, frame_size):
    page_fault = 0
    interrupt = 0
    write_back = 0

    frame_queue = Queue(maxsize=frame_size)

    for frame_iter, frame_id in enumerate(process_table):
        if frame_id in frame_queue.queue:
            continue

        if frame_queue.full():
            print(frame_queue)
            pass # TODO
        else:
            frame_size.put(frame_id)

        page_fault += 1
        interrupt += 1

        if dirty_bits[frame_iter] == 1:
            write_back += 1
            interrupt += 1
    
    return page_fault, interrupt, write_back


if __name__ == '__main__':
    process_table = random_reference()
    dirty_bits = random_dirty_bits()

    for frame_size in FRAME_list:
        start = time.process_time()
        print("FIFO:", FIFO(process_table, dirty_bits, frame_size))        
        # print("Opt:", Optimal(process_table, dirty_bits, frame_size))
        print("Exec time:", time.process_time() - start)
    
    # plt.plot(range(1, MAX_STRING), [process_table.count(i) for i in range(1, MAX_STRING)])
    # plt.show()
            

