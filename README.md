# Advanced Python Keylogger

This is an advanced, multi-featured keylogger written in Python, for educational purposes. It goes beyond simple keystroke recording to capture an entire snapshot of user activity, including active applications, system information, clipboard content, and screenshots. All collected text-based data is encrypted with AES-128 in CBC mode for security.

---

## Features

* **Keystroke Logging**: Records individual key presses and the special keys used (e.g., `Key.shift`).
* **Active Application Tracking**: Logs which application was in use when keys were pressed, providing context to the captured data.
* **System Information**: On startup, it gathers detailed host information, including hostname, IP address, operating system, and processor architecture.
* **Clipboard Monitoring**: Periodically captures and logs any text content from the system clipboard.
* **Screenshot Capture**: Takes screenshots of the entire screen at regular, defined intervals.
* **Data Encryption**: Automatically encrypts all generated log files using Fernet symmetric encryption (`cryptography` library) after the logging session is complete.
* **Timed Execution**: Runs in user defined time intervals, for a set number of iterations, allowing for controlled data capture sessions.
* **Modular Class-Based Design**: All logic is encapsulated within a `Keylogger` class, making the code clean, organized, and easy to maintain.

---

## Prerequisites

This script requires several external Python libraries.

**Dependencies:**
* `pynput`
* `requests`
* `Pillow`
* `cryptography`

## Usage

1.   **Install all dependencies**
2.   **Configure the Keylogger**: Open the `keylogger.py` file and modify the parameters in the `Keylogger` class constructor (`__init__`) to suit your needs:
    - `interval`: The time in seconds between each data capture cycle (clipboard and screenshot).
    - `iterations`: The total number of capture cycles to run before the program stops and encrypts the files.
    - `buffer_size`: The number of keystrokes to hold in memory before writing to the log file.

3.  **Run the script** from your terminal:
    ```bash
    python keylogger.py
    ```

4.  The script will run in the background for the configured duration. Once complete, it will create an `out` directory containing the encrypted log files (`.txt`) and screenshots (`.png`).

---

## Potential Improvements
- Add cross platform support for Windows/Linux as AppKit is currently being used which is just for Mac's
- Use a configuration file to settings and variables such as email addresses, time intervals, iterations etc..
- Add a requirements.txt file
