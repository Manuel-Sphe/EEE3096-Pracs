# Import libraries
import RPi.GPIO as GPIO
import random
import ES2EEPROMUtils
import os
import time
from time import sleep
# some global variables that need to change as we run the program
end_of_game = None  # set if the user wins or ends the game

# DEFINE THE PINS USED HERE
LED_value = [15, 13, 11]
LED_accuracy = 32
btn_submit = 16
btn_increase = 18
buzzer = 33
eeprom = ES2EEPROMUtils.ES2EEPROM()


# gloabal var
user = []
guesses = [0]
duration = [time.time()] # get the current time 

current_val = [-1]
ran_val = random.randint(0, pow(2, 3)-1)
bits = [0,0,0] 

# Print the game banner
def welcome():
    os.system('clear')
    print("  _   _                 _                  _____ _            __  __ _")
    print("| \ | |               | |                / ____| |          / _|/ _| |")
    print("|  \| |_   _ _ __ ___ | |__   ___ _ __  | (___ | |__  _   _| |_| |_| | ___ ")
    print("| . ` | | | | '_ ` _ \| '_ \ / _ \ '__|  \___ \| '_ \| | | |  _|  _| |/ _ \\")
    print("| |\  | |_| | | | | | | |_) |  __/ |     ____) | | | | |_| | | | | | |  __/")
    print("|_| \_|\__,_|_| |_| |_|_.__/ \___|_|    |_____/|_| |_|\__,_|_| |_| |_|\___|")
    print("")
    print("Guess the number and immortalise your name in the High Score Hall of Fame!")


# Print the game menu
def menu():
    global end_of_game
    option = input("Select an option:   H - View High Scores     P - Play Game       Q - Quit\n")
    option = option.upper()
    if option == "H":
        os.system('clear')
        print("HIGH SCORES!!")
        s_count, ss = fetch_scores()
        display_scores(s_count, ss)
    elif option == "P":
        os.system('clear')
        print("Hello")
        print("Starting a new round!")
        print("Use the buttons on the Pi to make and submit your guess!")
        print("Press and hold the guess button to cancel your game")
        ran_val = generate_number()
        while not end_of_game:
            pass
    elif option == "Q":
        print("Come back soon!")
        exit()
    else:
        print("Invalid option. Please select a valid one!")


def display_scores(count, raw_data):
    # print the scores to the screen in the expected format
    print("There are {} scores. Here are the top 3!".format(count))
    # print out the scores in the required format
    for i in range(3):
        print(i+1," - " ,raw_data[i][0],"took ",raw_data[i][1],"guesses")
    pass


# Setup Pins
def setup():
    # Setup board mode
    GPIO.setmode(GPIO.BOARD) # set numbering 
    # Setup regular GPIO
    for i in range (3):
        GPIO.setup(LED_value[i],GPIO.OUT,initial=GPIO.LOW) # setting the LEDS to output mode 
    
    GPIO.setup(LED_accuracy,GPIO.OUT,initial = GPIO.LOW)
    # buttons
    GPIO.setup(btn_submit,GPIO.IN,pull_up_down = GPIO.PUD_UP)


    GPIO.setup(btn_increase,GPIO.IN,pull_up_down=GPIO.PUD_UP)

    # Setup PWM channels
    global pi_pwm
    pi_pwm = GPIO.PWM(LED_accuracy,100)
    pi_pwm.start(0)

    GPIO.setup(buzzer,GPIO.OUT)
    GPIO.output(buzzer,GPIO.LOW)
    GPIO.setwarnings(False)	
    
    global buzz 
    buzz = GPIO.PWM(buzzer,1)
    buzz.start(0)
  
   ## while True:
      ##  for duty in range(101):
           ## pi_pwm.ChangeDutyCycle(duty)
            ##sleep(0.01)
       ## sleep(0.5)

        #for duty in range(100,-1,-1):
          #  pi_pwm.ChangeDutyCycle(duty)
           # sleep(0.01)
        #sleep(0.5)

            

    # Setup debouncing and callbacks

    GPIO.add_event_detect(btn_increase,GPIO.FALLING,callback = btn_increase_pressed,bouncetime = 300)

    GPIO.add_event_detect(btn_submit,GPIO.FALLING,callback = btn_guess_pressed,bouncetime = 300)
    
    


    pass


# Load high scores
def fetch_scores():
    # get however many scores there are
    score_count = None
    # Get the scores
    scores = []
    score_count = eeprom.read_byte(0) # 1st byte 
    for k in range(1, score_count):
        scores.append(eeprom.read_block(k,score_count))
    #scores.sort(key=lambda x: x[1])
    #print(scores)  
    # convert the codes back to ascii
    
    char_score  = [] 
    for i in range(len(scores)):
        string = ""
        for j in range(3):
            string += chr(scores[i][j])
        char_score.append([string,scores[i][3]])
    # returz)
    return score_count -1 , char_score


