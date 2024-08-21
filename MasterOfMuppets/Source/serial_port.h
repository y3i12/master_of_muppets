#pragma once

#include <cstdint>
#include <list>

#include <string>

typedef std::pair<std::string, std::string> serial_device;

template <typename serial_driver>
class serial_port {
public:

    serial_port( void ) {}
    ~serial_port( void ) { driver.close( ); }

    bool open_port( const std::string& port_name, size_t timeout = 0 ) {
        return driver.open_port( port_name, static_cast<int>( timeout ) );
    };

    bool close( void ) {
        return driver.close( );
    }

    virtual int32_t write( const uint8_t* buffer, size_t len ) {
        return driver.write( buffer, len );
    }

    virtual int32_t read( uint8_t* buffer, size_t len ) {
        return driver.read( buffer, len );
    }

    template <typename T>
    int32_t write( const T& value ) {
        return write( reinterpret_cast<const uint8_t*>( &value ), sizeof( value ) );
    }

    template <typename T>
    int32_t read( T& value ) {
        return read( reinterpret_cast<uint8_t*>( &value ), sizeof( value ) );
    }

    template <typename T>
    size_t available( void ) {
        return driver.available( );
    }

    void flush( void ) {
        driver.flush( );
    }

    static std::list<serial_device> get_devices( ) {
        return serial_driver::get_devices( );
    }

protected:
    serial_driver driver;
};
