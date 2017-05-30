import Tkinter as tk
import tkFileDialog
import tkMessageBox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib import pyplot as plt
import matplotlib.animation as animation
import datetime
import ttk

from usbswitch import *

class usbswitch_diagram_frame(tk.Frame):
    def __init__(self, master, controller, usbswitch):
        tk.Frame.__init__(self, master)
        self.config(borderwidth = 5, relief = tk.GROOVE, padx = 0)
        #self.grid_rowconfigure(, weight = 1)
        self.grid_columnconfigure(0,weight=1)
        self.usbswitch = usbswitch
        
        for k in range(0,8):
            self.grid_columnconfigure(k, weight = 0)

        #fluke frame
        self.flukeframe = tk.Frame(self)
        self.flukeframe.grid(row = 0, column = 0, columnspan = 8, sticky = 'ns')
        self.flukeframe.grid_columnconfigure(0, weight = 1)
        self.flukeframe.grid_columnconfigure(1, weight = 1)
        self.flukeframe.grid_columnconfigure(2, weight = 1)
        self.flukelbl = tk.Label(self.flukeframe, text = "Fluke 8808a", font = ("tkDefaultFont", 22), background = "peachpuff2")
        self.flukelbl.grid(row = 0, column = 0, columnspan = 3, sticky = 'ns')

        #connector canvas
        self.connectorcanvas = tk.Canvas(self)
        self.connectorcanvas.grid(row = 1, column = 0 , columnspan = 8, sticky = 'nsew')
        

        self.malbl = tk.Label(self.flukeframe, text = "mA", font = ("tkDefaultFont", 22), background = "peachpuff2")
        self.malbl.grid(row = 1, column = 2, sticky = 'nsew')
        
        self.lolbl = tk.Label(self.flukeframe, text = "LO", font = ("tkDefaultFont", 22), background = "peachpuff2")
        self.lolbl.grid(row = 1, column = 1, sticky = 'nsew')

        self.hilbl = tk.Label(self.flukeframe, text = "HI", font = ("tkDefaultFont", 22), background = "peachpuff2")
        self.hilbl.grid(row = 1, column = 0, sticky = 'nsew')
     
        #get relaybtn width
        #Fluke HI
        self.hinodex0 = 195
        self.hinodex1 = 230
        self.hinodey = 100
        self.startx0 = 20
        self.startx1 = 55
        self.buttonwidth = 105
        self.flukehitohinode = self.connectorcanvas.create_polygon([self.hinodex0,self.hinodey,self.hinodex1,self.hinodey, 360,5,325,5], fill = 'black')
        self.ch1tohinode = self.connectorcanvas.create_polygon([self.startx0,280,self.startx1,280,self.hinodex1,self.hinodey,self.hinodex0,self.hinodey], fill = 'black')
        self.ch2tohinode = self.connectorcanvas.create_polygon([self.startx0+self.buttonwidth,280,self.startx1+self.buttonwidth,280,self.hinodex1,self.hinodey,self.hinodex0,self.hinodey], fill = 'black')
        self.ch3tohinode = self.connectorcanvas.create_polygon([self.startx0+2*self.buttonwidth,280,self.startx1+2*self.buttonwidth,280,self.hinodex1,self.hinodey,self.hinodex0,self.hinodey], fill = 'black')
        #Fluke LO
        self.lonodex0 = 415
        self.lonodex1 = 450
        self.lonodey = 100
        self.flukelotolonode = self.connectorcanvas.create_polygon([self.lonodex0,self.lonodey,self.lonodex1,self.lonodey, 415,5,380,5], fill = 'black')
        self.ch5tolonode = self.connectorcanvas.create_polygon([self.startx0+4*self.buttonwidth,280,self.startx1+4*self.buttonwidth,280,self.lonodex1,self.lonodey,self.lonodex0,self.lonodey], fill = 'black')
        self.ch6tolonode = self.connectorcanvas.create_polygon([self.startx0+5*self.buttonwidth,280,self.startx1+5*self.buttonwidth,280,self.lonodex1,self.lonodey,self.lonodex0,self.lonodey], fill = 'black')
        self.ch7tolonode = self.connectorcanvas.create_polygon([self.startx0+6*self.buttonwidth,280,self.startx1+6*self.buttonwidth,280,self.lonodex1,self.lonodey,self.lonodex0,self.lonodey], fill = 'black')
        #Fluke mA
        self.mAnodex0 = 575
        self.mAnodex1 = 610
        self.mAnodey = 100
        self.flukemAtomAnode = self.connectorcanvas.create_polygon([self.mAnodex0,self.mAnodey,self.mAnodex1,self.mAnodey,485,5,450,5], fill = 'black')
        self.ch8tomAnode = self.connectorcanvas.create_polygon([self.startx0+7*self.buttonwidth,280,self.startx1+7*self.buttonwidth,280,self.mAnodex1,self.mAnodey,self.mAnodex0,self.mAnodey], fill = 'black')

        #Bottom Side - another canvas
        self.instrumentframe = tk.Frame(self)
        self.instrumentframe.grid(row = 4, column = 0, columnspan = 8, sticky = 'nsew')
        for k in range(0,8):
            self.instrumentframe.grid_columnconfigure(k, weight = 1)
        
        self.instrumentlbl = tk.Label(self.instrumentframe, text = "Instrument", font = ("tkDefaultFont", 18), background = "peachpuff2")
        self.instrumentlbl.grid(row = 1, column = 0, columnspan = 8, sticky = 'nsew')
        #self.flukecurrentlbl = tk.Label(self.instrumentframe, text = "Fluke", font = ("tkDefaultFont", 22), background = "peachpuff2")
        #self.flukecurrentlbl.grid(row = 1, column = 7, columnspan = 1, sticky = 'nsew')
        self.r1hilbl = tk.Label(self.instrumentframe, text = "R1-Hi", font = ("tkDefaultFont", 18), background = "peachpuff2")
        self.r1hilbl.grid(row = 0, column = 0, sticky = 'nsew')
        self.r2hilbl = tk.Label(self.instrumentframe, text = "R2-Hi", font = ("tkDefaultFont", 18), background = "peachpuff2")
        self.r2hilbl.grid(row = 0, column = 1, sticky = 'nsew')
        self.vhilbl = tk.Label(self.instrumentframe, text = "V-Hi", font = ("tkDefaultFont", 18), background = "peachpuff2")
        self.vhilbl.grid(row = 0, column = 2, sticky = 'nsew')
        self.nolbl = tk.Label(self.instrumentframe, text = " ", font = ("tkDefaultFont", 18), background = "peachpuff2")
        self.nolbl.grid(row = 0, column = 3, sticky = 'nsew')        
        self.r1lolbl = tk.Label(self.instrumentframe, text = "R1-Lo", font = ("tkDefaultFont", 18), background = "peachpuff2")
        self.r1lolbl.grid(row = 0, column = 4, sticky = 'nsew')
        self.r2lolbl = tk.Label(self.instrumentframe, text = "R2-Lo", font = ("tkDefaultFont", 18), background = "peachpuff2")
        self.r2lolbl.grid(row = 0, column = 5, sticky = 'nsew')
        self.vlolbl = tk.Label(self.instrumentframe, text = "V-Lo", font = ("tkDefaultFont", 18), background = "peachpuff2")
        self.vlolbl.grid(row = 0, column = 6, sticky = 'nsew')
        self.output1lbl = tk.Label(self.instrumentframe, text = "Heat Out", font = ("tkDefaultFont", 18), background = "peachpuff2")
        self.output1lbl.grid(row = 0, column = 7, sticky = 'nsew')

        self.closeallbtn = ttk.Button(self.instrumentframe, text = 'Close All', command = lambda: self.closeAllRelays() )
        self.closeallbtn.grid(row = 1, column = 0, columnspan = 8, sticky = 'nsew')
        #connector canvas to instrument
        self.connectorcanvas2 = tk.Canvas(self)
        self.connectorcanvas2.grid(row = 3, column = 0 , columnspan = 8, sticky = 'nsew')

        self.ch1toinstr = self.connectorcanvas2.create_polygon([self.startx0,5,self.startx1,5,self.startx1,275,self.startx0,275], fill = 'black')
        self.ch2toinstr = self.connectorcanvas2.create_polygon([self.startx0+self.buttonwidth,5,self.startx1+self.buttonwidth,5,self.startx1+self.buttonwidth,275,self.startx0+self.buttonwidth,275], fill = 'black')
        self.ch3toinstr = self.connectorcanvas2.create_polygon([self.startx0+2*self.buttonwidth,5,self.startx1+2*self.buttonwidth,5,self.startx1+2*self.buttonwidth,275,self.startx0+2*self.buttonwidth,275], fill = 'black')
        self.ch5toinstr = self.connectorcanvas2.create_polygon([self.startx0+4*self.buttonwidth,5,self.startx1+4*self.buttonwidth,5,self.startx1+4*self.buttonwidth-40,275,self.startx0+4*self.buttonwidth-40,275], fill = 'black')
        self.ch6toinstr = self.connectorcanvas2.create_polygon([self.startx0+5*self.buttonwidth,5,self.startx1+5*self.buttonwidth,5,self.startx1+5*self.buttonwidth-40,275,self.startx0+5*self.buttonwidth-40,275], fill = 'black')
        self.ch7toinstr = self.connectorcanvas2.create_polygon([self.startx0+6*self.buttonwidth,5,self.startx1+6*self.buttonwidth,5,self.startx1+6*self.buttonwidth-40,275,self.startx0+6*self.buttonwidth-40,275], fill = 'black')
        self.ch8toinstr = self.connectorcanvas2.create_polygon([self.startx0+7*self.buttonwidth,5,self.startx1+7*self.buttonwidth,5,self.startx1+7*self.buttonwidth-40,275,self.startx0+7*self.buttonwidth-40,275], fill = 'black')
        self.ch4toch2 = self.connectorcanvas2.create_polygon([self.startx0+3*self.buttonwidth,5,self.startx1+3*self.buttonwidth,5,self.startx1+3*self.buttonwidth,100, self.startx0+self.buttonwidth,100,
                                                              self.startx0+self.buttonwidth,5,self.startx1+self.buttonwidth,5, self.startx1+self.buttonwidth,65,self.startx0+3*self.buttonwidth,65,self.startx0+3*self.buttonwidth,5], fill = 'black')
        self.ch4toch6 = self.connectorcanvas2.create_polygon([self.startx0+3*self.buttonwidth,5,self.startx1+3*self.buttonwidth,5,self.startx1+3*self.buttonwidth,65, self.startx0+5*self.buttonwidth,65,
                                                              self.startx0+5*self.buttonwidth,5,self.startx1+5*self.buttonwidth,5, self.startx1+5*self.buttonwidth,100,self.startx0+3*self.buttonwidth,100,self.startx0+3*self.buttonwidth,5], fill = 'black')
        #canvas list
        
        self.btnstonodelist = [self.ch1tohinode, self.ch2tohinode, self.ch3tohinode, self.ch4toch2, self.ch5tolonode, self.ch6tolonode, self.ch7tolonode, self.ch8tomAnode]
        self.nodetoflukelist = [self.flukehitohinode, self.flukehitohinode, self.flukehitohinode,self.ch4toch2, self.flukelotolonode,self.flukelotolonode,self.flukelotolonode, self.flukemAtomAnode]
        self.flukecanvaslist = [self.connectorcanvas,self.connectorcanvas,self.connectorcanvas,self.connectorcanvas2,self.connectorcanvas,self.connectorcanvas,self.connectorcanvas,self.connectorcanvas]
        self.btnstoinstrlist = [self.ch1toinstr,self.ch2toinstr,self.ch3toinstr,self.ch4toch6,self.ch5toinstr,self.ch6toinstr,self.ch7toinstr,self.ch8toinstr]
        
        self.relaybtns = []
        for k in range(0,8):
            self.relaybtns.append(relaybtn(self,self.usbswitch.relays[k],self.btnstonodelist[k],self.nodetoflukelist[k],self.flukecanvaslist[k],self.btnstoinstrlist[k]))
            self.relaybtns[k].grid(row = 2, column = k, sticky = 'nsew')
    
    def closeAllRelays(self):
        self.usbswitch.turnOffAllRelays()
        for k in range(0,8):
            self.relaybtns[k].updateState()

        

