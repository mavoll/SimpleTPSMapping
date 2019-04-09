from tkinter import Button
from tkinter import Toplevel
from tkinter import Label


from tkinter import IntVar
from tkinter import Checkbutton
from tkinter import W

from collections import OrderedDict 

class PairsWindow(object):
    
    def __init__(self, parent):
        
        self.parent = parent
        self.window = Toplevel(parent.root)
        self.window.wm_title("Pairs")                
        #self.window.resizable(width=False, height=False)
        #self.window.geometry('{}x{}'.format(250, 450))
        self.window.attributes('-topmost', True)
        
        self.drawWidgets()   
        
    def drawWidgets(self):

        label1 = Label(self.window, text="Choose pairs you want to delete:")
        label1.pack(side="top", padx="10", pady="5")
        
        self.tmp = OrderedDict()
        self.tmp = {str(key) + ': ' + str(self.parent.pixel_points[key]) + ' ' + str(self.parent.fix_points[key]):IntVar(value=0) for key, value in enumerate(self.parent.fix_points)}
        
        for key, value in self.tmp.items():
            self.c = Checkbutton(self.window, text = str(key), variable = value, onvalue = 1, offvalue = 0)
            self.c.pack(side="top", anchor=W, padx="10", pady="5")
            
        btn1 = Button(self.window, text="Delete selected", command=lambda *args: self.del_sel(self.window))
        btn1.pack(side="top", fill="both", padx="10", pady="5")
        
        btn2 = Button(self.window, text="Save pairs to disk", command=lambda *args: self.parent.save_pairs())
        btn2.pack(side="top", fill="both", padx="10", pady="5")
        
    def update_gui(self):
               
        for widget in self.window.winfo_children():
            widget.destroy()
        self.drawWidgets()        
        
    def del_sel(self, window):                
        
        tmp = 0
        for i, key in enumerate(self.tmp.copy()):            
            if self.tmp[key].get() == 1:
                    i = i - tmp
                    self.tmp.pop(key)
                    #More lists than needed but too lazy to change it :)
                    self.parent.pixel_points.pop(i)
                    self.parent.fix_points.pop(i)
                    self.parent.refPt.pop( (i * 2) )
                    self.parent.refPt.pop( (i * 2) )
                    self.parent.inter_line_counter -= 2
                    tmp += 1
        
        self.update_gui()
        self.parent.draw()