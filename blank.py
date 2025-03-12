#!bin/python3

import board
import digitalio
from PIL import Image, ImageDraw, ImageFont
from adafruit_rgb_display import st7735
from datetime import datetime
import time

cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = digitalio.DigitalInOut(board.D24)

BAUDRATE = 24000000
spi = board.SPI()

disp = st7735.ST7735R(spi,
    rotation=180,
    height=128,
    x_offset=2,
    y_offset=3,   # 1.44" ST7735R
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=BAUDRATE,
)

if __name__ == "__main__":
    im = Image.new(mode="RGB", size=(128, 128), color="black")
    disp.image(im)
