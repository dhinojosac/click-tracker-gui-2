import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image
from pynput import mouse
from time import sleep

IS_PC = True    # debug in pc
if not IS_PC:
    import RPi.GPIO as GPIO

# Program class (do not modify!)
class Program:
    def __init__(self, steps, times):
        self.steps = steps
        self.times = times
        self.len = len(steps)

#***********************   EDITABLES   ***********************************
# PROGRAMS (define your custom programs)
program1_steps = ["warning","blank","sample","blank","match"]
program1_times = [2, 1.5, 2, 0.5, 3]

program2_steps = ["warning","blank","sample","blank","sample","blank","match"]
program2_times = [2, 1, 2, 0.5, 2, 0.5, 3]

program1 = Program(program1_steps, program1_times) # Init program 1
program2 = Program(program2_steps, program2_times) # Init program 2

# public variables (edit as you wish)
USE_PROGRAM = program1

wait_click = True   # wait click to pass to other stage
click_error = 0     # error at click 
IMAGE_SAMPLE  = "images/G1.png"
IMAGE_MATCH   = "images/G1.png"
IMAGE_NOMATCH = "images/G2.png"

#Configure GPIO control  
SUCCESS_LED = 17
FAIL_LED =27
TIME_LED_ON = 0.2         # Time led on 

#**************************************************************************

#private variables (do not modify!)
square_size = 200       # size box in warning
square_pos_x = None
square_pos_y = None
clicked = False
score = 0

#Function that indicates if the box was pressed or not. The time of the led on
# is added to the time between the appearence of squares.
def turn_on_led(status):
    if not IS_PC:
        GPIO.setmode(GPIO.BCM) #set mode to GPIO control
        GPIO.setup(SUCCESS_LED, GPIO.OUT) # set GPIO 17 as output SUCCESS LED
        GPIO.setup(FAIL_LED, GPIO.OUT) # set GPIO 27 as output FAIL LED

        if status == "SUCCESS":
            GPIO.output(SUCCESS_LED, True) ## turn on SUCCESS LED
            sleep(TIME_LED_ON)
            GPIO.output(SUCCESS_LED, False) ## turn off SUCCESS LED

        elif status == "FAIL":
            GPIO.output(FAIL_LED, True) ## Enciendo FAIL LED
            sleep(TIME_LED_ON)
            GPIO.output(FAIL_LED, False) ## turn off FAIL LED
        GPIO.cleanup() # clear GPIOs

def led_success():
    turn_on_led("SUCCESS")

def led_failed():
    turn_on_led("FAIL")

# On click calleable
def on_click(x, y, button, pressed):
    global square_pos_x, square_pos_y, score, clicked, app
    if button == mouse.Button.left and pressed==True:   #check if left click is pressed
        print("Left click: {},{}".format(x,y))          #debug: show cursor position on console
        if x>= square_pos_x-click_error and x<= square_pos_x+square_size+click_error and y>= square_pos_y-click_error and y<= square_pos_y+square_size+click_error : #check if click is inside square+error area.
            score=score+1                                   #add 1 to score if is a right click, inside a square+error area.
            print(">> CLICK INSIDE TARGET!")
            led_success()
        else:
            print(">> CLICK FAILED!")
            led_failed()
        app.nextStage()
        app.runStage()

    if button == mouse.Button.right and pressed ==True: #check if right click is pressed
        print("Right click: {},{}".format(x,y))         #debug: show cursor position on console

# Application Tk
class PerceptionApp(tk.Tk):
    
    def __init__(self, *args, **kwargs):
        self.prog2function = {
        "warning":  self.show_warning,
        "blank":    self.show_blank,
        "sample":   self.show_sample,
        "match":    self.show_match        
        }

        tk.Tk.__init__(self, *args, **kwargs)
        self.counter = 0 # counter time
        self.waitingClick = True
        self.stage = 0
        
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
        
        self.setProgram(USE_PROGRAM) #set program

        self.runProgram()

    def setProgram(self, program):
        self.program = program
    
    def runProgram(self):
        if self.program == None:
            print("Error, does't exist program")
        else:
            self.runStage()
        self.mUpdate()

    def mUpdate(self):
        if self.program.steps[self.stage] == "blank" or not wait_click:
            self.counter = self.counter + 1 # ticks every 500 ms
        #print("stage:{} program:{}  counter:{}".format(self.stage, self.program.steps[self.stage], self.counter)) #debug
        if self.counter >= self.program.times[self.stage]*2: # compare times
            print("[!] Next Stage") #debug
            self.nextStage()
            if self.stage>= self.program.len:
                self.finishMouseListener()
                self.destroy()
            else:
                self.runStage()
        
            self.counter = 0
        self.after(500, self.mUpdate)
    
    def runStage(self):
        self.prog2function[self.program.steps[self.stage]]()
    
    def nextStage(self):
        self.stage+=1
        if self.stage>= self.program.len:
            self.finishMouseListener()
            self.destroy()
        print(self.stage)

    def show_warning(self):
        print("[->]WARNING")
        global square_pos_x, square_pos_y
        colorval            = [255,0,0]
        rcol =  colorval            # square color
        colorval = "#%02x%02x%02x" % (rcol[0], rcol[1], rcol[2]) # rgb to hexadecimal format
        square_pos_x = (self.w_ws-square_size)/2
        square_pos_y = (self.w_hs-square_size)/2
        self.canvas.create_rectangle(square_pos_x, square_pos_y, square_pos_x+square_size, square_pos_y+square_size, fill=colorval) #create blue square


    def show_sample(self):
        print("[->]SAMPLE")
        w_i = 200
        h_i = 200
        self.img = ImageTk.PhotoImage(Image.open(IMAGE_SAMPLE))
        self.img_pos_w = (self.w_ws-w_i)/2
        self.img_pos_h = (self.w_hs-h_i)/2
        self.canvas.create_image(self.img_pos_w, self.img_pos_h, anchor=tk.NW, image=self.img) 
        self.canvas.image = self.img
    
    def show_match(self):
        print("[->]MATCH")
        w_i = 200
        h_i = 200
        inter_distance = 200
        self.img = ImageTk.PhotoImage(Image.open(IMAGE_MATCH))
        self.img_pos_w = (self.w_ws-w_i)/2
        self.img_pos_h = (self.w_hs-h_i)/2
        self.canvas.create_image(self.img_pos_w, self.img_pos_h, anchor=tk.NW, image=self.img) 
        self.canvas.image = self.img
        self.img2 = ImageTk.PhotoImage(Image.open(IMAGE_NOMATCH))
        self.canvas.create_image(self.img_pos_w + 200 + inter_distance, self.img_pos_h, anchor=tk.NW, image=self.img2) 
        self.canvas.image = self.img2

    def show_blank(self):
        print("[->]BLANK")
        self.canvas.delete("all")
    
    def startMouseListener(self):
        self.mouse_listener = mouse.Listener(on_click=on_click)     #sets mouse listener passing function prior defined
        self.mouse_listener.start()                                 #starts mouse listener

    def finishMouseListener(self):
        self.mouse_listener.stop()   #stop listener when program was ended

    

app= PerceptionApp()
app.mainloop()
print("[!] Your score is:{}".format(score))
