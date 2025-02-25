import serial.tools.list_ports
import rtmidi


def list_serial_ports():
    return serial.tools.list_ports.comports()


def list_midi_ports():
    midiin = rtmidi.MidiIn()
    midiout = rtmidi.MidiOut()
    available_ports_in = midiin.get_ports()
    available_ports_out = midiout.get_ports()
    return available_ports_in, available_ports_out
