#!bin/python3

import sys

# QR decoding
from pyzbar.pyzbar import decode
from PIL import Image

# Firefox
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
# from webdriver_manager.firefox import GeckoDriverManager

def launch_firefox():
    options = Options()
    options.add_argument("--headless")
    service = Service(executable_path="./geckodriver")
    driver = webdriver.Firefox(service=service, options=options)
    driver.get("https://python.org")
    print(driver.title)
    driver.close()

def take_photo():
    from picamera2 import Picamera2
    from libcamera import controls
    import time
    picam2 = Picamera2()
    picam2.start()
    picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous})
    time.sleep(1)
    return picam2.capture_image("main")

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        fn = sys.argv[1]
        img = Image.open(fn)
    else:
        print("Taking a photo...")
        img = take_photo()

    print(decode(img))
