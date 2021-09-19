
# Import libraries
import RPi.GPIO as GPIO
import random
import ES2EEPROMUtils
import os
from time import sleep
# some global variables that need to change as we run the program
end_of_game = None  # set if the user wins or ends the game

# DEFINE THE PINS USED HERE
LED_value = [11, 13, 15]
LED_accuracy = 32
btn_submit = 16
btn_increase = 18
buzzer = 33
eeprom = ES2EEPROMUtils.ES2EEPROM()

# gloabal var
user = ""
guesses = 0
scores = [["ChB", 5], ["Ada", 7], ["LSu", 4], ["EEE", 8]]

current_val = 0
ran_val =0
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
    setup()
    
   
    
    if option == "H":
        os.system('clear')
        print("HIGH SCORES!!")
        #save_scores()
        s_count, ss = fetch_scores()
        display_scores(s_count, ss)
    elif option == "P":
        os.system('clear')
        print("Starting a new round!")
        print("Use the buttons on the Pi to make and submit your guess!")
        print("Press and hold the guess button to cancel your game")
        
        value = generate_number()
        ran_val = value
        current_val = eval(input("Enter the value: "))

        bin_var = bin(current_val).replace("0b","")
        
        if current_val==0 or current_val ==1:
            bin_var = "00"+bin_var
        if(current_val==3 or current_val==2):
            bin_var = "0"+bin_var

        ls = list(bin_var)

        for i in range(3):
            val = int(ls[i])

            if val == 0:
                GPIO.output(LED_value[i], GPIO.LOW)
            else:
                GPIO.output(LED_value[i], GPIO.HIGH)

            



        while not end_of_game:
            pass
    elif option == "Q":
        print("Come back soon!")
        exit()
    else:
        print("Invalid option. Please select a valid one!")


def display_scores(count, raw_data):
    # print the scores to the screen in the expected format
    a, scores = fetch_scores
    print(scores)
    #print("There are {} scores. Here are the top 3!".format(count))
    # print out the scores in the required format
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

    pi_pwm = GPIO.PWM(LED_accuracy,100)
    pi_pwm.start(0)
    #setup buzzer
    GPIO.setup(buzzer,GPIO.OUT)
    GPIO.setwarnings(False)	

    # Setup debouncing and callbacks

    GPIO.add_event_detect(btn_increase,GPIO.FALLING,callback = btn_increase_pressed,bouncetime = 300)

    GPIO.add_event_detect(btn_submit,GPIO.FALLING,callback = btn_guess_pressed,bouncetime = 300)
    
    pass


# Load high scores
def fetch_scores():
    # get however many scores there are
    score_count = None
    
    #scores = ES2EEPROMUtils.read_block()
    score_count = eeprom.read_byte(0)
    scores = eeprom.read_block(1,score_count*4)
    # Get the scores
    char_score = [] 
    for i in range(score_count):
        string= ""
        for j in range(3):
            string += chr(scores[i][j])

        char_score.append([string,scores[i][3]])

    # convert the codes back to ascii
    # return back the results
    return score_count, char_score


# Save high scores
def save_scores():
    # fetch scores
    score_count = eeprom.read_byte(0)
    scores = eeprom.read_block(1, score_count*4)
    #num_scores , scores = fetch_scores()
    # include new score 
    data = []
    for i in range(score_count):
        data.append(scores[slice(i*4, i*4+4)])
    score = list(user)
    score = [ord(i) for i in score]
    score.append(guesses)
    data.append(score)
    
    # update total amount of scores
    score_count = score_count+1
    
    # write new scores
    data.sort(key=lambda x: x[3])
    data = [b for c in data for b in c]
    eeprom.write_block(1,data)
    eeprom.write_block(0,[score_count])
    pass


# Generate guess number
def generate_number():
    return random.randint(0, pow(2, 3)-1)


# Increase button pressed
def btn_increase_pressed(channel):
    # Increase the value shown on the LEDs

    print("Increased pressed(B0)!!!")
    # You can choose to have a global variable store the user's current guess, 
    # or just pull the value off the LEDs when a user makes a guess
    current_val = current_val+1
    bin_var = bin(current_val).replace("0b","")
    if current_val==0 or current_val ==1:
        bin_var = "00"+bin_var
    if(current_val==3 or current_val==2):
        bin_var = "0"+bin_var

    ls = list(bin_var)

    for i in range(3):
        val = int(ls[i])
        if val == 0:
            GPIO.output(LED_value[i], GPIO.LOW)
        else:
            GPIO.output(LED_value[i], GPIO.HIGH)        
    pass


# Guess button
def btn_guess_pressed(channel):
    # If they've pressed and held the button, clear up the GPIO and take them back to the menu screen
    print("Guess_Press(B1)!!!")

    # Compare the actual value with the user value displayed on the LEDs
    # Change the PWM LED
    # if it's close enough, adjust the buzzer
    # if it's an exact guess:
    # - Disable LEDs and Buzzer
    # - tell the user and prompt them for a name
    # - fetch all the scores
    # - add the new score
    # - sort the scores
    # - Store the scores back to the EEPROM, being sure to update the score count
    pass


# LED Brightness
def accuracy_leds():
    # Set the brightness of the LED based on how close the guess is to the answer
    # - The % brightness should be directly proportional to the % "closeness"
    # - For example if the answer is 6 and a user guesses 4, the brightness should be at 4/6*100 = 66%
    # - If they guessed 7, the brightness would be at ((8-7)/(8-6)*100 = 50%
    if(ran_val>current_val):
        duty = (current_val/ran_val)*100
        pi_pwm.ChangeDutyCycle(duty)
    if(ran_val<current_val:
        duty = (8-current_val)/(8-ran_val)*100
        pi_pwm.ChangeDutyCycle(duty)
    else:
       pi_pwm.ChangeDutyCycle(100)
    pass

# Sound Buzzer
def trigger_buzzer():
    # The buzzer operates differently from the LED
    # While we want the brightness of the LED to change(duty cycle), we want the frequency of the buzzer to change
    # The buzzer duty cycle should be left at 50%
    # If the user is off by an absolute value of 3, the buzzer should sound once every second
    difference = abs(ran_val - current_val)
    if(difference == 3):
        while true:
            GPIO.output(buzzer,GPIO.HIGH)
            sleep(0.5) # Delay in seconds
            GPIO.output(buzzer,GPIO.LOW)
            sleep(0.5)        
    # If the user is off by an absolute value of 2, the buzzer should sound twice every second
    if(difference == 2):
        while true:
            GPIO.output(buzzer,GPIO.HIGH)
            sleep(0.25) # Delay in seconds
            GPIO.output(buzzer,GPIO.LOW)
            sleep(0.25)   
    # If the user is off by an absolute value of 1, the buzzer should sound 4 times a second
    if(difference == 1):
        while true:
            GPIO.output(buzzer,GPIO.HIGH)
            sleep(0.125) # Delay in seconds
            GPIO.output(buzzer,GPIO.LOW)
            sleep(0.125)   
    pass


if __name__ == "__main__":
    try:
        # Call setup function
       
        welcome()

        while True:
            menu()
            pass
    except Exception as e:
        print(e)
    finally:
        GPIO.cleanup()
