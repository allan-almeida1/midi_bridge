#define SWITCH_PIN 5

#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <WiFiUdp.h>

// Wifi settings
const char* ssid = "Ap 201";
const char* password = "pzT6kozQ!g$G4!SG";

// OSC settings
const char* host = "192.168.100.16";
const int port = 8000;
WiFiUDP Udp;

const long DEBOUNCE_DELAY = 200; // ms
long lastDebounceTime = 0;
bool lastSwitchState = LOW;

void sendOSCMessage(const char* path, int value);

void setup() {
    pinMode(SWITCH_PIN, INPUT_PULLUP);

    Serial.begin(115200);

    WiFi.begin(ssid, password);
    Serial.print("Connecting to WiFi");
    while(WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("Connected");
    Serial.println(WiFi.localIP());
}

void loop() {
  int switchState = digitalRead(SWITCH_PIN);


  // If the switch state has been stable for a while
  if(switchState == HIGH && lastSwitchState == LOW) {
    if((millis() - lastDebounceTime) > DEBOUNCE_DELAY) {
      sendOSCMessage("/track/1/solo/toggle", 1);
      Serial.println("Sent OSC message to toggle solo on track 1");
      lastDebounceTime = millis();
    }
  }

  lastSwitchState = switchState;
}

void sendOSCMessage(const char* path, int value) {
  char buffer[64];  // Adjust size as needed
  int index = 0;

  // Add the OSC address
  index += sprintf(&buffer[index], "%s", path);
  index++;  // Null terminator
  while (index % 4 != 0) buffer[index++] = '\0';  // Pad to 4-byte boundary

  // Add the type tag
  buffer[index++] = ',';
  buffer[index++] = 'i';
  buffer[index++] = '\0';
  buffer[index++] = '\0';

  // Add the integer argument (32-bit big-endian)
  buffer[index++] = (value >> 24) & 0xFF;
  buffer[index++] = (value >> 16) & 0xFF;
  buffer[index++] = (value >> 8) & 0xFF;
  buffer[index++] = value & 0xFF;

  // Send the packet
  Udp.beginPacket(host, port);
  Udp.write((uint8_t*)buffer, index);
  Udp.endPacket();
}
