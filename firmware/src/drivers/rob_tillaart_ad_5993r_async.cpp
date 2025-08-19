#include <Arduino.h>
#include <cstring>
#include "drivers/rob_tillaart_ad_5993r_async.h"

namespace drivers {

rob_tillaart_ad_5993r_async::rob_tillaart_ad_5993r_async() :
    rob_tillaart_ad_5993r(),
    async_status_(async_status_t::READY),
    current_callback_(nullptr),
    current_user_data_(nullptr),
    transfer_start_time_(0)
{
    memset(dma_write_buffer_, 0, sizeof(dma_write_buffer_));
}

rob_tillaart_ad_5993r_async::~rob_tillaart_ad_5993r_async() {
    if (async_status_ == async_status_t::IN_PROGRESS) {
        abort_async_operation();
    }
}

void rob_tillaart_ad_5993r_async::initialize_async(const initialization_struct_t& initialization_struct,
                                                   uint8_t dma_channel) {
    // First initialize the base synchronous driver
    rob_tillaart_ad_5993r::initialize(initialization_struct);
    
    // Configure DMA I2C HAL
    dma_i2c_hal::dma_i2c_config_t dma_config;
    
    // Use the Wire instance directly (Teensy compatibility mode)
    dma_config.wire_instance = initialization_struct.wire;
    dma_config.dma_channel = dma_channel;
    dma_config.clock_frequency = k_wire_clock;
    dma_config.slave_address = 0x10;  // AD5593R default address
    dma_config.timeout_ms = 100;
    
    // Initialize DMA HAL
    dma_i2c_hal::error_code_t result = dma_hal_.init(dma_config);
    if (result == dma_i2c_hal::error_code_t::SUCCESS) {
        set_async_status(async_status_t::READY);
    }
}

dma_i2c_hal::error_code_t rob_tillaart_ad_5993r_async::set_values_async(const value_t values[],
                                                                        async_completion_callback_t callback,
                                                                        void* user_data) {
    if (!is_async_mode_available()) {
        return dma_i2c_hal::error_code_t::NOT_INITIALIZED;
    }
    
    if (!callback || !values) {
        return dma_i2c_hal::error_code_t::INVALID_PARAMETER;
    }
    
    // Check if already busy
    async_mutex_.lock();
    if (async_status_ == async_status_t::IN_PROGRESS) {
        async_mutex_.unlock();
        return dma_i2c_hal::error_code_t::BUSY;
    }
    
    // Store callback and user data
    current_callback_ = callback;
    current_user_data_ = user_data;
    set_async_status(async_status_t::IN_PROGRESS);
    transfer_start_time_ = micros();
    async_mutex_.unlock();
    
    // Prepare DMA buffer for multi-channel write
    if (!prepare_dac_write_buffer(values, k_channels)) {
        set_async_status(async_status_t::ERROR_OCCURRED);
        return dma_i2c_hal::error_code_t::INVALID_PARAMETER;
    }
    
    // Setup DMA transfer
    dma_i2c_hal::dma_i2c_transfer_t transfer;
    transfer.data_buffer = dma_write_buffer_;
    transfer.data_length = k_channels * 3; // Each channel: register(1) + value(2)
    transfer.register_address = 0x00; // Starting register
    transfer.is_write_operation = true;
    transfer.slave_address_override = 0; // Use default
    transfer.completion_context = this;
    
    // Start async transfer
    dma_i2c_hal::error_code_t result = dma_hal_.transfer_async(transfer, 
                                                               dma_completion_callback, 
                                                               this);
    
    if (result != dma_i2c_hal::error_code_t::SUCCESS) {
        set_async_status(async_status_t::ERROR_OCCURRED);
        current_callback_ = nullptr;
        current_user_data_ = nullptr;
    }
    
    return result;
}

dma_i2c_hal::error_code_t rob_tillaart_ad_5993r_async::set_channel_value_async(uint8_t channel_index,
                                                                               value_t value,
                                                                               async_completion_callback_t callback,
                                                                               void* user_data) {
    if (channel_index >= k_channels) {
        return dma_i2c_hal::error_code_t::INVALID_PARAMETER;
    }
    
    // Create single-channel value array
    value_t single_value[k_channels];
    memset(single_value, 0, sizeof(single_value));
    single_value[channel_index] = value;
    
    // Use the multi-channel async method (could be optimized for single channel)
    return set_values_async(single_value, callback, user_data);
}

dma_i2c_hal::error_code_t rob_tillaart_ad_5993r_async::set_all_channels_same_value_async(value_t value_for_all_channels,
                                                                                         async_completion_callback_t callback,
                                                                                         void* user_data) {
    // Create array with same value for all channels
    value_t all_same_values[k_channels];
    for (uint8_t i = 0; i < k_channels; ++i) {
        all_same_values[i] = value_for_all_channels;
    }
    
    return set_values_async(all_same_values, callback, user_data);
}

rob_tillaart_ad_5993r_async::async_status_t rob_tillaart_ad_5993r_async::get_async_status() const {
    return async_status_;
}

bool rob_tillaart_ad_5993r_async::is_async_operation_complete() const {
    return async_status_ == async_status_t::COMPLETED || 
           async_status_ == async_status_t::ERROR_OCCURRED ||
           async_status_ == async_status_t::READY;
}

dma_i2c_hal::error_code_t rob_tillaart_ad_5993r_async::get_last_async_error() const {
    return dma_hal_.get_last_error();
}

dma_i2c_hal::error_code_t rob_tillaart_ad_5993r_async::wait_for_async_completion(uint32_t timeout_ms) {
    if (!is_async_mode_available()) {
        return dma_i2c_hal::error_code_t::NOT_INITIALIZED;
    }
    
    return dma_hal_.wait_for_completion(timeout_ms);
}

dma_i2c_hal::error_code_t rob_tillaart_ad_5993r_async::abort_async_operation() {
    if (!is_async_mode_available()) {
        return dma_i2c_hal::error_code_t::NOT_INITIALIZED;
    }
    
    dma_i2c_hal::error_code_t result = dma_hal_.abort_transfer();
    set_async_status(async_status_t::ERROR_OCCURRED);
    
    return result;
}

void rob_tillaart_ad_5993r_async::reset_async_statistics() {
    async_mutex_.lock();
    stats_ = async_stats_t();
    async_mutex_.unlock();
}

uint32_t rob_tillaart_ad_5993r_async::get_current_transfer_duration_us() const {
    if (transfer_start_time_ == 0) {
        return 0;
    }
    return micros() - transfer_start_time_;
}

bool rob_tillaart_ad_5993r_async::is_async_mode_available() const {
    return dma_hal_.is_initialized();
}

bool rob_tillaart_ad_5993r_async::try_lock_async_operation(uint32_t timeout_ms) {
    return async_mutex_.lock(timeout_ms);
}

void rob_tillaart_ad_5993r_async::unlock_async_operation() {
    async_mutex_.unlock();
}

void rob_tillaart_ad_5993r_async::dma_completion_callback(dma_i2c_hal::transfer_state_t state,
                                                          dma_i2c_hal::error_code_t error,
                                                          void* user_data) {
    rob_tillaart_ad_5993r_async* instance = static_cast<rob_tillaart_ad_5993r_async*>(user_data);
    
    if (!instance || !instance->current_callback_) {
        return;
    }
    
    // Calculate transfer duration
    uint32_t duration_us = instance->get_current_transfer_duration_us();
    
    // Update status based on result
    bool success = (state == dma_i2c_hal::transfer_state_t::COMPLETED);
    instance->set_async_status(success ? async_status_t::COMPLETED : async_status_t::ERROR_OCCURRED);
    
    // Update statistics
    instance->update_statistics(success, error, duration_us);
    
    // Call user callback
    instance->current_callback_(success, error, instance->current_user_data_);
    
    // Clear current operation
    instance->current_callback_ = nullptr;
    instance->current_user_data_ = nullptr;
}

void rob_tillaart_ad_5993r_async::update_statistics(bool success, dma_i2c_hal::error_code_t error, uint32_t duration_us) {
    async_mutex_.lock();
    
    stats_.total_operations++;
    
    if (success) {
        stats_.successful_operations++;
    } else {
        stats_.failed_operations++;
        
        // Track specific error types
        switch (error) {
            case dma_i2c_hal::error_code_t::TIMEOUT:
                stats_.timeout_errors++;
                break;
            case dma_i2c_hal::error_code_t::NAK_RECEIVED:
                stats_.nak_errors++;
                break;
            case dma_i2c_hal::error_code_t::DMA_ERROR:
            case dma_i2c_hal::error_code_t::ARBITRATION_LOST:
                stats_.dma_errors++;
                break;
            default:
                break;
        }
    }
    
    // Update timing statistics
    if (duration_us > stats_.max_transfer_time_us) {
        stats_.max_transfer_time_us = duration_us;
    }
    
    // Calculate rolling average (simple moving average)
    if (stats_.total_operations == 1) {
        stats_.average_transfer_time_us = duration_us;
    } else {
        stats_.average_transfer_time_us = (stats_.average_transfer_time_us * 7 + duration_us) / 8;
    }
    
    async_mutex_.unlock();
}

bool rob_tillaart_ad_5993r_async::prepare_dac_write_buffer(const value_t values[], uint8_t num_channels) {
    if (!values || num_channels > k_channels) {
        return false;
    }
    
    // Clear buffer
    memset(dma_write_buffer_, 0, sizeof(dma_write_buffer_));
    
    // Pack DAC write commands into buffer
    // AD5593R format: [register_addr][data_high][data_low] for each channel
    uint8_t buffer_index = 0;
    
    for (uint8_t channel = 0; channel < num_channels; ++channel) {
        value_t rescaled_value = dac_value_rescale(values[channel]);
        
        // AD5593R DAC register addresses start at 0x10 for channel 0
        dma_write_buffer_[buffer_index++] = 0x10 + channel;
        dma_write_buffer_[buffer_index++] = (rescaled_value >> 8) & 0xFF;
        dma_write_buffer_[buffer_index++] = rescaled_value & 0xFF;
    }
    
    return true;
}

void rob_tillaart_ad_5993r_async::set_async_status(async_status_t status) {
    // Atomic status update (assuming aligned writes are atomic on ARM)
    async_status_ = status;
}

// async_dac_manager implementation

async_dac_manager::async_dac_manager(rob_tillaart_ad_5993r_async* driver) :
    async_driver_(driver),
    next_operation_sequence_(1)
{
}

async_dac_manager::~async_dac_manager() {
    if (operation_state_.operation_pending) {
        force_operation_completion();
    }
}

bool async_dac_manager::initiate_async_update(const rob_tillaart_ad_5993r::value_t values[]) {
    if (!async_driver_ || !values) {
        return false;
    }
    
    // Check if already busy
    operation_state_.state_mutex.lock();
    if (operation_state_.operation_pending) {
        operation_state_.state_mutex.unlock();
        return false;
    }
    
    // Setup operation state
    operation_state_.operation_pending = true;
    operation_state_.operation_completed = false;
    operation_state_.last_error = dma_i2c_hal::error_code_t::SUCCESS;
    operation_state_.completion_sequence = next_operation_sequence_++;
    operation_state_.state_mutex.unlock();
    
    // Start async operation
    dma_i2c_hal::error_code_t result = async_driver_->set_values_async(values, 
                                                                       async_operation_callback, 
                                                                       this);
    
    if (result != dma_i2c_hal::error_code_t::SUCCESS) {
        // Operation failed to start, reset state
        operation_state_.state_mutex.lock();
        operation_state_.operation_pending = false;
        operation_state_.last_error = result;
        operation_state_.state_mutex.unlock();
        return false;
    }
    
    return true;
}

bool async_dac_manager::is_operation_pending() const {
    return operation_state_.operation_pending;
}

bool async_dac_manager::is_operation_completed() const {
    return operation_state_.operation_completed;
}

uint32_t async_dac_manager::get_completion_sequence() const {
    return operation_state_.completion_sequence;
}

dma_i2c_hal::error_code_t async_dac_manager::get_operation_result() {
    operation_state_.state_mutex.lock();
    dma_i2c_hal::error_code_t result = operation_state_.last_error;
    operation_state_.state_mutex.unlock();
    return result;
}

bool async_dac_manager::check_and_clear_completion(uint32_t expected_sequence) {
    operation_state_.state_mutex.lock();
    
    bool completed = operation_state_.operation_completed && 
                    operation_state_.completion_sequence == expected_sequence;
    
    if (completed) {
        // Clear completion state for next operation
        operation_state_.operation_pending = false;
        operation_state_.operation_completed = false;
    }
    
    operation_state_.state_mutex.unlock();
    return completed;
}

void async_dac_manager::reset_operation_state() {
    operation_state_.state_mutex.lock();
    operation_state_.operation_pending = false;
    operation_state_.operation_completed = false;
    operation_state_.last_error = dma_i2c_hal::error_code_t::SUCCESS;
    operation_state_.state_mutex.unlock();
}

bool async_dac_manager::has_operation_error() const {
    return operation_state_.last_error != dma_i2c_hal::error_code_t::SUCCESS;
}

void async_dac_manager::force_operation_completion() {
    if (async_driver_) {
        async_driver_->abort_async_operation();
    }
    reset_operation_state();
}

void async_dac_manager::async_operation_callback(bool success, dma_i2c_hal::error_code_t error, void* user_data) {
    async_dac_manager* manager = static_cast<async_dac_manager*>(user_data);
    
    if (!manager) {
        return;
    }
    
    // Update operation state
    manager->operation_state_.state_mutex.lock();
    manager->operation_state_.operation_completed = true;
    manager->operation_state_.last_error = success ? dma_i2c_hal::error_code_t::SUCCESS : error;
    manager->operation_state_.state_mutex.unlock();
}

} // namespace drivers