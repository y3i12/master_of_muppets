#include <SLIPEncodedSerial.h>
#include <Wire.h>

#include "functionGenerator.h"

#include "master_of_muppets.hpp"
#include "adafruit_mcp_4728_driver.h"

#define TEST_LFO 1 // doesn't read from serial and outputs the same saw wave on all outs
funcgen gen;

_SLIPSerial< usb_serial_class > SLIPSerial( thisBoardsSerialUSB );

electric_mayhem< adafruit_mcp_4728_driver > the_muppets;

////////////////////////////////////////////////////////////////////////////////
// SETUP
////////////////////////////////////////////////////////////////////////////////

void setup( void ) {
  adafruit_mcp_4728_driver::initialization_struct_t initialization_structs[ dr_teeth::k_dac_count ] = {
        adafruit_mcp_4728_driver::initialization_struct_t( &Wire1, 4 ),
        adafruit_mcp_4728_driver::initialization_struct_t( &Wire2, 8 ),
        adafruit_mcp_4728_driver::initialization_struct_t( &Wire,  6 )
    };

    the_muppets.initialize( initialization_structs );

    gen.setFrequency( 100 );
    gen.setAmplitude( 32 * 1024 - 1);
}

////////////////////////////////////////////////////////////////////////////////
// TEST_LFO
// Instead of receiving serial data, generates a triangle wave into dr_teeth's
// read buffer
////////////////////////////////////////////////////////////////////////////////

void test_lfo( void ) {
    dr_teeth::reset();

    message_t::instance->type = message_t::k_set_dac_value;

    message_attribute_address_value_t* message_address_value = &message_set_dac_value_t::instance->first_address_value;
    float     t     = muppet_clock::what_time_is_it< float >() * 0.001f;
    uint16_t  value = gen.triangle( t ) + 32 * 1024;

    for ( message_set_dac_value_t::instance->count = 0; message_set_dac_value_t::instance->count < dr_teeth::k_total_channels; ++message_set_dac_value_t::instance->count ) {
        message_address_value[ message_set_dac_value_t::instance->count ].address = message_set_dac_value_t::instance->count;
        message_address_value[ message_set_dac_value_t::instance->count ].value   = value;
    }
}

////////////////////////////////////////////////////////////////////////////////
// SERIAL_READ
////////////////////////////////////////////////////////////////////////////////

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
    while( 1 ) {
#ifdef TEST_LFO
        test_lfo();
#else
        serial_read();
#endif
        
        muppet_clock::tiny_wait( 1 );
        dr_teeth::go_muppets( the_muppets );
    }
}

