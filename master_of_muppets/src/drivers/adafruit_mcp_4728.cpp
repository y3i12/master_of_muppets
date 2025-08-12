#include <Arduino.h>
#include <Wire.h>

#include "TeensyThreads.h"

#include "drivers/adafruit_mcp_4728.h"

namespace drivers {

void adafruit_mcp_4728::initialize( const initialization_struct_t& initialization_struct ) {
    ldac_port   = initialization_struct.ldac_port;

    pinMode( ldac_port, OUTPUT );
    this->disable( );

    initialization_struct.wire->begin( );
    initialization_struct.wire->setClock( k_wire_clock );

    uint16_t retry = 0;
    while ( retry++ < 100 && !mcp.begin( MCP4728_I2CADDR_DEFAULT, initialization_struct.wire ) ) {
        threads.delay( 10 );
    }

    if ( retry < 100 ) {
        for ( uint8_t channel_index = 0; channel_index < adafruit_mcp_4728::k_channels; ++channel_index ) {
            mcp.setChannelValue( static_cast< MCP4728_channel_t >( channel_index ), 0 );
        }
    }
}

void adafruit_mcp_4728::enable( void ) {
    digitalWrite( ldac_port, HIGH );
}

void adafruit_mcp_4728::disable( void ) {
    digitalWrite( ldac_port, LOW );
}

void adafruit_mcp_4728::set_channel_value( uint8_t channel_index, value_t value ) {
    if ( channel_index >= adafruit_mcp_4728::k_channels ) {
        return;  // Invalid channel index
    }
    value = dac_value_rescale( value );
    mcp.setChannelValue( static_cast< MCP4728_channel_t >( channel_index ), value );
}

void adafruit_mcp_4728::set_all_channels_same_value( value_t value_for_all_channels ) {
    value_for_all_channels = dac_value_rescale( value_for_all_channels );
    mcp.fastWrite( value_for_all_channels, value_for_all_channels, value_for_all_channels, value_for_all_channels );
}

void adafruit_mcp_4728::set_values( value_t values[ adafruit_mcp_4728::k_channels ] ) {
    mcp.fastWrite( dac_value_rescale( values[ 0 ] ), 
                   dac_value_rescale( values[ 1 ] ), 
                   dac_value_rescale( values[ 2 ] ), 
                   dac_value_rescale( values[ 3 ] ) );
}

} // namespace drivers
