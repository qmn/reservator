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

from picamera2 import Picamera2
from libcamera import controls

from pyzbar.pyzbar import decode, ZBarSymbol

if __name__ == "__main__":
    im = Image.new(mode="RGB", size=(128, 128), color="white")

    draw = ImageDraw.Draw(im)

    # Make it not anti-aliased, for legibility on small screens
    # https://stackoverflow.com/questions/5747739/
    draw.fontmode = "1"

    # Top bar
    draw.rectangle([(0, 0), (127, 15)], fill="#000080")
    # Basic font engine removes kerning but looks better overall
    arial = ImageFont.FreeTypeFont("/usr/share/fonts/truetype/msttcorefonts/arial.ttf", 11, layout_engine=ImageFont.Layout.BASIC)
    arial_bold = ImageFont.FreeTypeFont("/usr/share/fonts/truetype/msttcorefonts/arialbd.ttf", 12, layout_engine=ImageFont.Layout.BASIC)
    w95 = ImageFont.FreeTypeFont("w95font/W95font.otf", 13)
    w95b = ImageFont.FreeTypeFont("w95font/W95font-Bold.otf", 13)

    draw.text((2, 96), "You have not crashed!", fill="black", font=w95)
    draw.text((2, 2), "Reservator", fill="white", font=w95b)
    draw.rectangle([(0,112), (127,127)], fill="#b5b5b5") # D5D5D0
    draw.text((2, 113), "File Open Quit", fill="black", font=w95b)

    # Bottom lines
    draw.line([(0, 111), (127, 111)], width=2, fill="black")
    draw.line([(0, 127), (127, 127)], width=3, fill="black")

    base = im.copy()
    draw2 = ImageDraw.Draw(base)
    draw2.fontmode="1"
    draw2.text((2, 82), "Starting camera...", fill="black", font=w95)
    disp.image(base)

    picam2 = Picamera2()
    picam2.start()
    picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous})

    lasttime = datetime.now()
    while True:
        base2 = im.copy()
        qr1 =  picam2.capture_image("main")
        qr3 = qr1.resize((qr1.width // 5, qr1.height // 5))
        qr2 = qr1.resize((112, 63))
        x = decode(qr3, [ZBarSymbol.QRCODE])
        if x:
            print(x)
        draw2 = ImageDraw.Draw(base2)
        draw2.fontmode = "1"
        curtime = datetime.now()
        fps = 1. / (curtime - lasttime).total_seconds()
        lasttime = curtime
        draw2.text((80, 2), curtime.strftime("%I:%M:%S"), fill="white", font=w95)
        draw2.text((2, 82), f" fps: {fps:.1f}", fill="black", font=w95)
        base2.paste(qr2, (8, 20))
        disp.image(base2)
