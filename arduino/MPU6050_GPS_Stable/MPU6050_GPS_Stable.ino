#include <TinyGPS++.h>
#include <SoftwareSerial.h>
#include "I2Cdev.h"
#include "MPU6050_6Axis_MotionApps20.h"
//#include "MPU6050.h" // not necessary if using MotionApps include file
#if I2CDEV_IMPLEMENTATION == I2CDEV_ARDUINO_WIRE
  #include "Wire.h"
#endif

// define MPU instance 
MPU6050 mpu;                    // class default I2C address is 0x68; specific I2C addresses may be passed as a parameter here

// MPU control/status vars
uint8_t mpuIntStatus;   // holds actual interrupt status byte from MPU
uint8_t devStatus;      // return status after each device operation (0 = success, !0 = error)
uint16_t packetSize;    // expected DMP packet size (default is 42 bytes)
uint16_t fifoCount;     // count of all bytes currently in FIFO
uint8_t fifoBuffer[64]; // FIFO storage buffer

int ledPin = 13; // blink the led to show we are running

// orientation/motion vars
Quaternion q;           // [w, x, y, z]         quaternion container
VectorInt16 aa;         // [x, y, z]            accel sensor measurements
VectorInt16 aaReal;     // [x, y, z]            gravity-free accel sensor measurements
VectorInt16 aaWorld;    // [x, y, z]            world-frame accel sensor measurements
VectorFloat gravity;    // [x, y, z]            gravity vector
float ypr[3];           // [yaw, pitch, roll]   yaw/pitch/roll container and gravity vector

//###GPS Serial Setup
static const int RXPin = 4, TXPin = 3;
static const uint32_t GPSBaud = 9600;
// The TinyGPS++ object
TinyGPSPlus gps;

// The serial connection to the GPS device
SoftwareSerial ss(RXPin, TXPin);

// relative ypr[x] usage based on sensor orientation when mounted, e.g. ypr[PITCH]
#define PITCH   2     // defines the position within ypr[x] variable for PITCH; may vary due to sensor orientation when mounted
#define ROLL  3     // defines the position within ypr[x] variable for ROLL; may vary due to sensor orientation when mounted
#define YAW   1     // defines the position within ypr[x] variable for YAW; may vary due to sensor orientation when mounted


// uncomment "OUTPUT_READABLE_YAWPITCHROLL" if you want to see the yaw/
// pitch/roll angles (in degrees) calculated from the quaternions coming
// from the FIFO. Note this also requires gravity vector calculations.
// Also note that yaw/pitch/roll angles suffer from gimbal lock (for
// more info, see: http://en.wikipedia.org/wiki/Gimbal_lock)
#define OUTPUT_READABLE_YAWPITCHROLL

// uncomment "OUTPUT_READABLE_REALACCEL" if you want to see acceleration
// components with gravity removed. This acceleration reference frame is
// not compensated for orientation, so +X is always +X according to the
// sensor, just without the effects of gravity. If you want acceleration
// compensated for orientation, us OUTPUT_READABLE_WORLDACCEL instead.
//#define OUTPUT_READABLE_REALACCEL

// uncomment "OUTPUT_READABLE_WORLDACCEL" if you want to see acceleration
// components with gravity removed and adjusted for the world frame of
// reference (yaw is relative to initial orientation, since no magnetometer
// is present in this case). Could be quite handy in some cases.
//#define OUTPUT_READABLE_WORLDACCEL




// ****************************************************************************************************************************************************************************************
// NOTE: WE CHANGED THE FOLLOWING LINE IN MPU_6050_6Axis_MotionApps.h to 0x04 = 50 Hertz (50x/sec)
// 0x02,   0x16,   0x02,   0x00, 0x04                // D_0_22 inv_set_fifo_rate (WAS 0x01) ** EDIT HMZ

    // This very last 0x01 WAS a 0x09, which drops the FIFO rate down to 20 Hz. 0x07 is 25 Hz,
    // 0x01 is 100Hz. Going faster than 100Hz (0x00=200Hz) tends to result in very noisy data.
    // DMP output frequency is calculated easily using this equation: (200Hz / (1 + value))

    // It is important to make sure the host processor can keep up with reading and processing
    // the FIFO output at the desired rate. Handling FIFO overflow cleanly is also a good idea.

// ****************************************************************************************************************************************************************************************


// ================================================================
// ===                      INITIAL SETUP                       ===
// ================================================================

void setup() 
{
  // join I2C bus (I2Cdev library doesn't do this automatically)
  #if I2CDEV_IMPLEMENTATION == I2CDEV_ARDUINO_WIRE
    Wire.begin();
    TWBR = 12; // 400kHz I2C clock (200kHz if CPU is 8MHz)
  #elif I2CDEV_IMPLEMENTATION == I2CDEV_BUILTIN_FASTWIRE
    Fastwire::setup(400, true);
  #endif

  Serial.begin(9600);
  ss.begin(GPSBaud);
  
  // initialize device
  Serial.println(F("Initializing I2C devices..."));
  mpu.initialize();

  // verify connection
  Serial.println(F("Testing device connections..."));
  Serial.println(mpu.testConnection() ? F("MPU6050 connection successful") : F("MPU6050 connection failed"));

  // load and configure the DMP
  Serial.println(F("Initializing DMP"));
  devStatus = mpu.dmpInitialize();


    // INPUT CALIBRATED OFFSETS HERE; SPECIFIC FOR EACH UNIT AND EACH MOUNTING CONFIGURATION!!!!
 /*
     Calculated offsets:
    x gyro: 70
    y gyro: -18
    z gyro: 0
  
    x accel: -2499
    y accel: 679
    z accel: 2421
  */
    mpu.setXGyroOffset(70);
    mpu.setYGyroOffset(-18);
    mpu.setZGyroOffset(0);
    mpu.setXAccelOffset(-2499); 
    mpu.setYAccelOffset(679); 
    mpu.setZAccelOffset(2421); 
    
    
  // make sure it worked (returns 0 if so)
  if (devStatus == 0) 
    {
      // turn on the DMP, now that it's ready
      Serial.println(F("Enabling DMP"));
      mpu.setDMPEnabled(true);

      // enable Arduino interrupt detection
      Serial.println(F("Enabling interrupt detection (Arduino external interrupt 0)"));
      mpuIntStatus = mpu.getIntStatus();
      
      // get expected DMP packet size for later comparison
      packetSize = mpu.dmpGetFIFOPacketSize();
    } 
  else 
    {
      // ERROR!
      // 1 = initial memory load failed, 2 = DMP configuration updates failed (if it's going to break, usually the code will be 1)
      Serial.print(F("DMP Initialization failed code = "));
      Serial.println(devStatus);
    }

    pinMode(ledPin, OUTPUT);

} // setup()



