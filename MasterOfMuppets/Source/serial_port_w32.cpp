#include "serial_port_w32.h"

#include <sstream>
#include <iostream>

serial_w32_driver::serial_w32_driver( )
    : com( NULL )
    , dcb( { 0 } )
    , timeouts( { 0 } ) {
}


serial_w32_driver::~serial_w32_driver( ) {
    this->close( );
}

bool serial_w32_driver::open_port( const std::string& port_name, int timeout ) {
    this->close( );
    // OPEN_EXISTING || FILE_FLAG_OVERLAPPED?
    com = CreateFile( port_name.c_str( ), GENERIC_READ | GENERIC_WRITE, 0, 0, OPEN_EXISTING, 0, NULL );
    if ( com == INVALID_HANDLE_VALUE ) {
        WORD errorMessageID = ::GetLastError( );
        LPSTR messageBuffer = nullptr;
        size_t size = FormatMessageA( FORMAT_MESSAGE_ALLOCATE_BUFFER | FORMAT_MESSAGE_FROM_SYSTEM | FORMAT_MESSAGE_IGNORE_INSERTS, NULL, errorMessageID, MAKELANGID( LANG_NEUTRAL, SUBLANG_DEFAULT ), (LPSTR)&messageBuffer, 0, NULL );
        std::string message( messageBuffer, size );
        LocalFree( messageBuffer );
        this->close( );
        std::cout << message << std::endl;
        return false;
    }

    dcb.DCBlength = sizeof( dcb );
    GetCommState( com, &dcb );

    // 8N1 - Default Arduino parameters
    dcb.BaudRate = 480000000;
    dcb.ByteSize = 8;
    dcb.StopBits = ONESTOPBIT;
    dcb.Parity = NOPARITY;

    if ( !SetCommState( com, &dcb ) ) {
        this->close( );
        return false;
    }

    timeouts.ReadIntervalTimeout = timeout;
    timeouts.ReadTotalTimeoutConstant = timeout;
    timeouts.ReadTotalTimeoutMultiplier = 10;
    timeouts.WriteTotalTimeoutConstant = timeout;
    timeouts.WriteTotalTimeoutMultiplier = 10;

    if ( !SetCommTimeouts( com, &timeouts ) ) {
        this->close( );
        return false;
    }

    return true;
}

int32_t serial_w32_driver::write( const uint8_t* buffer, size_t len ) {
    DWORD nBytesWritten( -1 );

    if ( com ) {
        WriteFile( com, &buffer, len, &nBytesWritten, NULL );
    }

    return nBytesWritten;
}


int32_t serial_w32_driver::read( uint8_t* buffer, size_t len ) {
    DWORD nBytesRead( -1 );
    if ( com ) {
        ReadFile( com, buffer, len, &nBytesRead, NULL );
    }

    return nBytesRead;
}

bool serial_w32_driver::close( ) {
    if ( com ) {
        CloseHandle( com );
        com = NULL;
        return true;
    }
    return false;
}

size_t serial_w32_driver::available( void ) {
    // Device errors
    DWORD commErrors;
    // Device status
    COMSTAT commStatus;
    // Read status
    ClearCommError( com, &commErrors, &commStatus );
    // Return the number of pending bytes
    return commStatus.cbInQue;
}

std::list<serial_device> serial_w32_driver::get_devices( ) {
    std::list<serial_device> device_list;

    char lpTargetPath[5000];

    std::stringstream ss;

    for ( int i = 0; i < 255; i++ ) {
        ss.str( "" );
        ss.clear( );

        ss << "COM" << i;

        DWORD test = QueryDosDevice( ss.str( ).c_str( ), lpTargetPath, 5000 );

        if ( test != 0 ) {
            device_list.push_back( std::make_pair<>( ss.str( ), std::string( lpTargetPath ) ) );
        }
    }

    return device_list;
}
