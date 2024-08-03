#pragma once

#include <cstdint>

class muppet_clock {
public:
    muppet_clock( void ) {};

    template< typename T >
    static T what_time_is_it( void ) {
        return static_cast< T >( global_time_f );
    };

    static void wait(      uint32_t millis );
    static void tiny_wait( uint32_t micros );

    static uint32_t tick( void );
protected:
    

    // global time is the incremental time in millis
    static uint32_t          global_time;
    static float             global_time_f;

    // TODO: refactor the timers into structures
    // internal micros counter to update the millis timer
    static uint32_t          tick_time;
    static uint32_t          last_tick_time;
    static uint32_t          last_tick_delta;
};
