//
//    FILE: function_generator.cpp (formerly functionGenerator.cpp)
//  AUTHOR: Rob Tillaart
// VERSION: 0.3.0
// PURPOSE: wave form generating functions (use with care)
//     URL: https://github.com/RobTillaart/FunctionGenerator


#include "function_generator.h"


function_generator::function_generator(float period, float amplitude, float phase, float yShift)
{
  setPeriod(period);
  setAmplitude(amplitude);
  setPhase(phase);
  setYShift(yShift);
  setDutyCycle(50);  //  TODO param?
}


/////////////////////////////////////////////////////////////
//
//  CONFIGURATION
//
void function_generator::setPeriod(float period)
{
  _period = period;
  _freq1 = 1 / period;
  _freq2 = 2 * _freq1;
  _freq4 = 4 * _freq1;
  _freq0 = (float)TWO_PI * _freq1;
}


float function_generator::getPeriod()
{
  return _period;
}


void function_generator::setFrequency(float freq)
{
  setPeriod(1.0f / freq);
}


float function_generator::getFrequency()
{
  return _freq1;
}


void function_generator::setAmplitude(float ampl)
{
  _amplitude = ampl;
}


float function_generator::getAmplitude()
{
  return _amplitude;
}

void function_generator::setPhase(float phase)
{
  _phase = phase;
}


float function_generator::getPhase()
{
  return _phase;
}


void function_generator::setYShift(float yShift)
{
  _yShift = yShift;
}


float function_generator::getYShift()
{
  return _yShift;
}


void function_generator::setDutyCycle(float dutyCycle)
{
  //  negative dutyCycle? => 1-dc? or abs()?
  if (dutyCycle < 0)        _dutyCycle = 0.0;
  else if (dutyCycle > 100) _dutyCycle = 1.0;
  else                      _dutyCycle = dutyCycle * 0.01f;
}


float function_generator::getDutyCycle()
{
  return _dutyCycle * 100.0f;
}


void function_generator::setRandomSeed(uint32_t a, uint32_t b)
{
  //  prevent zero loops in random() function.
  if (a == 0) a = 123;
  if (b == 0) b = 456;
  _m_w = a;
  _m_z = b;
}


/////////////////////////////////////////////////////////////
//
//  FUNCTIONS
//
float function_generator::line()
{
  return _yShift + _amplitude;
}


float function_generator::zero()
{
  return 0;
}


float function_generator::sawtooth(float t, uint8_t mode)
{
  float rv;
  t += _phase;
  if (t >= 0.0)
  {
    t = (float)fmod(t, _period);
    if (mode == 1) t = _period - t;
    rv = _amplitude * (-1.0f + t *_freq2);
  }
  else
  {
    t = -t;
    t = (float)fmod(t, _period);
    if (mode == 1) t = _period - t;
    rv = _amplitude * ( 1.0f - t * _freq2);
  }
  rv += _yShift;
  return rv;
}


float function_generator::triangle(float t)
{
  float rv;
  t += _phase;
  if (t < 0.0)
  {
    t = -t;
  }
  t = (float)fmod(t, _period);
  if (t < (_period * _dutyCycle))
  {
    rv = _amplitude * (-1.0f + t * _freq2 / _dutyCycle);
  }
  else
  {
    //  mirror math
    t = _period - t;
    rv = _amplitude * (-1.0f + t * _freq2 /(1 - _dutyCycle));
  }
  rv += _yShift;
  return rv;
}


float function_generator::square(float t)
{
  float rv;
  t += _phase;
  if (t >= 0)
  {
    t = (float)fmod(t, _period);
    if (t < (_period * _dutyCycle)) rv = _amplitude;
    else rv = -_amplitude;
  }
  else
  {
    t = -t;
    t = (float)fmod(t, _period);
    if (t < (_period * _dutyCycle)) rv = -_amplitude;
    else rv = _amplitude;
  }
  rv += _yShift;
  return rv;
}


float function_generator::sinus(float t)
{
  float rv;
  t += _phase;
  rv = _amplitude * (float)sin(t * _freq0);
  rv += _yShift;
  return rv;
}


float function_generator::stair(float t, uint16_t steps, uint8_t mode)
{
  t += _phase;
  if (t >= 0)
  {
    t = (float)fmod(t, _period);
    if (mode == 1) t = _period - t;
    int level = static_cast< int >(steps * t / _period);
    return _yShift + _amplitude * (-1.0f + 2.0f * level / (steps - 1));
  }
  t = -t;
  t = (float)fmod(t, _period);
  if (mode == 1) t = _period - t;
  int level = static_cast<int>(steps * t / _period);
  return _yShift + _amplitude * (1.0f - 2.0f * level / (steps - 1));
}


float function_generator::random()
{
  float rv = _yShift + _amplitude * _random() * 0.2328306436E-9f;  //  div 0xFFFFFFFF
  return rv;
}


