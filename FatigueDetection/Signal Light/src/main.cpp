#include <Arduino.h>
const int pinNumber = 25; 

void setup(){ 
    Serial.begin(9600); 
    pinMode(pinNumber,OUTPUT); 
}
void loop() {
  char val = Serial.read();
  if(val == 'o')
  {
    digitalWrite(pinNumber,HIGH); 
    }
  if(val == 'c')
  {
    digitalWrite(pinNumber,LOW); 
    }
}