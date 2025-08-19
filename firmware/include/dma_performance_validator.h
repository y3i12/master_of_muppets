#pragma once

#include <cstdint>
#include "TeensyThreads.h"
#include "drivers/dma_i2c_hal.h"
#include "dma_error_handler.h"

namespace dma_validation {

/**
 * @brief Comprehensive performance validation and testing framework for DMA I2C
 * 
 * Provides real-time performance monitoring, constraint validation, and 
 * benchmarking capabilities for the Master of Muppets DMA implementation.
 */
class dma_performance_validator {
public:
    // Performance metrics structure
    struct performance_metrics_t {
        // Timing measurements (microseconds)
        uint32_t min_latency_us;
        uint32_t max_latency_us;
        uint32_t average_latency_us;
        uint32_t thread_slice_violations;
        uint32_t real_time_violations;
        
        // Throughput measurements
        uint32_t operations_per_second;
        uint32_t bytes_per_second;
        uint32_t concurrent_operations;
        
        // DMA vs Sync comparison
        uint32_t dma_operations_completed;
        uint32_t sync_operations_completed;
        uint32_t dma_time_saved_us;
        float dma_efficiency_percentage;
        
        // Threading metrics
        uint32_t mutex_contention_time_us;
        uint32_t thread_yield_count;
        uint32_t scheduling_jitter_us;
        
        // Error and reliability metrics
        uint32_t error_rate_ppm; // Parts per million
        uint32_t recovery_success_rate_percentage;
        uint32_t system_uptime_ms;
        
        performance_metrics_t() :
            min_latency_us( UINT32_MAX ), max_latency_us( 0 ), average_latency_us( 0 ),
            thread_slice_violations( 0 ), real_time_violations( 0 ),
            operations_per_second( 0 ), bytes_per_second( 0 ), concurrent_operations( 0 ),
            dma_operations_completed( 0 ), sync_operations_completed( 0 ), dma_time_saved_us( 0 ),
            dma_efficiency_percentage( 0.0f ), mutex_contention_time_us( 0 ), thread_yield_count( 0 ),
            scheduling_jitter_us( 0 ), error_rate_ppm( 0 ), recovery_success_rate_percentage( 100 ),
            system_uptime_ms( 0 ) {}
    };
    
    // Test configuration
    struct test_config_t {
        uint32_t test_duration_ms;
        uint32_t measurement_interval_ms;
        bool enable_stress_testing;
        bool enable_concurrent_testing;
        bool enable_error_injection;
        uint32_t target_operations_per_second;
        uint32_t max_acceptable_latency_us;
        uint32_t thread_slice_limit_us;
        
        test_config_t() :
            test_duration_ms( 30000 ), measurement_interval_ms( 1000 ),
            enable_stress_testing( false ), enable_concurrent_testing( true ),
            enable_error_injection( false ), target_operations_per_second( 1000 ),
            max_acceptable_latency_us( 1000 ), thread_slice_limit_us( 10 ) {}
    };
    
    // Real-time constraint validation
    struct constraint_status_t {
        bool latency_constraint_met;
        bool thread_slice_constraint_met;
        bool throughput_constraint_met;
        bool error_rate_constraint_met;
        bool overall_pass;
        
        constraint_status_t() :
            latency_constraint_met( true ), thread_slice_constraint_met( true ),
            throughput_constraint_met( true ), error_rate_constraint_met( true ),
            overall_pass( true ) {}
    };

private:
    // Measurement state
    struct measurement_state_t {
        uint32_t operation_count;
        uint32_t error_count;
        uint32_t last_measurement_time;
        uint32_t test_start_time;
        uint32_t total_latency_accumulator;
        uint32_t concurrent_operation_counter;
        bool measurement_active;
        
        measurement_state_t() :
            operation_count( 0 ), error_count( 0 ), last_measurement_time( 0 ),
            test_start_time( 0 ), total_latency_accumulator( 0 ), concurrent_operation_counter( 0 ),
            measurement_active( false ) {}
    };
    
