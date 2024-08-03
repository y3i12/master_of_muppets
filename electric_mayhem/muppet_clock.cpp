#pragma once

#include "muppet_clock.h"

uint32_t muppet_clock::global_time              = 0;
float    muppet_clock::global_time_f            = 0.0f;

uint32_t muppet_clock::tick_time                = 0;
uint32_t muppet_clock::last_tick_time           = 0;
uint32_t muppet_clock::last_tick_delta          = 0;

uint32_t muppet_clock::lap_time                 = 0;
uint32_t muppet_clock::last_lap_time            = 0;
uint32_t muppet_clock::last_lap_delta           = 0;

template < float >
float muppet_clock::what_time_is_it( void ) {
    return global_time_f;
}

void muppet_clock::lap( void ) {
    lap_time        = tick( );
    last_lap_delta  = lap_time - last_lap_time;
    last_lap_time   = lap_time;

    return last_lap_delta;
}

uint32_t muppet_clock::tick( void ) {
    tick_time       = micros();
    last_tick_delta = tick_time - last_tick_time;
    last_tick_time  = tick_time;

    global_time_f  += last_tick_delta / 1000.0f;
    global_time    += (uint32_t)global_time_f;

    return tick_time;
}
