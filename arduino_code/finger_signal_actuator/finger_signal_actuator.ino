#include <cvzone.h>

SerialData serialData(1, 3); //(numOfValsRec,digitsPerValRec)
int valsRec[1]; // array of int with size numOfValsRec 
int DETECTED = 13;
int NOT_DETECTED = 12;
int dist = 0;
int crit = 100;


void setup() {
  pinMode(12, OUTPUT);
  pinMode(13, OUTPUT);
  serialData.begin();
}

void loop() {

  serialData.Get(valsRec);
  Serial.print("finger distance :  ");
  dist = valsRec[0];

  if(dist > crit){
    // digitalWrite(DETECTED, valsRec[0]);
    digitalWrite(DETECTED, HIGH);
    digitalWrite(NOT_DETECTED, LOW);
  } else{
    // digitalWrite(NOT_DETECTED, valsRec[1]);
    digitalWrite(NOT_DETECTED, HIGH);
    digitalWrite(DETECTED, LOW);
  }

  if(dist == 0){
    digitalWrite(DETECTED, LOW);
    digitalWrite(NOT_DETECTED, LOW);
  }


// todo, adding servo motor control codes.
// Referting 'lecture05.ino' file
  
  
  delay(300);
}