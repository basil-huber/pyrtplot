#!/usr/bin/env python3
import tkinter as tk
import threading
from groundcontrol.plotting.rt_plot import RtPlot
from flightlog.parser import LineParser
from groundcontrol.utils import CircBuffer, BufferIndexedCollection
import time



class SubWindow(tk.Toplevel):
    def __init__(self, parent, checkbox_var):
        tk.Toplevel.__init__(self, parent)
        self.thread  = None
        self.is_visible = True
        self.checkbox_var = checkbox_var
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def toggle_visible(self):
        if self.is_visible:
            self.withdraw()
            if self.thread:
                self.thread.pause()
        else:
            self.deiconify()
            if self.thread:
                self.thread.resume()
        self.is_visible = not self.is_visible

    def on_closing(self):
        if self.is_visible:
            self.toggle_visible()
            self.checkbox_var.set(0)

    def set_thread(self,thread):
        self.thread = thread

from tkinter import messagebox
class MainWindow(tk.Tk):
    def __init__(self, buffers):
        tk.Tk.__init__(self)
        self.buffers = buffers

        tk.Label(self, text="Houston").pack()

        self.checkbox_values = {}
        for group_name in sorted(buffers.keys()):
            self.checkbox_values[group_name] = tk.IntVar()
            frame = tk.Frame(self)
            b = tk.Checkbutton(frame, text=group_name,
                command=lambda group_name=group_name: self.com(group_name),
                variable=self.checkbox_values[group_name])
            b.pack(side=tk.LEFT, )
            tk.Label(frame).pack(fill=tk.X, expand=True)
            frame.pack(expand=True, fill=tk.X)
            for var in buffers[group_name].get_variables():
                var_frame = tk.Frame(self)
                tk.Label(var_frame, width=3).pack(side=tk.LEFT, fill=tk.NONE, expand=False)
                tk.Checkbutton(var_frame,text=var).pack(side=tk.LEFT, fill=tk.NONE, expand=False)
                tk.Label(var_frame).pack(side=tk.LEFT, fill=tk.X, expand=True)
                var_frame.pack(fill=tk.X, expand=True)

        self.plot_windows = {}

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            for rt_plot in self.plot_windows.values():
                rt_plot.quit()
            self.destroy()


    def com(self, group_name):
        if not group_name in self.plot_windows:
            window = SubWindow(self, self.checkbox_values[group_name])
            window.title(group_name)
            rt_plot = RtPlot(window, self.buffers[group_name])
            rt_plot.pack(fill=tk.BOTH, expand=True)
            window.set_thread(rt_plot)
            rt_plot.start()
            self.plot_windows[group_name] = window
        else:
            self.plot_windows[group_name].toggle_visible()