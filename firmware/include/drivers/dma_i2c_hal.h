#pragma once

#include <cstdint>
#include <cstddef>
#include <Arduino.h>
#include <Wire.h>
#include "TeensyThreads.h"

// Teensy 4.1 compatibility layer for DMA I2C
// Note: This is a simplified implementation for Arduino/Teensy environment
// Full MCUXpresso SDK would provide hardware DMA, this provides async simulation

namespace drivers {

/**
 * @brief DMA I2C Hardware Abstraction Layer for IMXRT1062
 * 
 * Provides asynchronous I2C operations using DMA for zero CPU overhead during transfers.
 * Designed for integration with Master of Muppets threading architecture.
 */
class dma_i2c_hal {
public:
    // Transfer states
    enum class transfer_state_t : uint8_t {
        IDLE = 0,
        DMA_IN_PROGRESS,
        COMPLETED,
        ERROR_TIMEOUT,
        ERROR_NAK,
        ERROR_ARBITRATION,
        ERROR_DMA_FAILURE
    };
    
    // Error codes for detailed error reporting
    enum class error_code_t : uint8_t {
        SUCCESS = 0,
        BUSY,
        TIMEOUT,
        NAK_RECEIVED,
        ARBITRATION_LOST,
        DMA_ERROR,
        INVALID_PARAMETER,
        NOT_INITIALIZED
    };
    
    // Completion callback function type
    typedef void (*dma_completion_callback_t)(transfer_state_t state, error_code_t error, void* user_data);
    
    // Configuration structure for DMA I2C setup
    struct dma_i2c_config_t {
        TwoWire* wire_instance;                // Wire instance (Wire, Wire1, Wire2)
        uint8_t dma_channel;                   // DMA channel number (0-31) - unused in compatibility mode
        uint32_t clock_frequency;              // I2C clock frequency (typically 400000)
        uint8_t slave_address;                 // Default slave address for this instance
        uint32_t timeout_ms;                   // Transfer timeout in milliseconds
        
        dma_i2c_config_t() :
            wire_instance(nullptr),
            dma_channel(0),
            clock_frequency(400000),
            slave_address(0x10),
            timeout_ms(100)
        {}
    };
    
    // Transfer descriptor for async operations
    struct dma_i2c_transfer_t {
        uint8_t* data_buffer;                  // Data buffer pointer
        size_t data_length;                    // Number of bytes to transfer
        uint8_t register_address;              // Target register address
        bool is_write_operation;               // true for write, false for read
        uint8_t slave_address_override;        // Override default slave address (0 = use default)
        void* completion_context;              // User data passed to callback
        
        dma_i2c_transfer_t() :
            data_buffer(nullptr),
            data_length(0),
            register_address(0),
            is_write_operation(true),
            slave_address_override(0),
            completion_context(nullptr)
        {}
    };

private:
    // Internal handle structure (Teensy compatibility version)
    struct dma_i2c_handle_t {
        dma_completion_callback_t callback;    // User completion callback
        volatile transfer_state_t state;       // Current transfer state
        error_code_t last_error;               // Last error encountered
        void* user_data;                       // User data for callback
        uint32_t transfer_start_time;          // Transfer start timestamp
        dma_i2c_config_t config;              // Configuration copy
        
        // Async simulation state
        volatile bool async_operation_pending;
        volatile bool async_operation_complete;
        dma_i2c_transfer_t pending_transfer;
        
        dma_i2c_handle_t() :
            callback(nullptr),
            state(transfer_state_t::IDLE),
            last_error(error_code_t::SUCCESS),
            user_data(nullptr),
            transfer_start_time(0),
            async_operation_pending(false),
            async_operation_complete(false)
        {}
    };
    
    dma_i2c_handle_t handle_;
    bool initialized_;
    
    // Async operation simulation thread
    static void async_worker_thread(void* user_data);
    
    // Perform actual I2C transfer
    error_code_t perform_i2c_transfer(const dma_i2c_transfer_t& transfer);
    
    // Timeout checking
    bool is_transfer_timeout();

public:
    dma_i2c_hal();
    ~dma_i2c_hal();
    
    // Initialization and configuration
    error_code_t init(const dma_i2c_config_t& config);
    error_code_t deinit();
    bool is_initialized() const { return initialized_; }
    
    // Asynchronous transfer operations
    error_code_t transfer_async(const dma_i2c_transfer_t& transfer, 
                               dma_completion_callback_t callback, 
                               void* user_data);
    
    // Status and control operations
    transfer_state_t get_transfer_state() const { return handle_.state; }
    error_code_t get_last_error() const { return handle_.last_error; }
    bool is_transfer_complete() const;
    error_code_t wait_for_completion(uint32_t timeout_ms = 0); // 0 = use configured timeout
    error_code_t abort_transfer();
    
    // Utility functions
    static const char* state_to_string(transfer_state_t state);
    static const char* error_to_string(error_code_t error);
    
    // Resource management
    void reset_state();
    uint32_t get_transfer_duration_us() const;
};

} // namespace drivers