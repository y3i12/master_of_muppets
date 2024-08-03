#pragma once

#include <cstdint>
#include "messages.h"

struct dr_teeth {
  static const uint8_t k_dac_count        = 3;
  static const uint8_t k_channels_per_dac = 4;
  static const uint8_t k_total_channels   = k_dac_count * k_channels_per_dac;
  static const uint8_t k_buffer_size      = sizeof( message_attribute_address_value_t ) * ( k_total_channels - 1 ) + sizeof(message_set_dac_value_t);

  static uint8_t buffer[ k_buffer_size ];
  static uint8_t buffer_pos;

  static void    reset( void )        { buffer_pos = 0; message_t::instance->type = message_t::k_undefined; }
  static uint8_t write( uint8_t val ) { return buffer[ buffer_pos++ ] = val; }
};

/*
__define_static_message_instance_member__( message_t );
__define_static_message_instance_member__( message_set_dac_value_t );
*/