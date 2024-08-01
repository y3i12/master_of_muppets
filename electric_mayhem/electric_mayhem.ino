#include <OSCBoards.h>
#include <OSCBundle.h>
#include <SLIPEncodedSerial.h>

#include <Adafruit_MCP4728.h>
#include <Wire.h>

#include "functionGenerator.h"

#include "master_of_muppets.hpp"

#define STATUS_LED_PIN  13

// #define WIRE_CLOCK      100000
#define WIRE_CLOCK 1400000L

#define K( v )                                  ( v * 1024 )
#define MAX_VAL                                 4095
// #define MIN_INPUT_VOLTAGE                       1.5 // TL074
// #define MIN_INPUT_VOLTAGE                       1.6 // LM386
#define MIN_INPUT_VOLTAGE                       0   // LT1014?

#define VAL_START                               ( static_cast< uint16_t >( MAX_VAL / 5.0 * MIN_INPUT_VOLTAGE  )             ) // Value correction due to lack of callibration in the OpAmp
#define VAL_INTERVAL                            ( static_cast< uint16_t >( MAX_VAL - VAL_START                )             )
#define DAC_NORMALIZED_VAL( value )             ( static_cast< uint16_t >( ( value ) / K(64.0f) * VAL_INTERVAL ) + VAL_START )
#define SET_ADDRESS_VALUE( addr_value_struct )  needs_update = true; value_buffer[ addr_value_struct.address ] = DAC_NORMALIZED_VAL( addr_value_struct.value );
#define REFRESH_DAC_AFTER_MS                    100

#define TEST_LFO 1 // doesn't read from serial and outputs the same saw wave on all outs
funcgen gen;

Adafruit_MCP4728  mcp[ dr_teeth::k_dac_count ] = { };
uint8_t           ldac_ports[  ]               = { 4, 6, 8 };
TwoWire*          Wires[ 3 ]                   = { &Wire1, &Wire2, &Wire };

// global time and update time are in millis
uint32_t          global_time               = 0;    // incremental time
float             global_time_f             = 0.0f; // incremental time
// loop time is in micros
uint32_t          loop_time                 = 0;
uint32_t          last_loop_time            = 0;
uint32_t          last_loop_delta           = 0;
uint32_t          loop_update_after         = 512;
uint16_t          global_time_accummulator  = 0;
uint16_t          value_buffer[ dr_teeth::k_total_channels ]  = { };
bool              needs_update              = true;

_SLIPSerial<usb_serial_class>         SLIPSerial( thisBoardsSerialUSB );

////////////////////////////////////////////////////////////////////////////////
// Led status and blinking functions
////////////////////////////////////////////////////////////////////////////////
static uint32_t last_led_time = 0;
static bool     led_status    = false;

void statusLED(bool in_status) {
       if ( !led_status &&  in_status && ( global_time - last_led_time > 100 ) ) { last_led_time = global_time; led_status = true;  digitalWrite( STATUS_LED_PIN, HIGH); } 
  else if (  led_status && !in_status && ( global_time - last_led_time > 50  ) ) { last_led_time = global_time; led_status = false; digitalWrite( STATUS_LED_PIN, LOW); }
}

void blink( uint8_t num = 5, int time = 250 ) {
  for ( uint8_t i = 0; i < num; ++i )   {
    digitalWrite( STATUS_LED_PIN, HIGH ); delay( time );
    digitalWrite( STATUS_LED_PIN, LOW  ); delay( time );
  }
}

void ublink( void ) {
  statusLED( true  );
  statusLED( false );
}

////////////////////////////////////////////////////////////////////////////////
// SETUP
////////////////////////////////////////////////////////////////////////////////

