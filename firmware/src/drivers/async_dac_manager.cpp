#include <Arduino.h>
#include <cstring>
#include "drivers/async_dac_manager.h"

namespace drivers {

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