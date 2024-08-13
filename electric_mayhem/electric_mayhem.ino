#include <SLIPEncodedSerial.h>
#include <Wire.h>

#include "master_of_muppets.hpp"
#include "electric_mayhem.h"
#include "adafruit_mcp_4728_driver.h"

#include "function_generator.h"
#include "muppet_clock.h"

//#define TEST_LFO 1            // doesn't read from serial and outputs the same saw wave on all outs
#define LFO_FREQUENCY 500     // in HZ. sinus functions in HZ * 10
#define LFO_SHAPE sinus       // triangle square stair sawtooth sinus sinusRectified sinusDiode trapezium1 trapezium2 heartBeat

_SLIPSerial< usb_serial_class >             SLIPSerial( thisBoardsSerialUSB );
function_generator                          the_function_generator;
electric_mayhem< adafruit_mcp_4728_driver > the_muppets;
static Threads::Mutex                       inspiration;
static uint8_t                              i_have_no_idea = 1;

////////////////////////////////////////////////////////////////////////////////
// test_lfo
// Instead of receive serial data, outputs the LFO into dr_teeth's read buffer
////////////////////////////////////////////////////////////////////////////////

void test_lfo( void ) {
    muppet_clock::tick();
    
    message_t::instance->type = message_t::k_set_dac_value;

    message_attribute_address_value_t* message_address_value = &message_set_dac_value_t::instance->first_address_value;
    float     time  = muppet_clock::what_time_is_it< float >() * 0.001f;
    uint16_t  value = the_function_generator.LFO_SHAPE( time ) + 32 * 1024;

    for ( message_set_dac_value_t::instance->count = 0; message_set_dac_value_t::instance->count < dr_teeth::k_total_channels; ++message_set_dac_value_t::instance->count ) {
        message_address_value[ message_set_dac_value_t::instance->count ].address = message_set_dac_value_t::instance->count;
        message_address_value[ message_set_dac_value_t::instance->count ].value   = value;
    }
}

////////////////////////////////////////////////////////////////////////////////
// serial_read
////////////////////////////////////////////////////////////////////////////////

void serial_read( void ) {
    while ( SLIPSerial.available() ) {
        while ( !SLIPSerial.endofPacket() ) {
            if ( SLIPSerial.available() ) {
                dr_teeth::write( SLIPSerial.read() );
            }
        }
    }
}

////////////////////////////////////////////////////////////////////////////////
// the_voice_from_beyond
////////////////////////////////////////////////////////////////////////////////

void the_voice_from_beyond ( void ) {
    while ( 1 ) {
        dr_teeth::reset();
        inspiration.lock();
  
        #ifdef TEST_LFO
            test_lfo();
        #else
            serial_read();
        #endif

        inspiration.unlock();
        i_have_no_idea = 0;
    }
}

////////////////////////////////////////////////////////////////////////////////
// the_muppet_show
////////////////////////////////////////////////////////////////////////////////

void the_muppet_show ( void ) {
    while ( 1 ) {
        while ( i_have_no_idea ) {
            threads.yield();
        }

        inspiration.lock();
        dr_teeth::go_muppets( the_muppets );
        inspiration.unlock();
    }
}

////////////////////////////////////////////////////////////////////////////////
// setup
////////////////////////////////////////////////////////////////////////////////

void setup( void ) {
  adafruit_mcp_4728_driver::initialization_struct_t initialization_structs[ dr_teeth::k_dac_count ] = {
        adafruit_mcp_4728_driver::initialization_struct_t( &Wire1, 4 ),
        adafruit_mcp_4728_driver::initialization_struct_t( &Wire2, 8 ),
        adafruit_mcp_4728_driver::initialization_struct_t( &Wire,  6 )
    };

    the_muppets.initialize( initialization_structs );

    the_function_generator.setFrequency( LFO_FREQUENCY );
    the_function_generator.setAmplitude( 32 * 1024 - 1 );

    threads.addThread( the_muppet_show );
    threads.addThread( the_voice_from_beyond );
}

////////////////////////////////////////////////////////////////////////////////
// loop - just because it is required
////////////////////////////////////////////////////////////////////////////////

void loop(){threads.yield();}

// waka waka waka ...
