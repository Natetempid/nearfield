import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure

import Tkinter as tk

from instruments import lakeshore335

LARGE_FONT= ("Verdana", 12)

class GraphTk(tk.Tk):

    def __init__(self, *args, **kwargs):
        
        tk.Tk.__init__(self, *args, **kwargs)
        container = tk.Frame(self)

        container.pack(side="top", fill="both", expand = True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        #self.frames = {}

        frame = Page(container, self)

        #self.frames[StartPage] = frame

        frame.grid(row=0, column=0, sticky="nsew")
        frame.tkraise()
    #    self.show_frame(StartPage)

    #def show_frame(self, cont):

    #    frame = self.frames[cont]
    #    frame.tkraise()

        
class Page(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        label = tk.Label(self, text="Start Page", font=LARGE_FONT)
        label.pack(pady=10,padx=10)

        f = Figure(figsize=(5,5), dpi = 100)
        a = f.add_subplot(111)
        a.plot([1,2,3,4,5,6,7,8], [1,4,1,5,7,3,9,6])
        a.set_title('Test')

        canvas = FigureCanvasTkAgg(f, self)
        canvas.show()
        canvas.get_tk_widget().pack(side = tk.BOTTOM, fill = tk.BOTH, expand = True)

        canvas._tkcanvas.pack(side = tk.TOP, fill = tk.BOTH, expand = True)


app = GraphTk()
app.mainloop()