//  duty cycle variant takes more than twice as much time.
float function_generator::random_DC()
{
  static float rv = 0;
  float next = _yShift + _amplitude * _random() * 0.2328306436E-9f;  //  div 0xFFFFFFFF
  rv += (next - rv) * _dutyCycle;
  return rv;
}


/////////////////////////////////////////////////////////////
//
//  EXPERIMENTAL 0.2.7
//
float function_generator::sinusDiode(float t)
{
  float rv = sinus(t);
  if (rv < _yShift) return _yShift;
  return rv;

  // float rv;
  // t += _phase;
  // rv = sin(t * _freq0);
  // if (rv < 0) return _yShift;
  // rv *= amplitude;
  // rv += _yShift;
  // return rv;
}


float function_generator::sinusRectified(float t)
{
  // float rv = sinus(t);
  // if (rv < _yShift) return _yShift - rv;
  // return rv;

  float rv;
  t += _phase;
  rv = _amplitude * (float)sin(t * _freq0);
  if (rv < 0) rv = -rv;
  rv += _yShift;
  return rv;
}


float function_generator::trapezium1(float t)
{
  t += _phase + _period * _dutyCycle / 4;  //  zero point for t = 0
  if (t < 0)
  {
    t = -t;
  }
  t = (float)fmod(t, _period);

  if (t < _period * 0.5 * _dutyCycle)  //  rising part
  {
    return _yShift + -_amplitude + 2 * _amplitude * (t * 2  / (_period * _dutyCycle));
  }
  else if (t < _period * 0.5)  //  high part
  {
    return _yShift + _amplitude;
  }
  else if (t < _period * (0.5 + 0.5 * _dutyCycle))  //  falling part
  {
    return _yShift + _amplitude - 2 * _amplitude * ( (t * 2 - _period) / (_period * _dutyCycle));
  }
  else   //  low part
  {
    return _yShift + -_amplitude;
  }
}


float function_generator::trapezium2(float t)
{
  t += _phase + _period * _dutyCycle / 4;  //  zero point for t = 0
  if (t < 0)
  {
    t = -t;
  }
  t = (float)fmod(t, _period);

  if (t < _period * 0.25)  //  rising part
  {
    return _yShift + -_amplitude + 2 * _amplitude * (t * 4 / _period);
  }
  else if (t < _period * (0.25 + 0.5 * _dutyCycle))  //  high part
  {
    return _yShift + _amplitude;
  }
  else if (t < _period * (0.5 + 0.5 * _dutyCycle))  //  falling part
  {
    return _yShift + _amplitude - 2 * _amplitude * ((t - _period * (0.25f + 0.5f * _dutyCycle)) * 4 / _period);
  }
  else   //  low part
  {
    return _yShift + -_amplitude;
  }
}



//
//  EXPERIMENTAL HEARTBEAT  
//  => setFrequency(72.0 / 60.0);  //  BPM/60 = BPS.
float function_generator::heartBeat( float time_normalized )
{
  // Clamp input to valid range
  if ( time_normalized  < 0.0f ) time_normalized = 0.0f;
  if ( time_normalized >= 1.0f ) time_normalized = 0.999f;
  
  // Calculate array position with fractional part
  float  float_index = time_normalized * ( HEARTBEAT_LUT_SIZE - 1 );
  size_t index       = static_cast< size_t >( float_index );
  float  fraction    = float_index - index;
  
  // Bounds checking for interpolation
  if ( index >= HEARTBEAT_LUT_SIZE - 1 ) {
    return HEARTBEAT_LUT[ HEARTBEAT_LUT_SIZE - 1 ];
  }
  
  // Linear interpolation between adjacent points
  int16_t value1 = HEARTBEAT_LUT[ index     ];
  int16_t value2 = HEARTBEAT_LUT[ index + 1 ];
  
  return static_cast< int16_t >( value1 + fraction * ( value2 - value1 ) );
}






/////////////////////////////////////////////////////////////
//
//  PRIVATE
//
//  An example of a simple pseudo-random number generator is the
//  Multiply-with-carry method invented by George Marsaglia.
//  two initializers (not null)
uint32_t function_generator::_random()
{
  _m_z = 36969L * (_m_z & 65535L) + (_m_z >> 16);
  _m_w = 18000L * (_m_w & 65535L) + (_m_w >> 16);
  return (_m_z << 16) + _m_w;  /* 32-bit result */
}



/////////////////////////////////////////////////////////////
//
//  INTEGER VERSIONS FOR 8 BIT DAC
//
//  8 bits version
//  t = 0..9999 period 10000 in millis, returns 0..255

