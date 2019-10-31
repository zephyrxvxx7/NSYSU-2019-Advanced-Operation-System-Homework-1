import random
from collections import deque
import time
import argparse

parser = argparse.ArgumentParser(
    description='Page replacement simulator.\nRecommend use pypy3 execute this program.', formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument('mode', metavar='mode',
                    help="Select random reference strings mode\n'random': random reference\n'locality': locality reference\n'normal': normal distribution reference")

parser.add_argument('-m', dest='MAX_STRING', type=int,
                    help='Set the max number of reference string (default: 500)')

parser.add_argument('-r', dest='REFERENCE_TIMES', type=int,
                    help='Set the times of reference string (default: 100000)')


MAX_STRING = 500
MEMORY_REFERENCE_TIMES = 100000
FRAME_list = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

# Generate random reference string 
def random_reference():
    return [random.randint(1, MAX_STRING) for _ in range(MEMORY_REFERENCE_TIMES)]

# Generate locality reference string
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

# Generate normal distribution reference string
def normalvariate_reference():
    noramlvariate_table = list()

    for _ in range(MEMORY_REFERENCE_TIMES):
        tmp = 0
        while(tmp < 1 or tmp > MAX_STRING):
            tmp = int(random.normalvariate(int(MAX_STRING / 2), int(MAX_STRING / 5)))
        noramlvariate_table.append(tmp)
    
    return noramlvariate_table


def random_dirty_bits():
    return [random.randint(0, 1) for _ in range(MEMORY_REFERENCE_TIMES)]


def handle_hit_frame(frame_id, dirty_bit, frame_queue):
    for frame_dict in frame_queue:
        if frame_id == frame_dict['id']:
            if dirty_bit:
                frame_queue[frame_queue.index(frame_dict)]['mod'] = 1

            return True
    
    return False


def FIFO(process_table, dirty_bits, frame_size):
    page_fault = 0
    interrupt = 0
    write_back = 0

    frame_queue = deque(maxlen=frame_size)

    for frame_iter, frame_id in enumerate(process_table):
        if handle_hit_frame(frame_id, dirty_bits[frame_iter], frame_queue):
            continue

        if len(frame_queue) == frame_size:
            if frame_queue.popleft()['mod']:
                write_back += 1
                interrupt += 1

        frame_queue.append({'id': frame_id, 'mod': dirty_bits[frame_iter]})

        page_fault += 1
        interrupt += 1

    return [page_fault, interrupt, write_back]


def Optimal(process_table, dirty_bits, frame_size):

    def search_victim(frame_iter, frame_id, frame_list):
        victim_list = list([0] * frame_size)

        counter = 0
        for index, frame in enumerate(process_table[frame_iter:]):
            if frame in frame_list and victim_list[frame_list.index(frame)] == 0:
                victim_list[frame_list.index(frame)] = index
                counter += 1

            if counter == frame_size - 1:
                break

        return victim_list.index(0)

    page_fault = 0
    frame_list = []

    for frame_iter, frame_id in enumerate(process_table):
        if frame_id in frame_list:
            continue

        if len(frame_list) == frame_size:
            frame_list[search_victim(frame_iter, frame_id, frame_list)] = frame_id
        else:
            frame_list.append(frame_id)

        page_fault += 1

    return [page_fault]


def enhance_second_chance(process_table, dirty_bits, frame_size):
    # implementation url: http://courses.cs.tamu.edu/bart/cpsc410/Supplements/Slides/page-rep3.pdf

    def search_victim(frame_queue, frame_id):
        for _ in range(0, 2):
            # Step a
            for frame_dict in frame_queue:
                if frame_dict['ref'] == 0 and frame_dict['mod'] == 0:
                    frame_queue.remove(frame_dict)
                    return False

            # Step b
            for index, frame_dict in enumerate(list(frame_queue)):
                if frame_dict['ref'] == 0 and frame_dict['mod'] == 1:
                    frame_queue.remove(frame_dict)
                    return True
                else:
                    frame_queue[index]['ref'] = 0

    page_fault = 0
    interrupt = 0
    write_back = 0

    frame_queue = deque(maxlen=frame_size)

    for frame_iter, frame_id in enumerate(process_table):
        if handle_hit_frame(frame_id, dirty_bits[frame_iter], frame_queue):
            continue

        if len(frame_queue) == frame_size:
            if(search_victim(frame_queue, frame_id)):
                write_back += 1
                interrupt += 1

        frame_queue.append({'id': frame_id, 'ref': 1, 'mod': dirty_bits[frame_iter]})

        page_fault += 1
        interrupt += 1

    return [page_fault, interrupt, write_back]

# Not used
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

    return [page_fault, interrupt, write_back]

# Own algorithm, dirty frame is high priority not to kick out.
def QQ(process_table, dirty_bits, frame_size):
    page_fault = 0
    interrupt = 0
    write_back = 0

    frame_queue = deque(maxlen=frame_size)

    for frame_iter, frame_id in enumerate(process_table):
        if handle_hit_frame(frame_id, dirty_bits[frame_iter], frame_queue):
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

        frame_queue.append({'id': frame_id, 'mod': dirty_bits[frame_iter]})

        page_fault += 1
        interrupt += 1

    return [page_fault, interrupt, write_back]


if __name__ == '__main__':
    args = parser.parse_args()

    if args.MAX_STRING:
        MAX_STRING = args.MAX_STRING
    if args.REFERENCE_TIMES:
        MEMORY_REFERENCE_TIMES = args.REFERENCE_TIMES
    
    if args.mode == "random":
        frmae_table = random_reference()
    elif args.mode == "locality":
        frmae_table = locality_reference()
    elif args.mode == "normal":
        frmae_table = normalvariate_reference()
    else:
        parser.print_help()
        exit(2)
    
    dirty_bits = random_dirty_bits()

    def handle_print(result):
        return "\t\t".join(map(str, result))

    print("\t\tPage Fault\tInterrupt\tWrite Back")
    for frame_size in FRAME_list:
        print(f"[Frame size: {frame_size}]")

        start = time.process_time()
        print("FIFO:\t\t", handle_print(FIFO(frmae_table, dirty_bits, frame_size)))
        print("ESC:\t\t", handle_print(enhance_second_chance(frmae_table, dirty_bits, frame_size)))
        print("MYAL:\t\t", handle_print(QQ(frmae_table, dirty_bits, frame_size)))
        print("Opt:\t\t", handle_print(Optimal(frmae_table, dirty_bits, frame_size)))
        print(f"\nExec time:\t {time.process_time() - start}s\n")
