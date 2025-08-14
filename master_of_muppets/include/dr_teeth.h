#pragma once

#include <cstdint>

struct dr_teeth {
    static constexpr uint8_t  k_dac_count                   = 2;
    static constexpr uint8_t  k_channels_per_dac            = 8;
    static constexpr uint8_t  k_total_channels              = k_dac_count * k_channels_per_dac;

    static constexpr uint16_t k_max_value                   = 64 * 1024 - 1;
    
    static constexpr int      k_thread_slice_micros         = 10;
    static const int          k_force_refresh_every_millis  = 100;

    static uint16_t           input_buffer[  k_total_channels ];
    static uint16_t           output_buffer[ k_total_channels ];
    
    template< typename T >
    static void     go_muppets( T& muppets ) {
        for ( uint8_t muppet_index = 0; muppet_index < k_dac_count; ++muppet_index ) {
            if ( muppets.attention_please( muppet_index ) ) {
                uint8_t starting_channel = muppet_index * T::k_channels_per_dac;

                memcpy( &output_buffer[ starting_channel ], &input_buffer[ starting_channel ], sizeof( uint16_t ) * T::k_channels_per_dac );

                muppets.throw_muppet_in_the_mud( muppet_index );
                muppets.thanks( muppet_index );
            }
        }
    };
};
