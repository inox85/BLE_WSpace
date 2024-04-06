/*
  Battery Monitor

  This example creates a Bluetooth® Low Energy peripheral with the standard battery service and
  level characteristic. The A0 pin is used to calculate the battery level.

  The circuit:
  - Arduino MKR WiFi 1010, Arduino Uno WiFi Rev2 board, Arduino Nano 33 IoT,
    Arduino Nano 33 BLE, or Arduino Nano 33 BLE Sense board.

  You can use a generic Bluetooth® Low Energy central app, like LightBlue (iOS and Android) or
  nRF Connect (Android), to interact with the services and characteristics
  created in this sketch.

  This example code is in the public domain.
*/

//#define C3

#include <ArduinoBLE.h>
#include <esp_task_wdt.h>
#include <Filters.h>

#ifdef C3
  #define LED 3
#else
 #define LED LED_BUILTIN
#endif

#define GSR_ADC 32


 // Bluetooth® Low Energy Battery Service


BLEService BatteryService("19B1180F-E8F2-537E-4F6C-D104768A1214");
// Bluetooth® Low Energy Battery Level Characteristic
BLEUnsignedIntCharacteristic batteryLevelChar("19B12A19-E8F2-537E-4F6C-D104768A1214",  // standard 16-bit characteristic UUID
    BLERead | BLENotify); // remote clients will be able to get notifications if this characteristic changes
 // Bluetooth® Low Energy Battery Service

BLEService DataService("19B10000-E8F2-537E-4F6C-D104768A1214");
// Bluetooth® Low Energy Battery Level Characteristic
BLEUnsignedIntCharacteristic gsrChar("19B10002-E8F2-537E-4F6C-D104768A1214",  // standard 16-bit characteristic UUID
    BLERead | BLENotify); // remote clients will be able to get notifications if this characteristic changes
BLEUnsignedIntCharacteristic gsrCharRaw("19B10003-E8F2-537E-4F6C-D104768A1214",  // standard 16-bit characteristic UUID
    BLERead | BLENotify); // remote clients will be able to get notifications if this characteristic changes


FilterOnePole gsrFilter(LOWPASS, 1.0F);


int oldBatteryLevel = 0;  // last battery level reading from analog input
long previousMillis = 0;  // last time the battery level was checked, in ms



void setup() {
  Serial.begin(9600);    // initialize serial communication
  //while (!Serial);

  analogSetPinAttenuation(GSR_ADC, ADC_11db);
  
  initBLE();
  
  pinMode(LED, OUTPUT); // initialize the built-in LED pin to indicate when a central is connected
  digitalWrite(LED, HIGH);
  delay(1000);
  digitalWrite(LED, LOW);
  // begin initialization
  Serial.println("Bluetooth® device active, waiting for connections...");
}

void initBLE(){ 
    if (!BLE.begin()) {
    Serial.println("starting BLE failed!");
    while (1);
  }
 
  /* Set a local name for the Bluetooth® Low Energy device
     This name will appear in advertising packets
     and can be used by remote devices to identify this Bluetooth® Low Energy device
     The name can be changed but maybe be truncated based on space left in advertisement packet
  */
  BLE.setLocalName("EasySimp");
  BLE.setAdvertisedService(DataService); // add the service UUID
  BLE.setAdvertisedService(BatteryService); // add the service UUID

  DataService.addCharacteristic(gsrChar); // add the battery level characteristic
  DataService.addCharacteristic(gsrCharRaw); // add the battery level characteristic
  BatteryService.addCharacteristic(batteryLevelChar);

  BLE.addService(DataService); // Add the battery service
  BLE.addService(BatteryService); // Add the battery service

  gsrChar.writeValue(0); // set initial value for this characteristic
  gsrCharRaw.writeValue(0);
  batteryLevelChar.writeValue(20); // set initial value for this characteristic
  // start advertising
  BLE.advertise();
}

unsigned long lastBlink = 0;
bool blinkStatus = false;

void loop() {
  // wait for a Bluetooth® Low Energy central
  
  BLEDevice central = BLE.central();

  // if a central is connected to the peripheral:
  if (central) {
    Serial.print("Connected to central: ");
    // print the central's BT address:
    Serial.println(central.address());
    // turn on the LED to indicate the connection:
    digitalWrite(LED, HIGH);
    
    // check the battery level every 200ms
    // while the central is connected:
    while(central.connected()) {
        int gsr = analogRead(GSR_ADC);
        Serial.println("GSR_Raw: ");
        Serial.println(gsr);
        gsrCharRaw.writeValue(gsr);
        double calculatedGSR = gsrFilter.input(calcGSR(gsr));;
        Serial.println("GSR: ");
        Serial.println(calculatedGSR);
        gsrChar.writeValue(calculatedGSR);
    }
    
    // when the central disconnects, turn off the LED:
    digitalWrite(LED, LOW);
    Serial.print("Disconnected from central: ");
    Serial.println(central.address());
    BLE.end();
//    initBLE();
    esp_task_wdt_init(1, true);
    esp_task_wdt_add(NULL);
  }

//  while(central.connected()) {
//      int gsr = analogRead(32);
//      Serial.println("GSR: ");
//      Serial.println(gsr);
//      gsrChar.writeValue(gsr);
//  }
  
}


double calcGSR(int digit){

  double gsr = ((double)4095-(double)digit)*1000000/((double)digit * (double)(220));
  return gsr;
}
