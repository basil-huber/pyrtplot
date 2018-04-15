from groundcontrol.utils import CircBuffer
from pylab import *
import tkinter as tk
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import threading
import time
from groundcontrol.menu import AxisMenu

class RtPlot(tk.Frame, threading.Thread):
    def __init__(self, parent, data_buffer_dict, x_buffer, lock):
        tk.Frame.__init__(self, parent)
        threading.Thread.__init__(self)

        self.x_buffer = x_buffer
        self.lock = lock
        self.axis_menu = AxisMenu(self)
        self.axis_menu.pack(side=tk.LEFT)

        self.subplots_dict = {}
        self.fig, self.axes = subplots(len(data_buffer_dict),1, sharex=True)
        for i,var in enumerate(sorted(data_buffer_dict)):
            sp = {}
            sp['axis'] = self.axes[i]
            sp['buffer'] = data_buffer_dict[var]
            self.subplots_dict[var] = sp

        # self.draw_fig()

        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

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
            if self.lock:
                self.lock.acquire()
            axis.plot(self.x_buffer.head_view(500),sp['buffer'].head_view(500))
            if self.lock:
                self.lock.release()
            axis.set_ylim(self.axis_menu.get_limits())