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
from groundcontrol.menu import AxisMenu

class RtPlot(tk.Frame, threading.Thread):
    REFRESH_PERIOD = 0.01 # [s]
    XAXIS_WIDTH_DEFAULT = 500

    def __init__(self, parent, data_buffer_dict, x_buffer, lock):
        tk.Frame.__init__(self, parent)
        threading.Thread.__init__(self)

        self.x_buffer = x_buffer
        self.lock = lock

        

        self.subplots_dict = {}
        self.fig, self.axes = subplots(len(data_buffer_dict),1, sharex=True)
        for i,var in enumerate(sorted(data_buffer_dict)):
            sp = {}
            sp['axis'] = self.axes[i]
            sp['buffer'] = data_buffer_dict[var]
            sp['data'] = []
            self.subplots_dict[var] = sp
        self.fig.tight_layout()

        # create y axis menu
        plot_frame = tk.Frame(self)
        axis_menu_frame = tk.Frame(plot_frame)
        # tk.Label(axis_menu_frame).pack(fill=tk.BOTH, expand=True)
        for name, sp in self.subplots_dict.items():
            tk.Label(axis_menu_frame).pack(fill=tk.BOTH, expand=True)
            sp['axis_menu'] = AxisMenu(axis_menu_frame, name)
            sp['axis_menu'].pack()#fill=tk.Y, expand=True)
            tk.Label(axis_menu_frame).pack(fill=tk.BOTH, expand=True)
        axis_menu_frame.pack(side=tk.LEFT, fill=tk.Y)

        # create canvas for plotting
        self.canvas = FigureCanvasTkAgg(self.fig, plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        plot_frame.pack(fill=tk.BOTH, expand=True)

        # createx axis menu
        xaxis_menu_frame = tk.Frame(self)
        tk.Label(xaxis_menu_frame, width=AxisMenu.DEFAULT_VALUE_WIDTH).pack(fill=tk.NONE, expand=False, side=tk.LEFT)
        tk.Label(xaxis_menu_frame).pack(fill=tk.X, expand=True, side=tk.LEFT)
        tk.Label(xaxis_menu_frame, text='X axis').pack(side=tk.LEFT)
        self.xaxis_width = self.XAXIS_WIDTH_DEFAULT
        vcmd = (self.register(self.onValidate_xaxis_with),
            '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        w = tk.IntVar()
        w.set(self.xaxis_width)
        e = tk.Entry(xaxis_menu_frame, width=AxisMenu.DEFAULT_VALUE_WIDTH, textvariable=w,
            validate="key",validatecommand=vcmd)
        e.pack(side=tk.LEFT)
        tk.Label(xaxis_menu_frame, width=6).pack(side=tk.LEFT, expand=False, fill=tk.NONE)
        self.pause_button = tk.Button(xaxis_menu_frame, text="Pause", command=self.pause_toggle)
        self.pause_button.pack(side=tk.LEFT, expand=False, fill=tk.NONE)
        self.paused = False
        #tk.Label(xaxis_menu_frame).pack(fill=tk.X, expand=True, side=tk.LEFT)
        self.fff = tk.Frame(xaxis_menu_frame).pack(fill=tk.X, expand=True, side=tk.LEFT)
        xaxis_menu_frame.pack(expand = False, fill=tk.X)


    def run(self):
        self.running = True
        while self.running:
            try:
                self.update()
            except TclError:
               break

    def stop(self):
        self.running = False

    def pause_toggle(self):
        if not self.paused:
            self.paused = True
            self.pause_button["text"] = "Play"
            # NavigationToolbar2TkAgg(self.canvas, self.fff)

        else:
            self.paused = False
            self.pause_button["text"] = "Pause"
        
    def update(self):
        if not self.paused:
            self.draw_fig()
        self.canvas.draw()
        time.sleep(self.REFRESH_PERIOD)

    def onValidate_xaxis_with(self, d, i, P, s, S, v, V, W):
        if P == "":
            return True
        try:
            i = int(P)
            if i > 0:
                if self.lock:
                    self.lock.acquire() # use lock to avoid changing size during plotting
                self.xaxis_width = i
                if self.lock:
                    self.lock.release()
                return True
            else:
                return False
        except:
            pass
        return False

    def draw_fig(self):
        for sp in self.subplots_dict.values():
            axis = sp['axis']
            axis.clear()
            if self.lock:
                self.lock.acquire()
            axis.plot(self.x_buffer.head_view(self.xaxis_width),sp['buffer'].head_view(self.xaxis_width))
            if self.lock:
                self.lock.release()
            axis.set_ylim(sp['axis_menu'].get_limits())