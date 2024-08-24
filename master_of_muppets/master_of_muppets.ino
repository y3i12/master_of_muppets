#include <Wire.h>

#include "master_of_muppets.hpp"
#include "electric_mayhem.h"
#include "adafruit_mcp_4728_driver.h"

#include "function_generator.h"
#include "muppet_clock.h"

//#define LFO_FREQUENCY 1         // in HZ. sinus functions in HZ * 10 - comment this line to disable lfo testing
//#define LFO_SHAPE     triangle  // triangle square stair sawtooth sinus sinusRectified sinusDiode trapezium1 trapezium2 heartBeat
//#define LFO_CHANNEL   10

//#define DEBUG_LED       13        // port to analogWrite the value of DEBUG_CHANNEL as intensity (lfo or serial) - comment this line to disable blinking
//#define DEBUG_LED_BLINK           // makes the led blink
//#define DEBUG_CHANNEL   2         // which channel should go to the DEBUG_LED - comment this line to disable intensity showing

function_generator                          the_function_generator;
electric_mayhem< adafruit_mcp_4728_driver > the_muppets;
static Threads::Mutex                       inspiration;

// HARDWARE ORGANIZATION IS CURRENTLY:
//
// +-----------------+
// |  2   3   0   1  | dac 1
// |                 |
// |                 |
// |  2           1  | dac 3 ( +8 )
// |                 |
// |  3           0  | dac 3 ( +8 )
// |                 |
// |                 |
// |  3   2   1   0  | dac 2 ( +4 )
// +-----------------+
// The following array remaps it to MIDI channels
// +-----------------+
// |  1   2   3   4  |
// |                 |
// |                 |
// |  5           6  |
// |                 |
// |  7           8  |
// |                 |
// |                 |
// |  9  10  11  12  |
// +-----------------+
uint8_t channel_map[] = {
// +-----------------+
      2,  3,  0,  1,    // dac 1
// |                 |
// |                 |
     10,          9,    // dac 3
// |                 |
     11,          8,    // dac 3
// |                 |
// |                 |
      7,  6,  5,  4,    // dac 2
// +-----------------+
};

////////////////////////////////////////////////////////////////////////////////
// Led status and blinking functions
////////////////////////////////////////////////////////////////////////////////
#if defined( DEBUG_LED ) || defined( DEBUG_CHANNEL )

static float    last_led_time = 0.0f;
static bool     led_status    = false;

void ublink( bool make_it_on = false ) {
  
    if ( last_led_time > muppet_clock::what_time_is_it< float >() ) {
        last_led_time = 0;
    }

    #if defined( DEBUG_LED_BLINK ) && defined( DEBUG_CHANNEL )
        if ( !led_status && make_it_on && ( muppet_clock::what_time_is_it< float >() - last_led_time > 50.0f  ) ) { 
            last_led_time = muppet_clock::what_time_is_it< float >(); 
            led_status = true;
            analogWrite( DEBUG_LED, 255 );  
        } else if ( led_status && ( muppet_clock::what_time_is_it< float >() - last_led_time > 50.0f  ) ) { 
            last_led_time = muppet_clock::what_time_is_it< float >(); 
            led_status = false; 
            analogWrite( DEBUG_LED, dr_teeth::output_buffer[ channel_map[ DEBUG_CHANNEL ] ] >> 8 ); 
        }
    #elif defined( DEBUG_LED_BLINK ) && defined( DEBUG_LED )
        if ( !led_status && make_it_on && ( muppet_clock::what_time_is_it< float >() - last_led_time > 50.0f  ) ) { 
            last_led_time = muppet_clock::what_time_is_it< float >(); 
            led_status = true;
            analogWrite( DEBUG_LED, 255 );  
        } else if ( led_status && ( muppet_clock::what_time_is_it< float >() - last_led_time > 50.0f  ) ) { 
            last_led_time = muppet_clock::what_time_is_it< float >(); 
            led_status = false; 
            analogWrite( DEBUG_LED, 0 ); 
        }
    #elif defined( DEBUG_LED ) && defined( DEBUG_CHANNEL )
        if ( !led_status && ( muppet_clock::what_time_is_it< float >() - last_led_time > 50.0f  ) ) { 
            last_led_time = muppet_clock::what_time_is_it< float >(); 
            led_status = true;
        } else if ( led_status && ( muppet_clock::what_time_is_it< float >() - last_led_time > 50.0f  ) ) { 
            last_led_time = muppet_clock::what_time_is_it< float >(); 
            led_status = false; 
            analogWrite( DEBUG_LED, dr_teeth::output_buffer[ channel_map[ DEBUG_CHANNEL ] ] >> 8 ); 
        }
    #endif
      
}
#endif

////////////////////////////////////////////////////////////////////////////////
// test_lfo
// Instead of receive serial data, outputs the LFO into dr_teeth's read buffer
////////////////////////////////////////////////////////////////////////////////

void test_lfo( void ) {
    #ifdef DEBUG_LED
        ublink(true);
    #endif

    float     time  = muppet_clock::what_time_is_it< float >() * 0.001f;
    uint16_t  value = the_function_generator.LFO_SHAPE( time ) + 32 * 1024;

    #ifdef LFO_CHANNEL
    dr_teeth::input_buffer[ channel_map[ LFO_CHANNEL ] ] = value;
    #else
    for ( uint8_t channel_index = 0; channel_index < dr_teeth::k_total_channels; ++channel_index ) {
        dr_teeth::input_buffer[ channel_index ]   = value;
    }
    #endif

    #ifdef DEBUG_LED
        ublink();
    #endif
}

////////////////////////////////////////////////////////////////////////////////
// midi_read
////////////////////////////////////////////////////////////////////////////////

void setChannelValue( uint8_t channel_index, int pitch ) {
    #ifdef DEBUG_LED
        ublink(true);
    #endif

    channel_index -= 1; // from 1..12 MIDI domain to 0..11 array domain
    if ( channel_index >= dr_teeth::k_dac_count ) {
        return;
    }

    channel_index                           = channel_map[ channel_index ]; // unscrambles order from HW index to a more visual organization
    dr_teeth::input_buffer[ channel_index ] = static_cast< uint16_t >( ( pitch + 8192 ) * 4 );

    #ifdef DEBUG_LED
        ublink();
    #endif
}

void midi_read( void ) {
    usbMIDI.read();
}

////////////////////////////////////////////////////////////////////////////////
// the_voice_from_beyond
////////////////////////////////////////////////////////////////////////////////

void the_voice_from_beyond ( void ) {
    while ( 1 ) {
        muppet_clock::tick();
        inspiration.lock();

        #ifdef LFO_FREQUENCY
            test_lfo();
        #else
            midi_read();
        #endif


        inspiration.unlock();
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

    usbMIDI.setHandlePitchChange( setChannelValue );

    threads.addThread( the_muppet_show );
    threads.addThread( the_voice_from_beyond );
}

////////////////////////////////////////////////////////////////////////////////
// loop - just because it is required
////////////////////////////////////////////////////////////////////////////////

void loop(){threads.yield();}

// waka waka waka ...
