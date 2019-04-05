from tkinter import Button
from tkinter import Toplevel
from tkinter import Label


from tkinter import IntVar
from tkinter import Checkbutton
from tkinter import W

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
        
        self.tmp = {str(key) + ': ' + str(self.parent.pixel_points[key]) + ' ' + str(self.parent.fix_points[key]):IntVar(value=0) for key, value in enumerate(self.parent.fix_points)}
        
        for key, value in self.tmp.items():
            self.c = Checkbutton(self.window, text = str(key), variable = value, onvalue = 1, offvalue = 0)
            self.c.pack(side="top", anchor=W, padx="10", pady="5")
            
        btn1 = Button(self.window, text="Delete selected", command=lambda *args: self.del_sel(self.window))
        btn1.pack(side="top", fill="both", padx="10", pady="5")
        
        btn2 = Button(self.window, text="Save pairs to disk", command=lambda *args: self.save_pairs(self.window))
        btn2.pack(side="top", fill="both", padx="10", pady="5")
        
    def update_gui(self):
               
        for widget in self.window.winfo_children():
            widget.destroy()
        self.drawWidgets()
        self.window.update()
        
        
    def del_sel(self, window):
                
        #        parent.pixel_points
#        parent.fix_points.append(
#        parent.inter_line_counter       
        
        self.update_gui()