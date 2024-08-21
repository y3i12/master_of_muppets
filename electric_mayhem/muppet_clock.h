#pragma once

#include <cstdint>

class muppet_clock {
public:
    muppet_clock( void ) {};

    template< typename T >
    static T what_time_is_it( void ) {
        return static_cast< T >( global_time_f );
    };
    static uint32_t tick( void );
protected:
    static float             global_time_f;

    static uint32_t          tick_time;
    static uint32_t          last_tick_time;
    static uint32_t          last_tick_delta;
};
