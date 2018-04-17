from groundcontrol.utils import CircBuffer
from pylab import *
import tkinter as tk
from _tkinter import TclError
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import threading
import time
from groundcontrol.menu import axis_menu

class RtPlot(tk.Frame, threading.Thread):
    REFRESH_PERIOD = 0.01 # [s]

    def __init__(self, parent, buffers):
        tk.Frame.__init__(self, parent)
        threading.Thread.__init__(self, daemon=True)

        self.buffers = buffers

        self.fig, self.axes = subplots(len(buffers),1, sharex=True)
        self.subplots_dict = {}
        for i,var in enumerate(sorted(buffers.get_variables())):
            self.subplots_dict[var] = {'axis': self.axes[i]}
        self.fig.tight_layout()

        # create y axis menu
        plot_frame = tk.Frame(self)
        axis_menu_frame = tk.Frame(plot_frame)
        # tk.Label(axis_menu_frame).pack(fill=tk.BOTH, expand=True)
        for name, sp in self.subplots_dict.items():
            tk.Label(axis_menu_frame).pack(fill=tk.BOTH, expand=True)
            sp['axis_menu'] = axis_menu.Y(axis_menu_frame, name)
            sp['axis_menu'].pack()#fill=tk.Y, expand=True)
            tk.Label(axis_menu_frame).pack(fill=tk.BOTH, expand=True)
        axis_menu_frame.pack(side=tk.LEFT, fill=tk.Y)

        # create canvas for plotting
        self.canvas = FigureCanvasTkAgg(self.fig, plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        plot_frame.pack(fill=tk.BOTH, expand=True)

        # createx axis menu
        bottom_bar = tk.Frame(self)
        tk.Label(bottom_bar, width=axis_menu.Y.DEFAULT_VALUE_WIDTH).pack(fill=tk.NONE, expand=False, side=tk.LEFT)
        self.xaxis_menu_frame = axis_menu.X(bottom_bar, axis_width_max=buffers.max_len())
        self.xaxis_menu_frame.pack(expand = True, fill=tk.X)
        bottom_bar.pack(fill=tk.X, expand = True)


    def run(self):
        self.running = True
        while self.running:
            try:
                self.update()
            except TclError:
               break

    def stop(self):
        self.running = False
        
    def update(self):
        if not self.xaxis_menu_frame.is_paused():
            self.draw_fig()
        self.canvas.draw()
        time.sleep(self.REFRESH_PERIOD)

    def draw_fig(self):
        point_count = self.xaxis_menu_frame.get_axis_width()
        for var,sp in self.subplots_dict.items():
            axis = sp['axis']
            axis.clear()
            points = self.buffers.head_view(var,point_count)
            axis.plot(points[0], points[1])
            axis.set_ylim(sp['axis_menu'].get_limits())