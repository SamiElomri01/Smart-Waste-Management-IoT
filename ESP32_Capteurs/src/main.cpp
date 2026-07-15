#include <Arduino.h>
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>

const int TRIG_PIN = 18;
const int ECHO_PIN = 16;
const int HUM1_PIN = 4;
const int HUM2_PIN = 5;

#define SERVICE_UUID        "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
#define CHARACTERISTIC_UUID "beb5483e-36e1-4688-b7f5-ea07361b26a8"

BLEServer* pServer = NULL;
BLECharacteristic* pCharacteristic = NULL;
bool deviceConnected = false;
unsigned long lastSend = 0;

class MyServerCallbacks: public BLEServerCallbacks {
    void onConnect(BLEServer* pServer) { deviceConnected = true; Serial.println(">>> PI CONNECTE !"); }
    void onDisconnect(BLEServer* pServer) { deviceConnected = false; BLEDevice::startAdvertising(); }
};

void setup() {
  Serial.begin(115200);
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  analogReadResolution(12);

  BLEDevice::init("ESP32_SmartWaste");
  pServer = BLEDevice::createServer();
  pServer->setCallbacks(new MyServerCallbacks());

  BLEService *pService = pServer->createService(SERVICE_UUID);
  pCharacteristic = pService->createCharacteristic(
                      CHARACTERISTIC_UUID,
                      BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_NOTIFY
                    );
  pService->start();
  BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
  pAdvertising->addServiceUUID(SERVICE_UUID);
  pAdvertising->setScanResponse(true);
  BLEDevice::startAdvertising();
}

void loop() {
  if (millis() - lastSend >= 2000) {
    lastSend = millis();

    digitalWrite(TRIG_PIN, LOW); delayMicroseconds(2);
    digitalWrite(TRIG_PIN, HIGH); delayMicroseconds(10);
    digitalWrite(TRIG_PIN, LOW);
    long duree = pulseIn(ECHO_PIN, HIGH, 30000);
    float distance = (duree == 0) ? 999.0 : duree * 0.0343 / 2.0;

    int hum1 = analogRead(HUM1_PIN);
    int hum2 = analogRead(HUM2_PIN);

    String message = String(distance, 1) + "," + String(hum1) + "," + String(hum2);
    Serial.println("Envoi : " + message);

    pCharacteristic->setValue(message.c_str());
    if (deviceConnected) pCharacteristic->notify();
  }
}