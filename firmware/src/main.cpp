#include <Arduino.h>
#include <Wire.h>

#include "master_of_muppets.hpp"
#include "electric_mayhem.h"
#include "utils/scoped_lock.h"


#include "function_generator.h"
#include "muppet_clock.h"

// DMA Validation headers (always include for conditional compilation)
#include "dma_automatic_validation.h"
#include "dma_performance_validator.h"
#include "dma_error_handler.h"


#define MASTER_OF_MUPPETS_AD5593R
#define DENTAL_CHECK
// DMA operations are now always available via electric_mayhem
// Control DMA usage at runtime with set_dma_mode() - see setup() for configuration
// #define ENABLE_DMA_VALIDATION  // Enable comprehensive DMA validation system





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

// DMA Validation System Components - Using static storage to avoid heap allocation
#ifdef ENABLE_DMA_VALIDATION

// Static storage for validation objects (aligned properly)
static alignas(dma_diagnostics::dma_error_handler) 
    uint8_t g_error_handler_storage[sizeof(dma_diagnostics::dma_error_handler)];

static alignas(dma_validation::dma_performance_validator) 
    uint8_t g_perf_validator_storage[sizeof(dma_validation::dma_performance_validator)];

static alignas(dma_validation::dma_test_suite) 
    uint8_t g_test_suite_storage[sizeof(dma_validation::dma_test_suite)];

static alignas(dma_validation::dma_realtime_monitor) 
    uint8_t g_monitor_storage[sizeof(dma_validation::dma_realtime_monitor)];

static alignas(dma_validation::dma_automatic_validation) 
    uint8_t g_auto_validator_storage[sizeof(dma_validation::dma_automatic_validation)];

// Pointers to constructed objects
static dma_diagnostics::dma_error_handler*           g_error_handler           = nullptr;
static dma_validation::dma_performance_validator*    g_perf_validator          = nullptr;
static dma_validation::dma_test_suite*               g_test_suite              = nullptr;
static dma_validation::dma_realtime_monitor*         g_monitor                 = nullptr;
static dma_validation::dma_automatic_validation*     g_auto_validator          = nullptr;

static bool g_validation_mode_enabled = false;

#endif

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
// DMA Validation System Functions
////////////////////////////////////////////////////////////////////////////////

#ifdef ENABLE_DMA_VALIDATION

void initialize_dma_validation_system( void ) {
    Serial.println( "Initializing DMA Validation System..." );
    
    // Initialize error handler
    dma_diagnostics::dma_error_handler::error_config_t error_config;
    error_config.max_retry_attempts         = 3;
    error_config.retry_delay_base_ms        = 1;
    error_config.retry_delay_max_ms         = 10;
    error_config.enable_peripheral_reset    = true;
    error_config.enable_sync_fallback       = true;
    
    // Use placement new on static storage (no heap allocation)
    g_error_handler = new (g_error_handler_storage) 
        dma_diagnostics::dma_error_handler(error_config);
    
    // Initialize performance validator
    dma_validation::dma_performance_validator::test_config_t perf_config;
    perf_config.test_duration_ms              = 30000;
    perf_config.measurement_interval_ms       = 1000;
    perf_config.enable_stress_testing         = true;
    perf_config.enable_concurrent_testing     = true;
    perf_config.enable_error_injection        = true;
    perf_config.target_operations_per_second  = 1000;
    perf_config.max_acceptable_latency_us     = 1000;
    perf_config.thread_slice_limit_us         = 10;
    
    g_perf_validator = new (g_perf_validator_storage) 
        dma_validation::dma_performance_validator(perf_config);
    
    // Initialize test suite
    g_test_suite = new (g_test_suite_storage) 
        dma_validation::dma_test_suite(g_perf_validator, g_error_handler);
    
    // Initialize real-time monitor
    dma_validation::dma_realtime_monitor::monitor_config_t monitor_config;
    monitor_config.monitoring_interval_ms      = 5000;
    monitor_config.enable_automatic_alerts     = true;
    monitor_config.enable_performance_logging  = false; // Reduce overhead in main mode
    monitor_config.enable_constraint_checking  = true;
    monitor_config.alert_threshold_latency_us  = 2000;
    monitor_config.alert_threshold_error_rate  = 1.0f;
    
    g_monitor = new (g_monitor_storage) 
        dma_validation::dma_realtime_monitor(g_perf_validator, monitor_config);
    
    // Initialize automatic validation system
    dma_validation::dma_automatic_validation::validation_config_t val_config;
    val_config.current_phase                    = dma_validation::dma_automatic_validation::validation_phase_t::PHASE_1_IMMEDIATE;
    val_config.enable_automatic_progression     = false; // Manual control in main firmware
    val_config.enable_data_logging              = true;
    val_config.enable_serial_reporting          = true;
    val_config.enable_led_diagnostics           = true;
    val_config.enable_external_triggers         = false;
    val_config.enable_environmental_monitoring  = true;
    val_config.phase_duration_ms                = 3600000; // 1 hour
    val_config.test_interval_ms                 = 300000;  // 5 minutes between tests
    
    g_auto_validator = new (g_auto_validator_storage) 
        dma_validation::dma_automatic_validation(
            g_perf_validator, 
            g_test_suite, 
            g_monitor, 
            g_error_handler, 
            val_config
        );
    
    Serial.println( "DMA Validation System initialized successfully!" );
}

