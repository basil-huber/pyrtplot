import tkinter as tk


class Y(tk.Frame):
    DEFAULT_VALUE_WIDTH = 6
    FONT_SIZE_NAME = 12
    def __init__(self, parent, name, set_visible_callback=None):
        super().__init__(parent)
        self.set_visible_callback = set_visible_callback

        self.visible_var = tk.IntVar()
        self.visible_var.set(1)
        tk.Checkbutton(self, text=name, font=(None, self.FONT_SIZE_NAME),
            variable=self.visible_var, command=self.set_visible).pack()
        # tk.Label(self, text='Y axis').pack(side=tk.TOP)

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

    def set_visible(self, visible=None):
        if not visible:
            visible = self.visible_var.get()
        if self.set_visible_callback:
            self.set_visible_callback(visible)

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

class X(tk.Frame):
    AXIS_WIDTH_DEFAULT = 500

    def __init__(self, parent, axis_width_max=None, axis_width=None):
        super().__init__(parent)

        if axis_width:
            self.axis_width = axis_width
        else:
            self.axis_width = X.AXIS_WIDTH_DEFAULT
        self.axis_width_max = axis_width_max
        self.pause_callbacks = []
        self.play_callbacks = []

        self.axis_width_var = tk.IntVar()
        self.axis_width_var.set(self.axis_width)

        self.paused = False

        vcmd = (self.register(self.onValidate),'%P')

        tk.Label(self).pack(fill=tk.X, expand=True, side=tk.LEFT)
        tk.Label(self, text='X axis').pack(side=tk.LEFT)
        e = tk.Entry(self, width=Y.DEFAULT_VALUE_WIDTH, textvariable=self.axis_width_var,
            validate="key",validatecommand=vcmd)
        e.pack(side=tk.LEFT)
        tk.Label(self, width=6).pack(side=tk.LEFT, expand=False, fill=tk.NONE)
        self.pause_button = tk.Button(self, text="Pause", command=self.pause_toggle)
        self.pause_button.pack(side=tk.LEFT, expand=False, fill=tk.NONE)
        #tk.Label(self).pack(fill=tk.X, expand=True, side=tk.LEFT)
        self.fff = tk.Frame(self).pack(fill=tk.X, expand=True, side=tk.LEFT)

    def onValidate(self, value):
        if value == "":
            return True
        try:
            i = int(value)
            if i > 0 and (self.axis_width_max == None or i < self.axis_width_max):
                self.axis_width = i
                return True
            else:
                return False
        except:
            pass
        return False

    def get_axis_width(self):
        return self.axis_width

    def is_paused(self):
        return self.paused

    def add_pause_callback(self, callback):
        self.pause_callbacks.append(callback)

    def add_play_callback(self, callback):
        self.play_callbacks.append(callback)

    def pause_toggle(self):
        if not self.paused:
            self.paused = True
            self.pause_button["text"] = "Play"
            for callback in self.pause_callbacks:
                callback()
            # NavigationToolbar2TkAgg(self.canvas, self.fff)
        else:
            self.paused = False
            self.pause_button["text"] = "Pause"
            for callback in self.play_callbacks:
                callback()

    
