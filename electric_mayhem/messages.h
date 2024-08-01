#pragma once

#include <cstdint>

struct message_t {
    enum message_type {
        k_set_dac_value = '1',
        k_undefined = 255
    };

    static message_t* instance;
    uint8_t           type;

    message_t( uint8_t _type = message_type::k_undefined ) : type( _type ) {}
};

struct message_attribute_address_value_t {
    uint8_t  address;
    uint16_t value;

    message_attribute_address_value_t( uint8_t _address = 0, uint16_t _value = 0 )
        : address( _address ), value( _value ) {
    }
};

struct message_set_dac_value_t {
    static message_set_dac_value_t* instance;
    message_t                         message;
    uint8_t                           count;
    message_attribute_address_value_t first_address_value;

    message_set_dac_value_t( void ) : message( message_t::k_set_dac_value ), count( 0 ) {}
};
