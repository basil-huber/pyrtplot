#!/usr/bin/env python3
import tkinter as tk
import threading
from groundcontrol.plotting.rt_plot import RtPlot
from flightlog.parser import LineParser
from groundcontrol.utils import CircBuffer, BufferIndexedCollection
import time



class SubWindow(tk.Toplevel):
    def __init__(self, parent, title):
        tk.Toplevel.__init__(self, parent)
        self.title(title)
        self.thread  = None
        self.is_visible = True
        

    def set_visible(self, visible):
        if self.is_visible and not visible:
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


class PlotHandler(tk.Frame):
    def __init__(self, parent, group_name, data_buffer):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.group_name = group_name
        self.data_buffer = data_buffer

        self.subplot_visible_vars = {}
        self.visible_var = None
        self.window = None
        self.rt_plot = None
        self.visible = False
        self.plot_visible_var = tk.IntVar()

        self._create_menu()

    def create_window(self):
        self.window = SubWindow(self.parent, self.group_name)
        #self.window.title(self.group_name)
        self.rt_plot = RtPlot(self.window, self.data_buffer)
        self.rt_plot.pack(fill=tk.BOTH, expand=True)
        for var,subplot in self.rt_plot.subplots_dict.items():
            subplot.add_set_visible_callback(self.set_visible_subplot_visible_callback)
        self.window.set_thread(self.rt_plot)
        self.window.protocol("WM_DELETE_WINDOW", self.on_window_closing)
        self.rt_plot.start()

    def _create_menu(self):
        frame = tk.Frame(self)
        tk.Checkbutton(frame, text=self.group_name,
            command=self.set_plot_visible,
            variable=self.plot_visible_var).pack(side=tk.LEFT, fill=tk.NONE, expand=False)
        tk.Label(frame).pack(fill=tk.X, expand=True)
        frame.pack(expand=True, fill=tk.X)
        self.subplots_checkbox_frame = tk.Frame(self)
        for var in self.data_buffer.get_variables():
            var_frame = tk.Frame(self.subplots_checkbox_frame)
            tk.Label(var_frame, width=3).pack(side=tk.LEFT, fill=tk.NONE, expand=False)
            self.subplot_visible_vars[var] = tk.IntVar()
            self.subplot_visible_vars[var].set(True)
            tk.Checkbutton(var_frame, text=var, variable=self.subplot_visible_vars[var],
                command=lambda var_name=var: self.set_visible_subplot(var_name)).pack(side=tk.LEFT, fill=tk.NONE, expand=False)
            tk.Label(var_frame).pack(side=tk.LEFT, fill=tk.X, expand=True)
            var_frame.pack(fill=tk.X, expand=True)

    def set_plot_visible(self, visible=None):
        if visible == None:
            visible = self.plot_visible_var.get()
        if visible == self.visible:
            return
        print('setting plot %s visible: %r' % (self.group_name, visible))
        if visible:
            self.subplots_checkbox_frame.pack()
            if self.window == None:
                self.create_window()
            else:
                self.window.set_visible(True)
        else:
            self.subplots_checkbox_frame.pack_forget()
            self.window.set_visible(False)
        self.plot_visible_var.set(visible)
        self.visible = visible

    def set_visible_subplot(self, var_name, visible=None):
        if visible == None:
            visible = self.subplot_visible_vars[var_name].get()
        print('setting subplot %s:%s visible: %r' % (self.group_name, var_name, visible))

        if self.rt_plot:
            self.rt_plot.subplots_dict[var_name].set_visible(visible)

    def set_visible_subplot_visible_callback(self, visible, subplot):
        self.subplot_visible_vars[subplot.variable].set(visible)
    
    def on_window_closing(self):
        self.set_plot_visible(False)

        


from tkinter import messagebox
class MainWindow(tk.Tk):
    def __init__(self, buffers):
        tk.Tk.__init__(self)
        self.buffers = buffers

        self.plot_menus = {}
        for group_name in sorted(self.buffers.keys()):
            self.plot_menus[group_name] = PlotHandler(self, group_name, self.buffers[group_name])
            self.plot_menus[group_name].pack(fill=tk.X, expand = True)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            for plot in self.plot_menus.values():
                if plot.window:
                    plot.window.quit()
        self.destroy()