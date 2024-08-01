#pragma once

#include "serial/libserialport.h"


#include "serial_port.h"
#include "slip_encoded_serial_port.h"

class serial_libsp_driver {
public:
    serial_libsp_driver( );
    ~serial_libsp_driver( );

    bool open_port( const std::string& port_name, int timeout );
    bool close( );
    int32_t write( const uint8_t* buffer, size_t len );
    int32_t read( uint8_t* buffer, size_t len );
    size_t available( void );
    static std::list<serial_device> get_devices( );

private:
    struct sp_port* port;
};

typedef serial_port<serial_libsp_driver> serial_port_libsp;
typedef slip_encoded_serial_port<serial_libsp_driver> slip_encoded_serial_port_libsp;