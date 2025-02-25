# Serial <-> MIDI Bridge

This repo contains the source code for a simple serial to MIDI bridge with a GUI and an Arduino/ESP firmware to send MIDI messages when a digital input changes from LOW to HIGH.

## midi

Contains the code for the GUI application, written in python using PyQt5 and a modified version of [raspy135/serialmidi](https://github.com/raspy135/serialmidi)

To install and run, follow the steps:

1. Create virtual environment
```bash
python3 -m venv .venvmidi
```
2. Activate the venv
```bash
source .venvmidi/bin/activate
```
3. Install required python packages
```bash
pip install -r requirements.txt
```

## src

Contains the source code for the Arduino/ESP to listen for digital input changes in digital I/O 5 and send MIDI messages to the serial port.

## script 

Contains a Lua script that can be loaded into reaper and do pretty much anything you want. In my specific application case, it toggles the SOLO state of the first track.
