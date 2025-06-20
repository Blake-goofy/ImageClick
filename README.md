# Description
Automate mouse clicks using image detection in current screen

# How it works
Image search / click triggered by Alt+Enter
Use snipping tool or print screen and crop any png image you wish to automate and save to "input_images" folder.
Label according to which image you wish to click. Code will search images until the first image is found on screen.
Then it will automate mouse a left (center of image) in the order of the naming.

Example: 1_edge.png [not found] -> 2_folder.png [not found] -> 3_windows.png [found!] -> [stop looking through images]  

To link images, name them using the format #_find_name.png and #_click_name.png (where # is the priority number).
When the "find" image is detected onscreen, the script will automatically click the corresponding click image.

Example:
If 1_find_submit.png is visible, the script will click 1_click_submit.png.

# Requirements
1) Install python
2) In command prompt, enter:
   pip install pyautogui keyboard numpy opencv-python