    // Per-operation timing data
    struct operation_timing_t {
        uint32_t start_time_us;
        uint32_t end_time_us;
        bool is_dma_operation;
        uint8_t dac_index;
        drivers::dma_i2c_hal::error_code_t result;
    };
    
    performance_metrics_t metrics_;
    test_config_t config_;
    constraint_status_t constraints_;
    measurement_state_t state_;
    
    Threads::Mutex validator_mutex_;
    
    // Circular buffer for detailed timing analysis
    static const uint16_t TIMING_BUFFER_SIZE = 1000;
    operation_timing_t timing_buffer_[TIMING_BUFFER_SIZE];
    uint16_t timing_buffer_index_;
    
    // Stress testing state
    struct stress_test_state_t {
        bool active;
        uint32_t high_frequency_operations;
        uint32_t concurrent_bus_operations;
        uint32_t error_injection_count;
        
        stress_test_state_t() :
            active( false ), high_frequency_operations( 0 ),
            concurrent_bus_operations( 0 ), error_injection_count( 0 ) {}
    } stress_state_;
    
    // Internal methods
    void update_latency_statistics(uint32_t latency_us);
    void update_throughput_statistics();
    void validate_real_time_constraints();
    void record_operation_timing(const operation_timing_t& timing);
    void analyze_timing_patterns();
    
public:
    dma_performance_validator( const test_config_t& config = test_config_t() );
    ~dma_performance_validator();
    
    // Test control
    void start_performance_test();
    void stop_performance_test();
    bool is_test_active() const { return state_.measurement_active; }
    
    // Operation measurement interface
    void start_operation_measurement( uint8_t dac_index, bool is_dma_operation = true );
    void end_operation_measurement( uint8_t dac_index, drivers::dma_i2c_hal::error_code_t result );
    
    // Thread monitoring
    void record_thread_slice_usage( uint32_t slice_time_us );
    void record_mutex_contention( uint32_t contention_time_us );
    void record_thread_yield();
    
    // Real-time validation
    const constraint_status_t& validate_constraints();
    bool is_real_time_constraint_met() const;
    bool is_latency_acceptable( uint32_t latency_us ) const;
    
    // Stress testing
    void enable_stress_testing();
    void disable_stress_testing();
    void inject_error_scenario( uint8_t dac_index );
    
    // Metrics access
    const performance_metrics_t& get_current_metrics() const { return metrics_; }
    void reset_metrics();
    void update_metrics(); // Call periodically to refresh calculations
    
    // Reporting
    void print_performance_report() const;
    void print_constraint_validation() const;
    void print_timing_analysis() const;
    
    // Configuration
    void set_test_config( const test_config_t& config ) { config_ = config; }
    const test_config_t& get_test_config() const { return config_; }
    
    // Benchmarking utilities
    void benchmark_dma_vs_sync( uint32_t iterations = 100 );
    void benchmark_concurrent_operations( uint32_t concurrent_count = 2 );
    void benchmark_high_frequency_updates( uint32_t frequency_hz = 1000 );
};

/**
 * @brief Automated test suite for comprehensive DMA I2C validation
 * 
 * Provides pre-configured test scenarios for validation of DMA implementation.
 */
class dma_test_suite {
public:
    enum class test_scenario_t : uint8_t {
        BASIC_FUNCTIONALITY = 0,
        PERFORMANCE_BENCHMARK,
        STRESS_TEST,
        CONCURRENT_OPERATIONS,
        ERROR_RECOVERY,
        LONG_TERM_RELIABILITY,
        REAL_TIME_CONSTRAINTS
    };
    
    struct test_result_t {
        test_scenario_t scenario;
        bool passed;
        uint32_t duration_ms;
        uint32_t operations_completed;
        uint32_t errors_encountered;
        dma_performance_validator::performance_metrics_t metrics;
        const char* failure_reason;
        
