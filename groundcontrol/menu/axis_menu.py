import tkinter as tk


class AxisMenu(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        tk.Label(self, text='Y axis').pack(side=tk.TOP)

        min_frame = tk.Frame(self)
        self.min_checked = tk.IntVar()
        self.min_val = tk.DoubleVar()
        self.min_cb = tk.Checkbutton(min_frame, text='min', variable=self.min_checked)
        self.min_cb.pack(side=tk.LEFT)
        self.min_entry = tk.Entry(min_frame, textvariable=self.min_val)
        self.min_entry.pack(side=tk.RIGHT)
        min_frame.pack()

        max_frame = tk.Frame(self)
        self.max_checked = tk.IntVar()
        self.max_val = tk.DoubleVar()
        self.max_cb = tk.Checkbutton(max_frame, text='max', variable=self.max_checked)
        self.max_cb.pack(side=tk.LEFT)
        self.max_entry = tk.Entry(max_frame, textvariable=self.max_val)
        self.max_entry.pack(side=tk.RIGHT)
        max_frame.pack()

    def get_limits(self):
        min_lim = None
        max_lim = None
        if self.min_checked.get():
            try:
                min_lim = self.min_val.get()
            except:
                pass
        if self.max_checked.get():
            try:
                max_lim = self.max_val.get()
            except:
                pass
        if max_lim == min_lim:
            max_lim = None
        return (min_lim, max_lim)
