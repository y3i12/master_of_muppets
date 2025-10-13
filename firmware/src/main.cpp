#include <Arduino.h>
#include <Wire.h>

#include "master_of_muppets.hpp"
#include "electric_mayhem.h"
#include "utils/scoped_lock.h"


#include "function_generator.h"
#include "muppet_clock.h"

#define MASTER_OF_MUPPETS_AD5593R
// #define DENTAL_CHECK

#ifdef DENTAL_CHECK

function_generator                          the_function_generator;

// LFO Configuration - comment out LFO_ENABLED to use MIDI mode instead
// #define LFO_ENABLED
// #define LFO_CHANNEL_RESTRICT  0  // Uncomment to restrict LFO to one channel

// Debug LED Configuration  
#define DEBUG_LED_ENABLED
#define DEBUG_LED_BLINK_ENABLED

// Type-safe configuration constants (only active when features enabled)
namespace config {
    #ifdef LFO_ENABLED
    constexpr uint16_t lfo_frequency_hz = 1000;  // LFO frequency in Hz
    #endif
    
    #ifdef DEBUG_LED_ENABLED
    constexpr uint8_t debug_led_pin = LED_BUILTIN;
    constexpr uint8_t debug_channel = 0;  // Which channel to display on LED
    #endif
}

// For compatibility - LFO shape function selection
#ifdef LFO_ENABLED
#define LFO_SHAPE sinus  // triangle square stair sawtooth sinus sinusRectified sinusDiode trapezium1 trapezium2 heartBeat
#endif
#endif






#ifdef MASTER_OF_MUPPETS_AD5593R

#include "drivers/async_dac_manager.h"
#include "drivers/rob_tillaart_ad_5993r_async.h"
using dac_driver_t = drivers::rob_tillaart_ad_5993r_async;

// end of MASTER_OF_MUPPETS_AD5593R
#elif defined MASTER_OF_MUPPETS_MCP4728

// Note: MCP4728 does not currently support DMA operations
#include "drivers/adafruit_mcp_4728.h"
using dac_driver_t = drivers::adafruit_mcp_4728;

// end of MASTER_OF_MUPPETS_MCP4728
#else
#error "define a dac driver"
#endif




electric_mayhem< dac_driver_t > the_muppets;
static Threads::Mutex           inspiration;

// Direct channel indexing without remapping
// Channels are used directly as: DAC0[0,1,2,3], DAC1[4,5,6,7], DAC2[8,9,10,11]

////////////////////////////////////////////////////////////////////////////////
// Led status and blinking functions
////////////////////////////////////////////////////////////////////////////////
#ifdef DEBUG_LED_ENABLED

static float last_led_time = 0.0f;
static bool  led_status    = false;

void ublink( bool make_it_on = false ) {
  
    if ( last_led_time > muppet_clock::what_time_is_it< float >() ) {
        last_led_time = 0;
    }

    #if defined(DEBUG_LED_BLINK_ENABLED)
        if ( !led_status && make_it_on && ( muppet_clock::what_time_is_it< float >() - last_led_time > 50.0f  ) ) { 
            last_led_time = muppet_clock::what_time_is_it< float >(); 
            led_status = true;
            analogWrite(config::debug_led_pin, 255);  
        } else if ( led_status && ( muppet_clock::what_time_is_it< float >() - last_led_time > 50.0f  ) ) { 
            last_led_time = muppet_clock::what_time_is_it< float >(); 
            led_status = false; 
            analogWrite(config::debug_led_pin, dr_teeth::output_buffer[config::debug_channel] >> 8); 
        }
    #elif defined( DEBUG_LED_BLINK ) && defined( DEBUG_LED )
        if ( !led_status && make_it_on && ( muppet_clock::what_time_is_it< float >() - last_led_time > 50.0f  ) ) { 
            last_led_time = muppet_clock::what_time_is_it< float >(); 
            led_status = true;
            analogWrite(config::debug_led_pin, 255);  
        } else if ( led_status && ( muppet_clock::what_time_is_it< float >() - last_led_time > 50.0f  ) ) { 
            last_led_time = muppet_clock::what_time_is_it< float >(); 
            led_status = false; 
            analogWrite(config::debug_led_pin, 0); 
        }
    #elif defined( DEBUG_LED ) && defined( DEBUG_CHANNEL )
        if ( !led_status && ( muppet_clock::what_time_is_it< float >() - last_led_time > 50.0f  ) ) { 
            last_led_time = muppet_clock::what_time_is_it< float >(); 
            led_status = true;
        } else if ( led_status && ( muppet_clock::what_time_is_it< float >() - last_led_time > 50.0f  ) ) { 
            last_led_time = muppet_clock::what_time_is_it< float >(); 
            led_status = false; 
            analogWrite(config::debug_led_pin, dr_teeth::output_buffer[config::debug_channel] >> 8); 
        }
    #endif
      
}
#endif

////////////////////////////////////////////////////////////////////////////////
// test_lfo
// Instead of receive serial data, outputs the LFO into dr_teeth's read buffer
////////////////////////////////////////////////////////////////////////////////

#ifdef LFO_ENABLED
void test_lfo( void ) {
    #ifdef DEBUG_LED_ENABLED
        ublink(true);
    #endif

    float     time  = muppet_clock::what_time_is_it< float >() * dr_teeth::k_time_to_seconds_factor;
    uint16_t  value = the_function_generator.LFO_SHAPE( time ) + dr_teeth::k_audio_half_scale;

    #ifdef LFO_CHANNEL_RESTRICT
    dr_teeth::input_buffer[config::lfo_channel_restrict] = value;
    #else
    for ( uint8_t channel_index = 0; channel_index < dr_teeth::k_total_channels; ++channel_index ) {
        dr_teeth::input_buffer[ channel_index ]   = value;
    }
    #endif

    #ifdef DEBUG_LED_ENABLED
        ublink();
    #endif
}
#endif

////////////////////////////////////////////////////////////////////////////////
// midi_read
////////////////////////////////////////////////////////////////////////////////

// callback for pitch change
void set_channel_value( uint8_t channel_index, int pitch ) {
    #ifdef DEBUG_LED_ENABLED
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

    #ifdef DEBUG_LED_ENABLED
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
        
        {
            scoped_lock<Threads::Mutex> lock(inspiration);
            
            #ifdef LFO_ENABLED
                test_lfo();
            #else
                midi_read();
            #endif
        } // Automatic unlock here
    }
}

////////////////////////////////////////////////////////////////////////////////
// the_muppet_show
////////////////////////////////////////////////////////////////////////////////

void the_muppet_show ( void ) {
    while ( 1 ) {
        scoped_lock<Threads::Mutex> lock(inspiration);
        dr_teeth::go_muppets( the_muppets );
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

    // DMA channels for each DAC (0-31 available on Teensy 4.1)
    uint8_t dma_channels[ dr_teeth::k_dac_count ] = { 0, 1 };
    the_muppets.initialize( initialization_structs, dma_channels );
    
    // Set DMA mode (ENABLED allows fallback, REQUIRED fails if DMA unavailable, DISABLED for sync only)
    the_muppets.set_dma_mode( electric_mayhem< dac_driver_t >::dma_mode_t::ENABLED );

    #ifdef LFO_FREQUENCY
        the_function_generator.setFrequency(config::lfo_frequency_hz);
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

void loop( void ) 
{ 
    threads.yield( );
}

// waka waka waka ...
