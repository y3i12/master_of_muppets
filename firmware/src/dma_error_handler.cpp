#include <Arduino.h>
#include "dma_error_handler.h"
#include <cstring>

namespace dma_diagnostics {

// dma_error_handler implementation

dma_error_handler::dma_error_handler(const error_config_t& config) :
    log_write_index_(0),
    log_count_(0),
    config_(config),
    total_operations_(0),
    last_statistics_update_(0)
{
    // Initialize error log array
    for (uint8_t i = 0; i < MAX_ERROR_LOG_ENTRIES; ++i) {
        error_log_[i] = error_event_t();
    }
}

dma_error_handler::~dma_error_handler() {
    // Clean up any resources if needed
}

dma_error_handler::recovery_strategy_t dma_error_handler::handle_error(
    drivers::dma_i2c_hal::error_code_t error_code,
    uint8_t dac_index,
    uint8_t retry_count,
    uint32_t context_data) {
    
    if (dac_index >= 4) {
        dac_index = 0; // Clamp to valid range
    }
    
    // Create error event
    error_event_t event;
    event.timestamp_us = micros();
    event.error_code = error_code;
    event.dac_index = dac_index;
    event.retry_count = retry_count;
    event.context_data = context_data;
    event.severity = assess_error_severity(error_code, retry_count);
    event.recovery = determine_recovery_strategy(event);
    
    // Thread-safe logging and statistics update
    error_mutex_.lock();
    log_error_event(event);
    update_error_statistics(event);
    
    // Update recovery state
    recovery_state_.consecutive_errors[dac_index]++;
    recovery_state_.last_error_time[dac_index] = event.timestamp_us;
    error_mutex_.unlock();
    
    return event.recovery;
}

bool dma_error_handler::execute_recovery(const error_event_t& error_event) {
    switch (error_event.recovery) {
        case recovery_strategy_t::RETRY_IMMEDIATE:
            return retry_operation(error_event.dac_index, error_event.retry_count + 1);
            
        case recovery_strategy_t::RETRY_WITH_DELAY: {
            uint32_t delay_ms = calculate_retry_delay(error_event.retry_count);
            delay(delay_ms);
            return retry_operation(error_event.dac_index, error_event.retry_count + 1);
        }
        
        case recovery_strategy_t::FALLBACK_TO_SYNC:
            if (config_.enable_sync_fallback) {
                enable_sync_fallback(error_event.dac_index);
                error_mutex_.lock();
                statistics_.fallback_to_sync_count++;
                error_mutex_.unlock();
                return true;
            }
            return false;
            
        case recovery_strategy_t::RESET_PERIPHERAL:
            if (config_.enable_peripheral_reset && should_reset_peripheral(error_event.dac_index)) {
                reset_peripheral(error_event.dac_index);
                error_mutex_.lock();
                statistics_.peripheral_resets++;
                recovery_state_.peripheral_reset_count++;
                error_mutex_.unlock();
                return true;
            }
            return false;
            
        case recovery_strategy_t::SYSTEM_RESTART:
            // Log critical error and request system restart
            Serial.println(F("CRITICAL DMA ERROR: System restart required"));
            // In a production system, this might trigger a watchdog reset
            return false;
            
        case recovery_strategy_t::NONE:
        default:
            return false;
    }
}

bool dma_error_handler::retry_operation(uint8_t dac_index, uint8_t retry_count) {
    if (retry_count >= config_.max_retry_attempts) {
        return false;
    }
    
    // Reset consecutive error count on retry attempt
    error_mutex_.lock();
    recovery_state_.consecutive_errors[dac_index] = 0;
    error_mutex_.unlock();
    
    // The actual retry logic would be handled by the calling code
    // This just updates internal state
    return true;
}

void dma_error_handler::enable_sync_fallback(uint8_t dac_index) {
    if (dac_index < 4) {
        error_mutex_.lock();
        recovery_state_.fallback_mode[dac_index] = true;
        error_mutex_.unlock();
    }
}

void dma_error_handler::disable_sync_fallback(uint8_t dac_index) {
    if (dac_index < 4) {
        error_mutex_.lock();
        recovery_state_.fallback_mode[dac_index] = false;
        error_mutex_.unlock();
    }
}

bool dma_error_handler::is_sync_fallback_active(uint8_t dac_index) const {
    return (dac_index < 4) ? recovery_state_.fallback_mode[dac_index] : false;
}

void dma_error_handler::notify_success(uint8_t dac_index) {
    if (dac_index >= 4) return;
    
    error_mutex_.lock();
    // Reset consecutive error count on success
    recovery_state_.consecutive_errors[dac_index] = 0;
    
    // Re-enable DMA mode if in fallback (after some successful operations)
    if (recovery_state_.fallback_mode[dac_index]) {
        // Consider re-enabling DMA after a period of successful sync operations
        // This is a policy decision that could be configurable
        static uint32_t success_counter[4] = {0, 0, 0, 0};
        success_counter[dac_index]++;
        
        if (success_counter[dac_index] > 10) { // After 10 successful sync operations
            recovery_state_.fallback_mode[dac_index] = false;
            success_counter[dac_index] = 0;
        }
    }
    error_mutex_.unlock();
}

void dma_error_handler::increment_operation_count() {
    error_mutex_.lock();
    total_operations_++;
    
    // Update statistics periodically
    uint32_t current_time = millis();
    if (current_time - last_statistics_update_ > 1000) { // Every second
        update_statistics();
        last_statistics_update_ = current_time;
    }
    error_mutex_.unlock();
}

dma_error_handler::error_severity_t dma_error_handler::assess_error_severity(
    drivers::dma_i2c_hal::error_code_t error_code, uint8_t retry_count) {
    
    switch (error_code) {
        case drivers::dma_i2c_hal::error_code_t::SUCCESS:
            return error_severity_t::INFO;
            
        case drivers::dma_i2c_hal::error_code_t::BUSY:
            return (retry_count > 2) ? error_severity_t::WARNING : error_severity_t::INFO;
            
        case drivers::dma_i2c_hal::error_code_t::TIMEOUT:
            return (retry_count > 3) ? error_severity_t::ERROR : error_severity_t::WARNING;
            
        case drivers::dma_i2c_hal::error_code_t::NAK_RECEIVED:
            return (retry_count > 2) ? error_severity_t::ERROR : error_severity_t::WARNING;
            
        case drivers::dma_i2c_hal::error_code_t::ARBITRATION_LOST:
            return error_severity_t::WARNING; // Usually recoverable
            
        case drivers::dma_i2c_hal::error_code_t::DMA_ERROR:
            return (retry_count > 1) ? error_severity_t::CRITICAL : error_severity_t::ERROR;
            
        case drivers::dma_i2c_hal::error_code_t::INVALID_PARAMETER:
            return error_severity_t::CRITICAL; // Programming error
            
        case drivers::dma_i2c_hal::error_code_t::NOT_INITIALIZED:
            return error_severity_t::FATAL; // System configuration error
            
        default:
            return error_severity_t::ERROR;
    }
}

dma_error_handler::recovery_strategy_t dma_error_handler::determine_recovery_strategy(
    const error_event_t& error_event) {
    
    switch (error_event.error_code) {
        case drivers::dma_i2c_hal::error_code_t::BUSY:
            return (error_event.retry_count < 2) ? 
                recovery_strategy_t::RETRY_WITH_DELAY : recovery_strategy_t::FALLBACK_TO_SYNC;
                
        case drivers::dma_i2c_hal::error_code_t::TIMEOUT:
            if (error_event.retry_count < config_.max_retry_attempts) {
                return recovery_strategy_t::RETRY_WITH_DELAY;
            } else {
                return recovery_strategy_t::FALLBACK_TO_SYNC;
            }
            
        case drivers::dma_i2c_hal::error_code_t::NAK_RECEIVED:
            return (error_event.retry_count < 3) ? 
                recovery_strategy_t::RETRY_IMMEDIATE : recovery_strategy_t::FALLBACK_TO_SYNC;
                
        case drivers::dma_i2c_hal::error_code_t::ARBITRATION_LOST:
            return recovery_strategy_t::RETRY_WITH_DELAY;
            
        case drivers::dma_i2c_hal::error_code_t::DMA_ERROR:
            if (error_event.retry_count == 0) {
                return recovery_strategy_t::RETRY_IMMEDIATE;
            } else if (recovery_state_.consecutive_errors[error_event.dac_index] > 5) {
                return recovery_strategy_t::RESET_PERIPHERAL;
            } else {
                return recovery_strategy_t::FALLBACK_TO_SYNC;
            }
            
        case drivers::dma_i2c_hal::error_code_t::NOT_INITIALIZED:
        case drivers::dma_i2c_hal::error_code_t::INVALID_PARAMETER:
            return recovery_strategy_t::SYSTEM_RESTART;
            
        default:
            return recovery_strategy_t::FALLBACK_TO_SYNC;
    }
}

void dma_error_handler::log_error_event(const error_event_t& event) {
    error_log_[log_write_index_] = event;
    log_write_index_ = (log_write_index_ + 1) % MAX_ERROR_LOG_ENTRIES;
    
    if (log_count_ < MAX_ERROR_LOG_ENTRIES) {
        log_count_++;
    }
}

void dma_error_handler::update_error_statistics(const error_event_t& event) {
    statistics_.total_errors++;
    
    switch (event.error_code) {
        case drivers::dma_i2c_hal::error_code_t::TIMEOUT:
            statistics_.timeout_errors++;
            break;
        case drivers::dma_i2c_hal::error_code_t::NAK_RECEIVED:
            statistics_.nak_errors++;
            break;
        case drivers::dma_i2c_hal::error_code_t::DMA_ERROR:
            statistics_.dma_errors++;
            break;
        case drivers::dma_i2c_hal::error_code_t::ARBITRATION_LOST:
            statistics_.arbitration_errors++;
            break;
        default:
            break;
    }
}

void dma_error_handler::update_statistics() {
    if (total_operations_ > 0) {
        statistics_.error_rate_percentage = 
            (static_cast<float>(statistics_.total_errors) / total_operations_) * 100.0f;
    }
}

uint32_t dma_error_handler::calculate_retry_delay(uint8_t retry_count) {
    // Exponential backoff with jitter
    uint32_t delay = config_.retry_delay_base_ms << retry_count; // 2^retry_count
    delay = min(delay, config_.retry_delay_max_ms);
    
    // Add small random jitter (10% of delay)
    uint32_t jitter = delay / 10;
    if (jitter > 0) {
        delay += random(0, jitter);
    }
    
    return delay;
}

bool dma_error_handler::should_reset_peripheral(uint8_t dac_index) {
    if (dac_index >= 4) return false;
    
    // Reset if consecutive errors exceed threshold
    return recovery_state_.consecutive_errors[dac_index] > 10;
}

void dma_error_handler::reset_peripheral(uint8_t dac_index) {
    // Placeholder for peripheral reset logic
    // In actual implementation, this would reset the specific I2C peripheral
    Serial.print(F("Resetting I2C peripheral for DAC "));
    Serial.println(dac_index);
    
    // Reset consecutive error count
    recovery_state_.consecutive_errors[dac_index] = 0;
}

const dma_error_handler::error_event_t* dma_error_handler::get_error_log(uint8_t& count) const {
    count = log_count_;
    return error_log_;
}

const dma_error_handler::error_event_t& dma_error_handler::get_latest_error() const {
    if (log_count_ == 0) {
        static const error_event_t empty_event;
        return empty_event;
    }
    
    uint8_t latest_index = (log_write_index_ + MAX_ERROR_LOG_ENTRIES - 1) % MAX_ERROR_LOG_ENTRIES;
    return error_log_[latest_index];
}

bool dma_error_handler::has_critical_errors() const {
    // Check recent error log for critical or fatal errors
    for (uint8_t i = 0; i < log_count_; ++i) {
        if (error_log_[i].severity == error_severity_t::CRITICAL ||
            error_log_[i].severity == error_severity_t::FATAL) {
            return true;
        }
    }
    return false;
}

bool dma_error_handler::is_system_healthy() const {
    return statistics_.error_rate_percentage < config_.error_rate_threshold_percentage &&
           !has_critical_errors();
}

uint32_t dma_error_handler::get_time_since_last_error(uint8_t dac_index) const {
    if (dac_index >= 4 || recovery_state_.last_error_time[dac_index] == 0) {
        return UINT32_MAX; // No errors recorded
    }
    
    return micros() - recovery_state_.last_error_time[dac_index];
}

void dma_error_handler::reset_error_statistics() {
    error_mutex_.lock();
    statistics_ = error_statistics_t();
    total_operations_ = 0;
    recovery_state_ = recovery_state_t(); // Use assignment instead of memset
    log_count_ = 0;
    log_write_index_ = 0;
    error_mutex_.unlock();
}

const char* dma_error_handler::error_code_to_string(drivers::dma_i2c_hal::error_code_t error_code) const {
    return drivers::dma_i2c_hal::error_to_string(error_code);
}

const char* dma_error_handler::severity_to_string(error_severity_t severity) const {
    switch (severity) {
        case error_severity_t::INFO: return "INFO";
        case error_severity_t::WARNING: return "WARNING";
        case error_severity_t::ERROR: return "ERROR";
        case error_severity_t::CRITICAL: return "CRITICAL";
        case error_severity_t::FATAL: return "FATAL";
        default: return "UNKNOWN";
    }
}

const char* dma_error_handler::recovery_strategy_to_string(recovery_strategy_t strategy) const {
    switch (strategy) {
        case recovery_strategy_t::NONE: return "NONE";
        case recovery_strategy_t::RETRY_IMMEDIATE: return "RETRY_IMMEDIATE";
        case recovery_strategy_t::RETRY_WITH_DELAY: return "RETRY_WITH_DELAY";
        case recovery_strategy_t::FALLBACK_TO_SYNC: return "FALLBACK_TO_SYNC";
        case recovery_strategy_t::RESET_PERIPHERAL: return "RESET_PERIPHERAL";
        case recovery_strategy_t::SYSTEM_RESTART: return "SYSTEM_RESTART";
        default: return "UNKNOWN";
    }
}

// dma_timeout_watchdog implementation

dma_timeout_watchdog::dma_timeout_watchdog(dma_error_handler* error_handler, 
                                          const watchdog_config_t& config) :
    config_(config),
    error_handler_(error_handler),
    watchdog_active_(false)
{
}

dma_timeout_watchdog::~dma_timeout_watchdog() {
    stop_watchdog();
}

void dma_timeout_watchdog::start_operation_tracking(uint8_t dac_index) {
    if (dac_index >= 4) return;
    
    watchdog_mutex_.lock();
    trackers_[dac_index].operation_active = true;
    trackers_[dac_index].start_time_ms = millis();
    trackers_[dac_index].dac_index = dac_index;
    watchdog_mutex_.unlock();
}

void dma_timeout_watchdog::stop_operation_tracking(uint8_t dac_index) {
    if (dac_index >= 4) return;
    
    watchdog_mutex_.lock();
    if (trackers_[dac_index].operation_active) {
        uint32_t duration = millis() - trackers_[dac_index].start_time_ms;
        
        // Update statistics
        if (config_.enable_statistics) {
            if (duration > statistics_.max_operation_time_ms) {
                statistics_.max_operation_time_ms = duration;
            }
            
            // Simple moving average
            statistics_.average_operation_time_ms = 
                (statistics_.average_operation_time_ms + duration) / 2;
        }
        
        trackers_[dac_index].operation_active = false;
    }
    watchdog_mutex_.unlock();
}

bool dma_timeout_watchdog::is_operation_timeout(uint8_t dac_index) {
    if (dac_index >= 4) return false;
    
    watchdog_mutex_.lock();
    bool timeout = trackers_[dac_index].operation_active &&
                   (millis() - trackers_[dac_index].start_time_ms > config_.timeout_threshold_ms);
    watchdog_mutex_.unlock();
    
    return timeout;
}

void dma_timeout_watchdog::start_watchdog() {
    if (!watchdog_active_) {
        watchdog_active_ = true;
        threads.addThread(watchdog_thread, this);
    }
}

void dma_timeout_watchdog::stop_watchdog() {
    watchdog_active_ = false;
    // Note: TeensyThreads doesn't have a direct thread termination method
    // The thread will exit on next iteration
}

void dma_timeout_watchdog::watchdog_thread(void* user_data) {
    dma_timeout_watchdog* watchdog = static_cast<dma_timeout_watchdog*>(user_data);
    
    while (watchdog->watchdog_active_) {
        watchdog->check_timeouts();
        threads.delay(watchdog->config_.check_interval_ms);
    }
}

void dma_timeout_watchdog::check_timeouts() {
    uint32_t current_time = millis();
    
    for (uint8_t dac_index = 0; dac_index < 4; ++dac_index) {
        watchdog_mutex_.lock();
        bool timeout_detected = trackers_[dac_index].operation_active &&
            (current_time - trackers_[dac_index].start_time_ms > config_.timeout_threshold_ms);
        
        if (timeout_detected) {
            trackers_[dac_index].timeout_count++;
            statistics_.total_timeouts_detected++;
            
            if (config_.enable_auto_recovery && error_handler_) {
                // Report timeout to error handler
                dma_error_handler::recovery_strategy_t strategy = 
                    error_handler_->handle_error(drivers::dma_i2c_hal::error_code_t::TIMEOUT, 
                                               dac_index, 0, current_time);
                
                // Attempt recovery
                if (strategy != dma_error_handler::recovery_strategy_t::NONE) {
                    // Force stop the timed-out operation
                    trackers_[dac_index].operation_active = false;
                    
                    // The recovery will be handled by the error handler
                    dma_error_handler::error_event_t timeout_event;
                    timeout_event.timestamp_us = micros();
                    timeout_event.error_code = drivers::dma_i2c_hal::error_code_t::TIMEOUT;
                    timeout_event.severity = dma_error_handler::error_severity_t::ERROR;
                    timeout_event.recovery = strategy;
                    timeout_event.dac_index = dac_index;
                    timeout_event.retry_count = 0;
                    timeout_event.context_data = current_time;
                    
                    if (error_handler_->execute_recovery(timeout_event)) {
                        statistics_.successful_recoveries++;
                    } else {
                        statistics_.failed_recoveries++;
                    }
                }
            }
        }
        watchdog_mutex_.unlock();
    }
}

void dma_timeout_watchdog::reset_statistics() {
    watchdog_mutex_.lock();
    statistics_ = watchdog_statistics_t();
    watchdog_mutex_.unlock();
}

// dma_diagnostic_led implementation

dma_diagnostic_led::dma_diagnostic_led(uint8_t led_pin) :
    led_pin_(led_pin),
    current_pattern_(led_pattern_t::OFF),
    pattern_start_time_(0),
    last_update_time_(0),
    led_state_(false)
{
    pinMode(led_pin_, OUTPUT);
    digitalWrite(led_pin_, LOW);
}

dma_diagnostic_led::~dma_diagnostic_led() {
    digitalWrite(led_pin_, LOW);
}

void dma_diagnostic_led::set_pattern(led_pattern_t pattern) {
    if (pattern != current_pattern_) {
        current_pattern_ = pattern;
        pattern_start_time_ = millis();
        last_update_time_ = pattern_start_time_;
        led_state_ = false;
        update_led_state();
    }
}

void dma_diagnostic_led::update() {
    uint32_t current_time = millis();
    
    // Update at most every 10ms to avoid excessive processing
    if (current_time - last_update_time_ >= 10) {
        update_led_state();
        last_update_time_ = current_time;
    }
}

dma_diagnostic_led::pattern_timing_t dma_diagnostic_led::get_pattern_timing(led_pattern_t pattern) {
    pattern_timing_t timing;
    
    switch (pattern) {
        case led_pattern_t::OFF:
            timing = {1000, 0, 1, 0};
            break;
        case led_pattern_t::SOLID_ON:
            timing = {1000, 1000, 1, 0};
            break;
        case led_pattern_t::SLOW_BLINK:
            timing = {1000, 500, 1, 0};
            break;
        case led_pattern_t::FAST_BLINK:
            timing = {250, 125, 1, 0};
            break;
        case led_pattern_t::DOUBLE_BLINK:
            timing = {1000, 100, 2, 200};
            break;
        case led_pattern_t::TRIPLE_BLINK:
            timing = {1500, 100, 3, 150};
            break;
        case led_pattern_t::HEARTBEAT:
            timing = {1000, 50, 2, 100};
            break;
        case led_pattern_t::ERROR_PATTERN:
            timing = {2000, 200, 5, 200};
            break;
        case led_pattern_t::DMA_ACTIVE:
            timing = {100, 50, 1, 0};
            break;
        case led_pattern_t::SYNC_FALLBACK:
            timing = {500, 100, 1, 0};
            break;
        default:
            timing = {1000, 0, 1, 0};
            break;
    }
    
    return timing;
}

void dma_diagnostic_led::update_led_state() {
    pattern_timing_t timing = get_pattern_timing(current_pattern_);
    uint32_t elapsed = millis() - pattern_start_time_;
    uint32_t cycle_position = elapsed % timing.period_ms;
    
    bool should_be_on = false;
    
    if (timing.repeat_count == 1) {
        // Simple on/off pattern
        should_be_on = cycle_position < timing.on_time_ms;
    } else {
        // Repeated blink pattern
        uint32_t blink_cycle = timing.on_time_ms + timing.pause_time_ms;
        uint32_t total_blink_time = blink_cycle * timing.repeat_count;
        
        if (cycle_position < total_blink_time) {
            uint32_t blink_position = cycle_position % blink_cycle;
            should_be_on = blink_position < timing.on_time_ms;
        }
    }
    
    if (should_be_on != led_state_) {
        led_state_ = should_be_on;
        digitalWrite(led_pin_, led_state_ ? HIGH : LOW);
    }
}

void dma_diagnostic_led::indicate_dma_success() {
    set_pattern(led_pattern_t::SLOW_BLINK);
}

void dma_diagnostic_led::indicate_dma_error(drivers::dma_i2c_hal::error_code_t error_code) {
    set_pattern(led_pattern_t::ERROR_PATTERN);
}

void dma_diagnostic_led::indicate_sync_fallback() {
    set_pattern(led_pattern_t::SYNC_FALLBACK);
}

void dma_diagnostic_led::indicate_system_healthy() {
    set_pattern(led_pattern_t::HEARTBEAT);
}

void dma_diagnostic_led::indicate_critical_error() {
    set_pattern(led_pattern_t::FAST_BLINK);
}

} // namespace dma_diagnostics