import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image
from pynput import mouse

click_error = 0

square_pos_x = None
square_pos_y = None
square_size = 200

def on_click(x, y, button, pressed):
    global square_pos_x, square_pos_y
    if button == mouse.Button.left and pressed==True:   #check if left click is pressed
        print("Left click: {},{}".format(x,y))          #debug: show cursor position on console
        if x>= square_pos_x-click_error and x<= square_pos_x+square_size+click_error and y>= square_pos_y-click_error and y<= square_pos_y+square_size+click_error : #check if click is inside square+error area.
            score=score+1                                   #add 1 to score if is a right click, inside a square+error area.
            print(">> CLICK INSIDE TARGET!")
        else:
            print(">> CLICK FAILED!")

    if button == mouse.Button.right and pressed ==True: #check if right click is pressed
        print("Right click: {},{}".format(x,y))         #debug: show cursor position on console


class PerceptionApp(tk.Tk):
    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)
        self.counter = 0 # counter time
        self.waitingClick = True
        
        self.startMouseListener()

        tk.Tk.iconbitmap(self, default="")      # set icon 16x16
        tk.Tk.wm_title(self, "Perception App")  # set title
        ws = self.winfo_screenwidth()           # gets the width of screen
        hs = self.winfo_screenheight()          # gets the heigth of screen
        print("[!] SCREEN SIZE {}x{}".format(ws,hs))
        self.attributes("-fullscreen", True)    # set full screen
        self.configure(background='black')
        self.w_ws = ws
        self.w_hs = hs
        self.geometry("{}x{}+{}+{}".format(self.w_ws,self.w_hs,-10,-5)) #sets size of windows

        self.canvas = tk.Canvas(self, width=self.w_ws, height=self.w_hs) #create canvas with screen size
        self.canvas.configure(background='black')    #set background color
        self.canvas.pack()      #add canvas to window screen
        
        self.show_warning()
    
    def update(self):
        self.counter = self.counter + 1
       
        if self.counter == 6:
            self.show_sample()
        elif self.counter == 12:
            self.show_match()
        elif self.counter == 18:
            self.finishMouseListener()
            self.destroy()

        self.after(500, self.update)

    def show_warning(self):
        global square_pos_x, square_pos_y
        self.canvas.delete("all")
        square_size         = 200   # square width pixels
        colorval            = [255,0,0]
        rcol =  colorval            # square color
        colorval = "#%02x%02x%02x" % (rcol[0], rcol[1], rcol[2]) # rgb to hexadecimal format
        square_pos_x = (self.w_ws-square_size)/2
        square_pos_y = (self.w_hs-square_size)/2
        self.canvas.create_rectangle(square_pos_x, square_pos_y, square_pos_x+square_size, square_pos_y+square_size, fill=colorval) #create blue square
        self.after(500, self.update)

    def show_sample(self):
        self.canvas.delete("all")
        w_i = 200
        h_i = 200
        self.img = ImageTk.PhotoImage(Image.open("images/G1.png"))
        self.img_pos_w = (self.w_ws-w_i)/2
        self.img_pos_h = (self.w_hs-h_i)/2
        self.canvas.create_image(self.img_pos_w, self.img_pos_h, anchor=tk.NW, image=self.img) 
        self.canvas.image = self.img
    
    def show_match(self):
        w_i = 200
        h_i = 200
        self.img = ImageTk.PhotoImage(Image.open("images/G1.png"))
        self.img_pos_w = (self.w_ws-w_i)/2
        self.img_pos_h = (self.w_hs-h_i)/2
        self.canvas.create_image(self.img_pos_w, self.img_pos_h, anchor=tk.NW, image=self.img) 
        self.canvas.image = self.img
        self.img2 = ImageTk.PhotoImage(Image.open("images/G2.png"))
        self.canvas.create_image(self.img_pos_w + 200, self.img_pos_h, anchor=tk.NW, image=self.img2) 
        self.canvas.image = self.img2
    
    def startMouseListener(self):
        self.mouse_listener = mouse.Listener(on_click=on_click)     #sets mouse listener passing function prior defined
        self.mouse_listener.start()                                 #starts mouse listener

    def finishMouseListener(self):
        self.mouse_listener.stop()   #stop listener when program was ended



app= PerceptionApp()
app.mainloop()
