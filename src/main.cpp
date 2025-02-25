#include <Arduino.h>

#define MIDI_CHANNEL_ON 0x90
#define MIDI_CHANNEL_OFF 0x80
#define MIDI_C4 60
#define MIDI_VELOCITY_MAX 127
#define MIDI_VELOCITY_MIN 0
#define SWITCH_PIN 5

const long DEBOUNCE_DELAY = 100; // ms
long lastDebounceTime = 0;
bool lastSwitchState = LOW;

/**
 * @brief Send a MIDI note on message
 * 
 * @param note Note to play
 * @param velocity Velocity of the note
 */
void sendMIDINoteOn(int note, int velocity);

/**
 * @brief Send a MIDI note off message
 * 
 * @param note Note to stop playing
 * @param velocity Velocity of the note
 */
void sendMIDINoteOff(int note, int velocity);


void setup() {
  // Setup serial for MIDI
  Serial.begin(115200);

  // Setup switch pin
  pinMode(SWITCH_PIN, INPUT_PULLUP);
}

void loop() {
  int switchState = digitalRead(SWITCH_PIN);


  // If the switch state has been stable for a while
  if(switchState == HIGH && lastSwitchState == LOW) {
    if((millis() - lastDebounceTime) > DEBOUNCE_DELAY) {
      sendMIDINoteOn(MIDI_C4, MIDI_VELOCITY_MAX);
      delay(200);
      sendMIDINoteOff(MIDI_C4, MIDI_VELOCITY_MIN);
      lastDebounceTime = millis();
    }
  }

  lastSwitchState = switchState;
}

void sendMIDINoteOn(int note, int velocity) {
  Serial.write(MIDI_CHANNEL_ON);
  Serial.write(note);
  Serial.write(velocity);
}

void sendMIDINoteOff(int note, int velocity) {
  Serial.write(MIDI_CHANNEL_OFF);
  Serial.write(note);
  Serial.write(velocity);
}