/*

uint8_t ifgsaw(uint16_t t, uint16_t period = 1000)
{
 return 255L * t / period;
}


uint8_t ifgtri(uint16_t t, uint16_t period = 1000)
{
 if (t * 2 < period) return 510L * t / period;
 return 255L - 510L * t / period;
}


uint8_t ifgsqr(uint16_t t, uint16_t period = 1000)
{
 if (t * 2 < period) return 510L * t / period;
 return 255L - 510L * t / period;
}


uint8_t ifgsin(uint16_t t, uint16_t period = 1000)
{
 return sin(355L * t / period / 113); // LUT
}


uint8_t ifgstr(uint16_t t, uint16_t period = 1000, uint16_t steps = 8)
{
 int level = 1L * steps * t / period;
 return 255L * level / (steps - 1);
}

*/


/////////////////////////////////////////////////////////////
//
//  SIMPLE float ONES
//
//  t = 0..period
//  period = 0.001 ... 10000 ?

/*
float fgsaw(float t, float period = 1.0)
{
 if (t >= 0) return -1.0 + 2 * t / period;
 return 1.0 + 2 * t / period;
}


float fgtri(float t, float period = 1.0)
{
 if (t < 0) t = -t;
 if (t * 2 < period) return -1.0 + 4 * t / period;
 return 3.0 - 4 * t / period;
}


float fgsqr(float t, float period = 1.0)
{
 if (t >= 0)
 {
 if ( 2 * t < period) return 1.0;
 return -1.0;
 }
 t = -t;
 if (2 * t < period) return -1.0;
 return 1.0;
}


float fgsin(float t, float period = 1.0)
{
 return sin(TWO_PI * t / period);
}


float fgstr(float t, float period = 1.0, uint16_t steps = 8)
{
 if (t >= 0)
 {
 int level = steps * t / period;
 return -1.0 + 2.0 * level / (steps - 1);
 }
 t = -t;
 int level = steps * t / period;
 return 1.0 - 2.0 * level / (steps - 1);
}
*/


/////////////////////////////////////////////////////////////
//
//  FULL floatS ONES
//
//  SAWTOOTH
float fgsaw(float t, float period = 1.0f, float amplitude = 1.0f, float phase = 0.0f, float yShift = 0.0f)
{
  t += phase;
  if (t >= 0)
  {
    if (t >= period) t = (float)fmod(t, period);
    return yShift + amplitude * (-1.0f + 2 * t / period);
  }
  t = -t;
  if (t >= period) t = (float)fmod(t, period);
  return yShift + amplitude * ( 1.0f - 2 * t / period);
}


//  TRIANGLE
float fgtri(float t, float period = 1.0f, float amplitude = 1.0f, float phase = 0.0f, float yShift = 0.0f, float dutyCycle = 0.50f)
{
  t += phase;
  if (t < 0) t = -t;
  if (t >= period) t = (float)fmod(t, period);
  // 50 % dutyCycle = faster
  // if (t * 2 < period) return yShift + amplitude * (-1.0 + 4 * t / period);
  // return yShift + amplitude * (3.0f - 4 * t / period);
  if (t < dutyCycle * period) return yShift + amplitude * (-1.0f + 2 * t / (dutyCycle * period));
  // return yShift + amplitude * (-1.0f + 2 / (1 - dutyCycle) - 2 * t / ((1 - dutyCycle) * period));
  return yShift + amplitude * (-1.0f + 2 / (1 - dutyCycle) * ( 1 - t / period));
}


//  SQUARE
float fgsqr(float t, float period = 1.0, float amplitude = 1.0, float phase = 0.0, float yShift = 0.0, float dutyCycle = 0.50)
{
  t += phase;
  if (t >= 0)
  {
    if (t >= period) t = (float)fmod(t, period);
    if (t < dutyCycle * period) return yShift + amplitude;
    return yShift - amplitude;
  }
  t = -t;
  if (t >= period) t = (float)fmod(t, period);
  if (t < dutyCycle * period) return yShift - amplitude;
  return yShift + amplitude;
}


//  SINUS
float fgsin(float t, float period = 1.0, float amplitude = 1.0, float phase = 0.0, float yShift = 0.0)
{
  t += phase;
  float rv = yShift + amplitude * (float)sin(TWO_PI * t / period);
  return rv;
}


//  STAIR
float fgstr(float t, float period = 1.0, float amplitude = 1.0, float phase = 0.0, float yShift = 0.0, uint16_t steps = 8)
{
  t += phase;
  if (t >= 0)
  {
    if (t >= period) t = (float)fmod(t, period);
    int level = static_cast< int >( steps * t / period );
    return yShift + amplitude * (-1.0f + 2.0f * level / (steps - 1));
  }
  t = -t;
  if (t >= period) t = (float)fmod(t, period);
  int level = static_cast<int>( steps * t / period );
  return yShift + amplitude * (1.0f - 2.0f * level / (steps - 1));
}


//  -- END OF FILE --

