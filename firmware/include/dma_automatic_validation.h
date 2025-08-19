#pragma once

#include <cstdint>
#include <cstring>
#include "TeensyThreads.h"
#include "dma_performance_validator.h"
#include "dma_error_handler.h"
#include "drivers/dma_i2c_hal.h"
#include "SD.h"

namespace dma_validation {

/**
 * @brief Comprehensive automatic DMA validation system
 * 
 * Implements the three-phase validation methodology with automatic test execution,
 * external hardware integration, and comprehensive data logging capabilities.
 * Based on Season 04 DMA Hardware Testing Plan Knowledge Base.
 */
class dma_automatic_validation {
public:
    // Validation phases as per knowledge base
    enum class validation_phase_t : uint8_t {
        PHASE_1_IMMEDIATE = 0,    // 1-2 weeks: Leverage existing test infrastructure
        PHASE_2_ADVANCED,          // 2-4 weeks: Professional equipment integration
        PHASE_3_PRODUCTION        // 1-2 weeks: Production test procedures
    };
    
    // Test categories for Phase 1
    enum class phase1_test_t : uint8_t {
        BASIC_FUNCTIONALITY = 0,
        STRESS_TESTING,
        CONCURRENT_OPERATIONS,
        PERFORMANCE_BASELINE,
        ERROR_INJECTION,
        LONG_TERM_STABILITY
    };
    
    // Test categories for Phase 2 (requires external equipment)
    enum class phase2_test_t : uint8_t {
        TIMING_ANALYSIS = 0,
        PERFORMANCE_MEASUREMENT,
        SIGNAL_INTEGRITY,
        ENVIRONMENTAL_STRESS,
        EMC_COMPLIANCE,
        POWER_EFFICIENCY
    };
    
    // Test categories for Phase 3
    enum class phase3_test_t : uint8_t {
        PRODUCTION_TESTING = 0,
        FIELD_DIAGNOSTICS,
        CALIBRATION_PROCEDURES,
        QUALITY_CONTROL
    };
    
    // External trigger configuration for test equipment
    struct external_trigger_config_t {
        uint8_t trigger_pin;           // GPIO pin for trigger output
        bool enable_logic_analyzer;    // Enable trigger for logic analyzer
        bool enable_oscilloscope;      // Enable trigger for oscilloscope
        uint32_t trigger_delay_us;     // Delay before trigger
        uint32_t trigger_duration_us;  // Trigger pulse duration
        
        external_trigger_config_t() :
            trigger_pin(33), enable_logic_analyzer(false), 
            enable_oscilloscope(false), trigger_delay_us(0),
            trigger_duration_us(10) {}
    };
    
    // Environmental monitoring configuration
    struct environmental_config_t {
        bool enable_temperature_monitoring;
        bool enable_voltage_monitoring;
        bool enable_humidity_monitoring;
        float temperature_min_c;
        float temperature_max_c;
        float voltage_min_v;
        float voltage_max_v;
        uint8_t humidity_min_percent;
        uint8_t humidity_max_percent;
        
        environmental_config_t() :
            enable_temperature_monitoring(true),
            enable_voltage_monitoring(true),
            enable_humidity_monitoring(false),
            temperature_min_c(-20.0f), temperature_max_c(70.0f),
            voltage_min_v(4.5f), voltage_max_v(5.5f),
            humidity_min_percent(10), humidity_max_percent(90) {}
    };
    
    // Comprehensive test configuration
    struct validation_config_t {
        validation_phase_t current_phase;
        bool enable_automatic_progression;  // Auto-advance through phases
        bool enable_data_logging;           // Log to SD card
        bool enable_serial_reporting;       // Real-time Serial output
        bool enable_led_diagnostics;        // Visual status indication
        bool enable_external_triggers;      // Hardware test equipment triggers
        bool enable_environmental_monitoring;
        uint32_t phase_duration_ms;         // Duration per phase
        uint32_t test_interval_ms;          // Interval between tests
        external_trigger_config_t trigger_config;
        environmental_config_t env_config;
        
        validation_config_t() :
            current_phase(validation_phase_t::PHASE_1_IMMEDIATE),
            enable_automatic_progression(true),
            enable_data_logging(true),
            enable_serial_reporting(true),
            enable_led_diagnostics(true),
            enable_external_triggers(false),
            enable_environmental_monitoring(true),
            phase_duration_ms(86400000),  // 24 hours default
            test_interval_ms(60000) {}    // 1 minute between tests
    };
    
