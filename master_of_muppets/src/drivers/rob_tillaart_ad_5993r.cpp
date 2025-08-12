#include <Arduino.h>
#include <Wire.h>

#include "TeensyThreads.h"

#include "drivers/rob_tillaart_ad_5993r.h"

namespace drivers {

void rob_tillaart_ad_5993r::initialize( const initialization_struct_t& initialization_struct ) {
    ldac_port   = initialization_struct.ldac_port;

    pinMode( ldac_port, OUTPUT );
    this->disable( );

    initialization_struct.wire->begin( );
    initialization_struct.wire->setClock( k_wire_clock );

    // Initialize AD5593R with default I2C address (0x10)
    ad5593r = AD5593R(0x10, initialization_struct.wire);
    
    uint16_t retry = 0;
    while ( retry++ < 100 && !ad5593r.begin() ) {
        threads.delay( 10 );
    }

    if ( retry < 100 ) {
        // Set all 8 channels to DAC mode
        ad5593r.setDACmode(0xFF);  // Set pins 0-7 as DAC
        
        // Initialize all 8 channels to 0
        for ( uint8_t channel_index = 0; channel_index < rob_tillaart_ad_5993r::k_channels; ++channel_index ) {
            ad5593r.writeDAC( channel_index, 0 );
        }
    }
}

void rob_tillaart_ad_5993r::enable( void ) {
    digitalWrite( ldac_port, HIGH );
}

void rob_tillaart_ad_5993r::disable( void ) {
    digitalWrite( ldac_port, LOW );
}

void rob_tillaart_ad_5993r::set_channel_value( uint8_t channel_index, value_t value ) {
    if ( channel_index >= rob_tillaart_ad_5993r::k_channels ) {
        return;  // Invalid channel index
    }
    value = dac_value_rescale( value );
    ad5593r.writeDAC( channel_index, value );
}

void rob_tillaart_ad_5993r::set_all_channels_same_value( value_t value_for_all_channels ) {
    value_for_all_channels = dac_value_rescale( value_for_all_channels );
    for ( uint8_t channel_index = 0; channel_index < rob_tillaart_ad_5993r::k_channels; ++channel_index ) {
        ad5593r.writeDAC( channel_index, value_for_all_channels );
    }
}

void rob_tillaart_ad_5993r::set_values( value_t values[ rob_tillaart_ad_5993r::k_channels ] ) {
    for ( uint8_t channel_index = 0; channel_index < rob_tillaart_ad_5993r::k_channels; ++channel_index ) {
        ad5593r.writeDAC( channel_index, dac_value_rescale( values[ channel_index ] ) );
    }
}

} // namespace drivers
