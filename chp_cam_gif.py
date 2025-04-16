from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from datetime import datetime as dt
import time
import os
import cv2
import re
from PIL import Image

pattern = re.compile(r'\/screenshot\_([0-9]+)\.png')
camera_name_pattern = re.compile(r'^(.*)\n')
camera_loc_pattern = re.compile(r'^.*\n(.*)\n')

browser = webdriver.Chrome()
url = 'https://cwwp2.dot.ca.gov/vm/loc/d3/hwy80atoldagsta.htm'
browser.get(url)
browser.implicitly_wait(5)

info = browser.find_element(By.XPATH, '//*[@id="wxText"]')
camera_info = info.get_attribute('innerText')

el = browser.find_element(By.XPATH, '//*[@id="my-video"]/button').click()
browser.implicitly_wait(25)
el = browser.find_element(By.XPATH, '//*[@id="my-video"]')
browser.implicitly_wait(5)

camera_info_matches = re.findall(camera_name_pattern, camera_info)
camera_location_matches = re.findall(camera_loc_pattern, camera_info)

start_time = time.time()
screenshot_count = 0
duration_seconds = 5
filenames = []

print('[%s] Taking screenshots of %s at %s CHP Traffic Camera' %(dt.now().strftime("%Y-%m-%d %H:%M:%S"), camera_info_matches[0], camera_location_matches[0]))
while time.time() - start_time < duration_seconds:
    screenshot_count += 1
    filename = os.path.join(os.getcwd(), f"screenshot_{screenshot_count}.png")
    filenames.append(filename)
    el.screenshot(filename)
    browser.save_screenshot(filename)
browser.quit()

for f in filenames:
    image = cv2.imread(f)
    y_start, y_end = 80, 475
    x_start, x_end = 25, 560
    cropped_image = image[y_start:y_end, x_start:x_end]
    screenshot_num = re.findall(pattern, f)
    cv2.imwrite(os.getcwd()+"/"+"screenshot_"+str(screenshot_num[0])+'.png', cropped_image)

for f in filenames[0:4]:
    os.remove(f)
filenames = filenames[4:]

for f in filenames:
    img = Image.open(f)
    screenshot_num = re.findall(pattern, f)
    org_size = img.size
    pixelate_lvl = 2
    
    img = img.resize(
        size=(org_size[0] // pixelate_lvl, org_size[1] // pixelate_lvl),
        resample=0)
    img = img.resize(org_size, resample=0)
    img = img.convert("P", palette=Image.ADAPTIVE, colors=256)
    
    gray_palette = []
    palette = img.getpalette()
    for i in range(0, len(palette), 3):
        r, g, b = palette[i], palette[i+1], palette[i+2]
        gray_value = int(0.2 * r + 0.7 * g + 0.05 * b)
        gray_palette.extend([gray_value, gray_value, gray_value])
        img.putpalette(gray_palette)
        img.convert('RGB').save(os.getcwd()+"/"+"screenshot_"+str(screenshot_num[0])+'.png')

print('[%s] Screenshots converted to grayscale and pixelated' %dt.now().strftime("%Y-%m-%d %H:%M:%S"))

print('[%s] Create gif from screenshots' %dt.now().strftime("%Y-%m-%d %H:%M:%S"))
images = [Image.open(image_path) for image_path in filenames]
output_gif_path = 'out.gif'
duration = 2
loop = 10
images[0].save(
    output_gif_path,
    save_all=True,
    append_images=images[1:],
    duration=duration,
    loop=loop)

for f in filenames:
    os.remove(f)
