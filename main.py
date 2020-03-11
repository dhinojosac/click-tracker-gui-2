import tkinter as tk
from tkinter import ttk

LARGE_FONT = ("Verdana", 12)

class PerceptionApp(tk.Tk):
    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)

        tk.Tk.iconbitmap(self, default="") # set icon 16x16
        tk.Tk.wm_title(self, "Perception App") # set title
        ws = self.winfo_screenwidth() #gets the width of screen
        hs = self.winfo_screenheight() #gets the heigth of screen
        print("[!] SCREEN SIZE {}x{}".format(ws,hs))
        self.attributes("-fullscreen", True)
        self.configure(background='black')
        self.w_ws = ws
        self.w_hs = hs
        self.geometry("{}x{}+{}+{}".format(self.w_ws,self.w_hs,-10,-5)) #sets size of windows

        self.canvas = tk.Canvas(self, width=self.w_ws, height=self.w_hs) #create canvas with screen size
        self.canvas.configure(background='black')    #set background color
        self.canvas.pack()      #add canvas to window screen
        
        self.show_square()
        

    def show_square(self):
        square_size         = 200 # square width pixels
        colorval            =  [255,0,0]
        rcol =  colorval
        colorval = "#%02x%02x%02x" % (rcol[0], rcol[1], rcol[2]) # rgb to hexadecimal format
        square_pos_x = (self.w_ws-square_size)/2
        square_pos_y = (self.w_hs-square_size)/2
        self.canvas.create_rectangle(square_pos_x, square_pos_y, square_pos_x+square_size, square_pos_y+square_size, fill=colorval) #create blue square



app= PerceptionApp()
app.mainloop()