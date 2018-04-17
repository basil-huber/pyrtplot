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
        self.is_visible = True
        self.checkbox_var = checkbox_var
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def toggle_visible(self):
        if self.is_visible:
            self.withdraw()
        else:
            self.deiconify()
        self.is_visible = not self.is_visible
    def on_closing(self):
        if self.is_visible:
            self.toggle_visible()
            self.checkbox_var.set(0)

from tkinter import messagebox
class MainWindow(tk.Tk):
    def __init__(self, buffers):
        tk.Tk.__init__(self)
        self.buffers = buffers

        tk.Label(self, text="Houston").pack()

        self.checkbox_values = {}
        for group_name in sorted(buffers.keys()):
            self.checkbox_values[group_name] = tk.IntVar()
            b = tk.Checkbutton(self, text=group_name,
                command=lambda group_name=group_name: self.com(group_name),
                variable=self.checkbox_values[group_name])
            b.pack(side="top")

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
            rt_plot = RtPlot(window, buffers[group_name])
            rt_plot.pack(fill=tk.BOTH, expand=True)
            rt_plot.start()
            self.plot_windows[group_name] = window
        else:
            self.plot_windows[group_name].toggle_visible()


filename = 'LOG_0.LOG'

max_len = 1000

with LineParser(filename) as parser:
    groups = parser.parse_groups()
    buffers = {}
    for group in groups.values():
        variables = group['variables']
        #var_list = [(var, variables[var]['nb']) for var in variables]
        i = 0
        var_list = []
        for var in variables:
            var_list.append((var, variables[var]['nb']))
            i+= 1
            if i >= 3:
                break
        buffers[group['name']] = BufferIndexedCollection(var_list, max_len)

    group_buffer_indices = {group: 1 for group in buffers}
    class ParserThread(threading.Thread):
        def __init__(self, daemon=True):
            threading.Thread.__init__(self, daemon=True)
        def run(self):
            try:
                for entry in parser:
                    var_name = entry[0]
                    values = []
                    i0 = 0
                    for var in buffers[var_name].variables:
                        i1 = i0 + var[1]
                        values.append(entry[1][i0:i1])
                        i0 = i1
                    buffers[var_name].push(group_buffer_indices[var_name], values)
                    group_buffer_indices[var_name] += 1

                    time.sleep(0.0001)
            except ValueError:
                pass



    
    

    parser_thread = ParserThread()
    parser_thread.start()

    root = MainWindow(buffers)
    root.mainloop()
    