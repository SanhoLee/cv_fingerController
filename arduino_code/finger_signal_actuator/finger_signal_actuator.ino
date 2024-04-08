#include <cvzone.h>
#include <Servo.h>

Servo myServo;
SerialData serialData(1, 3); //(numOfValsRec,digitsPerValRec)
int valsRec[1]; // array of int with size numOfValsRec 
int DETECTED = 13;
int NOT_DETECTED = 12;
int dist = 0;
int crit = 100;

int dist_servo = 0;
int servoOutPin = 9;


void setup() {
  myServo.attach(servoOutPin);

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


  dist_servo = map(dist, 0, 249, 0, 179);
  myServo.write(dist_servo);
  dist_servo=0;

// todo, adding servo motor control codes.
// Referting 'lecture05.ino' file
  
  
  delay(100);
}