    // Validation results structure
    struct validation_result_t {
        validation_phase_t phase;
        uint8_t test_id;
        const char* test_name;
        bool passed;
        uint32_t timestamp_ms;
        uint32_t duration_ms;
        uint32_t operations_completed;
        uint32_t errors_encountered;
        float error_rate_ppm;
        float efficiency_percentage;
        dma_performance_validator::performance_metrics_t metrics;
        dma_performance_validator::constraint_status_t constraints;
        const char* failure_reason;
        
        // Environmental conditions during test
        float temperature_c;
        float voltage_v;
        uint8_t humidity_percent;
        
        validation_result_t() :
            phase(validation_phase_t::PHASE_1_IMMEDIATE),
            test_id(0), test_name(nullptr), passed(false),
            timestamp_ms(0), duration_ms(0), operations_completed(0),
            errors_encountered(0), error_rate_ppm(0.0f),
            efficiency_percentage(0.0f), failure_reason(nullptr),
            temperature_c(25.0f), voltage_v(5.0f), humidity_percent(50) {}
    };
    
    // Acceptance criteria structure (from knowledge base)
    struct acceptance_criteria_t {
        // Phase 1 criteria
        struct {
            float min_efficiency_improvement;     // >50% vs sync
            uint32_t max_error_rate_ppm;         // <1000 PPM
            uint32_t max_thread_slice_us;        // 10μs
            uint32_t min_operations_per_second;  // >1000 ops/sec
            uint32_t min_stability_hours;        // 8+ hours
        } phase1;
        
        // Phase 2 criteria
        struct {
            float min_latency_reduction;         // >90%
            float min_throughput_increase;       // >100%
            uint32_t max_interrupt_latency_us;   // <5μs
            float max_timing_jitter_us;          // <1μs
            float max_error_rate_percent;        // <0.1%
        } phase2;
        
        // Phase 3 criteria
        struct {
            float min_production_pass_rate;      // >99%
            uint32_t max_test_duration_minutes;  // <10 min
            float max_false_positive_rate;       // <0.1%
            uint32_t min_diagnostic_coverage;    // >95%
        } phase3;
        
        acceptance_criteria_t() {
            phase1.min_efficiency_improvement = 50.0f;
            phase1.max_error_rate_ppm = 1000;
            phase1.max_thread_slice_us = 10;
            phase1.min_operations_per_second = 1000;
            phase1.min_stability_hours = 8;
            
            phase2.min_latency_reduction = 90.0f;
            phase2.min_throughput_increase = 100.0f;
            phase2.max_interrupt_latency_us = 5;
            phase2.max_timing_jitter_us = 1.0f;
            phase2.max_error_rate_percent = 0.1f;
            
            phase3.min_production_pass_rate = 99.0f;
            phase3.max_test_duration_minutes = 10;
            phase3.max_false_positive_rate = 0.1f;
            phase3.min_diagnostic_coverage = 95;
        }
    };

private:
    // Core components
    dma_performance_validator* validator_;
    dma_test_suite* test_suite_;
    dma_realtime_monitor* monitor_;
    dma_diagnostics::dma_error_handler* error_handler_;
    
    // Configuration
    validation_config_t config_;
    acceptance_criteria_t criteria_;
    
    // State management
    volatile bool validation_active_;
    validation_phase_t current_phase_;
    uint32_t phase_start_time_;
    uint32_t last_test_time_;
    uint8_t current_test_index_;
    
    // Results storage
    static const uint16_t MAX_RESULTS = 1000;
    validation_result_t results_[MAX_RESULTS];
    uint16_t result_index_;
    uint16_t result_count_;
    
    // Threading
    Threads::Mutex validation_mutex_;
    Threads::ThreadWait validation_thread_wait_;
    
    // Data logging
    File log_file_;
    char log_filename_[32];
    uint32_t log_entry_count_;
    
    // External triggers
    uint8_t trigger_pin_;
    volatile bool trigger_armed_;
    
    // Environmental monitoring
    float current_temperature_;
    float current_voltage_;
    uint8_t current_humidity_;
    
