import time
import queue
import rtmidi
import serial
import threading
import logging
import sys
import time
from PyQt5.QtCore import QObject, pyqtSignal
# Serial MIDI Bridge
# Ryan Kojima


logging.basicConfig(level=logging.DEBUG)

midiin_message_queue = queue.Queue()
midiout_message_queue = queue.Queue()


def get_midi_length(message):
    if len(message) == 0:
        return 100
    opcode = message[0]
    if opcode >= 0xf4:
        return 1
    if opcode in [0xf1, 0xf3]:
        return 2
    if opcode == 0xf2:
        return 3
    if opcode == 0xf0:
        if message[-1] == 0xf7:
            return len(message)

    opcode = opcode & 0xf0
    if opcode in [0x80, 0x90, 0xa0, 0xb0, 0xe0]:
        return 3
    if opcode in [0xc0, 0xd0]:
        return 2

    return 100


class midi_input_handler(object):
    def __init__(self, port):
        self.port = port
        self._wallclock = time.time()

    def __call__(self, event, data=None):
        message, deltatime = event
        self._wallclock += deltatime
        # logging.debug("[%s] @%0.6f %r" % (self.port, self._wallclock, message))
        midiin_message_queue.put(message)


class MidiBridge(QObject):
    output_message = pyqtSignal(str)
    note_received = pyqtSignal()

    def __init__(self, serial_port_name, serial_baud, given_port_name_in, given_port_name_out):
        super().__init__()
        self.serial_port_name = serial_port_name
        self.serial_baud = serial_baud
        self.given_port_name_in = given_port_name_in
        self.given_port_name_out = given_port_name_out
        self.start = False
        self.midi_ready = False
        self.thread_running = True
        self.ser = None

    def set_serial_port_name(self, serial_port_name):
        self.serial_port_name = serial_port_name

    def set_serial_baud(self, serial_baud):
        self.serial_baud = serial_baud

    def set_given_port_name_in(self, given_port_name_in):
        self.given_port_name_in = given_port_name_in

    def set_given_port_name_out(self, given_port_name_out):
        self.given_port_name_out = given_port_name_out

    def serial_watcher(self):
        receiving_message = []
        running_status = 0

        while self.midi_ready == False:
            time.sleep(0.1)

        while self.thread_running:
            data = self.ser.read()
            if data:
                for elem in data:
                    receiving_message.append(elem)
                # Running status
                if len(receiving_message) == 1:
                    if (receiving_message[0] & 0xf0) != 0:
                        running_status = receiving_message[0]
                    else:
                        receiving_message = [
                            running_status, receiving_message[0]]

                message_length = get_midi_length(receiving_message)
                if message_length <= len(receiving_message):
                    self.output_message.emit(str(receiving_message))
                    self.note_received.emit()
                    logging.debug(receiving_message)
                    midiout_message_queue.put(receiving_message)
                    receiving_message = []

    def midi_watcher(self):
        midiin = rtmidi.MidiIn()
        midiout = rtmidi.MidiOut()
        available_ports_out = midiout.get_ports()
        available_ports_in = midiin.get_ports()
        logging.info("IN : '" + "','".join(available_ports_in) + "'")
        self.output_message.emit(
            "IN : '" + "','".join(available_ports_in) + "'")
        logging.info("OUT : '" + "','".join(available_ports_out) + "'")
        self.output_message.emit(
            "OUT : '" + "','".join(available_ports_out) + "'")
        logging.info("Listening for MIDI messages...")
        self.output_message.emit("Listening for MIDI messages...")

        port_index_in = -1
        port_index_out = -1
        for i, s in enumerate(available_ports_in):
            if self.given_port_name_in in s:
                port_index_in = i
        for i, s in enumerate(available_ports_out):
            if self.given_port_name_out in s:
                port_index_out = i

        if port_index_in == -1:
            print("MIDI IN Device name is incorrect. Please use listed device name.")
        if port_index_out == -1:
            print("MIDI OUT Device name is incorrect. Please use listed device name.")
        if port_index_in == -1 or port_index_out == -1:
            self.thread_running = False
            self.midi_ready = True
            sys.exit()

        midiout.open_port(port_index_out)
        in_port_name = midiin.open_port(port_index_in)

        self.midi_ready = True

        midiin.ignore_types(sysex=False, timing=False, active_sense=False)
        midiin.set_callback(midi_input_handler(in_port_name))

        try:
            while self.thread_running:
                try:
                    message = midiout_message_queue.get(timeout=0.4)
                except queue.Empty:
                    continue
                midiout.send_message(message)
        finally:
            # Properly close MIDI ports before exiting
            midiout.close_port()
            midiin.close_port()

    def serial_writer(self):
        while self.midi_ready == False:
            time.sleep(0.1)
        while self.thread_running:
            try:
                message = midiin_message_queue.get(timeout=0.4)
            except queue.Empty:
                continue
            self.output_message.emit(str(message))
            logging.debug(message)
            value = bytearray(message)
            self.ser.write(value)

    def run(self):
        try:
            self.output_message.emit("Opening serial port...")
            logging.info("Opening serial port...")
            self.ser = serial.Serial(self.serial_port_name, self.serial_baud)
            self.start = True
        except serial.serialutil.SerialException:
            print("Serial port opening error.")
            self.midi_watcher()
            sys.exit()

        self.ser.timeout = 0.4

        s_watcher = threading.Thread(target=self.serial_watcher)
        s_writer = threading.Thread(target=self.serial_writer)
        m_watcher = threading.Thread(target=self.midi_watcher)

        s_watcher.start()
        s_writer.start()
        m_watcher.start()

        # Ctrl-C handler
        try:
            while self.start:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Terminating.")
            self.thread_running = False
            sys.exit(0)

    def stop(self):
        self.thread_running = False
        self.ser.close()
        self.midi_ready = True
        self.start = False
