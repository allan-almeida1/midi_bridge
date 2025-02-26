from PyQt5.QtWidgets import QLabel, QWidget, QComboBox, QTextEdit, QCheckBox
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import pyqtSlot, QTimer
from PyQt5 import uic
from utils import list_serial_ports, list_midi_ports
from bridge.serialmidi import MidiBridge
from gui.worker import MidiBridgeWorker
import sys
import os


class MainWindow(QWidget):
    led: QLabel
    combo_box_serial: QComboBox
    output_area: QTextEdit
    checkbox_start: QCheckBox

    def __init__(self):
        super().__init__()
        ui_file = self.resource_path('ui/main_window.ui')
        uic.loadUi(ui_file, self)

        self.midi_bridge = None
        self.midi_bridge_worker = None

        self.led_off = QPixmap(self.resource_path('gui/images/led_off.png'))
        self.led_on = QPixmap(self.resource_path('gui/images/led_on.png'))

        self.led.setPixmap(self.led_off)
        self.led.setScaledContents(True)

        self.refresh_button.setIcon(QIcon(self.resource_path('gui/images/refresh.png')))

        self.serial_ports = list_serial_ports()
        if self.serial_ports:
            self.combo_box_serial.addItem('')
            self.combo_box_serial.addItems(
                [port.device for port in self.serial_ports])

        self.midi_in_ports, self.midi_out_ports = list_midi_ports()
        self.combo_box_midi_in.addItem('')
        self.combo_box_midi_in.addItems(self.midi_in_ports)
        self.combo_box_midi_out.addItem('')
        self.combo_box_midi_out.addItems(self.midi_out_ports)

        self.output_area.setReadOnly(True)

        self.log_message('MIDI bridge started.')

        self.checkbox_start.stateChanged.connect(self.start_stop)

        self.refresh_button.clicked.connect(self.refresh_ports)

        self.refresh_ports()
    
    def resource_path(self, relative_path):
        """ Get the absolute path to the resource, works for dev and for PyInstaller """
        base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
        return os.path.join(base_path, relative_path)

    def refresh_ports(self):
        self.log_message('Searching for ports...')
        self.serial_ports = list_serial_ports()

        self.log_message('Serial ports found:')
        for port in self.serial_ports:
            self.log_message(f'  {port.device}')

        self.combo_box_serial.clear()
        self.combo_box_serial.addItem('')
        self.combo_box_serial.addItems(
            [port.device for port in self.serial_ports])

        self.midi_in_ports, self.midi_out_ports = list_midi_ports()

        self.log_message('MIDI In ports found:')
        for port in self.midi_in_ports:
            self.log_message(f'  {port}')

        self.log_message('MIDI Out ports found:')
        for port in self.midi_out_ports:
            self.log_message(f'  {port}')

        self.combo_box_midi_in.clear()
        self.combo_box_midi_in.addItem('')
        self.combo_box_midi_in.addItems(self.midi_in_ports)
        if 'Driver IAC Barramento 1' in self.midi_in_ports:
            self.combo_box_midi_in.setCurrentText('Driver IAC Barramento 1')

        self.combo_box_midi_out.clear()
        self.combo_box_midi_out.addItem('')
        self.combo_box_midi_out.addItems(self.midi_out_ports)
        if 'Driver IAC Barramento 1' in self.midi_out_ports:
            self.combo_box_midi_out.setCurrentText('Driver IAC Barramento 1')

    @pyqtSlot(str)
    def on_output_message(self, message):
        self.log_message(message)

    @pyqtSlot()
    def on_note_received(self):
        self.led.setPixmap(self.led_on)
        QTimer.singleShot(100, lambda: self.led.setPixmap(self.led_off))

    def log_message(self, message):
        self.output_area.append(message)
        self.output_area.verticalScrollBar().setValue(
            self.output_area.verticalScrollBar().maximum())

    def start_stop(self):
        if self.checkbox_start.isChecked():
            if self.combo_box_serial.currentText() == '':
                self.log_message('No serial port selected.')
                return
            if self.combo_box_midi_in.currentText() == '':
                self.log_message('No MIDI In port selected.')
                return
            if self.combo_box_midi_out.currentText() == '':
                self.log_message('No MIDI Out port selected.')
                return
            self.run_midi_bridge()
        else:
            if self.midi_bridge is not None:
                self.midi_bridge_worker.stop()
                self.midi_bridge_worker.wait()
                self.led.setPixmap(self.led_off)
                self.log_message('MIDI bridge stopped.')

    def run_midi_bridge(self):
        serial_port_name = self.combo_box_serial.currentText()
        serial_baud = 115200
        given_port_name_in = self.combo_box_midi_in.currentText()
        given_port_name_out = self.combo_box_midi_out.currentText()

        self.midi_bridge = MidiBridge(
            serial_port_name, serial_baud, given_port_name_in, given_port_name_out)
        self.midi_bridge.output_message.connect(self.on_output_message)
        self.midi_bridge.note_received.connect(self.on_note_received)
        self.midi_bridge_worker = MidiBridgeWorker(self.midi_bridge)
        self.midi_bridge_worker.start()
