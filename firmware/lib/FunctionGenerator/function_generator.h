#pragma once
//
//    FILE: function_generator.h (formerly functionGenerator.h)
//  AUTHOR: Rob Tillaart
// VERSION: 0.3.0
// PURPOSE: wave form generating functions (use with care)
//     URL: https://github.com/RobTillaart/FunctionGenerator
//
// y3i12- NOTE: the library remains the same as coded by Rob Tillaart,
//    the change makes it compliant with standard C++, making it possible
//    to be used in non-arduino projects. the class was renamed.


#include <cstdint>
#include <math.h>

#define FUNCTIONGENERATOR_LIB_VERSION           (F("0.3.0"))

#ifndef TWO_PI
#define TWO_PI M_2_PI
#endif

class function_generator
{
public:

  static constexpr int16_t HEARTBEAT_LUT_SIZE = 32;
  static constexpr int16_t HEARTBEAT_LUT[ HEARTBEAT_LUT_SIZE ] = {
    2000,   4000,  6000,  8000, 10000, 12000, 14000, 16000,
    18000, 20000, 22000, 24000, 26000, 28000, 30000, 32000,
    30000, 28000, 26000, 24000, 22000, 20000, 18000, 16000,
    14000, 12000, 10000,  8000,  6000,  4000,  2000,     0
  };


  function_generator(float period = 1.0, float amplitude = 1.0, float phase = 0.0, float yShift = 0.0);


  /////////////////////////////////////////////////////////////
  //
  //  CONFIGURATION
  //
  void  setPeriod(float period = 1.0);
  float getPeriod();

  void  setFrequency(float freq = 1.0);
  float getFrequency();

  void  setAmplitude(float ampl = 1.0);
  float getAmplitude();

  void  setPhase(float phase = 0.0);
  float getPhase();

  void  setYShift(float yShift = 0.0);
  float getYShift();

  void  setDutyCycle(float dutyCycle);
  float getDutyCycle();

  void  setRandomSeed(uint32_t a, uint32_t b = 314159265);


  /////////////////////////////////////////////////////////////
  //
  //  FUNCTIONS
  //
  //  constant amplitude
  float line();
  //  constant zero for calibration.
  float zero();

  //  standard wave forms
  float sawtooth(float t, uint8_t mode = 0);  //  0 ==>  /|.   1 ==> sawtooth |\.
  float triangle(float t);
  float square(float t);
  float sinus(float t);
  float stair(float t, uint16_t steps = 8, uint8_t mode = 0);

  float random();
  float random_DC();  //  duty cycle variant. Experimental.

  /////////////////////////////////////////////////////////////
  //
  //  EXPERIMENTAL 0.2.7
  //
  float sinusDiode(float t);
  float sinusRectified(float t);
  float trapezium1(float t);
  float trapezium2(float t);
  float heartBeat(float t);  //  72 BPM = 72/60 = 1 setFrequency(1.2)


private:
    inline long map( long x, long in_min, long in_max, long out_min, long out_max ) {
        return ( x - in_min ) * ( out_max - out_min ) / ( in_max - in_min ) + out_min;
    }

  float _period;
  float _freq0;
  float _freq1;
  float _freq2;
  float _freq4;
  float _amplitude;
  float _phase;
  float _yShift;
  float _dutyCycle;

  //  Marsaglia 'constants'
  uint32_t _m_w = 1;
  uint32_t _m_z = 2;
  uint32_t _random();
};


//  -- END OF FILE --

