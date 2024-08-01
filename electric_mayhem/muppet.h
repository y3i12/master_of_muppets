#pragma once

#include <cstdint>

template < typename dac_driver_t >
class muppet {
    typedef dac_driver_t::value_t     value_t;
    typedef dac_driver_t::dac_t       dac_t;
    typedef dac_driver_t::wire_t      wire_t;
public:
    muppet( wire_t* the_wire, uint8_t the_ldac_port ) : dac( the_wire, the_ldac_port ) { }

    void initialize( void ) { dac.initialize(); }

protected:
    dac_t    dac;


};