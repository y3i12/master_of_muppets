#include <Arduino.h>
#include "drivers/dma_i2c_hal.h"
#include "TeensyThreads.h"
#include <Wire.h>

namespace drivers {

dma_i2c_hal::dma_i2c_hal() : initialized_(false) {
    reset_state();
}

dma_i2c_hal::~dma_i2c_hal() {
    if (initialized_) {
        deinit();
    }
}

dma_i2c_hal::error_code_t dma_i2c_hal::init(const dma_i2c_config_t& config) {
    if (initialized_) {
        return error_code_t::BUSY;
    }
    
    if (!config.wire_instance) {
        return error_code_t::INVALID_PARAMETER;
    }
    
    // Store configuration
    handle_.config = config;
    
    // Initialize I2C peripheral using Arduino Wire library
    config.wire_instance->begin();
    config.wire_instance->setClock(config.clock_frequency);
    
    // Start async worker thread for simulating DMA operations
    threads.addThread(async_worker_thread, this);
    
    initialized_ = true;
    handle_.state = transfer_state_t::IDLE;
    handle_.last_error = error_code_t::SUCCESS;
    
    return error_code_t::SUCCESS;
}

dma_i2c_hal::error_code_t dma_i2c_hal::deinit() {
    if (!initialized_) {
        return error_code_t::NOT_INITIALIZED;
    }
    
    // Abort any ongoing transfer
    if (handle_.state == transfer_state_t::DMA_IN_PROGRESS) {
        abort_transfer();
    }
    
    // Note: TeensyThreads doesn't have direct thread termination
    // The worker thread will exit when initialized_ is false
    
    initialized_ = false;
    reset_state();
    
    return error_code_t::SUCCESS;
}

dma_i2c_hal::error_code_t dma_i2c_hal::transfer_async(const dma_i2c_transfer_t& transfer,
                                                      dma_completion_callback_t callback,
                                                      void* user_data) {
    if (!initialized_) {
        return error_code_t::NOT_INITIALIZED;
    }
    
    if (handle_.state == transfer_state_t::DMA_IN_PROGRESS) {
        return error_code_t::BUSY;
    }
    
    if (!transfer.data_buffer || transfer.data_length == 0 || !callback) {
        return error_code_t::INVALID_PARAMETER;
    }
    
    // Store callback and user data
    handle_.callback = callback;
    handle_.user_data = user_data;
    handle_.transfer_start_time = micros();
    
    // Store transfer for async processing
    handle_.pending_transfer = transfer;
    handle_.async_operation_pending = true;
    handle_.async_operation_complete = false;
    
    // Update state before starting transfer
    handle_.state = transfer_state_t::DMA_IN_PROGRESS;
    handle_.last_error = error_code_t::SUCCESS;
    
    return error_code_t::SUCCESS;
}

bool dma_i2c_hal::is_transfer_complete() const {
    return handle_.state == transfer_state_t::COMPLETED || 
           handle_.state == transfer_state_t::ERROR_TIMEOUT ||
           handle_.state == transfer_state_t::ERROR_NAK ||
           handle_.state == transfer_state_t::ERROR_ARBITRATION ||
           handle_.state == transfer_state_t::ERROR_DMA_FAILURE;
}

dma_i2c_hal::error_code_t dma_i2c_hal::wait_for_completion(uint32_t timeout_ms) {
    if (!initialized_) {
        return error_code_t::NOT_INITIALIZED;
    }
    
    uint32_t timeout = timeout_ms ? timeout_ms : handle_.config.timeout_ms;
    uint32_t start_time = millis();
    
    while (handle_.state == transfer_state_t::DMA_IN_PROGRESS) {
        if (millis() - start_time > timeout) {
            handle_.state = transfer_state_t::ERROR_TIMEOUT;
            handle_.last_error = error_code_t::TIMEOUT;
            abort_transfer();
            return error_code_t::TIMEOUT;
        }
        yield(); // Allow other threads to run
    }
    
    return handle_.last_error;
}

dma_i2c_hal::error_code_t dma_i2c_hal::abort_transfer() {
    if (!initialized_) {
        return error_code_t::NOT_INITIALIZED;
    }
    
    if (handle_.state == transfer_state_t::DMA_IN_PROGRESS) {
        handle_.async_operation_pending = false;
        handle_.async_operation_complete = true;
        handle_.state = transfer_state_t::ERROR_DMA_FAILURE;
        handle_.last_error = error_code_t::DMA_ERROR;
        return error_code_t::SUCCESS;
    }
    
    return error_code_t::SUCCESS;
}

void dma_i2c_hal::async_worker_thread(void* user_data) {
    dma_i2c_hal* hal_instance = static_cast<dma_i2c_hal*>(user_data);
    
    while (hal_instance->initialized_) {
        if (hal_instance->handle_.async_operation_pending && !hal_instance->handle_.async_operation_complete) {
            // Perform the actual I2C transfer
            error_code_t result = hal_instance->perform_i2c_transfer(hal_instance->handle_.pending_transfer);
            
            // Update state based on transfer result
            if (result == error_code_t::SUCCESS) {
                hal_instance->handle_.state = transfer_state_t::COMPLETED;
                hal_instance->handle_.last_error = error_code_t::SUCCESS;
            } else {
                hal_instance->handle_.state = transfer_state_t::ERROR_DMA_FAILURE;
                hal_instance->handle_.last_error = result;
            }
            
            // Mark operation complete and call callback
            hal_instance->handle_.async_operation_complete = true;
            hal_instance->handle_.async_operation_pending = false;
            
            if (hal_instance->handle_.callback) {
                hal_instance->handle_.callback(hal_instance->handle_.state, 
                                              hal_instance->handle_.last_error,
                                              hal_instance->handle_.user_data);
            }
        }
        
        threads.yield();
        threads.delay(1); // Small delay to prevent busy waiting
    }
}

dma_i2c_hal::error_code_t dma_i2c_hal::perform_i2c_transfer(const dma_i2c_transfer_t& transfer) {
    TwoWire* wire = handle_.config.wire_instance;
    if (!wire) {
        return error_code_t::NOT_INITIALIZED;
    }
    
    uint8_t slave_addr = transfer.slave_address_override ? 
                        transfer.slave_address_override : handle_.config.slave_address;
    
    if (transfer.is_write_operation) {
        // Write operation
        wire->beginTransmission(slave_addr);
        
        // Write register address if specified
        if (transfer.register_address != 0) {
            wire->write(transfer.register_address);
        }
        
        // Write data
        for (size_t i = 0; i < transfer.data_length; ++i) {
            wire->write(transfer.data_buffer[i]);
        }
        
        uint8_t result = wire->endTransmission();
        
        switch (result) {
            case 0: return error_code_t::SUCCESS;
            case 2: return error_code_t::NAK_RECEIVED;
            case 3: return error_code_t::NAK_RECEIVED;
            case 4: return error_code_t::TIMEOUT;
            default: return error_code_t::DMA_ERROR;
        }
    } else {
        // Read operation
        if (transfer.register_address != 0) {
            // Write register address first
            wire->beginTransmission(slave_addr);
            wire->write(transfer.register_address);
            uint8_t write_result = wire->endTransmission(false); // Repeated start
            
            if (write_result != 0) {
                return error_code_t::NAK_RECEIVED;
            }
        }
        
        // Request data
        size_t bytes_received = wire->requestFrom(slave_addr, transfer.data_length);
        
        if (bytes_received != transfer.data_length) {
            return error_code_t::NAK_RECEIVED;
        }
        
        // Read received data
        for (size_t i = 0; i < transfer.data_length && wire->available(); ++i) {
            transfer.data_buffer[i] = wire->read();
        }
        
        return error_code_t::SUCCESS;
    }
}

bool dma_i2c_hal::is_transfer_timeout() {
    if (handle_.state != transfer_state_t::DMA_IN_PROGRESS) {
        return false;
    }
    
    uint32_t elapsed_time = micros() - handle_.transfer_start_time;
    return elapsed_time > (handle_.config.timeout_ms * 1000);
}

void dma_i2c_hal::reset_state() {
    handle_.state = transfer_state_t::IDLE;
    handle_.last_error = error_code_t::SUCCESS;
    handle_.callback = nullptr;
    handle_.user_data = nullptr;
    handle_.transfer_start_time = 0;
}

uint32_t dma_i2c_hal::get_transfer_duration_us() const {
    if (handle_.transfer_start_time == 0) {
        return 0;
    }
    return micros() - handle_.transfer_start_time;
}

const char* dma_i2c_hal::state_to_string(transfer_state_t state) {
    switch (state) {
        case transfer_state_t::IDLE: return "IDLE";
        case transfer_state_t::DMA_IN_PROGRESS: return "DMA_IN_PROGRESS";
        case transfer_state_t::COMPLETED: return "COMPLETED";
        case transfer_state_t::ERROR_TIMEOUT: return "ERROR_TIMEOUT";
        case transfer_state_t::ERROR_NAK: return "ERROR_NAK";
        case transfer_state_t::ERROR_ARBITRATION: return "ERROR_ARBITRATION";
        case transfer_state_t::ERROR_DMA_FAILURE: return "ERROR_DMA_FAILURE";
        default: return "UNKNOWN";
    }
}

const char* dma_i2c_hal::error_to_string(error_code_t error) {
    switch (error) {
        case error_code_t::SUCCESS: return "SUCCESS";
        case error_code_t::BUSY: return "BUSY";
        case error_code_t::TIMEOUT: return "TIMEOUT";
        case error_code_t::NAK_RECEIVED: return "NAK_RECEIVED";
        case error_code_t::ARBITRATION_LOST: return "ARBITRATION_LOST";
        case error_code_t::DMA_ERROR: return "DMA_ERROR";
        case error_code_t::INVALID_PARAMETER: return "INVALID_PARAMETER";
        case error_code_t::NOT_INITIALIZED: return "NOT_INITIALIZED";
        default: return "UNKNOWN";
    }
}

} // namespace drivers