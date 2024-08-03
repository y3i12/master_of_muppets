#pragma once

#include "Arduino.h"
#include "muppet_clock.h"

uint32_t muppet_clock::global_time              = 0;
float    muppet_clock::global_time_f            = 0.0f;

uint32_t muppet_clock::tick_time                = 0;
uint32_t muppet_clock::last_tick_time           = 0;
uint32_t muppet_clock::last_tick_delta          = 0;

void muppet_clock::wait( uint32_t millis ) {
    delay( millis );
    tick( );
}

void muppet_clock::tiny_wait( uint32_t micros ) {
    delayMicroseconds( micros );
    tick( );
 }

uint32_t muppet_clock::tick( void ) {
    tick_time       = micros();
    last_tick_delta = tick_time - last_tick_time;
    last_tick_time  = tick_time;

    global_time_f  += last_tick_delta / 1000.0f;
    global_time    += (uint32_t)global_time_f;

    return tick_time;
}
