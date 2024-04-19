#include <ArduinoBLE.h>
#include <esp_task_wdt.h>
#include <Filters.h>
#include <math.h>

#ifdef C3
  #define LED 3
#else
 #define LED LED_BUILTIN
#endif

#define GSR_ADC 32

//BLEService BatteryService("19B1180F-E8F2-537E-4F6C-D104768A1214");
// Bluetooth® Low Energy Battery Level Characteristic
//BLEUnsignedIntCharacteristic batteryLevelChar("19B12A19-E8F2-537E-4F6C-D104768A1214",  // standard 16-bit characteristic UUID
//    BLERead | BLENotify); // remote clients will be able to get notifications if this characteristic changes
// Bluetooth® Low Energy Battery Service

BLEService DataService("19B10000-E8F2-537E-4F6C-D104768A1214");
// Bluetooth® Low Energy Battery Level Characteristic
BLEUnsignedIntCharacteristic xChar("19B10001-E8F2-537E-4F6C-D104768A1214",  // standard 16-bit characteristic UUID
    BLERead | BLENotify); // remote clients will be able to get notifications if this characteristic changes
BLEUnsignedIntCharacteristic yChar("19B10002-E8F2-537E-4F6C-D104768A1214",  // standard 16-bit characteristic UUID
    BLERead | BLENotify); // remote clients will be able to get notifications if this characteristic changes
BLEUnsignedIntCharacteristic zChar("19B10003-E8F2-537E-4F6C-D104768A1214",  // standard 16-bit characteristic UUID
    BLERead | BLENotify); // remote clients will be able to get notifications if this characteristic changes   
BLEUnsignedIntCharacteristic moduleChar("19B10004-E8F2-537E-4F6C-D104768A1214",  // standard 16-bit characteristic UUID
    BLERead | BLENotify); // remote clients will be able to get notifications if this characteristic changes


//FilterOnePole gsrFilter(LOWPASS, 1.0F);
//FilterOnePole hrFilterHP(LOWPASS, 2.0F);
//FilterOnePole hrFilterLP(HIGHPASS, 1.0F);
//FilterOnePole beatFilter(LOWPASS, 0.5F);

int oldBatteryLevel = 0;  // last battery level reading from analog input



void setup() {
  Serial.begin(115200);    // initialize serial communication
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
 

  BLE.setLocalName("Accelerometro");
  BLE.setAdvertisedService(DataService); // add the service UUID

  DataService.addCharacteristic(xChar); // add the battery level characteristic
  DataService.addCharacteristic(yChar); // add the battery level characteristic
  DataService.addCharacteristic(zChar);
  DataService.addCharacteristic(moduleChar);

  BLE.addService(DataService); // Add the battery service

  xChar.writeValue(0); // set initial value for this characteristic
  yChar.writeValue(0);
  zChar.writeValue(0); // set initial value for this characteristic
  moduleChar.writeValue(0);
  // start advertising
  
  BLE.advertise();
    
}


void loop() {
  
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
    
    while(central.connected()) 
    {    
      for(float i = 0; i < 2 * M_PI; i += 0.01) {  // Genera un ciclo completo della sinusoide
      int value = 2048 + (2047 * sin(i));  // Genera il valore analogico della sinusoide
      xChar.writeValue(value); // set initial value for this characteristic
      yChar.writeValue(value);
      zChar.writeValue(value);
      delayMicroseconds(10);  // Puoi regolare questa velocità a seconda delle tue esigenze
    }
        
      
        
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


}
