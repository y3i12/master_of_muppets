#pragma once

#include <windows.h>

#include "serial_port.h"
#include "slip_encoded_serial_port.h"

class serial_w32_driver {
public:
    serial_w32_driver( );
    ~serial_w32_driver( );

    bool open_port( const std::string& port_name, int timeout );
    bool close( void );
    int32_t write( const uint8_t* buffer, size_t len );
    int32_t read( uint8_t* buffer, size_t len );
    size_t available( void );
    void flush( void );
    static std::list<serial_device> get_devices( );


private:
    HANDLE com;
    DCB dcb;
    COMMTIMEOUTS timeouts;
};

typedef serial_port<serial_w32_driver>              serial_port_w32;
typedef slip_encoded_serial_port<serial_w32_driver> slip_encoded_serial_port_w32;