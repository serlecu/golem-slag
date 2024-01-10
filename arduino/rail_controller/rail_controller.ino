#include <Grove_I2C_Motor_Driver.h>
#include <Wire.h>
#include "avr/wdt.h" //software reset watchdog

#define ENDSTOP_A 2

bool railStopped = true;
bool wireError = false;
unsigned long serialTimeout = 0;
byte nextByte;
int serialIndex = 0;
char serialIn[8] = "";
unsigned char _i2c_add = 0x0f;
unsigned char STEPPER_FREQ = F_31372Hz; // Must be F_31372Hz, F_3921Hz, F_490Hz, F_122Hz, F_30Hz
int _step_cnt = 0;
int dir = 1;
bool wasTriggered = false;
int speedPot = 160;//80;// 45-200
int speedDelay = 50;// 45-200
uint32_t reconnectWireTimer = 0;
unsigned long lastLoopTime = 0;
int resetCounter = 0;
unsigned long resetTimer = 0;

void(* resetFunc) (void) = 0; // esta es la funcion


void setup() {
  // wdt_disable(); //init reset Watchdog

  Serial.begin(9600);
  delay(2000);
  Serial.println("Ready to ROCK!");

  pinMode(13, OUTPUT);
  pinMode(2, INPUT);
  pinMode(3, INPUT);
  
  pinMode(8, INPUT);

  Wire.begin();
  delay(1000);
  if (stepperFrequence(STEPPER_FREQ) != 0){
    wireError = true;
  }
  Wire.onRequest(requestEvents);
  Wire.onReceive(receiveEvents);

  // pinMode(SCL,OUTPUT); // SCL = 19
  // for(int i = 0; i<9; i++){
  //   digitalWrite(SCL, HIGH);
  //   delayMicroseconds(2);
  //   digitalWrite(SCL, LOW);
  //   delayMicroseconds(2);
  // }

  speedDelay = random(156) + 45;

  // wdt_enable(WDTO_8S); //set watchdog 8s
}

void loop() {
  // Temporizador
  lastLoopTime = millis();
  // // fake inSerial
  // if (speedTimer > ((random(4)+4) * 60000)) {
  //   // speedDelay = random(156) + 45;
  //   speedTimer = 0;
  // }

  

  // Serial In
  if (Serial.available()) {
    //read next byte in serial stream
    nextByte = Serial.read();
    // check if nextByte is a newline character
    if (nextByte == '\n') {
      // append null character to serialIn bytearray
      serialIn[serialIndex++] = '\0';
      // convert serialIn to int
      int msgValue = String(serialIn).toInt();
      // set speedDelay
      if (msgValue > 1500) {
        railStopped = true;
      } else {
        railStopped = false;
        speedDelay = constrain(msgValue, 40, 1000);
      }
      // clear serialIn
      serialIn[0] = '\0';
      serialIndex = 0;
      serialFlush();
      digitalWrite(13, HIGH);
      serialTimeout = 0;
    } else {
      // append to serialIn bytearray
      serialIn[serialIndex] = nextByte;
      digitalWrite(13, LOW);
      serialIndex++;
    }
  } else {
    digitalWrite(13, LOW);
  }

  // Parar rail si no hay recepción Serial
  if (serialTimeout >= 4000 && !railStopped) {
    Serial.println(F("Ya no se reciben mensajes serial"));
    railStopped = true;
    // Serial.end();
    // delay(1000);
    // Serial.begin(9600);
    // delay(1000);
    // serialTimeout = 0;
    // Serial.println(F("Serial reabierto"));
  }

  if( wireError && reconnectWireTimer > 2000 ){
    Serial.println(F("Reconectando I2C ..."));
    reconnectWireTimer = 0;
    resetWire();
  }

  // I2C Out
  if (!railStopped && !wireError) {
    // Enviar orden a driver
    if ( stepperRun(1 * dir) != 0 ) { // paso
      wireError = true;
      Serial.println(F("Error en conexión I2C al enviar orden de PASO"));
    }
    if ( stop() != 0) { // parada
      wireError = true;
      Serial.println(F("Error en conexión I2C al enviar orden de PARADA"));
    }
    
    delay(speedDelay);// 10-100
  }

  handleEndSwitches();

  // Actualizar contadores
  if (reconnectWireTimer < 3000 && wireError){
    reconnectWireTimer += millis() - lastLoopTime;
  }
  if (!railStopped && serialTimeout < 4000) {
    serialTimeout += millis() - lastLoopTime;
  }
}