        test_result_t() :
            scenario( test_scenario_t::BASIC_FUNCTIONALITY ), passed( false ),
            duration_ms( 0 ), operations_completed( 0 ), errors_encountered( 0 ),
            failure_reason( nullptr ) {}
    };

private:
    dma_performance_validator* validator_;
    dma_diagnostics::dma_error_handler* error_handler_;
    
    test_result_t results_[7]; // One for each test scenario
    uint8_t completed_tests_;
    
    // Individual test methods
    test_result_t test_basic_functionality();
    test_result_t test_performance_benchmark();
    test_result_t test_stress_test();
    test_result_t test_concurrent_operations();
    test_result_t test_error_recovery();
    test_result_t test_long_term_reliability();
    test_result_t test_real_time_constraints();

public:
    dma_test_suite( dma_performance_validator* validator, 
                   dma_diagnostics::dma_error_handler* error_handler );
    ~dma_test_suite();
    
    // Test execution
    bool run_all_tests();
    test_result_t run_single_test( test_scenario_t scenario );
    
    // Results access
    const test_result_t& get_test_result( test_scenario_t scenario ) const;
    uint8_t get_completed_test_count() const { return completed_tests_; }
    bool all_tests_passed() const;
    
    // Reporting
    void print_test_results() const;
    void print_summary() const;
    
    // Utility methods
    static const char* scenario_to_string( test_scenario_t scenario );
    static test_scenario_t string_to_scenario( const char* scenario_name );
};

/**
 * @brief Real-time performance monitor for continuous validation
 * 
 * Provides ongoing monitoring of DMA performance during normal operation.
 */
class dma_realtime_monitor {
public:
    struct monitor_config_t {
        uint32_t monitoring_interval_ms;
        bool enable_automatic_alerts;
        bool enable_performance_logging;
        bool enable_constraint_checking;
        uint32_t alert_threshold_latency_us;
        float alert_threshold_error_rate;
        
        monitor_config_t() :
            monitoring_interval_ms( 5000 ), enable_automatic_alerts( true ),
            enable_performance_logging( false ), enable_constraint_checking( true ),
            alert_threshold_latency_us( 2000 ), alert_threshold_error_rate( 1.0f ) {}
    };
    
    enum class alert_level_t : uint8_t {
        NONE = 0,
        INFO,
        WARNING,
        CRITICAL
    };
    
    struct performance_alert_t {
        uint32_t timestamp_ms;
        alert_level_t level;
        const char* message;
        uint32_t metric_value;
        uint32_t threshold_value;
    };

private:
    dma_performance_validator* validator_;
    monitor_config_t config_;
    
    volatile bool monitor_active_;
    Threads::Mutex monitor_mutex_;
    
    // Alert system
    performance_alert_t recent_alerts_[16];
    uint8_t alert_index_;
    uint8_t alert_count_;
    
    // Monitoring thread
    static void monitoring_thread( void* user_data );
    void check_performance_constraints();
    void generate_alert( alert_level_t level, const char* message, 
                       uint32_t metric_value = 0, uint32_t threshold_value = 0 );

public:
    dma_realtime_monitor( dma_performance_validator* validator,
                        const monitor_config_t& config = monitor_config_t() );
    ~dma_realtime_monitor();
    
    // Monitor control
    void start_monitoring();
    void stop_monitoring();
    bool is_monitoring_active() const { return monitor_active_; }
    
    // Alert access
    const performance_alert_t* get_recent_alerts( uint8_t& count ) const;
    alert_level_t get_highest_alert_level() const;
    void clear_alerts();
    
    // Configuration
    void set_config( const monitor_config_t& config ) { config_ = config; }
    const monitor_config_t& get_config() const { return config_; }
    
    // Status
    bool is_performance_acceptable() const;
    uint32_t get_time_since_last_alert() const;
};

} // namespace dma_validation