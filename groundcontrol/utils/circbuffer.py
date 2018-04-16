import numpy as np
from collections import OrderedDict
import threading

class CircBuffer():
    def __init__(self, max_len, width=1, dtype=float):
        self.max_len = max_len
        self.width = width
        self.head = -1
        self.length = 0
        self.array = np.ndarray(shape=(max_len,width), dtype=float)
        self.array.fill(np.nan)

    def push(self, value):
        if self.length < self.max_len:
            self.head += 1
            self.length += 1
        else:
            self.head = (self.head + 1) % (self.length)
        self.array[self.head,:] = value

    def head_view(self,count):
        tail = self.head + 1 - count
        if tail >= 0:
            return self.array[tail:self.head+1,:]
        elif self.length < self.max_len:
            return self.array[0:self.head+1,:]
        else:
            return np.concatenate((self.array[tail:self.length+1,:],self.array[0:self.head+1,:]))#, self.array[tail:self.length+1])

class BufferIndexedCollection():
    def __init__(self, variables, max_len):
        self.buffer_list = OrderedDict()
        for v in variables:
            self.buffer_list[v[0]] = CircBuffer(max_len, v[1])
        self.index_buffer = CircBuffer(max_len, 1)
        self.lock = threading.Lock()

    def variables(self):
        return self.buffer_list.keys()

    def push(self, index, values):
        self.lock.acquire()
        for value,var_buffer in zip(values, self.buffer_list.values()):
            var_buffer.push(value)
        self.index_buffer.push(index)
        self.lock.release()

    def head_view(self, var, count):
        self.lock.acquire()
        values = (self.index_buffer.head_view(count), self.buffer_list[var].head_view(count))
        self.lock.release()
        return values

    def __len__(self):
        return len(self.buffer_list)

