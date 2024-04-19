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
    
BLEUnsignedIntCharacteristic temperatureChar("19B10005-E8F2-537E-4F6C-D104768A1214",  // standard 16-bit characteristic UUID
    BLERead | BLENotify); // remote clients will be able to get notifications if this characteristic changes


FilterOnePole gsrFilter(LOWPASS, 0.1F);
FilterOnePole hrFilterHP( LOWPASS, 2.0F );
FilterOnePole hrFilterLP( HIGHPASS, 1.0F );
FilterOnePole beatFilter( LOWPASS, 0.5F);

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
  DataService.addCharacteristic(temperatureChar);
  BatteryService.addCharacteristic(batteryLevelChar);
  
  

  BLE.addService(DataService); // Add the battery service
  BLE.addService(BatteryService); // Add the battery service

  gsrChar.writeValue(0); // set initial value for this characteristic
  gsrCharRaw.writeValue(0);
  batteryLevelChar.writeValue(0); // set initial value for this characteristic
  hrChar.writeValue(0);
  temperatureChar.writeValue(0);
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

  //Setup to sense a nice looking saw tooth on the plotter
  byte ledBrightness = 0xFF; //Options: 0=Off to 255=50mA
  byte sampleAverage = 8; //Options: 1, 2, 4, 8, 16, 32
  byte ledMode = 3; //Options: 1 = Red only, 2 = Red + IR, 3 = Red + IR + Green
  int sampleRate = 3200; //Options: 50, 100, 200, 400, 800, 1000, 1600, 3200
  int pulseWidth = 411; //Options: 69, 118, 215, 411
  int adcRange = 16384; //Options: 2048, 4096, 8192, 16384

  particleSensor.setup(ledBrightness, sampleAverage, ledMode, sampleRate, pulseWidth, adcRange); //Configure sensor with these settings
  particleSensor.enableDIETEMPRDY(); //Enable the temp ready interrupt. This is required.

}


double prevValue = 0;
unsigned long prevMillis = 0;

const byte RATE_SIZE = 4; //Increase this for more averaging. 4 is good.
byte rates[RATE_SIZE]; //Array of heart rates
byte rateSpot = 0;
long lastBeat = 0; //Time at which the last beat occurred

float beatsPerMinute;
int beatAvg;


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
        //hrChar.writeValue(readHR())

        int gsr_adc = analogRead(GSR_ADC);
        double gsr = ((double)4095-(double)gsr_adc)*1000000/((double)gsr_adc * (double)(220));
        double filteredGSR = gsrFilter.input(gsr);;
        //Serial.print("GSR: ");
        //Serial.print(filteredGSR);
        gsrChar.writeValue(filteredGSR);
        double hr_signal = hrFilterLP.input(hrFilterHP.input(particleSensor.getIR()));
        checkZeroCrossing(hr_signal);
        temperatureChar.writeValue((int)(particleSensor.readTemperature() * 100.0));
        
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


double checkZeroCrossing(double hr_signal){

  if(prevValue < 0 && hr_signal > 0)
  {
    prevValue = hr_signal;
    calculateMovingAverage((double)(millis() - prevMillis));
    prevMillis = millis();
    digitalWrite(LED_BUILTIN, HIGH);
    return 100;
  }
  
  prevValue = hr_signal;
  
  digitalWrite(LED_BUILTIN, LOW);
  
  return 0;
}

const int NUM_READINGS = 20;
double readings[NUM_READINGS]; // Array per mantenere le letture
int sample_index = 0; // Indice corrente dell'array circolare

double calculateMovingAverage(double newValue) {
  // Aggiorna l'array circolare con la nuova lettura
  readings[sample_index] = newValue;
  sample_index = (sample_index + 1) % NUM_READINGS; // Aggiorna l'indice (ritorna a 0 quando raggiunge NUM_READINGS)

  // Calcola la somma di tutti i valori nell'array
  double sum = 0;
  for (int i = 0; i < NUM_READINGS; ++i) {
    sum += readings[i];
  }
  
  // Calcola la media mobile
  double m = sum / (double)NUM_READINGS;

  double beat_min = beatFilter.input((((double)100000.0)/m)* (double)60.0);
 
  //Serial.println(beat_min);
  hrChar.writeValue((beat_min));
  return beat_min;

}
