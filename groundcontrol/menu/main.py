#!/usr/bin/env python3

from flightlog.parser import LineParser


filename = 'LOG_0.LOG'

with LineParser(filename) as parser:
    groups = parser.parse_groups()
    # change keys from indices to names
    groups = {g['name'] : g for g in groups.values()}


from tkinter import *
from tkinter import ttk
from groundcontrol.plotting.rt_plot import RtPlot

plot_windows = {}
def com(group_name):
    if not group_name in plot_windows:
        window = Toplevel(root)
        window.title(group_name)
        rt_plot = RtPlot(window)


        plot_windows[group_name] = window
    else:
        plot_windows[group_name].destroy()
        del plot_windows[group_name]

root = Tk()

w = Label(root, text="Houston")
w.pack()


for g in sorted(groups.keys()):
    b = Checkbutton(root, text=g, command = lambda group_name=g: com(group_name))
    b.pack(side="top")





root.mainloop()