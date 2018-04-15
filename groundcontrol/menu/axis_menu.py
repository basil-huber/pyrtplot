import tkinter as tk


class AxisMenu(tk.Frame):
    DEFAULT_VALUE_WIDTH = 6
    FONT_SIZE_NAME = 12
    def __init__(self, parent, name):
        super().__init__(parent)

        tk.Label(self, text=name, font=(None, self.FONT_SIZE_NAME)).pack()
        tk.Label(self, text='Y axis').pack(side=tk.TOP)

        max_frame = tk.Frame(self)
        self.max_checked = tk.IntVar()
        self.max_val = tk.DoubleVar()
        max_cb = tk.Checkbutton(max_frame, text='max', variable=self.max_checked)
        max_cb.pack(side=tk.LEFT)
        max_entry = tk.Entry(max_frame, textvariable=self.max_val, width=self.DEFAULT_VALUE_WIDTH)
        max_entry.pack(side=tk.RIGHT)
        max_frame.pack()

        min_frame = tk.Frame(self)
        self.min_checked = tk.IntVar()
        self.min_val = tk.DoubleVar()
        min_cb = tk.Checkbutton(min_frame, text='min', variable=self.min_checked)
        min_cb.pack(side=tk.LEFT)
        min_entry = tk.Entry(min_frame, textvariable=self.min_val, width=self.DEFAULT_VALUE_WIDTH)
        min_entry.pack(side=tk.RIGHT)
        min_frame.pack()


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
