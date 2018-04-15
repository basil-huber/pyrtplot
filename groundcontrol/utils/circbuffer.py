import numpy as np

import numpy as np

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


