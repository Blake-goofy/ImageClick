import pyautogui
import cv2
import numpy as np
import glob
import keyboard
import os

def easeOutQuad(x):
    return 1 - (1 - x) * (1 - x)

def image_match(image_path, threshold=0.9):
    screen = pyautogui.screenshot()
    screen_gray = cv2.cvtColor(np.array(screen), cv2.COLOR_BGR2GRAY)
    template = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    result = cv2.matchTemplate(screen_gray, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)
    if max_val < threshold:
        return None
    center = (max_loc[0] + template.shape[1] // 2, max_loc[1] + template.shape[0] // 2)
    return center

def on_hotkey():
    all_images = sorted(glob.glob("./input_images/*.png"))

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
        singles = [f for f in files if "_find_" not in os.path.basename(f) and "_click_" not in os.path.basename(f)]

        # Try find/click pair
        for find_img in finds:
            base_name = os.path.basename(find_img).replace("_find_", "_click_")
            click_img = os.path.join(os.path.dirname(find_img), base_name)
            if os.path.exists(click_img):
                print(f"Looking for linked pair: {os.path.basename(find_img)} + {os.path.basename(click_img)}")
                loc = image_match(find_img)
                if loc:
                    click_loc = image_match(click_img)
                    if click_loc:
                        pyautogui.moveTo(click_loc[0], click_loc[1], duration=0.5, tween=easeOutQuad)
                        pyautogui.click()
                        print(f"Clicked on {os.path.basename(click_img)}")
                        return
        # Fallback to single direct click images
        for image in singles:
            loc = image_match(image)
            if loc:
                pyautogui.moveTo(loc[0], loc[1], duration=0, tween=easeOutQuad)
                pyautogui.click()
                print(f"Clicked on {os.path.basename(image)}")
                return

    print("No matching image found.")

print("Ready. Press Alt+Enter to scan and click with linked image support.")
keyboard.add_hotkey("alt+enter", on_hotkey)
keyboard.wait()