void handleEndSwitches(){

  bool pinStatus = digitalRead(2);

  // Leer finales de carro
  if (pinStatus == HIGH & !wasTriggered ) {
    dir *= -1;
    wasTriggered = true;
    // Serial.println("EndStop triggered");
  } else if (pinStatus == LOW & wasTriggered ) {
    wasTriggered = false;
  }
}

byte stop() {
  Wire.beginTransmission(_i2c_add); // begin transmission
  Wire.write(MotorSpeedSet);              // set pwm header
  Wire.write(0);              // send speed of motor1
  Wire.write(0);              // send speed of motor2
  byte status = Wire.endTransmission();    		        // stop transmitting
  delay(4);
  return status;	
}

byte direction(unsigned char _direction) {
    Wire.beginTransmission(_i2c_add); // begin transmission
    Wire.write(DirectionSet);               // Direction control header
    Wire.write(_direction);                 // send direction control information
    Wire.write(Nothing);                    // need to send this byte as the third byte(no meaning)
    byte status = Wire.endTransmission();    		        // stop transmitting
    delay(4); 				                // wait
    return status;
}

byte stepperFrequence(unsigned char _frequence) {
    if (_frequence < F_31372Hz || _frequence > F_30Hz) {
        Serial.println("frequence error! Must be F_31372Hz, F_3921Hz, F_490Hz, F_122Hz, F_30Hz");
        return;
    }
    Wire.beginTransmission(_i2c_add); // begin transmission
    Wire.write(PWMFrequenceSet);            // set frequence header
    Wire.write(_frequence);                 // send frequence
    Wire.write(Nothing);                    // need to send this byte as the third byte(no meaning)
    byte status = Wire.endTransmission();    		        // stop transmitting
    delay(4); 				                // wait
    return status;
}

byte stepperRun(int _step) {

    int _direction = 1;
    if (_step > 0) {
        _direction = 1; //clockwise
        _step = _step > 1024 ? 1024 : _step;
    } else if (_step < 0) {
        _direction = -1; //anti-clockwise
        _step = _step < -1024 ? 1024 : -(_step);
    }

    int _speed1 = speedPot;
    int _speed2 = speedPot;
    Wire.beginTransmission(_i2c_add); // begin transmission
    Wire.write(MotorSpeedSet);              // set pwm header
    Wire.write(_speed1);              // send speed of motor1
    Wire.write(_speed2);              // send speed of motor2
    byte status = Wire.endTransmission();    		        // stop transmitting
    delay(1); 				                // wait
    if( status != 0 ) {
      return status;
    }

    if (_direction == 1) {				// Sentido Horario
        for (int i = 0; i < _step; i++) {
            switch (_step_cnt) {
                case 0 : direction(0b0001); break;
                case 1 : direction(0b0101); break;
                case 2 : direction(0b0100); break;
                case 3 : direction(0b0110); break;

                case 4 : direction(0b0010); break;
                case 5 : direction(0b1010); break;
                case 6 : direction(0b1000); break;
                case 7 : direction(0b1001); break;
            }
            _step_cnt = (_step_cnt + 1) % 8;
        }
    } else if (_direction == -1) { // Sentido Anti-horario
        for (int i = 0; i < _step; i++) {
            switch (_step_cnt) {
                case 0 : direction(0b1001); break;
                case 1 : direction(0b1000); break;
                case 2 : direction(0b1010); break;
                case 3 : direction(0b0010); break;

                case 4 : direction(0b0110); break;
                case 5 : direction(0b0100); break;
                case 6 : direction(0b0101); break;
                case 7 : direction(0b0001); break;
            }
            _step_cnt = (_step_cnt + 1) % 8;
        }
    }

    return 0;
}

int n = 0;

void requestEvents()
{
  Serial.println(F("Recibidos datos I2C: "));
  // Wire.write(n);
}

void receiveEvents(int numBytes)
{  
  n = Wire.read();
  Serial.println(F("Recibidos datos I2C: "));
}

void resetWire(){
  //restart board
  // pinMode(8, OUTPUT);
  // digitalWrite(8, LOW);
  // delay(100);
  // pinMode(8, INPUT);
  // delay(2000);

  // for(int i = 0; i<9; i++){
  //   digitalWrite(SCL, HIGH);
  //   delayMicroseconds(2);
  //   digitalWrite(SCL, LOW);
  //   delayMicroseconds(2);
  // }

  //restart I2C
  Wire.beginTransmission(_i2c_add);
  byte err = Wire.endTransmission();
  if (err == 0){
    wireError = false;
    stepperFrequence(STEPPER_FREQ); //Default: F_3921Hz
    reconnectWireTimer = 0;
  }
}

void serialFlush(){
  while(Serial.available() > 0) {
      char t = Serial.read();
    }
}