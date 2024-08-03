#pragma once

#include "messages.h"
#include "muppet_clock.h"
#include "dr_teeth.h"
#include "electric_mayhem.h"

uint8_t                     dr_teeth::buffer[ dr_teeth::k_buffer_size ] = { 0 };
uint8_t                     dr_teeth::buffer_pos                        = 0;

//uint32_t                    dr_teeth::last_led_time                     = 0;
//bool                        dr_teeth::led_status                        = false;

message_t*                  message_t::instance                         = reinterpret_cast< message_t*               >( dr_teeth::buffer );
message_set_dac_value_t*    message_set_dac_value_t::instance           = reinterpret_cast< message_set_dac_value_t* >( dr_teeth::buffer );
