#pragma once

#include <cstdint>
#include <Adafruit_MCP4728.h>

#include "dr_teeth.h"

class Wire;

class adafruit_mcp_4728_driver {
public:
    typedef uint16_t value_t;
    struct initialization_struct_t {
        initialization_struct_t( Wire* the_wire, uint8_t the_ldac_port ) : wire( the_wire ), ldac_port( the_ldac_port ) { }
        
        Wire*   wire;
        uint8_t ldac_port;
    };

    void initialize( const initialization_struct_t& initialization_struct );

    void enable( void );
    void disable( void );

    void set_channel_value( uint8_t channel_index, value_t value );
    void set_all_channels_same_value( value_t value_for_all_channels );
    void set_values( value_t values[ dr_teeth::k_channels_per_dac ] );

protected:
    Wire*               wire;
    uint8_t             ldac_port;
    Adafruit_MCP4728    mcp;
};
