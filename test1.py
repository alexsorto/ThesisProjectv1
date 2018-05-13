import time
import lcddriver
import pygame
import requests
import json

from pirc522 import RFID

pygame.init()
pygame.display.set_mode()

display = lcddriver.lcd()

rdr = RFID()

enteredValue = ""
transactionType = 0

def wipeLcdLine(line):
    display.lcd_display_string("", line)


def runAnimation(frame):
    if(frame == 0):
        display.lcd_display_string("Payment:$" + enteredValue, 1)
        wipeLcdLine(2)
        display.lcd_display_string('      (())      ', 2)
    if(frame == 1):
        wipeLcdLine(2)
        display.lcd_display_string("Payment:$" + enteredValue, 1)
        display.lcd_display_string('     ((  ))     ', 2)
    if(frame == 2):
        wipeLcdLine(2)
        display.lcd_display_string("Payment:$" + enteredValue, 1)
        display.lcd_display_string('    (((  )))    ', 2)
    if(frame == 3):
        wipeLcdLine(2)
        display.lcd_display_string("Payment:$" + enteredValue, 1)
        display.lcd_display_string('   (((    )))   ', 2)
    if(frame == 4):
        wipeLcdLine(2)
        display.lcd_display_string("Payment:$" + enteredValue, 1)
        display.lcd_display_string('  (((      )))  ', 2)
    if(frame == 5):
        wipeLcdLine(2)
        display.lcd_display_string("Payment:$" + enteredValue, 1)
        display.lcd_display_string(' (((        ))) ', 2)
    if(frame == 6):
        wipeLcdLine(2)
        display.lcd_display_string("Payment:$" + enteredValue, 1)
        display.lcd_display_string('(((          )))', 2)



def requestUID():

  waitNFCInput = 1
  aniLoop = 0
  while waitNFCInput == 1:
      runAnimation(aniLoop)
      if(aniLoop == 6):
        aniLoop = 0
      else:
        aniLoop = aniLoop + 1

      (error, tag_type) = rdr.request()
      if not error:
          print("Tag detected")
          (error, uid) = rdr.anticoll()
          if not error:
              print("UID: " + str(uid))

              display.lcd_clear()
              display.lcd_display_string("Code OK", 2)

              waitNFCInput = 2

              # Select Tag is required before Auth
              if not rdr.select_tag(uid):
                  # Auth for block 10 (block 2 of sector 2) using default shipping key A
                  if not rdr.card_auth(rdr.auth_a, 10, [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF], uid):
                      # This will print something like (False, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
                      print("Reading block 10: " + str(rdr.read(10)))
                      # Always stop crypto1 when done working
                      rdr.stop_crypto()
                      return uid;

# Calls GPIO cleanup
rdr.cleanup()

# returneduid = requestUID()
# print("Returned ID" + str(returneduid))


def initValueEnterState():
    display.lcd_clear()
    display.lcd_display_string('Enter Amount:', 1)


def updateEnteredValue(key):
    global enteredValue
    enteredValue = enteredValue + key
    display.lcd_display_string('Enter Amount:', 1)
    display.lcd_display_string("$" + enteredValue, 2)



def backspaceEnteredValue():
    display.lcd_clear()

    global enteredValue
    enteredValue2 = enteredValue
    enteredValue2 = enteredValue2[:-1]
    enteredValue = enteredValue2
    print(enteredValue)

    display.lcd_display_string('Enter Amount:', 1)
    display.lcd_display_string("$" + enteredValue2, 2)

def reportPaymentResult(success,credit):
    display.lcd_clear()
    if(success == 1):
        display.lcd_display_string("Success!", 1)
        display.lcd_display_string("Credit: $" + str(credit), 2)
        time.sleep(2)

        initMenu()

    if(success == 0):
        display.lcd_display_string("Failed!", 1)
        display.lcd_display_string("No Credit", 2)
        time.sleep(2)

        initMenu()

def reportReloadResult(success,credit):
    display.lcd_clear()
    if(success == 1):
        display.lcd_display_string("Success!", 1)
        display.lcd_display_string("Credit: $" + str(credit), 2)
        time.sleep(2)
        initMenu()


    if(success == 0):
        display.lcd_display_string("Load Failed", 1)
        display.lcd_display_string("No Connection", 2)
        time.sleep(2)

        initMenu()


def submitValue():
    display.lcd_clear()

    global transactionType
    global enteredValue

    floatValue = float(enteredValue)

    userUid = requestUID()

    if(transactionType == 1):
        requestBody = json.dumps({'companyid': 1, 'uid': userUid, 'amount':floatValue, 'consoleid':1})

        response = requests.post('http://192.168.42.125:8081/takeCredit', json={'companyid': 1, 'uid': userUid, 'amount':floatValue, 'consoleid':1})
        print(requestBody)
        print(response.status_code)
        print(response.text)
        responseJSON = json.loads(response.text)

        rSuccess = responseJSON["success"]
        newCredit = responseJSON["credit"]

        reportPaymentResult(rSuccess,newCredit)
        
        

    elif(transactionType == 2):
        requestBody = json.dumps({'companyid': 1, 'uid': userUid, 'amount':floatValue, 'consoleid':1})
        print(requestBody)

        response = requests.post('http://192.168.42.125:8081/addCredit', json={'companyid': 1, 'uid': userUid, 'amount':floatValue, 'consoleid':1})
        print(response.status_code)
        print(response.text)
        responseJSON = json.loads(response.text)
        rSuccess = responseJSON["success"]
        newCredit = responseJSON["credit"]

        reportReloadResult(rSuccess,newCredit)


def requestInput():

    display.lcd_clear()
    global enteredValue
    enteredValue = ""
    
    display.lcd_display_string('Enter Amount:', 1)
    display.lcd_display_string("$" + enteredValue, 2)



    userInputting = 1

    while(userInputting == 1):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_KP0:
                    updateEnteredValue("0")
                if event.key == pygame.K_KP1:
                    updateEnteredValue("1")
                if event.key == pygame.K_KP2:
                 updateEnteredValue("2")
                if event.key == pygame.K_KP3:
                    updateEnteredValue("3")
                if event.key == pygame.K_KP4:
                    updateEnteredValue("4")
                if event.key == pygame.K_KP5:
                    updateEnteredValue("5")
                if event.key == pygame.K_KP6:
                    updateEnteredValue("6")
                if event.key == pygame.K_KP7:
                    updateEnteredValue("7")
                if event.key == pygame.K_KP8:
                    updateEnteredValue("8")
                if event.key == pygame.K_KP9:
                    updateEnteredValue("9")
                if event.key == pygame.K_KP_PERIOD:
                    updateEnteredValue(".")
                if event.key == pygame.K_BACKSPACE:
                    print("Deleting string 1")
                    backspaceEnteredValue()
                if event.key == pygame.K_KP_ENTER:
                    print("Entering Value")
                    submitValue()
                    userInputting = 2

def initMenu():

    waitingMenuChoice = 1
    display.lcd_clear()


    display.lcd_display_string("1. Fare Payment", 1)
    display.lcd_display_string('2. Reload', 2)

    while(waitingMenuChoice == 1):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_KP1:
                    global transactionType
                    transactionType = 1
                    waitingMenuChoice = 2
                    requestInput()
                if event.key == pygame.K_KP2:
                    global transactionType
                    transactionType = 2
                    waitingMenuChoice = 2

                    requestInput()




initMenu()


