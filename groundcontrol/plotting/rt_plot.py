from groundcontrol.utils import CircBuffer
from groundcontrol.menu import axis_menu

import tkinter as tk
from _tkinter import TclError

from pylab import *
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure

import threading
import time
from collections import OrderedDict

class RtPlot(tk.Frame, threading.Thread):
    REFRESH_PERIOD = 0.01 # [s]

    def __init__(self, parent, buffers):
        tk.Frame.__init__(self, parent)
        threading.Thread.__init__(self, daemon=True)
        self.paused = False
        self.resume_event = threading.Event()

        self.buffers = buffers

        # create matplotlib figure
        self.fig, axes = subplots(len(buffers),1, sharex=True)
        self.fig.tight_layout()

        # create subplots
        self.subplots_dict = OrderedDict()
        for i,var in enumerate(buffers.get_variables()):
            self.subplots_dict[var] = RtSubplot(var)
            self.subplots_dict[var].set_axes(axes[i])
            self.subplots_dict[var].add_set_visible_callback(self.subplot_set_visible_callback)
        
        # create y axis menu
        plot_frame = tk.Frame(self)
        self.yaxis_menu_frame = tk.Frame(plot_frame)
        for i,subplot in enumerate(self.subplots_dict.values()):
            subplot.create_axis_menu(self.yaxis_menu_frame).pack(fill=tk.Y, expand=True)
        self.yaxis_menu_frame.pack(side=tk.LEFT, fill=tk.Y)
        #self.yaxis_menu_frame.pack_propagate(False)

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
        self.xaxis_menu_frame.add_pause_callback(self.pause)
        self.xaxis_menu_frame.add_play_callback(self.resume)
        bottom_bar.pack(fill=tk.X, expand = False)

        #self.arrange_subplots()

    def pause(self):
        self.paused = True

    def resume(self):
        if self.paused:
            self.resume_event.set()

    def run(self):
        self.running = True
        while self.running:
            try:
                if self.paused:
                    self.resume_event.wait()
                    self.resume_event.clear()
                    self.paused = False

                self.update()
            except TclError:
               break

    def stop(self):
        self.running = False
        
    def update(self):
        self.draw_fig()
        self.canvas.draw()
        time.sleep(self.REFRESH_PERIOD)

    def draw_fig(self):
        point_count = self.xaxis_menu_frame.get_axis_width()
        for subplot in self.subplots_dict.values():
            subplot.plot(self.buffers.head_view(subplot.variable, point_count))

    def subplot_set_visible_callback(self, visible, subplot):
        self.arrange_subplots()

    def arrange_subplots(self):
        self.fig.clear()

        # find visible subplots
        visible_subplots = []
        for name,subplot in self.subplots_dict.items():
            if subplot.visible:
                visible_subplots.append(subplot)

        for i,subplot in enumerate(visible_subplots):
            subplot.set_axes(self.fig.add_subplot(len(visible_subplots),1,i+1))
        self.fig.tight_layout()
        
        # remove all yaxis menus
        for child in self.yaxis_menu_frame.winfo_children():
            child.pack_forget()
        for subplot in visible_subplots:
            subplot.get_axis_menu().pack(fill=tk.BOTH, expand=True)

        self.fig.tight_layout()



class RtSubplot():
    def __init__(self, variable):
        self.axes = None
        self.variable = variable

        self.visible = True
        self.set_visible_callbacks = []

    def create_axis_menu(self, parent):
        self.axis_menu_frame = tk.Frame(parent)
        tk.Label(self.axis_menu_frame, font=(None, 1), bg='red').pack(fill=tk.BOTH, expand=True)
        self.axis_menu = axis_menu.Y(self.axis_menu_frame, self.variable, self.set_visible)
        self.axis_menu.pack(fill=tk.X, expand=False)
        tk.Label(self.axis_menu_frame, font=(None, 1), bg='green').pack(fill=tk.BOTH, expand=True)
        return self.axis_menu_frame

    def get_axis_menu(self):
        return self.axis_menu_frame

    def plot(self, data):
        self.axes.clear()
        self.axes.plot(data[0], data[1])
        self.axes.set_ylim(self.axis_menu.get_limits())

    def add_set_visible_callback(self, callback):
        self.set_visible_callbacks.append(callback)

    def set_visible(self, visible):
        if visible == self.visible:
            return

        self.visible = visible
        
        for callback in self.set_visible_callbacks:
            callback(visible, self)
        #show()

    def set_axes(self, axes):
        self.axes = axes