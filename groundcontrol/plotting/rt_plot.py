from groundcontrol.utils import CircBuffer
import random

buffer = CircBuffer(max_len=1000, shape=(1000,))
buffer.push(0)
buffer.push(0)
buffer.push(0)

from pylab import *
import tkinter as tk
from drawnow import drawnow, figure

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import threading
import time
from groundcontrol.menu import AxisMenu

class RtPlot(tk.Frame, threading.Thread):
    def __init__(self, parent, data_buffer_dict, x_buffer, lock):
        tk.Frame.__init__(self, parent)
        threading.Thread.__init__(self)

        self.x_buffer = x_buffer

        self.axis_menu = AxisMenu(self)
        self.axis_menu.pack(side=tk.LEFT)

        canvas = tk.Canvas(parent);#, width=w, height=h)
        canvas.pack()

        self.subplots_dict = {}
        self.fig, self.axes = subplots(len(data_buffer_dict),1, sharex=True)
        for i,var in enumerate(sorted(data_buffer_dict)):
            sp = {}
            print(var)
            sp['axis'] = self.axes[i]
            sp['buffer'] = data_buffer_dict[var]
            self.subplots_dict[var] = sp

        self.draw_fig()

        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        # _thread.start_new_thread ( self.thread, () )

    def run(self):
        while True:
            try:
                self.update()
            except:
                break

    def update(self):
        self.draw_fig()
        self.canvas.draw()
        time.sleep(0.01)

    def draw_fig(self):
        for sp in self.subplots_dict.values():
            axis = sp['axis']
            axis.clear()
            lock.acquire()
            axis.plot(self.x_buffer.head_view(500),sp['buffer'].head_view(500))
            lock.release()
            axis.set_ylim(self.axis_menu.get_limits())

data_buffer_dict = {}
for i in range(0,3):
    data_buffer_dict['var%d' % (i)] = CircBuffer(max_len=5000, shape=(5000,))
    data_buffer_dict['var%d' % (i)].push(0)
x_buffer = CircBuffer(max_len=5000, shape=(5000,))
x_buffer.push(0)

lock = threading.Lock()

root = tk.Tk()
window = tk.Toplevel(root)
rt_plot = RtPlot(window, data_buffer_dict, x_buffer, lock)
rt_plot.pack()

class DummyReader(threading.Thread):
    def __init__(self, lock):
        threading.Thread.__init__(self)
        self.lock = lock
    def run(self):
        i=3
        while 1:
            lock.acquire()
            for b in data_buffer_dict.values():
                b.push(b.head_view(1)[0] + (2*random()-1))
            x_buffer.push(i)
            lock.release()
            i += 1
            time.sleep(0.001)

dummy = DummyReader(lock)
dummy.start()
rt_plot.start()

from tkinter import messagebox
def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        root.destroy()
root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()