# Save high scores
def save_scores():
     # fetch scores
    score_count,scores = fetch_scores()
    scores.append([user[-1], guesses[-1]])
    score_count+=1
    scores.sort(key=lambda x: x[1])
    for i, score in enumerate(scores):
        data_to_write = []
        # get the string
        for letter in score[0]:
            data_to_write.append(ord(letter))
        data_to_write.append(score[1])
        eeprom.write_block(i+1, data_to_write)
    eeprom.write_block(0,[score_count])
    pass


# Generate guess number
def generate_number():
    return random.randint(0, pow(2, 3)-1)


# Increase button pressed
def btn_increase_pressed(channel):
    # Increase the value shown on the LEDs
    
    current = current_val[-1]
    current = current+1
    if(current>7):
        current =0
    bin_var = bin(current).replace("0b","")
        
    if current==0 or current ==1:
        bin_var = "00"+bin_var
    if(current==3 or current==2):
        bin_var = "0"+bin_var
    ls = list(bin_var)
    #current+= 1
    current_val.append(current)
    for i in range(3):
        val = int(ls[i])

        if val == 0:
            GPIO.output(LED_value[i], GPIO.LOW)
        else:
            GPIO.output(LED_value[i], GPIO.HIGH)       
    #print('rand value: ',ran_val)
    #print('current value: ',current_val[-1])
    #print("Increased pressed(B0)!!!")
    # You can choose to have a global variable store the user's current guess, 
    # or just pull the value off the LEDs when a user makes a guess
    pass


# Guess button
def btn_guess_pressed(channel):
    # If they've pressed and held the button, clear up the GPIO and take them back to the menu screen
    # Change the PWM LED
    # if it's close enough, adjust the buzzer
    # if it's an exact guess:
    # - Disable LEDs and Buzzer
    # - tell the user and prompt them for a name
    # - fetch all the scores
    # - add the new score
    # - sort the scores
    # - Store the scores back to the EEPROM, being sure to update the score count
    #print("Guess_Press(B1)!!!")
    count = guesses[-1]+1
    # hold to end the end 
    global duration
    global end_of_game
    global btn_submit
    btn_submit = 16 
    count1 = time.time()
    while GPIO.input(btn_submit)==GPIO.LOW:
        time.sleep(0.01)
    elasped = time.time() - count1

    if elasped >=2:
        GPIO.cleanup()
        end_of_game = True
        elasped =0

    # Compare the actual value with the user value displayed on the LEDs
    if(count1 - duration[-1]) >= 0.3:
        if(ran_val == current_val[-1]):
            for i in range (3):
                GPIO.setup(LED_value[i],GPIO.OUT,initial=GPIO.LOW)
            GPIO.output(buzzer,GPIO.LOW)
            buzz.stop()
            pi_pwm.stop()
            
            name = input("Enter your name: ")
            user.append(name)
            #count = len(current_val)-1
            guesses.append(count)
            save_scores()
            menu()
        else:
            trigger_buzzer()
            accuracy_leds()
    pass


# LED Brightness
def accuracy_leds():
    # Set the brightness of the LED based on how close the guess is to the answer
    # - The % brightness should be directly proportional to the % "closeness"
    # - For example if the answer is 6 and a user guesses 4, the brightness should be at 4/6*100 = 66%
    # - If they guessed 7, the brightness would be at ((8-7)/(8-6)*100 = 50%
    duty = 0
    if(ran_val>current_val[-1]):
        duty = (current_val[-1]/ran_val)*100
    if(ran_val<current_val[-1]):
        duty = (8-current_val[-1])/(8-ran_val)*100
    
    pi_pwm.ChangeDutyCycle(duty)
    #time.sleep(120)
    #pi_pwm.stop()
    pass

# Sound Buzzer
def trigger_buzzer():
    # The buzzer operates differently from the LED
    # While we want the brightness of the LED to change(duty cycle), we want the frequency of the buzzer to change
    # The buzzer duty cycle should be left at 50%
    # If the user is off by an absolute value of 3, the buzzer should sound once every second
    # If the user is off by an absolute value of 2, the buzzer should sound twice every second
    # If the user is off by an absolute value of 1, the buzzer should sound 4 times a second
    buzz.ChangeDutyCycle(50)

    difference = abs(ran_val - current_val[-1])

    if difference == 3:
         buzz.ChangeFrequency(1)
    elif difference == 2:
         buzz.ChangeFrequency(2)
    elif difference == 1:
         buzz.ChangeFrequency(4)
    else:
        buzz.ChangeDutyCycle(0.00000000001)
    pass


if __name__ == "__main__":
    try:
        # Call setup function
        setup()
        
        welcome()
        while True:
            menu()
    except Exception as e:
        print(e)
    finally:
        GPIO.cleanup()
        pi_pwm.stop()
        buzz.stop()
