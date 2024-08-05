#pragma once

#include <cstdint>

#include "messages.h"

struct dr_teeth {
    static const uint8_t  k_dac_count        = 1;
    static const uint8_t  k_channels_per_dac = 4;
    static const uint8_t  k_total_channels   = k_dac_count * k_channels_per_dac;
    static const uint8_t  k_buffer_size      = sizeof( message_attribute_address_value_t ) * ( k_total_channels - 1 ) + sizeof( message_set_dac_value_t );
    static const uint16_t k_max_value        = 64 * 1024 - 1;

    static uint8_t  buffer[ k_buffer_size ];
    static uint8_t  buffer_pos;
    static uint16_t value_buffer[ k_total_channels ];

    static void     reset( void )        { buffer_pos = 0; message_t::instance->type = message_t::k_undefined; }
    static uint8_t  write( uint8_t val ) { return buffer[ buffer_pos++ ] = val; }
  
    static void muppet_is_doing_stuff( void ) { }

    template< typename T >
    static void     go_muppets( T& muppets ) {
        if ( message_t::k_set_dac_value == message_t::instance->type ) {

            message_attribute_address_value_t* message_address_value( &message_set_dac_value_t::instance->first_address_value );

            for ( uint8_t i = 0; i < message_set_dac_value_t::instance->count; ++i ) {
                message_attribute_address_value_t& addr_value_struct = message_address_value[ i ];
                value_buffer[ addr_value_struct.address ]  = addr_value_struct.value;
            }

            muppets.attention_please( );
            muppets.all_together( value_buffer );
            muppets.well_done( );
        }
    };

//protected:
    //static void statusLED( bool in_status ) {
    //    if ( !led_status && in_status && ( muppet_clock::what_time_is_it< uint32_t >() - last_led_time > 100 ) ) { 
    //        last_led_time = muppet_clock::what_time_is_it< uint32_t >( ); 
    //        led_status = true;  
    //        digitalWrite( STATUS_LED_PIN, HIGH ); 
    //    } 
    //    else if ( led_status && !in_status && ( muppet_clock::what_time_is_it< uint32_t >( ) - last_led_time > 50 ) ) {
    //        last_led_time = muppet_clock::what_time_is_it< uint32_t >( );
    //        led_status = false; 
    //        digitalWrite( STATUS_LED_PIN, LOW ); 
    //    }
    //}
    //
    //void ublink( void ) {
    //    statusLED( true );
    //    statusLED( false );
    //}
    //
    //static uint32_t last_led_time;
    //static bool     led_status;
};
