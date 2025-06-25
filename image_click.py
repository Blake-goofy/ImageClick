import pyautogui
import cv2
import numpy as np
import glob
import os
import time
import socket
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

TRIGGER_FILE = "trigger.txt"

def easeOutQuad(x):
    return 1 - (1 - x) * (1 - x)

def image_match(image_path, threshold=0.99):
    screen = pyautogui.screenshot()
    screen_gray = cv2.cvtColor(np.array(screen), cv2.COLOR_BGR2GRAY)
    template = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    result = cv2.matchTemplate(screen_gray, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)
    if max_val < threshold:
        return None
    center = (max_loc[0] + template.shape[1] // 2, max_loc[1] + template.shape[0] // 2)
    return center

def try_find_and_click(image, timeout=3, interval=0.3):
    """Try to find and click an image for up to `timeout` seconds."""
    end_time = time.time() + timeout
    while time.time() < end_time:
        loc = image_match(image)
        if loc:
            pyautogui.moveTo(loc[0], loc[1], duration=0, tween=easeOutQuad)
            pyautogui.click()
            print(f"Clicked on {os.path.basename(image)}")
            return True
        time.sleep(interval)
    print(f"Failed to find {os.path.basename(image)} in chain.")
    return False

def process_folder(folder):
    all_images = sorted(glob.glob(f"{folder}/*.png"))

    # Group by base priority number
    priorities = {}
    for path in all_images:
        filename = os.path.basename(path)
        if "_" not in filename:
            continue
        prefix = filename.split("_", 1)[0]
        if not prefix.isdigit():
            continue
        priorities.setdefault(int(prefix), []).append(path)

    for priority in sorted(priorities):
        files = priorities[priority]
        finds = [f for f in files if "_find_" in os.path.basename(f)]
        chain_files = [f for f in files if "_chain_" in os.path.basename(f)]
        singles = [f for f in files if "_find_" not in os.path.basename(f) and "_click_" not in os.path.basename(f) and "_chain_" not in os.path.basename(f)]

        if finds:
            # Only process _click_ or chain if _find_ is found
            for find_img in finds:
                base_name = os.path.basename(find_img).replace("_find_", "_click_")
                click_img = os.path.join(os.path.dirname(find_img), base_name)
                chain_start = [f for f in chain_files if "_click_chain_1_" in os.path.basename(f)]
                print(f"Looking for find image: {os.path.basename(find_img)}")
                loc = image_match(find_img)
                if loc:
                    print(f"Located find image: {find_img} at {loc}")
                    # If chain, do the chain
                    if chain_start:
                        chain_num = 1
                        current_img = chain_start[0]
                        while True:
                            if not try_find_and_click(current_img):
                                return
                            chain_num += 1
                            next_chain = [f for f in chain_files if f"_chain_{chain_num}_" in os.path.basename(f)]
                            if not next_chain:
                                return
                            current_img = next_chain[0]
                    # Otherwise, just click the click_img
                    elif os.path.exists(click_img):
                        click_loc = image_match(click_img)
                        if click_loc:
                            pyautogui.moveTo(click_loc[0], click_loc[1], duration=0, tween=easeOutQuad)
                            pyautogui.click()
                            print(f"Clicked on {os.path.basename(click_img)}")
                            return
                else:
                    print(f"Did not find {os.path.basename(find_img)}; skipping clicks for this priority.")
            # If there was a _find_, never fall through to chain/singles for this priority
            continue

        # Fallback to chain without find
        chain_start = [f for f in chain_files if "_click_chain_1_" in os.path.basename(f)]
        if chain_start:
            chain_num = 1
            current_img = chain_start[0]
            while True:
                if not try_find_and_click(current_img):
                    return
                chain_num += 1
                next_chain = [f for f in chain_files if f"_chain_{chain_num}_" in os.path.basename(f)]
                if not next_chain:
                    return
                current_img = next_chain[0]

        # Fallback to single direct click images
        for image in singles:
            loc = image_match(image)
            if loc:
                pyautogui.moveTo(loc[0], loc[1], duration=0, tween=easeOutQuad)
                pyautogui.click()
                print(f"Clicked on {os.path.basename(image)}")
                return

    print("No matching image found.")

def server_mode(host='127.0.0.1', port=50007):
    print(f"ImageClick server listening on {host}:{port}")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        while True:
            conn, addr = s.accept()
            with conn:
                folder = conn.recv(1024).decode('utf-8').strip()
                print(f"Received folder: {folder}")
                result = process_folder(folder)
                conn.sendall(result.encode('utf-8'))

class TriggerHandler(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        self.last_time = None

    def on_modified(self, event):
        if event.src_path.endswith(TRIGGER_FILE):
            with open(TRIGGER_FILE, "r") as f:
                lines = f.read().splitlines()
                folder = lines[0] if lines else None
                time_val = lines[1] if len(lines) > 1 else None
                if time_val == self.last_time:
                    #print("No change in time, ignoring trigger.")
                    return
                self.last_time = time_val
                if folder:
                    print(f"Triggered for folder: {folder}")
                    process_folder(folder)

if __name__ == "__main__":
    if not os.path.exists(TRIGGER_FILE):
        with open(TRIGGER_FILE, "w") as f:
            f.write("")
    event_handler = TriggerHandler()
    observer = Observer()
    observer.schedule(event_handler, ".", recursive=False)
    observer.start()
    print("Watching for trigger file changes...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()