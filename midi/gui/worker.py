from PyQt5.QtCore import QThread


class MidiBridgeWorker(QThread):
    def __init__(self, midi_bridge):
        super().__init__()
        self.midi_bridge = midi_bridge

    def run(self):
        self.midi_bridge.run()

    def stop(self):
        self.midi_bridge.stop()
