#include <Grove_I2C_Motor_Driver.h>
#include <Wire.h>
#include "avr/wdt.h" //software reset watchdog

#define ENDSTOP_A 2

unsigned char _i2c_add = 0x0f;
int _step_cnt = 0;
int dir = 1;
bool wasTriggered = false;
int speedPot = 80;// 45-200
int speedDelay = 50;// 45-200
int speedTimer = 0;
unsigned long lastLoopTime = 0;
int resetCounter = 0;
unsigned long resetTimer = 0;

void(* resetFunc) (void) = 0; // esta es la funcion


void setup() {
  // wdt_disable(); //init reset Watchdog

  Serial.begin(9600);
  pinMode(13, OUTPUT);
  pinMode(2, INPUT);
  pinMode(3, INPUT);

  Wire.begin();
  delay(1000);
  Wire.onRequest(requestEvents);
  Wire.onReceive(receiveEvents);

  speedDelay = random(156) + 45;

  // wdt_enable(WDTO_8S); //set watchdog 8s
}

void loop() {
  // Temporizador
  lastLoopTime = millis();
  if (speedTimer > ((random(4)+4) * 60000)) {
    speedDelay = random(156) + 45;
    speedTimer = 0;
  }


  // if (Serial.available() > 0) {
  //   // look for the next valid integer in the incoming serial stream:
  //   int msgValue = Serial.parseInt();
  //   digitalWrite(13, HIGH);
  //   // Read Serial for value 
  //   if (Serial.read() == '\n') {
  //     // constrain the values to 0 - 255 and invert
  //     speedDelay = constrain(msgValue, 40, 1000);
  //   }
  // }

  // Serial.print("EndStopA: ");
  // Serial.println(digitalRead(2));

  //speedDelay = map(analogRead(A0), 0, 1024, 2, 1000);
  // Serial.print("Speed: ");
  // Serial.println(speedDelay);

  // Enviar orden a driver
  stepperRun(1 * dir); // paso
  stop();
  delay(speedDelay);// 10-100

  handleEndSwitches();

  // Actualizar contador
  speedTimer += millis() - lastLoopTime;

  //Reset after 5 mins
  // if (resetTimer > 4000) {
  //   if (resetCounter < 5 ) { // 5 mins = 75
  //     // wdt_reset(); //avoids reset
  //     resetCounter ++;
  //     resetTimer = 0;
  //   }
  //   else {
  //     Serial.println("RESET");
  //     Serial.println(millis());
  //     resetCounter = 0;
  //     delay(10);
  //     resetFunc(); // la llamo con esto reset
  //   }
  // }
  // resetTimer += millis() - lastLoopTime;

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

void stop() {
  Wire.beginTransmission(_i2c_add); // begin transmission
  Wire.write(MotorSpeedSet);              // set pwm header
  Wire.write(0);              // send speed of motor1
  Wire.write(0);              // send speed of motor2
  Wire.endTransmission();    		        // stop transmitting
  delay(4); 	
}

void direction(unsigned char _direction) {
    Wire.beginTransmission(_i2c_add); // begin transmission
    Wire.write(DirectionSet);               // Direction control header
    Wire.write(_direction);                 // send direction control information
    Wire.write(Nothing);                    // need to send this byte as the third byte(no meaning)
    Wire.endTransmission();                 // stop transmitting
    delay(4); 				                // wait
}

void stepperFrequence(unsigned char _frequence) {
    if (_frequence < F_31372Hz || _frequence > F_30Hz) {
        Serial.println("frequence error! Must be F_31372Hz, F_3921Hz, F_490Hz, F_122Hz, F_30Hz");
        return;
    }
    Wire.beginTransmission(_i2c_add); // begin transmission
    Wire.write(PWMFrequenceSet);            // set frequence header
    Wire.write(_frequence);                 // send frequence
    Wire.write(Nothing);                    // need to send this byte as the third byte(no meaning)
    Wire.endTransmission();                 // stop transmitting
    delay(4); 				                // wait
}

void stepperRun(int _step) {

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
    Wire.endTransmission();    		        // stop transmitting
    delay(1); 				                // wait

    if (_direction == 1) {				// Sentido Horario
        for (int i = 0; i < _step; i++) {
            switch (_step_cnt) {
                case 0 : direction(0b0001); direction(0b0101); break;
                case 1 : direction(0b0100); direction(0b0110); break;
                case 2 : direction(0b0010); direction(0b1010); break;
                case 3 : direction(0b1000); direction(0b1001); break;
            }
            _step_cnt = (_step_cnt + 1) % 4;
        }
    } else if (_direction == -1) { // Sentido Anti-horario
        for (int i = 0; i < _step; i++) {
            switch (_step_cnt) {
                case 0 : direction(0b1000); direction(0b1010); break;
                case 1 : direction(0b0010); direction(0b0110); break;
                case 2 : direction(0b0100); direction(0b0101); break;
                case 3 : direction(0b0001); direction(0b1001); break;
            }
            _step_cnt = (_step_cnt + 1) % 4;
        }
    }
}

int n = 0;

void requestEvents()
{
  Serial.println(F("---> recieved request"));
  Serial.print(F("sending value : "));
  Serial.println(n);
  Wire.write(n);
}

void receiveEvents(int numBytes)
{  
  Serial.println(F("---> recieved events"));
  n = Wire.read();
  Serial.print(numBytes);
  Serial.println(F("bytes recieved"));
  Serial.print(F("recieved value : "));
  Serial.println(n);
}