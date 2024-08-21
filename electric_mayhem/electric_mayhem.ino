#include <SLIPEncodedSerial.h>
#include <Wire.h>

#include "master_of_muppets.hpp"
#include "electric_mayhem.h"
#include "adafruit_mcp_4728_driver.h"

#include "function_generator.h"
#include "muppet_clock.h"


//#define LFO_FREQUENCY 1         // in HZ. sinus functions in HZ * 10 - comment this line to disable lfo testing
#define LFO_SHAPE     triangle  // triangle square stair sawtooth sinus sinusRectified sinusDiode trapezium1 trapezium2 heartBeat

// #define DEBUG_LED     13        // port to analogWrite the value of DEBUG_CHANNEL as intensity (lfo or serial) - comment this line to disable blinking
#define DEBUG_CHANNEL 0         // which channel should go to the DEBUG_LED - comment this line to disable intensity showing


_SLIPSerial< usb_serial_class >             SLIPSerial( thisBoardsSerialUSB );
function_generator                          the_function_generator;
electric_mayhem< adafruit_mcp_4728_driver > the_muppets;
static Threads::Mutex                       inspiration;

////////////////////////////////////////////////////////////////////////////////
// Led status and blinking functions
////////////////////////////////////////////////////////////////////////////////
static float    last_led_time = 0.0f;
static bool     led_status    = false;

#ifdef DEBUG_LED

void ublink( bool make_it_on = false ) {
  
    if ( last_led_time > muppet_clock::what_time_is_it< float >() ) {
        last_led_time = 0;
    }

    #if defined( DEBUG_LED ) && defined( DEBUG_CHANNEL )
        if ( !led_status && make_it_on && ( muppet_clock::what_time_is_it< float >() - last_led_time > 50.0f  ) ) { 
            last_led_time = muppet_clock::what_time_is_it< float >(); 
            led_status = true;
            analogWrite( DEBUG_LED, 255 );  
        } else if ( led_status && ( muppet_clock::what_time_is_it< float >() - last_led_time > 50.0f  ) ) { 
            last_led_time = muppet_clock::what_time_is_it< float >(); 
            led_status = false; 
            analogWrite( DEBUG_LED, dr_teeth::value_buffer[ DEBUG_CHANNEL ] >> 8 ); 
        }
    #elif defined( DEBUG_LED )
        if ( !led_status && make_it_on && ( muppet_clock::what_time_is_it< float >() - last_led_time > 50.0f  ) ) { 
            last_led_time = muppet_clock::what_time_is_it< float >(); 
            led_status = true;
            analogWrite( DEBUG_LED, 255 );  
        } else if ( led_status && ( muppet_clock::what_time_is_it< float >() - last_led_time > 50.0f  ) ) { 
            last_led_time = muppet_clock::what_time_is_it< float >(); 
            led_status = false; 
            analogWrite( DEBUG_LED, 0 ); 
        }
    #elif defined( DEBUG_CHANNEL )
        if ( !led_status && ( muppet_clock::what_time_is_it< float >() - last_led_time > 50.0f  ) ) { 
            last_led_time = muppet_clock::what_time_is_it< float >(); 
            led_status = true;
        } else if ( led_status && ( muppet_clock::what_time_is_it< float >() - last_led_time > 50.0f  ) ) { 
            last_led_time = muppet_clock::what_time_is_it< float >(); 
            led_status = false; 
            analogWrite( DEBUG_LED, dr_teeth::value_buffer[ DEBUG_CHANNEL ] >> 8 ); 
        }
    #endif
      
}
#endif

////////////////////////////////////////////////////////////////////////////////
// test_lfo
// Instead of receive serial data, outputs the LFO into dr_teeth's read buffer
////////////////////////////////////////////////////////////////////////////////

void test_lfo( void ) {
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
    if ( SLIPSerial.available() ) {
        while ( !SLIPSerial.endofPacket() ) {
            if ( SLIPSerial.available() ) {
                dr_teeth::write( SLIPSerial.read() );
            } else {
                threads.yield();
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
        muppet_clock::tick();
        inspiration.lock();

        #ifdef DEBUG_LED
            ublink(true);
        #endif

        #ifdef LFO_FREQUENCY
            test_lfo();
        #else
            serial_read();
        #endif


        inspiration.unlock();

        #ifdef DEBUG_LED
            ublink();
        #endif

    }
}

////////////////////////////////////////////////////////////////////////////////
// the_muppet_show
////////////////////////////////////////////////////////////////////////////////

void the_muppet_show ( void ) {
    while ( 1 ) {
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

    #ifdef LFO_FREQUENCY
        the_function_generator.setFrequency( LFO_FREQUENCY );
        the_function_generator.setAmplitude( 32 * 1024 - 1 );
    #endif

    threads.addThread( the_muppet_show );
    threads.addThread( the_voice_from_beyond );
}

////////////////////////////////////////////////////////////////////////////////
// loop - just because it is required
////////////////////////////////////////////////////////////////////////////////

void loop(){threads.yield();}

// waka waka waka ...
