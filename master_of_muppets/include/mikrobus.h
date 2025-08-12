#pragma once

#include <SPI.h>
#include <Wire.h>
#include <HardwareSerial.h>

#define MIKROBUS_1_SPI        SPI1
#define MIKROBUS_1_I2C        Wire2
#define MIKROBUS_1_UART       Serial2

#define MIKROBUS_1_AN         23 // A9
#define MIKROBUS_1_RST        2
#define MIKROBUS_1_CS         0
#define MIKROBUS_1_SCK        27
#define MIKROBUS_1_MISO       1
#define MIKROBUS_1_MOSI       26
#define MIKROBUS_1_PWM        3
#define MIKROBUS_1_INT        4
#define MIKROBUS_1_RX         7
#define MIKROBUS_1_TX         8
#define MIKROBUS_1_SCL        24
#define MIKROBUS_1_SDA        25

#define MIKROBUS_2_SPI        SPI
#define MIKROBUS_2_I2C        Wire1
#define MIKROBUS_2_UART       Serial8

#define MIKROBUS_2_AN         22 // A8
#define MIKROBUS_2_RST        21
#define MIKROBUS_2_CS         37
#define MIKROBUS_2_SCK        13
#define MIKROBUS_2_MISO       12
#define MIKROBUS_2_MOSI       11
#define MIKROBUS_2_PWM        36
#define MIKROBUS_2_INT        33
#define MIKROBUS_2_RX         34
#define MIKROBUS_2_TX         35
#define MIKROBUS_2_SCL        16
#define MIKROBUS_2_SDA        17

namespace mikroe {

struct mikroBUS { };

#define define_mikroBUS( __bn__ )                                             \
struct mirkoBUS##__bn__ : public mikroBUS {                                   \
    static constexpr int             bus_number = __bn__;                     \
    static constexpr SPIClass&       spi        = MIKROBUS_##__bn__##_SPI;    \
    static constexpr TwoWire&        two_wire   = MIKROBUS_##__bn__##_I2C;    \
    static constexpr HardwareSerial& serial     = MIKROBUS_##__bn__##_UART;   \
                                                                              \
    struct pins {                                                             \
        static constexpr int analog             = MIKROBUS_##__bn__##_AN;     \
        static constexpr int reset              = MIKROBUS_##__bn__##_RST;    \
                                                                              \
        struct spi {                                                          \
            static constexpr int chip_select    = MIKROBUS_##__bn__##_CS;     \
            static constexpr int clock          = MIKROBUS_##__bn__##_SCK;    \
            static constexpr int miso           = MIKROBUS_##__bn__##_MISO;   \
            static constexpr int mosi           = MIKROBUS_##__bn__##_MOSI;   \
        };                                                                    \
                                                                              \
        static constexpr int pwm                = MIKROBUS_##__bn__##_PWM;    \
        static constexpr int interrupt          = MIKROBUS_##__bn__##_INT;    \
                                                                              \
        struct serial {                                                       \
            static constexpr int receive        = MIKROBUS_##__bn__##_RX;     \
            static constexpr int transmit       = MIKROBUS_##__bn__##_TX;     \
        };                                                                    \
        struct two_wire {                                                     \
            static constexpr int clock          = MIKROBUS_##__bn__##_SCL;    \
            static constexpr int data           = MIKROBUS_##__bn__##_SDA;    \
        };                                                                    \
    };                                                                        \
};

define_mikroBUS( 1 );
define_mikroBUS( 2 );

}; // namespace mikroe