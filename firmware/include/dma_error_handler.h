#pragma once

#include <cstdint>
#include "drivers/dma_i2c_hal.h"
#include "TeensyThreads.h"

namespace dma_diagnostics {

/**
 * @brief Comprehensive error handling and diagnostic system for DMA I2C operations
 * 
 * Provides centralized error handling, recovery mechanisms, and diagnostic capabilities
 * for the Master of Muppets DMA I2C implementation.
 */
class dma_error_handler {
public:
    // Error severity levels
    enum class error_severity_t : uint8_t {
        INFO = 0,           // Informational, no action needed
        WARNING,            // Potential issue, monitor
        ERROR,              // Recoverable error, retry possible
        CRITICAL,           // Critical error, may require system restart
        FATAL               // Fatal error, system shutdown required
    };
    
    // Recovery strategies
    enum class recovery_strategy_t : uint8_t {
        NONE = 0,           // No recovery attempt
        RETRY_IMMEDIATE,    // Retry immediately
        RETRY_WITH_DELAY,   // Retry after delay
        FALLBACK_TO_SYNC,   // Fall back to synchronous operation
        RESET_PERIPHERAL,   // Reset I2C peripheral
        SYSTEM_RESTART      // Request system restart
    };
    
    // Error event structure
    struct error_event_t {
        uint32_t timestamp_us;
        drivers::dma_i2c_hal::error_code_t error_code;
        error_severity_t severity;
        recovery_strategy_t recovery;
        uint8_t dac_index;
        uint8_t retry_count;
        uint32_t context_data;
        
        error_event_t() :
            timestamp_us( 0 ), error_code( drivers::dma_i2c_hal::error_code_t::SUCCESS ),
            severity( error_severity_t::INFO ), recovery( recovery_strategy_t::NONE ),
            dac_index( 0 ), retry_count( 0 ), context_data( 0 ) {}
    };
    
    // Error statistics
    struct error_statistics_t {
        uint32_t total_errors;
        uint32_t timeout_errors;
        uint32_t nak_errors;
        uint32_t dma_errors;
        uint32_t arbitration_errors;
        uint32_t successful_recoveries;
        uint32_t failed_recoveries;
        uint32_t fallback_to_sync_count;
        uint32_t peripheral_resets;
        float error_rate_percentage;
        
        error_statistics_t() :
            total_errors( 0 ), timeout_errors( 0 ), nak_errors( 0 ), dma_errors( 0 ),
            arbitration_errors( 0 ), successful_recoveries( 0 ), failed_recoveries( 0 ),
            fallback_to_sync_count( 0 ), peripheral_resets( 0 ), error_rate_percentage( 0.0f ) {}
    };
    
    // Configuration for error handling behavior
    struct error_config_t {
        uint8_t max_retry_attempts;
        uint32_t retry_delay_base_ms;
        uint32_t retry_delay_max_ms;
        float error_rate_threshold_percentage;
        bool enable_peripheral_reset;
        bool enable_sync_fallback;
        uint32_t watchdog_timeout_ms;
        
        error_config_t() :
            max_retry_attempts( 3 ), retry_delay_base_ms( 1 ), retry_delay_max_ms( 100 ),
            error_rate_threshold_percentage( 5.0f ), enable_peripheral_reset( true ),
            enable_sync_fallback( true ), watchdog_timeout_ms( 1000 ) {}
    };

private:
    static const uint8_t MAX_ERROR_LOG_ENTRIES = 32;
    
    error_event_t error_log_[MAX_ERROR_LOG_ENTRIES];
    uint8_t log_write_index_;
    uint8_t log_count_;
    
    error_statistics_t statistics_;
    error_config_t config_;
    
    uint32_t total_operations_;
    uint32_t last_statistics_update_;
    
    Threads::Mutex error_mutex_;
    
    // Recovery state tracking
    struct recovery_state_t {
        uint8_t consecutive_errors[4];  // Per DAC error count
        uint32_t last_error_time[4];    // Per DAC last error timestamp
        bool fallback_mode[4];          // Per DAC sync fallback state
        uint32_t peripheral_reset_count;
        
        recovery_state_t() : peripheral_reset_count( 0 ) {
            for ( uint8_t i = 0; i < 4; ++i ) {
                consecutive_errors[i] = 0;
                last_error_time[i] = 0;
                fallback_mode[i] = false;
            }
        }
    } recovery_state_;
    
    // Internal helper methods
    error_severity_t assess_error_severity( drivers::dma_i2c_hal::error_code_t error_code, uint8_t retry_count );
    recovery_strategy_t determine_recovery_strategy( const error_event_t& error_event );
    void log_error_event( const error_event_t& event );
    void update_error_statistics( const error_event_t& event );
    uint32_t calculate_retry_delay( uint8_t retry_count );
    bool should_reset_peripheral( uint8_t dac_index );
    void reset_peripheral( uint8_t dac_index );

public:
    dma_error_handler( const error_config_t& config = error_config_t() );
    ~dma_error_handler();
    
    // Primary error handling interface
    recovery_strategy_t handle_error( drivers::dma_i2c_hal::error_code_t error_code,
                                    uint8_t dac_index,
                                    uint8_t retry_count = 0,
                                    uint32_t context_data = 0 );
    
    // Recovery execution
    bool execute_recovery( const error_event_t& error_event );
    bool retry_operation( uint8_t dac_index, uint8_t retry_count );
    void enable_sync_fallback( uint8_t dac_index );
    void disable_sync_fallback( uint8_t dac_index );
    bool is_sync_fallback_active( uint8_t dac_index ) const;
    
