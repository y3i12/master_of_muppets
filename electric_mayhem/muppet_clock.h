#pragma once

#include <cstdint>

class muppet_clock {
public:
    muppet_clock( void ) {};

    // gets the global time - there is a specialization for float type, returning global_time_f
    template< typename T >
    static T what_time_is_it( void ) {
        return static_cast< time_t >( global_time );
    };

    static void wait(      uint32_t millis ) { delay( millis );             tick( ); }
    static void tiny_wait( uint32_t micros ) { delayMicroseconds( micros ); tick( ); }

    static uint32_t lap( void );
protected:
    static uint32_t tick( void );
    

    // global time is the incremental time in millis
    static uint32_t          global_time;
    static float             global_time_f;

    // TODO: refactor the timers into structures
    // internal micros counter to update the millis timer
    static uint32_t          tick_time;
    static uint32_t          last_tick_time;
    static uint32_t          last_tick_delta;

    // lap time is in micros
    static uint32_t          lap_time;
    static uint32_t          last_lap_time;
    static uint32_t          last_lap_delta;
};
