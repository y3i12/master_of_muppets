#pragma once

#include "dr_teeth.h"

template < typename dac_driver_t > 
class electric_mayhem {
public:
    typedef typename dac_driver_t::value_t       value_t;
    typedef typename dac_driver_t::init_struct_t initialization_struct_t;

    electric_mayhem( void ) { };

    void initialize( const initialization_struct_t initialization_struct[ dr_teeth::k_dac_count ] );

    void attention_please( void );
    void attention_please( uint8_t dac_index );
    
    void one_handed_single_muppet_work( uint8_t dac_index, uint8_t channel_index, value_t value );

    void single_muppet_work( uint8_t dac_index, value_t value_for_all_channels );
    void single_muppet_work( uint8_t dac_index, value_t values[ dr_teeth::k_channels_per_dac ] );

    void all_together( value_t value_for_everyone );
    void all_together( value_t values_per_dac_and_channel[ dr_teeth::k_channels_per_dac * dr_teeth::k_dac_count ] );

    void well_done( void );
    void well_done( uint8_t dac_index );

protected:

    // global time and update time are in millis
    static uint32_t          global_time = 0;      // incremental time
    static float             global_time_f = 0.0f; // incremental time

    // loop time is in micros
    static uint32_t          loop_time                  = 0;
    static uint32_t          last_loop_time             = 0;
    static uint32_t          last_loop_delta            = 0;
    static uint16_t          global_time_accummulator   = 0;

    dac_driver_t muppets[dr_teeth::k_dac_count];

    inline bool vaid_dac(      uint8_t dac_index     ) { return dac_index     < dr_teeth::k_dac_count;        }
    inline bool valid_channel( uint8_t channel_index ) { return channel_index < dr_teeth::k_channels_per_dac; }
};

template < class dac_driver_t >
void electric_mayhem< dac_driver_t >::initialize( const initialization_struct_t initialization_struct[ dr_teeth::k_dac_count ] ) {
    for ( uint8_t dac_index = 0; dac_index < dr_teeth::k_dac_count; ++dac_index ) {
        muppets[ dac_index ].initialize( initialization_struct[ dac_index ] );
    }
}

template < class dac_driver_t >
void electric_mayhem< dac_driver_t >::attention_please( void ) {
    for ( uint8_t dac_index = 0; dac_index < dr_teeth::k_dac_count; ++dac_index ) {
        muppets[ dac_index ].enable( );
    }
}

template < class dac_driver_t >
void electric_mayhem< dac_driver_t >::attention_please( uint8_t dac_index ) {
    muppets[ dac_index ].enable( );
}

template < class dac_driver_t >
void electric_mayhem< dac_driver_t >::one_handed_single_muppet_work( uint8_t dac_index, uint8_t channel_index, value_t value ) {
    muppets[ dac_index ].set_channel_value( channel_index, value );
}

template < class dac_driver_t >
void electric_mayhem< dac_driver_t >::single_muppet_work( uint8_t dac_index, value_t value_for_all_channels ) {
    muppets[ dac_index ].set_all_channels_same_value( value_for_all_channels );
}

template < class dac_driver_t >
void electric_mayhem< dac_driver_t >::single_muppet_work( uint8_t dac_index, value_t values[ dr_teeth::k_channels_per_dac ] ) {
    muppets[ dac_index ].set_values( values );
}

template < class dac_driver_t >
void electric_mayhem< dac_driver_t >::all_together( value_t value_for_everyone ) {
    for ( uint8_t dac_index = 0; dac_index < dr_teeth::k_dac_count; ++dac_index ) {
        muppets[ dac_index ].set_all_channels_same_value( value_for_everyone );
    }
}

template < class dac_driver_t >
void electric_mayhem< dac_driver_t >::all_together( value_t values_per_dac_and_channel[ dr_teeth::k_channels_per_dac * dr_teeth::k_dac_count ] ) {
    for ( uint8_t dac_index = 0; dac_index < dr_teeth::k_dac_count; ++dac_index ) {
        muppets[ dac_index ].set_values( &values_per_dac_and_channel[ dac_index * dr_teeth::k_channels_per_dac ] );
    }
}

template < class dac_driver_t >
void electric_mayhem< dac_driver_t >::well_done( void ) {
    for ( uint8_t dac_index = 0; dac_index < dr_teeth::k_dac_count; ++dac_index ) {
        muppets[ dac_index ].disable( );
    }
}

template < class dac_driver_t >
void electric_mayhem< dac_driver_t >::well_done( uint8_t dac_index ) {
    muppets[ dac_index ].disable( );
}


