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
#include "MAX30105.h"
#include "heartRate.h"



#ifdef C3
  #define LED 3
#else
 #define LED LED_BUILTIN
#endif

#define GSR_ADC 32

MAX30105 particleSensor;


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
BLEUnsignedIntCharacteristic hrChar("19B10004-E8F2-537E-4F6C-D104768A1214",  // standard 16-bit characteristic UUID
    BLERead | BLENotify); // remote clients will be able to get notifications if this characteristic changes

FilterOnePole gsrFilter(LOWPASS, 1.0F);


int oldBatteryLevel = 0;  // last battery level reading from analog input
long previousMillis = 0;  // last time the battery level was checked, in ms




void setup() {
  Serial.begin(115200);    // initialize serial communication
  //while (!Serial);

  analogSetPinAttenuation(GSR_ADC, ADC_11db);
  
  initBLE();
  initHRSensor();
  
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
 

  BLE.setLocalName("EasySimp");
  BLE.setAdvertisedService(DataService); // add the service UUID
  BLE.setAdvertisedService(BatteryService); // add the service UUID

  DataService.addCharacteristic(gsrChar); // add the battery level characteristic
  DataService.addCharacteristic(gsrCharRaw); // add the battery level characteristic
  DataService.addCharacteristic(hrChar);
  BatteryService.addCharacteristic(batteryLevelChar);
  

  BLE.addService(DataService); // Add the battery service
  BLE.addService(BatteryService); // Add the battery service

  gsrChar.writeValue(0); // set initial value for this characteristic
  gsrCharRaw.writeValue(0);
  batteryLevelChar.writeValue(0); // set initial value for this characteristic
  hrChar.writeValue(0);
  // start advertising
  
  BLE.advertise();
  
}


void initHRSensor()
{
  if (!particleSensor.begin(Wire, I2C_SPEED_FAST)) //Use default I2C port, 400kHz speed
  {
    Serial.println("MAX30105 was not found. Please check wiring/power. ");
    while (1);
  }

//  //Setup to sense a nice looking saw tooth on the plotter
//  byte ledBrightness = 0x1F; //Options: 0=Off to 255=50mA
//  byte sampleAverage = 8; //Options: 1, 2, 4, 8, 16, 32
//  byte ledMode = 3; //Options: 1 = Red only, 2 = Red + IR, 3 = Red + IR + Green
//  int sampleRate = 3200; //Options: 50, 100, 200, 400, 800, 1000, 1600, 3200
//  int pulseWidth = 411; //Options: 69, 118, 215, 411
//  int adcRange = 4096; //Options: 2048, 4096, 8192, 16384
//
//  particleSensor.setup(ledBrightness, sampleAverage, ledMode, sampleRate, pulseWidth, adcRange); //Configure sensor with these settings
//
//  //Arduino plotter auto-scales annoyingly. To get around this, pre-populate
//  //the plotter with 500 of an average reading from the sensor
//
//  //Take an average of IR readings at power up
//  const byte avgAmount = 64;
//  long baseValue = 0;
//  for (byte x = 0 ; x < avgAmount ; x++)
//  {
//    baseValue += particleSensor.getIR(); //Read the IR value
//  }
//  baseValue /= avgAmount;
//
//  //Pre-populate the plotter so that the Y scale is close to IR values
//  for (int x = 0 ; x < 500 ; x++)
//    Serial.println(baseValue);


  particleSensor.setup(); //Configure sensor with default settings
  particleSensor.setPulseAmplitudeRed(0x0A); //Turn Red LED to low to indicate sensor is running
  particleSensor.setPulseAmplitudeGreen(0); //Turn off Green LED
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
      
      hrChar.writeValue(readHR());      
      //readGSR();  
      
      //readHR();
      //readHR();
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


void readGSR()
{
    int gsr_adc = analogRead(GSR_ADC);
    double gsr = ((double)4095-(double)gsr_adc)*1000000/((double)gsr_adc * (double)(220));
    double filteredGSR = gsrFilter.input(gsr);;
    //Serial.print("GSR: ");
    //Serial.print(filteredGSR);
    gsrChar.writeValue(filteredGSR);
}

const byte RATE_SIZE = 4; //Increase this for more averaging. 4 is good.
byte rates[RATE_SIZE]; //Array of heart rates
byte rateSpot = 0;
long lastBeat = 0; //Time at which the last beat occurred

float beatsPerMinute;
int beatAvg;

int readHR(){
  
  long irValue = particleSensor.getIR();

  if (checkForBeat(irValue) == true)
  {
    //We sensed a beat!
    long delta = millis() - lastBeat;
    lastBeat = millis();

    beatsPerMinute = 60 / (delta / 1000.0);

    if (beatsPerMinute < 255 && beatsPerMinute > 20)
    {
      rates[rateSpot++] = (byte)beatsPerMinute; //Store this reading in the array
      rateSpot %= RATE_SIZE; //Wrap variable

      //Take average of readings
      beatAvg = 0;
      for (byte x = 0 ; x < RATE_SIZE ; x++)
        beatAvg += rates[x];
      beatAvg /= RATE_SIZE;
    }
  }

  return beatAvg;
  
}
