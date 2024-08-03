#include <OSCBoards.h>
#include <OSCBundle.h>
#include <SLIPEncodedSerial.h>

#include <Adafruit_MCP4728.h>
#include <Wire.h>

#include "functionGenerator.h"

#include "master_of_muppets.hpp"
#include "adafruit_mcp_4728_driver.h"

#define STATUS_LED_PIN  13

#define K( v )                                  ( v * 1024 )
#define MAX_VAL                                 4095

#define DAC_NORMALIZED_VAL( value )             ( static_cast< uint16_t >( ( value ) / K( 64.0f ) * MAX_VAL ) )
#define SET_ADDRESS_VALUE( addr_value_struct )  needs_update = true; value_buffer[ addr_value_struct.address ] = DAC_NORMALIZED_VAL( addr_value_struct.value );
#define REFRESH_DAC_AFTER_MS                    100

#define TEST_LFO 1 // doesn't read from serial and outputs the same saw wave on all outs
funcgen gen;

uint16_t          value_buffer[ dr_teeth::k_total_channels ]  = { };
bool              needs_update              = true;

_SLIPSerial<usb_serial_class>         SLIPSerial( thisBoardsSerialUSB );

electric_mayhem< adafruit_mcp_4728_driver > the_muppets;

////////////////////////////////////////////////////////////////////////////////
// Led status and blinking functions
////////////////////////////////////////////////////////////////////////////////
// static uint32_t last_led_time = 0;
// static bool     led_status    = false;

// void statusLED(bool in_status) {
//        if ( !led_status &&  in_status && ( global_time - last_led_time > 100 ) ) { last_led_time = global_time; led_status = true;  digitalWrite( STATUS_LED_PIN, HIGH); } 
//   else if (  led_status && !in_status && ( global_time - last_led_time > 50  ) ) { last_led_time = global_time; led_status = false; digitalWrite( STATUS_LED_PIN, LOW); }
// }

// void blink( uint8_t num = 5, int time = 250 ) {
//   for ( uint8_t i = 0; i < num; ++i )   {
//     digitalWrite( STATUS_LED_PIN, HIGH ); delay( time );
//     digitalWrite( STATUS_LED_PIN, LOW  ); delay( time );
//   }
// }

// void ublink( void ) {
//   statusLED( true  );
//   statusLED( false );
// }

////////////////////////////////////////////////////////////////////////////////
// SETUP
////////////////////////////////////////////////////////////////////////////////

void setup( void ) {
  adafruit_mcp_4728_driver::initialization_struct_t init_structs[ dr_teeth::k_dac_count ] = {
    adafruit_mcp_4728_driver::initialization_struct_t( &Wire1, 4 ),
    adafruit_mcp_4728_driver::initialization_struct_t( &Wire2, 8 ),
    adafruit_mcp_4728_driver::initialization_struct_t( &Wire,  6 )
  };

  the_muppets.initialize( init_structs );

  gen.setFrequency(50);
  gen.setAmplitude(K(32)-1);
  
  muppet_clock::lap();
}



//#define TRI_WAVE_HZ(hz) static_cast< uint16_t >( abs( static_cast< int32_t >( global_time * hz * ( K( 128 ) / 1000 ) % ( K( 128 ) ) ) - K( 64 ) ) - 1 ) 

void test_lfo( void ) {
  dr_teeth::reset();

  message_t::instance->type = message_t::k_set_dac_value;

  message_attribute_address_value_t* message_address_value = &message_set_dac_value_t::instance->first_address_value;
  float     t     = muppet_clock::what_time_is_it< float >() * 0.001f;
  uint16_t  value = gen.triangle(t) + K(32);

  for ( message_set_dac_value_t::instance->count = 0; message_set_dac_value_t::instance->count < dr_teeth::k_total_channels; ++message_set_dac_value_t::instance->count ) {
    message_address_value[message_set_dac_value_t::instance->count].address = message_set_dac_value_t::instance->count;
    message_address_value[message_set_dac_value_t::instance->count].value   = value;
  }
}

void serial_read( void ) {
  while ( SLIPSerial.available() ) {
    dr_teeth::reset();

    while ( !SLIPSerial.endofPacket() ) {
      if ( SLIPSerial.available() ) {
        dr_teeth::write( SLIPSerial.read() );
      }
    }
  }
}

////////////////////////////////////////////////////////////////////////////////
// LOOP
////////////////////////////////////////////////////////////////////////////////

void loop( void ) {
  muppet_clock::lap();

  // Receives data from usb serial into the buffer, using slip decoding

#ifdef TEST_LFO
  test_lfo();
#else
  serial_read();
#endif
    
  dr_teeth::go_muppets( the_muppets );
}

