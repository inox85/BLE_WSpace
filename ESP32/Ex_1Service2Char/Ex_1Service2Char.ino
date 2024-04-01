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

#include <ArduinoBLE.h>
#include <esp_task_wdt.h>

 // Bluetooth® Low Energy Battery Service
BLEService batteryService("19B10000-E8F2-537E-4F6C-D104768A1214");
 // Bluetooth® Low Energy Battery Service
BLEService customService("19B10001-E8F2-537E-4F6C-D104768A1214");

BLEService ledService("19B10004-E8F2-537E-4F6C-D104768A1214");

BLEService stringService("19B10006-E8F2-537E-4F6C-D104768A1214");

BLEService buttonService("19B1000A-E8F2-537E-4F6C-D104768A1214");

// Bluetooth® Low Energy Battery Level Characteristic
BLEUnsignedCharCharacteristic batteryLevelChar("19B10002-E8F2-537E-4F6C-D104768A1214",  // standard 16-bit characteristic UUID
    BLERead | BLENotify); // remote clients will be able to get notifications if this characteristic changes

BLEUnsignedCharCharacteristic customChar("19B10003-E8F2-537E-4F6C-D104768A1214",  // standard 16-bit characteristic UUID
    BLERead | BLEWrite | BLENotify); // remote clients will be able to get notifications if this characteristic changes
    
BLEUnsignedCharCharacteristic ledChar("19B10005-E8F2-537E-4F6C-D104768A1214",  // standard 16-bit characteristic UUID
    BLERead | BLEWrite); // remote clients will be able to get notifications if this characteristic changes

BLECharacteristic stringChar("19B10007-E8F2-537E-4F6C-D104768A1214",  // standard 16-bit characteristic UUID
    BLERead | BLEWrite | BLENotify, 20); // remote clients will be able to get notifications if this characteristic changes

BLEUnsignedCharCharacteristic buttonChar("19B1000B-E8F2-537E-4F6C-D104768A1214",  // standard 16-bit characteristic UUID
    BLERead | BLEWrite |BLENotify); // remote clients will be able to get notifications if this characteristic changes

int oldBatteryLevel = 0;  // last battery level reading from analog input
long previousMillis = 0;  // last time the battery level was checked, in ms

void setup() {
  Serial.begin(9600);    // initialize serial communication
  while (!Serial);
  
  initBLE();
  
  pinMode(18, INPUT);
  
  pinMode(LED_BUILTIN, OUTPUT); // initialize the built-in LED pin to indicate when a central is connected
  pinMode(18, OUTPUT); // initialize the built-in LED pin to indicate when a central is connected  
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
  BLE.setLocalName("Forometro");
  BLE.setAdvertisedService(batteryService); // add the service UUID
  //BLE.setAdvertisedService(customService); // add the service UUID
  //BLE.setAdvertisedService(stringService); // add the service UUID
  //BLE.setAdvertisedService(buttonService); // add the service UUID
  
  batteryService.addCharacteristic(batteryLevelChar); // add the battery level characteristic
  batteryService.addCharacteristic(customChar); // add the battery level characteristic
  batteryService.addCharacteristic(ledChar); // add the battery level characteristic
  batteryService.addCharacteristic(stringChar);
  batteryService.addCharacteristic(buttonChar);
  
  BLE.addService(batteryService); // Add the battery service
//  BLE.addService(customService); // Add the battery service
//  BLE.addService(ledService); // Add the battery service
//  BLE.addService(stringService);
//  BLE.addService(buttonService);
  
  
  batteryLevelChar.writeValue(oldBatteryLevel); // set initial value for this characteristic
  customChar.writeValue(0);
  ledChar.writeValue(0);
  buttonChar.writeValue(0);
  
  String val = "Ciaone";
  char charArray[val.length() + 1]; // +1 per il terminatore nullo
  val.toCharArray(charArray, val.length() + 1);
  stringChar.writeValue(charArray, sizeof(charArray));
  stringChar.writeValue("Ciaone");
  /* Start advertising Bluetooth® Low Energy.  It will start continuously transmitting Bluetooth® Low Energy
     advertising packets and will be visible to remote Bluetooth® Low Energy central devices
     until it receives a new connection */

  // start advertising
  BLE.advertise();
}

bool buttonState = false;

void loop() {
  // wait for a Bluetooth® Low Energy central
  BLEDevice central = BLE.central();

  // if a central is connected to the peripheral:
  if (central) {
    Serial.print("Connected to central: ");
    // print the central's BT address:
    Serial.println(central.address());
    // turn on the LED to indicate the connection:
    digitalWrite(LED_BUILTIN, HIGH);
    
    // check the battery level every 200ms
    // while the central is connected:
    while (central.connected()) {
      long currentMillis = millis();
      // if 200ms have passed, check the battery level:
      if (currentMillis - previousMillis >= 100) {
        //Serial.println(currentMillis);
        previousMillis = currentMillis;
        updateBatteryLevel();
        
        if(ledChar.value() == 0)
          digitalWrite(18,LOW);
        else
          digitalWrite(18,HIGH);
      }
    }
    // when the central disconnects, turn off the LED:
    digitalWrite(LED_BUILTIN, LOW);
    Serial.print("Disconnected from central: ");
    Serial.println(central.address());
    BLE.end();
    initBLE();
    esp_task_wdt_init(1, true);
    esp_task_wdt_add(NULL);

  }
}

int count = 0;

void updateBatteryLevel() {
  /* Read the current voltage level on the A0 analog input pin.
     This is used here to simulate the charge level of a battery.
  */
  count++;
  
  int battery = count;
  int batteryLevel = map(battery, 0, 1023, 0, 100);

  if (batteryLevel != oldBatteryLevel) {      // if the battery level has changed
    
    Serial.print("Battery Level % is now: "); // print it
    Serial.println(batteryLevel);
    Serial.print("Custom char:");
    Serial.println(customChar.value());
    Serial.println(ledChar.value());

    buttonState = !buttonState;
    buttonChar.writeValue(buttonState);
    
    batteryLevelChar.writeValue(batteryLevel);  // and update the battery level characteristic
    customChar.writeValue(batteryLevel/10);
    String val = "Ciaone" + (String)batteryLevel;
    char charArray[val.length() + 1]; // +1 per il terminatore nullo
    val.toCharArray(charArray, val.length() + 1);
    stringChar.writeValue(charArray, sizeof(charArray));
    oldBatteryLevel = batteryLevel;           // save the level for next comparison
  }
}
