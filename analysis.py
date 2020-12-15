from csv import reader, writer
from itertools import islice
from collections import defaultdict

from terminalHelpers import ProgressMeter

def file_iter(path):
    with open(path) as f:
        r = reader(f, delimiter='\t')
        header = next(r)
        for a, b, v in r:
            yield a, b, int(v)

def get_file_len(path):
    for i, _ in enumerate(file_iter(path)):
        pass
    return i + 1

def int_iter(path):
    for _, _, v in file_iter(path):
        yield v

def make_buckets(path):
    nums = list(int_iter(path))
    max_value = max(nums)
    print('max', max_value)
    buckets = [0] * 50
    for v in nums:
        buckets[(v - 1) // 5] += 1
    i = len(buckets) - 1
    while buckets[i] == 0:
        del buckets[i]
        i -= 1
    
    for i, v in enumerate(buckets):
        print(i * 5, '-', i * 5 + 5, ':', f'{v:>8}')
    return buckets

def make_globs(path, threshold):
    word_to_glob_key = dict()

    def add_to(dest_word: str, add_word: str):
        word_to_glob_key[add_word] = word_to_glob_key[dest_word]

    def merge_into(dest_glob_key: int, move_glob_key: int):
        for word, key in word_to_glob_key.items():
            if key == move_glob_key:
                word_to_glob_key[word] = dest_glob_key

    last_key = -1
    meter = ProgressMeter()
    file_len = get_file_len()
    for i, (w0, w1, score) in enumerate(file_iter()):
        meter.update_meter(100 * i / file_len)
        if score > threshold:
            continue
        
        w0_in, w1_in = w0 in word_to_glob_key, w1 in word_to_glob_key
        if w0_in and w1_in:
            merge_into(word_to_glob_key[w0], word_to_glob_key[w1])
        elif w0_in:
            add_to(w0, w1)
        elif w1_in:
            add_to(w1, w0)
        else:
            last_key += 1
            word_to_glob_key[w0] = last_key
            word_to_glob_key[w1] = last_key

    print(len(word_to_glob_key))
    globs = defaultdict(list)
    for k, v in word_to_glob_key.items():
        globs[v].append(k)
    return globs.values()


if __name__ == "__main__":
    # for glob in islice(make_globs(4), 10):
    #     print(', '.join(glob))
    make_buckets('inverse-output.csv')
    # with open('globs.csv', 'w+') as f:
    #     writer(f).writerows(make_globs(3))