    // Operation success notification
    void notify_success( uint8_t dac_index );
    void increment_operation_count();
    
    // Statistics and monitoring
    const error_statistics_t& get_error_statistics() const { return statistics_; }
    void reset_error_statistics();
    void update_statistics();
    
    // Configuration management
    void set_config( const error_config_t& config ) { config_ = config; }
    const error_config_t& get_config() const { return config_; }
    
    // Diagnostic interface
    const error_event_t* get_error_log( uint8_t& count ) const;
    const error_event_t& get_latest_error() const;
    bool has_critical_errors() const;
    
    // Watchdog and health monitoring
    bool is_system_healthy() const;
    uint32_t get_time_since_last_error( uint8_t dac_index ) const;
    
    // Debug and diagnostic output
    void print_error_summary() const;
    void print_error_log() const;
    const char* error_code_to_string( drivers::dma_i2c_hal::error_code_t error_code ) const;
    const char* severity_to_string( error_severity_t severity ) const;
    const char* recovery_strategy_to_string( recovery_strategy_t strategy ) const;
};

/**
 * @brief Timeout watchdog for DMA operations
 * 
 * Provides timeout detection and automatic recovery for stuck DMA operations.
 */
class dma_timeout_watchdog {
public:
    struct watchdog_config_t {
        uint32_t timeout_threshold_ms;
        uint32_t check_interval_ms;
        bool enable_auto_recovery;
        bool enable_statistics;
        
        watchdog_config_t() :
            timeout_threshold_ms( 500 ), check_interval_ms( 100 ),
            enable_auto_recovery( true ), enable_statistics( true ) {}
    };
    
    struct watchdog_statistics_t {
        uint32_t total_timeouts_detected;
        uint32_t successful_recoveries;
        uint32_t failed_recoveries;
        uint32_t max_operation_time_ms;
        uint32_t average_operation_time_ms;
        
        watchdog_statistics_t() :
            total_timeouts_detected( 0 ), successful_recoveries( 0 ),
            failed_recoveries( 0 ), max_operation_time_ms( 0 ),
            average_operation_time_ms( 0 ) {}
    };

private:
    struct operation_tracker_t {
        bool operation_active;
        uint32_t start_time_ms;
        uint8_t dac_index;
        uint32_t timeout_count;
        
        operation_tracker_t() :
            operation_active( false ), start_time_ms( 0 ),
            dac_index( 0 ), timeout_count( 0 ) {}
    } trackers_[4]; // One per DAC
    
    watchdog_config_t config_;
    watchdog_statistics_t statistics_;
    dma_error_handler* error_handler_;
    
    Threads::Mutex watchdog_mutex_;
    volatile bool watchdog_active_;
    
    // Watchdog thread function
    static void watchdog_thread( void* user_data );
    void check_timeouts();

public:
    dma_timeout_watchdog( dma_error_handler* error_handler, 
                        const watchdog_config_t& config = watchdog_config_t() );
    ~dma_timeout_watchdog();
    
    // Operation tracking
    void start_operation_tracking( uint8_t dac_index );
    void stop_operation_tracking( uint8_t dac_index );
    bool is_operation_timeout( uint8_t dac_index );
    
    // Control
    void start_watchdog();
    void stop_watchdog();
    bool is_watchdog_active() const { return watchdog_active_; }
    
    // Statistics
    const watchdog_statistics_t& get_statistics() const { return statistics_; }
    void reset_statistics();
    
    // Configuration
    void set_config( const watchdog_config_t& config ) { config_ = config; }
    const watchdog_config_t& get_config() const { return config_; }
};

/**
 * @brief Diagnostic LED controller for visual error indication
 * 
 * Provides visual feedback for DMA operation status and errors using
 * built-in LED patterns.
 */
class dma_diagnostic_led {
public:
    enum class led_pattern_t : uint8_t {
        OFF = 0,            // LED off
        SOLID_ON,           // Solid on
        SLOW_BLINK,         // 1Hz blink
        FAST_BLINK,         // 4Hz blink
        DOUBLE_BLINK,       // Double blink pattern
        TRIPLE_BLINK,       // Triple blink pattern
        HEARTBEAT,          // Heartbeat pattern
        ERROR_PATTERN,      // Specific error indication
        DMA_ACTIVE,         // DMA operation in progress
        SYNC_FALLBACK       // Sync fallback active
    };

private:
    uint8_t led_pin_;
    led_pattern_t current_pattern_;
    uint32_t pattern_start_time_;
    uint32_t last_update_time_;
    bool led_state_;
    
    // Pattern timing parameters
    struct pattern_timing_t {
        uint32_t period_ms;
        uint32_t on_time_ms;
        uint8_t repeat_count;
        uint32_t pause_time_ms;
    };
    
    pattern_timing_t get_pattern_timing( led_pattern_t pattern );
    void update_led_state();

public:
    dma_diagnostic_led( uint8_t led_pin = LED_BUILTIN );
    ~dma_diagnostic_led();
    
    // Pattern control
    void set_pattern( led_pattern_t pattern );
    led_pattern_t get_pattern() const { return current_pattern_; }
    
    // Update method (should be called regularly)
    void update();
    
    // Convenience methods for common indications
    void indicate_dma_success();
    void indicate_dma_error( drivers::dma_i2c_hal::error_code_t error_code );
    void indicate_sync_fallback();
    void indicate_system_healthy();
    void indicate_critical_error();
};

} // namespace dma_diagnostics