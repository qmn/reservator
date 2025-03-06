# Reservator: a tool for promoting human-friendly interfaces

_Reservator_ (working name) is a device that automatically books rooms
of a certain room booking system. Its rooms display QR codes on iPads,
which, mind you, are fully capable of implementing _this exact
functionality_. This project protests the surrendering of human-first
interfaces for the misguided goal of simplifying machine-to-machine
communication.

## Required packages

Install required dependencies:

    $ sudo apt-get install python3-picamera2 python3-pip
    $ pip3 install pyzbar selenium PyImage

Get the (unofficial Armv7) geckodriver:

    $ curl -LO https://github.com/jamesmortensen/geckodriver-arm-binaries/releases/download/v0.34.0/geckodriver-v0.34.0-linux-armv7l.tar.gz
    $ tar xzf geckodriver-v0.34.0-linux-armv7l.tar.gz
