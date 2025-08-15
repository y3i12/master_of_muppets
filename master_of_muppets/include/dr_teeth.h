#pragma once

#include <cstdint>

struct dr_teeth {
    static constexpr uint8_t  k_dac_count                   = 2;
    static constexpr uint8_t  k_channels_per_dac            = 8;
    static constexpr uint8_t  k_total_channels              = k_dac_count * k_channels_per_dac;

    static constexpr uint16_t k_max_value                   = 64 * 1024 - 1;
    
    static constexpr int      k_thread_slice_micros         = 10;
    static constexpr int      k_force_refresh_every_millis  = 100;

    // Audio/Signal Processing Constants
    static constexpr uint16_t k_audio_half_scale            = 32 * 1024;
    static constexpr float    k_time_to_seconds_factor      = 0.001f;
    static constexpr uint16_t k_midi_pitch_zero_offset      = 8192;   // from 0 - 8192, we have negative bend
    static constexpr uint16_t k_midi_pitch_14_bit_max       = 0x3FFF; // and from 8193 till k_midi_pitch_14_bit_max positive
    static constexpr uint8_t  k_midi_to_framework_scale     = 4;

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