void start_dma_validation( void ) {
    if ( !g_auto_validator ) {
        Serial.println( "ERROR: Validation system not initialized!" );
        return;
    }
    
    Serial.println( "Starting DMA background validation..." );
    if ( g_auto_validator->start_validation() ) {
        Serial.println( "Validation started successfully!" );
    } else {
        Serial.println( "ERROR: Failed to start validation!" );
    }
}

void stop_dma_validation( void ) {
    if ( g_auto_validator && g_auto_validator->is_validation_active() ) {
        Serial.println( "Stopping DMA validation..." );
        g_auto_validator->stop_validation();
        Serial.println( "Validation stopped." );
    }
}

void handle_validation_commands( void ) {
    if ( !Serial.available( ) || !g_auto_validator ) {
        return;
    }
    
    char cmd = Serial.read( );
    
    switch ( cmd ) 
    {
        case 'v':
        case 'V':
            if ( g_validation_mode_enabled ) 
            {
                stop_dma_validation( );
                g_validation_mode_enabled = false;
                Serial.println( "DMA Validation disabled" );
            } 
            else 
            {
                g_validation_mode_enabled = true;
                start_dma_validation( );
                Serial.println( "DMA Validation enabled" );
            }
            break;
            
        case 'r':
        case 'R':
            if ( g_auto_validator ) 
            {
                Serial.println( "\n=== DMA VALIDATION STATUS ===" );
                g_auto_validator->print_validation_summary( );
                
                auto stats = g_auto_validator->get_statistics( );
                Serial.print( "Pass rate: " );
                Serial.print( (float)stats.total_tests_passed / (float)stats.total_tests_run * 100.0f );
                Serial.println( "%" );
            }
            break;
            
        case 's':
        case 'S':
            if ( g_auto_validator ) 
            {
                Serial.println( "\n=== CURRENT SYSTEM STATUS ===" );
                Serial.print( "DMA Mode: " );
                auto dma_mode = the_muppets.get_dma_mode();
                if (dma_mode == electric_mayhem< dac_driver_t >::dma_mode_t::ENABLED) {
                    Serial.println( "ENABLED (with fallback)" );
                } else if (dma_mode == electric_mayhem< dac_driver_t >::dma_mode_t::REQUIRED) {
                    Serial.println( "REQUIRED" );
                } else {
                    Serial.println( "DISABLED (sync only)" );
                }
                Serial.print( "Validation Active: " );
                Serial.println( g_validation_mode_enabled ? "YES" : "NO" );
                
                if ( g_monitor ) 
                {
                    Serial.print( "Performance Acceptable: " );
                    Serial.println( g_monitor->is_performance_acceptable() ? "YES" : "NO" );
                }
            }
            break;
            
        case 'h':
        case 'H':
        case '?':
            Serial.println( "\n=== DMA VALIDATION COMMANDS ===" );
            Serial.println( "v - Toggle validation on/off" );
            Serial.println( "r - Show validation results" );
            Serial.println( "s - Show system status" );
            Serial.println( "h - Show this help" );
            break;
    }
}

void cleanup_validation_system( void ) 
{
    // Call destructors explicitly (placement new cleanup)
    if ( g_auto_validator ) 
    {
        if ( g_auto_validator->is_validation_active( ) ) 
        {
            g_auto_validator->stop_validation( );
        }
        g_auto_validator->~dma_automatic_validation();
        g_auto_validator = nullptr;
    }
    
    if ( g_monitor ) 
    {
        if ( g_monitor->is_monitoring_active( ) ) 
        {
            g_monitor->stop_monitoring( );
        }
        g_monitor->~dma_realtime_monitor();
        g_monitor = nullptr;
    }
    
    if ( g_test_suite ) 
    {
        g_test_suite->~dma_test_suite();
        g_test_suite = nullptr;
    }
    
    if ( g_perf_validator ) 
    {
        g_perf_validator->~dma_performance_validator();
        g_perf_validator = nullptr;
    }
    
    if ( g_error_handler ) 
    {
        g_error_handler->~dma_error_handler();
        g_error_handler = nullptr;
    }
}

#endif // ENABLE_DMA_VALIDATION

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

    // Initialize DMA Validation System if enabled
    #ifdef ENABLE_DMA_VALIDATION
    Serial.begin( 115200 );
    delay( 1000 ); // Wait for Serial to initialize
    Serial.println( "\n========================================" );
    Serial.println( "MASTER OF MUPPETS - DMA VALIDATION MODE" );
    Serial.println( "========================================" );
    Serial.println( "DMA Mode: ENABLED" );
    Serial.println( "Validation System: AVAILABLE" );
    Serial.println( "Commands: v=toggle, r=results, s=status, h=help" );
    Serial.println( "========================================\n" );
    
    // Initialize but don't start validation automatically
    initialize_dma_validation_system();
    #endif
}

////////////////////////////////////////////////////////////////////////////////
// loop - just because it is required
////////////////////////////////////////////////////////////////////////////////

void loop( void ) 
{ 
    threads.yield( );
    
    // Handle DMA validation commands if enabled
    #ifdef ENABLE_DMA_VALIDATION
    handle_validation_commands( );
    #endif
}

// waka waka waka ...
