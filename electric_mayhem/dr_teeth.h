#pragma once

#include <cstdint>

#include "messages.h"
//#include "muppet_clock.h"

struct dr_teeth {
    static const uint8_t k_dac_count        = 3;
    static const uint8_t k_channels_per_dac = 4;
    static const uint8_t k_total_channels   = k_dac_count * k_channels_per_dac;
    static const uint8_t k_buffer_size      = sizeof( message_attribute_address_value_t ) * ( k_total_channels - 1 ) + sizeof( message_set_dac_value_t );

    static uint8_t buffer[ k_buffer_size ];
    static uint8_t buffer_pos;

    static void    reset( void )        { buffer_pos = 0; message_t::instance->type = message_t::k_undefined; }
    static uint8_t write( uint8_t val ) { return buffer[ buffer_pos++ ] = val; }

  
    static void     muppet_is_doing_stuff( void ) { };

protected:
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
    //static uint32_t last_led_time;
    //static bool     led_status;

};

/*
__define_static_message_instance_member__( message_t );
__define_static_message_instance_member__( message_set_dac_value_t );
*/


void statusLED( bool in_status ) {
    if ( !led_status && in_status && ( global_time - last_led_time > 100 ) ) { last_led_time = global_time; led_status = true;  digitalWrite( STATUS_LED_PIN, HIGH ); } else if ( led_status && !in_status && ( global_time - last_led_time > 50 ) ) { last_led_time = global_time; led_status = false; digitalWrite( STATUS_LED_PIN, LOW ); }
}

void blink( uint8_t num = 5, int time = 250 ) {
    for ( uint8_t i = 0; i < num; ++i ) {
        digitalWrite( STATUS_LED_PIN, HIGH ); delay( time );
        digitalWrite( STATUS_LED_PIN, LOW ); delay( time );
    }
}

void ublink( void ) {
    statusLED( true );
    statusLED( false );
}