class relaybtn(tk.Button):
    def __init__(self,master, relay, pathbtntonode,pathnodetofluke,flukecanvas,pathbtntoinstr,):
        tk.Button.__init__(self, master, command = lambda:self.change_state())
        self.master = master
        self.relay = relay
        self.state = "Off"
        self.config(text = "Relay %d" % self.relay.number, font = ("tkDefaultFont", 18), background = "red")
        self.pathbtntonode = pathbtntonode
        self.pathnodetofluke = pathnodetofluke
        self.pathbtntoinstr = pathbtntoinstr
        self.flukecanvas = flukecanvas
        #when the button is initialized, I need to check the status of the switch. If it is on, I need to change the button state.        
        self.checkStartUpState()

    def checkStartUpState(self):
        if self.relay.status:
            #then relay is switched on
            self.change_state()
    
    def turnOnPath(self):
        #this turns the relay and corresponding paths green
        self.state = "On"
        self.config(background = "green4")
        #raise the paths
        self.flukecanvas.tag_raise(self.pathbtntonode)
        self.flukecanvas.tag_raise(self.pathnodetofluke)
        self.master.connectorcanvas2.tag_raise(self.pathbtntoinstr)
        #change colors
        self.flukecanvas.itemconfig(self.pathbtntonode, fill = "green4")
        self.flukecanvas.itemconfig(self.pathnodetofluke, fill = "green4")
        self.master.connectorcanvas2.itemconfig(self.pathbtntoinstr, fill = "green4")

    def turnOffPath(self):
        #this turns relay red and paths black
        self.state = "Off"
        self.config(background = "red")
        #raise the paths
        self.flukecanvas.tag_raise(self.pathbtntonode)
        self.flukecanvas.tag_raise(self.pathnodetofluke)
        self.master.connectorcanvas2.tag_raise(self.pathbtntoinstr)
        #change colors
        self.flukecanvas.itemconfig(self.pathbtntonode, fill = "black")
        self.flukecanvas.itemconfig(self.pathnodetofluke, fill = "black")
        self.master.connectorcanvas2.itemconfig(self.pathbtntoinstr, fill = "black")

    def updateState(self):
        #after an event is executed, this checks the status of the relay and updates the relay button and path
        if self.relay.status: #then the relay is on
            self.turnOnPath()
        else:
            self.turnOffPath()

    def change_state(self):
        if self.state == "Off":
            self.turnOnPath()
            self.relay.turnOn()
            self.relay.status = 1
        else:
            self.turnOffPath()
            self.relay.turnOff()
            self.relay.status = 0