// ================================================================
// ===                    MAIN PROGRAM LOOP                     ===
// ================================================================

void loop(void)
{
    
  processAccelGyro();
  
  digitalWrite(ledPin, HIGH);   // sets the LED on
  delay(25);                  // waits for a second
  digitalWrite(ledPin, LOW);    // sets the LED off
  
}   // loop()



// ================================================================
// ===                    PROCESS ACCEL/GYRO IF AVAILABLE       ===
// ================================================================

void processAccelGyro() 
{
  
  // Get INT_STATUS byte
  mpuIntStatus = mpu.getIntStatus();

  // get current FIFO count
  fifoCount = mpu.getFIFOCount();

  // check for overflow (this should never happen unless our code is too inefficient)
  if ((mpuIntStatus & 0x10) || fifoCount == 1024) 
    {
      // reset so we can continue cleanly
      mpu.resetFIFO();
      //Serial.println(F("FIFO overflow!"));
      return;
    } 
  
  if (mpuIntStatus & 0x02)  // otherwise continue processing
    {
      // check for correct available data length
      if (fifoCount < packetSize) 
        return; //  fifoCount = mpu.getFIFOCount();

      // read a packet from FIFO
      mpu.getFIFOBytes(fifoBuffer, packetSize);
      
      // track FIFO count here in case there is > 1 packet available
      fifoCount -= packetSize;

      #ifdef OUTPUT_READABLE_YAWPITCHROLL
        // display Euler angles in degrees
        // uncomment "OUTPUT_READABLE_YAWPITCHROLL" if you want to see the yaw/
        // pitch/roll angles (in degrees) calculated from the quaternions coming
        // from the FIFO. Note this also requires gravity vector calculations.
        // Also note that yaw/pitch/roll angles suffer from gimbal lock (for
        // more info, see: http://en.wikipedia.org/wiki/Gimbal_lock)
        mpu.dmpGetQuaternion(&q, fifoBuffer);
        mpu.dmpGetGravity(&gravity, &q);
        mpu.dmpGetYawPitchRoll(ypr, &q, &gravity);
        Serial.print("y-p-r-lat-long-elv,");
        Serial.print(ypr[0] * 180/M_PI);
        Serial.print(",");
        Serial.print(ypr[1] * 180/M_PI);
        Serial.print(",");
        Serial.print(ypr[2] * 180/M_PI);
        Serial.print(",");
       while (ss.available() > 0)
        if (gps.encode(ss.read()));
        
       
       Serial.print(gps.location.lat(), 6);
       Serial.print(",");
       Serial.print(gps.location.lng(), 6);
       Serial.print(",");
       Serial.println(gps.altitude.meters());   
      #endif

      #ifdef OUTPUT_READABLE_REALACCEL
        // display real acceleration, adjusted to remove gravity
        // uncomment "OUTPUT_READABLE_REALACCEL" if you want to see acceleration
        // components with gravity removed. This acceleration reference frame is
        // not compensated for orientation, so +X is always +X according to the
        // sensor, just without the effects of gravity. If you want acceleration
        // compensated for orientation, us OUTPUT_READABLE_WORLDACCEL instead.
        mpu.dmpGetQuaternion(&q, fifoBuffer);
        mpu.dmpGetAccel(&aa, fifoBuffer);
        mpu.dmpGetGravity(&gravity, &q);
        mpu.dmpGetLinearAccel(&aaReal, &aa, &gravity);
        Serial.print("areal\t");
        Serial.print(aaReal.x);
        Serial.print("\t");
        Serial.print(aaReal.y);
        Serial.print("\t");
        Serial.println(aaReal.z);
      #endif

      #ifdef OUTPUT_READABLE_WORLDACCEL
        // display initial world-frame acceleration, adjusted to remove gravity
        // and rotated based on known orientation from quaternion
        // uncomment "OUTPUT_READABLE_WORLDACCEL" if you want to see acceleration
        // components with gravity removed and adjusted for the world frame of
        // reference (yaw is relative to initial orientation, since no magnetometer
        // is present in this case). Could be quite handy in some cases.
        mpu.dmpGetQuaternion(&q, fifoBuffer);
        mpu.dmpGetAccel(&aa, fifoBuffer);
        mpu.dmpGetGravity(&gravity, &q);
        mpu.dmpGetLinearAccel(&aaReal, &aa, &gravity);
        mpu.dmpGetLinearAccelInWorld(&aaWorld, &aaReal, &q);
        Serial.print("aworld\t");
        Serial.print(aaWorld.x);
        Serial.print("\t");
        Serial.print(aaWorld.y);
        Serial.print("\t");
        Serial.println(aaWorld.z);
      #endif
    } // if (mpuIntStatus & 0x02)
}  // processAccelGyro() 
