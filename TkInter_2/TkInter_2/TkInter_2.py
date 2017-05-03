
import Tkinter as tk
import serial
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib import pyplot as plt
import matplotlib.animation as animation
from collections import deque
import random
import datetime
from instruments import lakeshore335
import ttk
HISTORY_LEN = 200

lkshr = lakeshore335('ASRL3::INSTR')
class App(tk.Frame):
    def __init__(self, master=None, **kwargs):
        tk.Frame.__init__(self, master, **kwargs)

        self.running = False
        self.ani = None

        btns = tk.Frame(self)
        btns.pack()

        lbl = tk.Label(btns, text="Number of points")
        lbl.pack(side=tk.LEFT)

        self.points_ent = tk.Entry(btns, width=5)
        self.points_ent.insert(0, '500')
        self.points_ent.pack(side=tk.LEFT)

        lbl = tk.Label(btns, text="update interval (s)")
        lbl.pack(side=tk.LEFT)

        self.interval = tk.Entry(btns, width=5)
        self.interval.insert(0, '1')
        self.interval.pack(side=tk.LEFT)

        self.btn = tk.Button(btns, text='Start', command=self.on_click)
        self.btn.pack(side=tk.LEFT)

        self.fig = plt.Figure()
        self.ax1 = self.fig.add_subplot(111)
        self.line, = self.ax1.plot([], [], lw=2)
        self.canvas = FigureCanvasTkAgg(self.fig,master=master)
        self.canvas.show()
        self.canvas.get_tk_widget().pack()

    def on_click(self):
        if self.ani is None: #if I haven't initialized the animation through the start command then run self.start
            return self.start()
        if self.running: #then the user wants to stop the measurement
            self.ani.event_source.stop()
            lkshr.stop_event.set()
            self.btn.config(text='Start')
        else:
            return self.start()
            self.btn.config(text='Stop')
        self.running = not self.running

    def start(self):
        lkshr.measureA(int(self.interval.get()))
        self.ani = animation.FuncAnimation(self.fig, self.update_graph, interval = int(self.interval.get())*1000 + 1, repeat=False)
        self.running = True
        self.btn.config(text='Stop')
        self.ani._start()

    def update_graph(self, i):
        xlistA = []
        ylistA = []
        for elem in lkshr.listA:
            xlistA.append((elem['datetime'] - datetime.datetime(1970,1,1)).total_seconds())
            ylistA.append(elem['data'])
        
        self.line.set_data(xlistA,ylistA)
        if xlistA and ylistA:
            self.ax1.set_ylim(min(ylistA), max(ylistA))
            self.ax1.set_xlim(min(xlistA), max(xlistA))
        return self.line,

def main():
    root = tk.Tk()
    app = App(root)
    app.pack()
    root.mainloop()
    lkshr.close()

if __name__ == '__main__':
    main()