void setup( void ) {
  global_time = millis( );
  
  gen.setFrequency(50);
  gen.setAmplitude(K(32)-1);

  // blink( 10, 100 );

  for ( uint8_t dac_index = 0; dac_index < dr_teeth::k_dac_count; ++dac_index ) {
    pinMode( ldac_ports[ dac_index ], OUTPUT);
    digitalWrite( ldac_ports[ dac_index ], LOW );

    //pinMode( rdy_ports[ dac_index ], INPUT);

    Wires[ dac_index ]->begin( );
    Wires[ dac_index ]->setClock( WIRE_CLOCK );
    

    uint16_t retry = 0;
    while ( retry++ < 100 && !mcp[ dac_index ].begin( MCP4728_I2CADDR_DEFAULT, Wires[ dac_index ] ) ) {
      delay( 10 );
      global_time = millis( );
      ublink( );
    }

    if ( retry < 100 ) {
      for ( uint8_t dac_channel = 0; dac_channel < dr_teeth::k_channels_per_dac; ++dac_channel ) {
        mcp[ dac_index ].setChannelValue( static_cast< MCP4728_channel_t >( dac_channel ), 0 );
      }
    }
  }

  // blink( 2, 300 );
  loop_time = last_loop_time = micros( );
}



//#define TRI_WAVE_HZ(hz) static_cast< uint16_t >( abs( static_cast< int32_t >( global_time * hz * ( K( 128 ) / 1000 ) % ( K( 128 ) ) ) - K( 64 ) ) - 1 ) 

void test_lfo( void ) {
  dr_teeth::reset();

  message_t::instance->type = message_t::k_set_dac_value;

  message_attribute_address_value_t* message_address_value = &message_set_dac_value_t::instance->first_address_value;
  float t = global_time_f * 0.001;
  //uint16_t                           value                 = TRI_WAVE_HZ(100);
  uint16_t                           value                 = gen.triangle(t) + K(32);
  for ( message_set_dac_value_t::instance->count = 0; message_set_dac_value_t::instance->count < dr_teeth::k_total_channels; ++message_set_dac_value_t::instance->count ) {
    message_address_value[message_set_dac_value_t::instance->count].address = message_set_dac_value_t::instance->count;
    message_address_value[message_set_dac_value_t::instance->count].value   = value;
    SET_ADDRESS_VALUE(message_address_value[message_set_dac_value_t::instance->count]);
  }

  //needs_update = true;
}



void update( void ) {

  for ( uint8_t dac_index = 0; dac_index < dr_teeth::k_dac_count; ++dac_index ) {
    
    
      digitalWrite( ldac_ports[ dac_index ], HIGH );

       mcp[ dac_index ].fastWrite( value_buffer[ dac_index * dr_teeth::k_channels_per_dac + 0 ],
                                   value_buffer[ dac_index * dr_teeth::k_channels_per_dac + 1 ],
                                   value_buffer[ dac_index * dr_teeth::k_channels_per_dac + 2 ],
                                   value_buffer[ dac_index * dr_teeth::k_channels_per_dac + 3 ] );

      digitalWrite( ldac_ports[ dac_index ], LOW );
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
    if ( message_t::k_set_dac_value == message_t::instance->type ) {
      needs_update = true;

      message_attribute_address_value_t* message_address_value( &message_set_dac_value_t::instance->first_address_value );
      
      for ( uint8_t i = 0; i < message_set_dac_value_t::instance->count; ++i ) {
        SET_ADDRESS_VALUE( message_address_value[ i ] );
      }
    }
  }
}

////////////////////////////////////////////////////////////////////////////////
// LOOP
////////////////////////////////////////////////////////////////////////////////

void loop( void ) {
  loop_time         = micros( );
  last_loop_delta   = loop_time - last_loop_time;
  last_loop_time    = loop_time;
  global_time_f    += last_loop_delta / 1000.0f;
  global_time      += (uint32_t)global_time_f;

  // Receives data from usb serial into the buffer, using slip decoding

#ifdef TEST_LFO
  test_lfo();
#else
  serial_read();
#endif
    
   needs_update = true;
  
  if ( needs_update ) {
    update();
    needs_update = false;
  }
}