    // Statistics
    struct validation_statistics_t {
        uint32_t total_tests_run;
        uint32_t total_tests_passed;
        uint32_t total_operations;
        uint32_t total_errors;
        uint32_t total_duration_ms;
        float overall_efficiency;
        float overall_error_rate;
        
        validation_statistics_t() :
            total_tests_run(0), total_tests_passed(0),
            total_operations(0), total_errors(0),
            total_duration_ms(0), overall_efficiency(0.0f),
            overall_error_rate(0.0f) {}
    } statistics_;
    
    // Internal methods
    void validation_thread_function();
    static void validation_thread_entry(void* user_data);
    
    // Phase 1 test implementations
    validation_result_t run_phase1_basic_functionality();
    validation_result_t run_phase1_stress_testing();
    validation_result_t run_phase1_concurrent_operations();
    validation_result_t run_phase1_performance_baseline();
    validation_result_t run_phase1_error_injection();
    validation_result_t run_phase1_long_term_stability();
    
    // Phase 2 test implementations (external equipment)
    validation_result_t run_phase2_timing_analysis();
    validation_result_t run_phase2_performance_measurement();
    validation_result_t run_phase2_signal_integrity();
    validation_result_t run_phase2_environmental_stress();
    validation_result_t run_phase2_emc_compliance();
    validation_result_t run_phase2_power_efficiency();
    
    // Phase 3 test implementations
    validation_result_t run_phase3_production_testing();
    validation_result_t run_phase3_field_diagnostics();
    validation_result_t run_phase3_calibration_procedures();
    validation_result_t run_phase3_quality_control();
    
    // Utility methods
    bool check_acceptance_criteria(const validation_result_t& result);
    void log_result_to_sd(const validation_result_t& result);
    void print_result_to_serial(const validation_result_t& result);
    void update_led_status(validation_phase_t phase, bool test_active, bool test_passed);
    void trigger_external_equipment();
    void read_environmental_sensors();
    void update_statistics(const validation_result_t& result);
    
public:
    dma_automatic_validation(dma_performance_validator* validator,
                            dma_test_suite* test_suite,
                            dma_realtime_monitor* monitor,
                            dma_diagnostics::dma_error_handler* error_handler,
                            const validation_config_t& config = validation_config_t());
    ~dma_automatic_validation();
    
    // Validation control
    bool start_validation();
    void stop_validation();
    bool is_validation_active() const { return validation_active_; }
    
    // Phase control
    void set_validation_phase(validation_phase_t phase);
    validation_phase_t get_current_phase() const { return current_phase_; }
    bool advance_to_next_phase();
    
    // Test execution
    validation_result_t run_single_test(validation_phase_t phase, uint8_t test_id);
    bool run_current_phase_tests();
    bool run_all_phases();
    
    // Results access
    const validation_result_t* get_results(uint16_t& count) const;
    const validation_result_t& get_latest_result() const;
    const validation_statistics_t& get_statistics() const { return statistics_; }
    
    // Acceptance criteria
    bool check_phase_acceptance(validation_phase_t phase) const;
    bool check_overall_acceptance() const;
    const acceptance_criteria_t& get_acceptance_criteria() const { return criteria_; }
    void set_acceptance_criteria(const acceptance_criteria_t& criteria) { criteria_ = criteria; }
    
    // Configuration
    void set_config(const validation_config_t& config) { config_ = config; }
    const validation_config_t& get_config() const { return config_; }
    
    // External equipment integration
    void enable_external_triggers(const external_trigger_config_t& trigger_config);
    void disable_external_triggers();
    void manual_trigger();
    
    // Environmental monitoring
    void enable_environmental_monitoring(const environmental_config_t& env_config);
    void disable_environmental_monitoring();
    void get_environmental_conditions(float& temperature, float& voltage, uint8_t& humidity) const;
    
    // Data logging
    bool initialize_sd_logging();
    void flush_log_data();
    uint32_t get_log_entry_count() const { return log_entry_count_; }
    
    // Reporting
    void print_validation_summary() const;
    void print_phase_report(validation_phase_t phase) const;
    void print_detailed_statistics() const;
    void export_results_to_csv();
    
    // Utility methods
    static const char* phase_to_string(validation_phase_t phase);
    static const char* get_test_name(validation_phase_t phase, uint8_t test_id);
    uint32_t get_estimated_completion_time() const;
    float get_progress_percentage() const;
};

} // namespace dma_validation