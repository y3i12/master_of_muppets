#include "serial_port_libsp.h"

#include <iostream>
#include <sstream>

serial_libsp_driver::serial_libsp_driver( void )
    : port( 0 ) {
}


serial_libsp_driver::~serial_libsp_driver( void ) {
    this->close( );
}

bool serial_libsp_driver::open_port( const std::string& port_name, int timeout ) {
    this->close( );
    if ( sp_get_port_by_name( port_name.c_str( ), &port ) != SP_OK ) {
        return false;
    }

    if ( sp_open( port, SP_MODE_READ_WRITE ) != SP_OK ) {
        return false;
    }

    sp_set_baudrate( port, 480000000 );
    sp_set_bits( port, 8 );
    sp_set_parity( port, SP_PARITY_NONE );
    sp_set_stopbits( port, 1 );
    sp_set_flowcontrol( port, SP_FLOWCONTROL_NONE );

    return true;
}

int32_t serial_libsp_driver::write( const uint8_t* buffer, size_t len ) {
    if ( !port ) return -1;

    return sp_blocking_write( port, buffer, len, 0 );
    //return sp_nonblocking_write( port, buffer, len );
}


int32_t serial_libsp_driver::read( uint8_t* buffer, size_t len ) {
    if ( !port ) return -1;

    return sp_blocking_read( port, buffer, len, 0 );
    //return sp_nonblocking_read( port, buffer, len );
}

bool serial_libsp_driver::close( void ) {
    if ( !port ) { return false; }

    if ( port && sp_close( port ) != SP_OK ) {
        sp_free_port( port );
        port = 0;
        return false;
    }

    sp_free_port( port );
    port = 0;
    return true;
}

void serial_libsp_driver::flush( void ) {
    if ( !port ) return;

    sp_flush( port, SP_BUF_OUTPUT );
}

size_t serial_libsp_driver::available( void ) {
    if ( !port ) return 0;

    return sp_input_waiting( port );
}

std::list<serial_device> serial_libsp_driver::get_devices( ) {
    std::list<serial_device> device_list;
    struct sp_port** port_list;

    enum sp_return result = sp_list_ports( &port_list );
    if ( result != SP_OK ) {
        return device_list;
    }

    for ( uint32_t i = 0; port_list[i] != NULL; ++i ) {
        struct sp_port* port = port_list[i];
        std::stringstream ss;


        ss << sp_get_port_description( port )
            << ", Manufacturer: " << ( sp_get_port_usb_manufacturer( port ) ? sp_get_port_usb_manufacturer( port ) : "unknown" )
            << ", Product: " << ( sp_get_port_usb_product( port ) ? sp_get_port_usb_product( port ) : "unknown" )
            << ", Serial: " << ( sp_get_port_usb_serial( port ) ? sp_get_port_usb_serial( port ) : "unknown" );

        if ( sp_get_port_transport( port ) == SP_TRANSPORT_USB ) {
            device_list.push_back( serial_device( sp_get_port_name( port ), ss.str( ) ) );
        }
    }

    sp_free_port_list( port_list );

    return device_list;
}
