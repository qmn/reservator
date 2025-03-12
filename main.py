#!bin/python3

import os
import sys
import time
import json
from datetime import datetime

# Display
import board
import digitalio
from adafruit_rgb_display import st7735

# Camera
from picamera2 import Picamera2
from libcamera import controls

# QR decoding
from PIL import Image, ImageDraw, ImageFont
from pyzbar.pyzbar import decode, ZBarSymbol

# Selenium+Chrome
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

class Display:
    def __init__(self):
        cs_pin = digitalio.DigitalInOut(board.CE0)
        dc_pin = digitalio.DigitalInOut(board.D25)
        reset_pin = digitalio.DigitalInOut(board.D24)
        BAUDRATE = 24000000
        spi = board.SPI()
        self.disp = st7735.ST7735R(spi,
            rotation=180,
            height=128,
            x_offset=2,
            y_offset=3,   # 1.44" ST7735R
            cs=cs_pin,
            dc=dc_pin,
            rst=reset_pin,
            baudrate=BAUDRATE,
        )
        self.lasttime = datetime.now()
        self.create_background()
        self.disp.image(self.background)
        self.console = []

    # Create the background image
    def create_background(self):
        self.background = Image.new(mode="RGB", size=(128, 128), color="white")
        draw = ImageDraw.Draw(self.background)
        # Make it not anti-aliased, for legibility on small screens
        # https://stackoverflow.com/questions/5747739/
        draw.fontmode = "1"
        # Top bar
        draw.rectangle([(0, 0), (127, 15)], fill="#000080")
        # Basic font engine removes kerning but looks better overall
        arial = ImageFont.FreeTypeFont("/usr/share/fonts/truetype/msttcorefonts/arial.ttf", 11, layout_engine=ImageFont.Layout.BASIC)
        arial_bold = ImageFont.FreeTypeFont("/usr/share/fonts/truetype/msttcorefonts/arialbd.ttf", 12, layout_engine=ImageFont.Layout.BASIC)
        self.w95 = ImageFont.FreeTypeFont("w95font/W95font.otf", 13)
        self.w95b = ImageFont.FreeTypeFont("w95font/W95font-Bold.otf", 13)

        draw.text((2, 2), "Reservator", fill="white", font=self.w95b)
        draw.rectangle([(0,112), (127,127)], fill="#b5b5b5") # D5D5D0
        draw.text((2, 113), "File Open Quit", fill="black", font=self.w95b)
        # Bottom lines
        draw.line([(0, 111), (127, 111)], width=2, fill="black")
        draw.line([(0, 127), (127, 127)], width=3, fill="black")

    # Draw the preview image from the camera, update the FPS and clock
    def tick(self, preview):
        img = self.background.copy()
        img.paste(preview, (0, 16))
        draw = ImageDraw.Draw(img)
        draw.fontmode = "1"
        # Write FPS
        curtime = datetime.now()
        fps = 1. / (curtime - self.lasttime).total_seconds()
        self.lasttime = curtime
        draw.text((2, 82), f" fps: {fps:.1f}", fill="black", font=self.w95)
        # Write time
        draw.text((80, 2), curtime.strftime("%I:%M:%S"), fill="white", font=self.w95)
        self.disp.image(img)

    def log(self, *s):
        img = self.background.copy()
        self.console.append(" ".join(str(ss) for ss in s))
        self.console = self.console[-5:]
        draw = ImageDraw.Draw(img)
        draw.fontmode = "1"
        for i, ss in enumerate(self.console):
            draw.text((2, 15*(i+1)), ss, fill="black", font=self.w95)
        # Write time
        curtime = datetime.now()
        draw.text((80, 2), curtime.strftime("%I:%M:%S"), fill="white", font=self.w95)
        self.disp.image(img)

# Start display first
display = Display()
display.log("Starting Reservator...")

def print_and_log(*args):
    print(*args)
    display.log(*args)

def start_chrome(headless=True):
    options = Options()
    service = Service(executable_path="/usr/bin/chromedriver")
    if headless:
        options.add_argument("--headless")
    options.add_argument("--no-memcheck")
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def start_camera():
    picam2 = Picamera2()
    picam2.start()
    picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous})
    return picam2

def load_cookie(driver, cookie_fn):
    with open(cookie_fn, "r") as f:
        cookies = json.load(f)
    print_and_log("  Getting cic50milk.roomzilla.me...")
    driver.get("https://cic50milk.roomzilla.me")
    print_and_log("  Adding cookie...")
    driver.add_cookie(cookies[0])
    print_and_log("  Cookie added.")

def is_roomzilla(url):
    return url.startswith("https://adhoc.roomzilla.me")

def reserve_room(driver, url):
    print_and_log("  Getting", url)
    driver.get(url)
    print_and_log("  Finding buttons...")
    buttons = driver.find_elements(By.TAG_NAME, "button")
    buttons_dict = {b.text: b for b in buttons}
    if "Use Now" in buttons_dict:
        # buttons_dict["Use Now"].click()
        print_and_log("  Could have clicked 'Use Now'")
        time.sleep(1)
    else:
        print_and_log("  Failed to find 'Use Now'")
        print_and_log(f"  Buttons are {list(buttons_dict.keys())}")
        print_and_log("  " + driver.title)
        time.sleep(1)

def main(cookie):
    print_and_log("Starting driver...")
    driver = start_chrome(True)
    print_and_log("Loading cookie...")
    load_cookie(driver, cookie)
    print_and_log("Starting camera...")
    camera = start_camera()
    print_and_log("Begin event loop...")
    # Event loop
    while True:
        img = camera.capture_image("main")
        qr_img = img.resize((img.width // 5, img.height // 5))
        preview_img = img.resize((128, 72))
        data = decode(qr_img, [ZBarSymbol.QRCODE])
        display.tick(preview_img)
        if data:
            for code in data:
                url = code.data.decode("ascii")
                if is_roomzilla(url):
                    reserve_room(driver, url)

def main_get_cookie():
    print("No cookie was supplied, and cookie.json wasn't found.")
    print("Starting Chrome on X display. If it fails, set $DISPLAY (and check your Xvfb/x11vnc).")
    driver = start_chrome(False)
    driver.get("cic50milk.roomzilla.me")
    print("Log in on the screen, and press Enter to save the cookie.")
    input("[Press Enter here once you've logged in]")
    cookies = driver.get_cookies()
    with open("cookie.json", "w") as f:
        json.dump(cookies, f)
    driver.close()

if __name__ == "__main__":
    if not os.path.exists("cookie.json"):
        main_get_cookie()
    main("cookie.json")
