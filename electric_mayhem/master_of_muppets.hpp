#pragma once

#include "messages.h"
#include "dr_teeth.h"
#include "electric_mayhem.h"

uint8_t                     dr_teeth::buffer[ dr_teeth::k_buffer_size ] = { 0 };
uint8_t                     dr_teeth::buffer_pos                        = 0;

message_t*                  message_t::instance                         = reinterpret_cast< message_t*               >( dr_teeth::buffer );
message_set_dac_value_t*    message_set_dac_value_t::instance           = reinterpret_cast< message_set_dac_value_t* >( dr_teeth::buffer );
