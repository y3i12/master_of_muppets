#pragma once

#include <cstdint>
#include <AD5593R.h>

#include "dr_teeth.h"

class TwoWire;

namespace drivers {

class rob_tillaart_ad_5993r {
public:
    const static uint32_t k_wire_clock = 400000L;
    const static uint16_t k_max_val    = 4095;
    const static uint8_t  k_channels   = 8;

    typedef uint16_t value_t;

    struct initialization_struct_t {
        initialization_struct_t( TwoWire* the_wire, uint8_t the_a0_port ) : 
            wire(    the_wire    ),
            a0_port( the_a0_port )
        { }
        
        TwoWire* wire;
        uint8_t  a0_port;
    };

    rob_tillaart_ad_5993r( void ) : wire( 0 ), ad5593r( 0x10 ) { }
    
    void initialize( const initialization_struct_t& initialization_struct );

    void enable( void );
    void disable( void );

    void set_channel_value( uint8_t channel_index, value_t value );
    void set_all_channels_same_value( value_t value_for_all_channels );
    void set_values( value_t values[ k_channels ] );

protected:
    TwoWire* wire;
    uint8_t  a0_port;
    AD5593R  ad5593r;

    inline value_t dac_value_rescale( value_t value ) { return static_cast< value_t >( static_cast< uint32_t >( value ) * k_max_val / dr_teeth::k_max_value ); }
};

} // namespace drivers
