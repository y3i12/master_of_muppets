#include <Arduino.h>
#include <Wire.h>

#include "master_of_muppets.hpp"
#include "electric_mayhem.h"


#include "function_generator.h"
#include "muppet_clock.h"


#define MASTER_OF_MUPPETS_AD5993R
// #define DENTAL_CHECK





#ifdef DENTAL_CHECK

function_generator                          the_function_generator;

#define LFO_FREQUENCY   1000        // in HZ. sinus functions in HZ * 10 - comment this line to disable lfo testing
#define LFO_SHAPE       sinus       // triangle square stair sawtooth sinus sinusRectified sinusDiode trapezium1 trapezium2 heartBeat
// #define LFO_CHANNEL     0        // restricts the LFO to one channel - coment this line to send the LFO to all chanells

#define DEBUG_LED       LED_BUILTIN // port to analogWrite the value of DEBUG_CHANNEL as intensity (lfo or serial) - comment this line to disable blinking
#define DEBUG_LED_BLINK             // makes the led blink
#define DEBUG_CHANNEL   0           // which channel should go to the DEBUG_LED - comment this line to disable intensity showing
#endif






#ifdef MASTER_OF_MUPPETS_AD5993R
#include "drivers/rob_tillaart_ad_5993r.h"
using dac_driver_t = drivers::rob_tillaart_ad_5993r;
#endif

#ifdef MASTER_OF_MUPPETS_MCP4728
#include "drivers/adafruit_mcp_4728.h"
using dac_driver_t = drivers::adafruit_mcp_4728;
#endif




electric_mayhem< dac_driver_t > the_muppets;
static Threads::Mutex           inspiration;

// Direct channel indexing without remapping
// Channels are used directly as: DAC0[0,1,2,3], DAC1[4,5,6,7], DAC2[8,9,10,11]

////////////////////////////////////////////////////////////////////////////////
// Led status and blinking functions
////////////////////////////////////////////////////////////////////////////////
#if defined( DEBUG_LED ) || defined( DEBUG_CHANNEL )

static float last_led_time = 0.0f;
static bool  led_status    = false;

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
            analogWrite( DEBUG_LED, dr_teeth::output_buffer[ DEBUG_CHANNEL ] >> 8 ); 
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
            analogWrite( DEBUG_LED, dr_teeth::output_buffer[ DEBUG_CHANNEL ] >> 8 ); 
        }
    #endif
      
}
#endif

////////////////////////////////////////////////////////////////////////////////
// test_lfo
// Instead of receive serial data, outputs the LFO into dr_teeth's read buffer
////////////////////////////////////////////////////////////////////////////////

#if defined( LFO_FREQUENCY )
void test_lfo( void ) {
    #ifdef DEBUG_LED
        ublink(true);
    #endif

    float     time  = muppet_clock::what_time_is_it< float >() * dr_teeth::k_time_to_seconds_factor;
    uint16_t  value = the_function_generator.LFO_SHAPE( time ) + dr_teeth::k_audio_half_scale;

    #ifdef LFO_CHANNEL
    dr_teeth::input_buffer[ LFO_CHANNEL ] = value;
    #else
    for ( uint8_t channel_index = 0; channel_index < dr_teeth::k_total_channels; ++channel_index ) {
        dr_teeth::input_buffer[ channel_index ]   = value;
    }
    #endif

    #ifdef DEBUG_LED
        ublink();
    #endif
}
#endif

////////////////////////////////////////////////////////////////////////////////
// midi_read
////////////////////////////////////////////////////////////////////////////////

// callback for pitch change
void set_channel_value( uint8_t channel_index, int pitch ) {
    #ifdef DEBUG_LED
        ublink(true);
    #endif

    channel_index -= 1; // from 1-based MIDI domain to 0-based array domain
    if ( channel_index >= dr_teeth::k_total_channels ) {
        return;
    }
 
    // converts from from MIDI 14 bit to common framework 16 bit
    dr_teeth::input_buffer[ channel_index ] = static_cast< uint16_t >(
        min( pitch + dr_teeth::k_midi_pitch_zero_offset, dr_teeth::k_midi_pitch_14_bit_max ) * dr_teeth::k_midi_to_framework_scale 
    );

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
  dac_driver_t::initialization_struct_t initialization_structs[ dr_teeth::k_dac_count ] = {
        dac_driver_t::initialization_struct_t( &Wire2, 11 ),
        dac_driver_t::initialization_struct_t( &Wire1, 37 ),
    };

    the_muppets.initialize( initialization_structs );

    #ifdef LFO_FREQUENCY
        the_function_generator.setFrequency( LFO_FREQUENCY );
        the_function_generator.setAmplitude( dr_teeth::k_audio_half_scale - 1 );
    #endif

    usbMIDI.setHandlePitchChange( set_channel_value );
    threads.setSliceMicros( dr_teeth::k_thread_slice_micros );
    threads.addThread( the_muppet_show );
    threads.addThread( the_voice_from_beyond );
}

////////////////////////////////////////////////////////////////////////////////
// loop - just because it is required
////////////////////////////////////////////////////////////////////////////////

void loop( void ) { threads.yield( ); }

// waka waka waka ...
