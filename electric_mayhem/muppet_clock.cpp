#include "Arduino.h"
#include "muppet_clock.h"

float    muppet_clock::global_time_f            = 0.0f;

uint32_t muppet_clock::tick_time                = 0;
uint32_t muppet_clock::last_tick_time           = 0;
uint32_t muppet_clock::last_tick_delta          = 0;

uint32_t muppet_clock::tick( void ) {
    tick_time       = micros();
    last_tick_delta = tick_time - last_tick_time;
    last_tick_time  = tick_time;

    global_time_f  += last_tick_delta / 1000.0f;

    if ( global_time_f > 1000000000.0f ) {
        global_time_f -= 1000000000.0f;
    }

    return tick_time;
}
