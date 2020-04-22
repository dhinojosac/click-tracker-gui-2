import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image
from pynput import mouse
from time import sleep
import random

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
USE_PROGRAM = program2

wait_click = True   # wait click to pass to other stage
success_pass = True # pass to next stage only if you click in the box
click_error = 0     # error at click 

IMAGE_MATCH_PRIM    = "images/G1.png"
IMAGE_NONMATCH_PRIM = "images/G2.png"
IMAGE_MATCH_SEC     = "images/G3.png"
IMAGE_NONMATCH_SEC  = "images/G4.png"

side_nonmatch_random = True # to set random side on nonmatch image
side_nonmatch  = "right" #left or right

nonmatch_distance = 250 #distance nonmatch image 250 px
match_iterations_enable = True #enable iteration in nonmatch stage using differents distances 
match_iterations = [0, 125, 150, 175, 200, 225, 250] #distances between images match/nonmatch stage

#trials
primary_pair_images = [IMAGE_MATCH_PRIM, IMAGE_NONMATCH_PRIM] #pair of images ratio 1
secondary_pair_images = [IMAGE_MATCH_SEC, IMAGE_NONMATCH_SEC] #pair of images ratio 2
trials = 5                      #Number of trial of a session [Set 1 for 1 trial]
trials_ratio =  [3,2]           #ratio of trials [ only first parameter is taken into account to get ratio]
trials_ratio_random = True     #ratio secuencial or random
fix_side_trials = False         #fix side after each trial

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
nonmatch_iters = 0
sides = ["left", "right"]

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
            if match_iterations_enable and app.program.steps[app.stage] == "match": #interation in match/nonmatch stage
                app.addIterMatch()
                if app.niter >= len(match_iterations):
                    app.trials+=1
                    if app.trials >= app.ratio:
                        app.setImages(secondary_pair_images)
                    if app.trials>= trials:
                        app.destroy()
                    if fix_side_trials != True:
                        app.calculateSide()
                    app.restartTrialState()
                    

            elif success_pass:
                app.nextStage()
        else:
            print(">> CLICK FAILED!")
            led_failed()
        if not success_pass:
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
        self.niter = 0
        self.trials = 0

        self.startMouseListener()

        self.getRatioTrials()
        self.setRandomRatio()
        self.getTrialImage()

        self.setImages(primary_pair_images)
        self.calculateSide()

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
    
    def setRandomRatio(self):
        if trials_ratio_random:
            self.session_images = [1] * self.ratio + [2] * (trials-self.ratio)
            random.shuffle(self.session_images)
            print(self.session_images)
    
    def getTrialImage(self):
        if self.session_images[self.trials] == 1:
            self.setImages(primary_pair_images)
        elif self.session_images[self.trials]==2:
            self.setImages(secondary_pair_images)

    def setImages(self, images_add):
        self.match_image = images_add[0]
        self.nonmatch_image = images_add[1]
    
    def restartTrialState(self):
        self.stage = 0
        self.niter = 0
        self.counter = 0
        self.show_blank()
        self.getTrialImage()


    def getRatioTrials(self):
        self.ratio = trials_ratio[0]

    
    def addIterMatch(self):
        self.niter+=1

    def setProgram(self, program):
        self.program = program
    
    def runProgram(self):
        if self.program == None:
            print("Error, does't exist program")
        else:
            self.runStage()
        self.mUpdate()
    
    def calculateSide(self):
        #Set side random if sode_nonmatch_random is true
        if side_nonmatch_random == True:
            self.side_nonmatch = random.choice(sides)
        else:
            self.side_nonmatch = side_nonmatch

    def mUpdate(self):
        if self.program.steps[self.stage] == "blank" or not wait_click:
            self.counter = self.counter + 1 # ticks every 500 ms
        #print("stage:{} program:{}  counter:{}".format(self.stage, self.program.steps[self.stage], self.counter)) #debug
        if self.counter >= self.program.times[self.stage]*2: # compare times
            print("[!] Next Stage") #debug
            self.nextStage()
            if self.stage>= self.program.len: #check stages limit
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

    # Shows warning stage
    def show_warning(self):
        print("[->]WARNING")
        global square_pos_x, square_pos_y
        colorval            = [255,0,0]
        rcol =  colorval            # square color
        colorval = "#%02x%02x%02x" % (rcol[0], rcol[1], rcol[2]) # rgb to hexadecimal format
        square_pos_x = (self.w_ws-square_size)/2
        square_pos_y = (self.w_hs-square_size)/2
        self.canvas.create_rectangle(square_pos_x, square_pos_y, square_pos_x+square_size, square_pos_y+square_size, fill=colorval) #create blue square

    # Shows sample stage
    def show_sample(self):
        print("[->]SAMPLE")
        w_i = 200
        h_i = 200
        self.img = ImageTk.PhotoImage(Image.open(self.match_image))
        self.img_pos_w = (self.w_ws-w_i)/2
        self.img_pos_h = (self.w_hs-h_i)/2
        self.canvas.create_image(self.img_pos_w, self.img_pos_h, anchor=tk.NW, image=self.img) 
        self.canvas.image = self.img
    
    # Shows Match/Nonmatch stage
    def show_match(self):
        global square_pos_x, square_pos_y
        print("[->]MATCH")
        w_i = 200
        h_i = 200

        #center position 
        self.img_pos_w = (self.w_ws-w_i)/2
        self.img_pos_h = (self.w_hs-h_i)/2
        square_pos_y = self.img_pos_h

        #set match image
        if match_iterations_enable:
            if self.side_nonmatch == "left":
                square_pos_x =  self.img_pos_w  + match_iterations[self.niter] 
            else:
                square_pos_x =  self.img_pos_w  - match_iterations[self.niter] 
        else:
            square_pos_x = 0
        self.img = ImageTk.PhotoImage(Image.open(self.match_image))
        self.canvas.create_image(square_pos_x, self.img_pos_h, anchor=tk.NW, image=self.img) 
        self.canvas.image = self.img

        #set nonmatch image
        if self.side_nonmatch == "left":
            pos_nonmatch = self.img_pos_w - nonmatch_distance
        else:
            pos_nonmatch = self.img_pos_w + nonmatch_distance

        self.img2 = ImageTk.PhotoImage(Image.open(self.nonmatch_image))
        self.canvas.create_image(pos_nonmatch, self.img_pos_h, anchor=tk.NW, image=self.img2) 
        self.canvas.image = self.img2
        
        
    # Shows blank stage
    def show_blank(self):
        print("[->]BLANK")
        self.canvas.delete("all")
    
    # Enable mouse listener
    def startMouseListener(self):
        self.mouse_listener = mouse.Listener(on_click=on_click)     #sets mouse listener passing function prior defined
        self.mouse_listener.start()                                 #starts mouse listener
    
    # Disable mouse listener
    def finishMouseListener(self):
        self.mouse_listener.stop()   #stop listener when program was ended

    

app= PerceptionApp()
app.mainloop()
print("\n*****************************************")
print("[!] Your score is:{}".format(score))
print("*****************************************\n")