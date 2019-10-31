import random
from collections import deque
import time

MAX_STRING = 500
MEMORY_REFERENCE_TIMES = 100000
FRAME_list = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]


def random_reference():
    return [random.randint(1, MAX_STRING) for _ in range(MEMORY_REFERENCE_TIMES)]


def locality_reference():
    locality_table = list()

    while(len(locality_table) <= MEMORY_REFERENCE_TIMES):
        interval_range = random.randint(MAX_STRING * 0.05, MAX_STRING * 0.1)
        interval_loc = random.randint(1, MAX_STRING)

        if interval_loc + interval_range <= MAX_STRING:
            locality_table.extend([random.randint(
                interval_loc, interval_loc + interval_range) for _ in range(random.randint(500, 1000))])
        else:
            locality_table.extend([random.randint(
                interval_loc - interval_range, interval_loc) for _ in range(random.randint(500, 1000))])

    return locality_table[:MEMORY_REFERENCE_TIMES]


def random_noramlvariate():
    noramlvariate_table = list()

    for _ in range(MEMORY_REFERENCE_TIMES):
        tmp = 0
        while(tmp < 1 or tmp > MAX_STRING):
            tmp = int(random.normalvariate(int(MAX_STRING / 2), int(MAX_STRING / 5)))
        noramlvariate_table.append(tmp)
    
    return noramlvariate_table


def random_dirty_bits():
    return [random.randint(0, 1) for _ in range(MEMORY_REFERENCE_TIMES)]


def FIFO(process_table, dirty_bits, frame_size):
    page_fault = 0
    interrupt = 0
    write_back = 0

    frame_queue = deque(maxlen=frame_size)

    for frame_iter, frame_id in enumerate(process_table):
        hit_flag = False
        for frame_dict in frame_queue:
            if frame_id == frame_dict['id']:
                temp_dict = frame_dict
                if dirty_bits[frame_iter]:
                    temp_dict['mod'] = dirty_bits[frame_iter]
                frame_queue[frame_queue.index(frame_dict)] = temp_dict
                hit_flag = True
                break

        if hit_flag:
            continue

        if len(frame_queue) == frame_size:
            if frame_queue.popleft()['mod']:
                write_back += 1
                interrupt += 1

        temp_dict = dict()
        temp_dict['id'] = frame_id
        temp_dict['mod'] = dirty_bits[frame_iter]
        frame_queue.append(temp_dict)

        page_fault += 1
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
                if frame in frame_list and victim_list[frame_list.index(frame)] == 0:
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
    # implementation url: http://courses.cs.tamu.edu/bart/cpsc410/Supplements/Slides/page-rep3.pdf

    def generate_dict(id, ref_bit, mod_bit):
        return({'id': id, 'ref': ref_bit, 'mod': mod_bit})

    def search_victim(frame_queue, frame_id, dirty_bit):
        for _ in range(0, 2):
            # Step a
            for frame_dict in frame_queue:
                if frame_dict['ref'] == 0 and frame_dict['mod'] == 0:
                    frame_queue.remove(frame_dict)
                    frame_queue.append(generate_dict(frame_id, 1, dirty_bit))

                    return frame_queue, 0

            # Step b
            for index, frame_dict in enumerate(list(frame_queue)):
                if frame_dict['ref'] == 0 and frame_dict['mod'] == 1:
                    frame_queue.remove(frame_dict)
                    frame_queue.append(generate_dict(frame_id, 1, dirty_bit))

                    return frame_queue, 1
                else:
                    frame_queue.remove(frame_dict)
                    frame_dict['ref'] = 0
                    frame_queue.insert(index, frame_dict)

    page_fault = 0
    interrupt = 0
    write_back = 0

    frame_queue = deque(maxlen=frame_size)

    for frame_iter, frame_id in enumerate(process_table):

        # search hit
        hit_flag = False
        for frame_dict in frame_queue:
            if frame_id == frame_dict['id']:
                hit_flag = True
                break

        if hit_flag:
            continue

        if len(frame_queue) == frame_size:

            frame_queue, write_flag = search_victim(frame_queue, frame_id, dirty_bits[frame_iter])

            if write_flag:
                write_back += 1
                interrupt += 1

        frame_queue.append(generate_dict(frame_id, 1, dirty_bits[frame_iter]))

        page_fault += 1
        interrupt += 1

    return page_fault, interrupt, write_back


def enhance_FIFO(process_table, dirty_bits, frame_size):
    page_fault = 0
    interrupt = 0
    write_back = 0

    frame_queue = deque(maxlen=frame_size)

    for frame_iter, frame_id in enumerate(process_table):
        if frame_id in frame_queue:
            continue

        if len(frame_queue) == frame_size:
            if abs(frame_id - frame_queue[-1]) > abs(frame_id - frame_queue[0]):
                frame_queue.pop()
            else:
                frame_queue.popleft()
        else:
            frame_queue.append(frame_id)

        page_fault += 1
        interrupt += 1

        if dirty_bits[frame_iter] == 1:
            write_back += 1
            interrupt += 1

    return page_fault, interrupt, write_back


def QQ(process_table, dirty_bits, frame_size):
    page_fault = 0
    interrupt = 0
    write_back = 0

    frame_queue = deque(maxlen=frame_size)

    for frame_iter, frame_id in enumerate(process_table):
        hit_flag = False
        for frame_dict in frame_queue:
            if frame_id == frame_dict['id']:
                temp_dict = frame_dict
                if dirty_bits[frame_iter]:
                    temp_dict['mod'] = 1
                frame_queue[frame_queue.index(frame_dict)] = temp_dict
                hit_flag = True
                break

        if hit_flag:
            continue

        if len(frame_queue) == frame_size:
            for frame_dict in frame_queue:
                if frame_dict['mod'] == 0:
                    frame_queue.remove(frame_dict)
                    break

            if len(frame_queue) == frame_size:
                frame_queue.popleft()
                write_back += 1
                interrupt += 1

        temp = dict()
        temp['id'] = frame_id
        temp['mod'] = dirty_bits[frame_iter]
        frame_queue.append(temp)

        page_fault += 1
        interrupt += 1

    return page_fault, interrupt, write_back


if __name__ == '__main__':
    frmae_table = random_reference()
    dirty_bits = random_dirty_bits()

    for frame_size in FRAME_list:
        start = time.process_time()
        print("FIFO:", FIFO(frmae_table, dirty_bits, frame_size))
        print("ESC:", enhance_second_chance(frmae_table, dirty_bits, frame_size))
        print("MYAL:", QQ(frmae_table, dirty_bits, frame_size))
        print("Opt:", Optimal(frmae_table, dirty_bits, frame_size))
        print("Exec time:", time.process_time() - start)

