/*
  Heart beat plotting!
  By: Nathan Seidle @ SparkFun Electronics
  Date: October 20th, 2016
  https://github.com/sparkfun/MAX30105_Breakout

  Shows the user's heart beat on Arduino's serial plotter

  Instructions:
  1) Load code onto Redboard
  2) Attach sensor to your finger with a rubber band (see below)
  3) Open Tools->'Serial Plotter'
  4) Make sure the drop down is set to 115200 baud
  5) Checkout the blips!
  6) Feel the pulse on your neck and watch it mimic the blips

  It is best to attach the sensor to your finger using a rubber band or other tightening
  device. Humans are generally bad at applying constant pressure to a thing. When you
  press your finger against the sensor it varies enough to cause the blood in your
  finger to flow differently which causes the sensor readings to go wonky.

  Hardware Connections (Breakoutboard to Arduino):
  -5V = 5V (3.3V is allowed)
  -GND = GND
  -SDA = A4 (or SDA)
  -SCL = A5 (or SCL)
  -INT = Not connected

  The MAX30105 Breakout can handle 5V or 3.3V I2C logic. We recommend powering the board with 5V
  but it will also run at 3.3V.
*/

#include <Wire.h>
#include "MAX30105.h"
#include <Filters.h>

MAX30105 particleSensor;


FilterOnePole hrFilterHP( LOWPASS, 2.0F );
FilterOnePole hrFilterLP( HIGHPASS, 1.0F );
FilterOnePole beatFilter( LOWPASS, 0.1F);


void setup()
{
  Serial.begin(115200);
  Serial.println("Initializing...");

  pinMode(LED_BUILTIN, OUTPUT);
  // Initialize sensor
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

  //Arduino plotter auto-scales annoyingly. To get around this, pre-populate
  //the plotter with 500 of an average reading from the sensor

  //Take an average of IR readings at power up
  const byte avgAmount = 64;
  long baseValue = 0;
  for (byte x = 0 ; x < avgAmount ; x++)
  {
    baseValue += particleSensor.getIR(); //Read the IR value
  }
  baseValue /= avgAmount;

  //Pre-populate the plotter so that the Y scale is close to IR values
  for (int x = 0 ; x < 500 ; x++)
    Serial.println(baseValue);
}

void loop()
{
  
  double hr_signal = hrFilterLP.input(hrFilterHP.input(particleSensor.getIR()));
  
  //Serial.print("hr:"); // Etichetta della prima traccia
  //Serial.print(hr_signal);    // Dati della prima traccia
  //Serial.print(";");      // Separatore

  //Serial.print("crossing:"); // Etichetta della seconda traccia
  //Serial.print("HEARTH_BEAT: "); Serial.print(hr_signal); Serial.print("  ");
  //Serial.print("BEAT: "); Serial.print(checkZeroCrossing(hr_signal)); Serial.print("  ");
  //Serial.print("HR_T: "); Serial.print(checkZeroCrossing(hr_signal)); Serial.print("  ");
  //Serial.println();    // Dati della seconda traccia
  
  //Serial.println(";");    // Terminatore di linea
  checkZeroCrossing(hr_signal);
}

double prevValue = 0;
unsigned long prevMillis = 0;


double checkZeroCrossing(double hr_signal){

  if(prevValue < 0 && hr_signal > 0){
    prevValue = hr_signal;
    calculateMovingAverage(millis() - prevMillis);
    prevMillis = millis();
    digitalWrite(LED_BUILTIN, HIGH);
    return 100;

  }
  prevValue = hr_signal;
  
  digitalWrite(LED_BUILTIN, LOW);
  
  return 0;
}


const int NUM_READINGS = 10;
unsigned long readings[NUM_READINGS]; // Array per mantenere le letture
int sample_index = 0; // Indice corrente dell'array circolare


unsigned long calculateMovingAverage(unsigned long newValue) {
  // Aggiorna l'array circolare con la nuova lettura
  readings[sample_index] = newValue;
  sample_index = (sample_index + 1) % NUM_READINGS; // Aggiorna l'indice (ritorna a 0 quando raggiunge NUM_READINGS)

  // Calcola la somma di tutti i valori nell'array
  unsigned long sum = 0;
  for (int i = 0; i < NUM_READINGS; ++i) {
    sum += readings[i];
  }
  
  // Calcola la media mobile
  unsigned long m = sum / NUM_READINGS;

  double beat_min = beatFilter.input(((1000.0)/(double)m)* 60.0);
 
  Serial.println(beat_min);
  return m;
}
