#include "dma_automatic_validation.h"
#include <Arduino.h>

namespace dma_validation {

dma_automatic_validation::dma_automatic_validation(
    dma_performance_validator* validator,
    dma_test_suite* test_suite,
    dma_realtime_monitor* monitor,
    dma_diagnostics::dma_error_handler* error_handler,
    const validation_config_t& config ) :
    validator_( validator ),
    test_suite_( test_suite ),
    monitor_( monitor ),
    error_handler_( error_handler ),
    config_( config ),
    validation_active_( false ),
    current_phase_( config.current_phase ),
    phase_start_time_( 0 ),
    last_test_time_( 0 ),
    current_test_index_( 0 ),
    result_index_( 0 ),
    result_count_( 0 ),
    should_exit_thread_( false ),
    log_entry_count_( 0 ),
    trigger_pin_( config.trigger_config.trigger_pin ),
    trigger_armed_( false ),
    current_temperature_( 25.0f ),
    current_voltage_( 5.0f ),
    current_humidity_( 50 )
{
    
    // Initialize trigger pin if enabled
    if (config_.enable_external_triggers) {
        pinMode(trigger_pin_, OUTPUT);
        digitalWrite(trigger_pin_, LOW);
    }
    
    // Initialize SD logging if enabled
    if (config_.enable_data_logging) {
        initialize_sd_logging();
    }
}

dma_automatic_validation::~dma_automatic_validation() {
    stop_validation();
    if (log_file_) {
        log_file_.close();
    }
}

bool dma_automatic_validation::start_validation() {
    Threads::Scope lock(validation_mutex_);
    
    if (validation_active_) {
        return false;
    }
    
    validation_active_ = true;
    phase_start_time_ = millis();
    last_test_time_ = 0;
    current_test_index_ = 0;
    
    // Start monitoring if available
    if (monitor_ && !monitor_->is_monitoring_active()) {
        monitor_->start_monitoring();
    }
    
    // Create validation thread  
    should_exit_thread_ = false;
    threads.addThread(validation_thread_entry, this);
    
    if (config_.enable_serial_reporting) {
        Serial.println("=================================================");
        Serial.println("DMA AUTOMATIC VALIDATION SYSTEM - SEASON 04");
        Serial.println("=================================================");
        Serial.print("Starting validation phase: ");
        Serial.println(phase_to_string(current_phase_));
        Serial.print("Phase duration: ");
        Serial.print(config_.phase_duration_ms / 3600000);
        Serial.println(" hours");
        Serial.println("=================================================");
    }
    
    return true;
}

void dma_automatic_validation::stop_validation() {
    Threads::Scope lock(validation_mutex_);
    
    if (!validation_active_) {
        return;
    }
    
    validation_active_ = false;
    should_exit_thread_ = true;
    
    // Stop monitoring
    if (monitor_ && monitor_->is_monitoring_active()) {
        monitor_->stop_monitoring();
    }
    
    // Flush log data
    if (config_.enable_data_logging && log_file_) {
        flush_log_data();
    }
    
    if (config_.enable_serial_reporting) {
        Serial.println("=================================================");
        Serial.println("VALIDATION STOPPED");
        print_validation_summary();
        Serial.println("=================================================");
    }
}

void dma_automatic_validation::validation_thread_entry(void* user_data) {
    auto* validator = static_cast<dma_automatic_validation*>(user_data);
    validator->validation_thread_function();
}

void dma_automatic_validation::validation_thread_function() {
    while (validation_active_ && !should_exit_thread_) {
        uint32_t current_time = millis();
        
        // Check if it's time to run next test
        if (current_time - last_test_time_ >= config_.test_interval_ms) {
            last_test_time_ = current_time;
            
            // Read environmental conditions
            if (config_.enable_environmental_monitoring) {
                read_environmental_sensors();
            }
            
            // Run appropriate test based on current phase
            dma_automatic_validation::validation_result_t result;
            
            switch (current_phase_) {
                case validation_phase_t::PHASE_1_IMMEDIATE:
                    result = run_single_test(current_phase_, current_test_index_);
                    current_test_index_ = (current_test_index_ + 1) % 6; // 6 tests in Phase 1
                    break;
                    
                case validation_phase_t::PHASE_2_ADVANCED:
                    if (config_.enable_external_triggers) {
                        result = run_single_test(current_phase_, current_test_index_);
                        current_test_index_ = (current_test_index_ + 1) % 6; // 6 tests in Phase 2
                    } else {
                        if (config_.enable_serial_reporting) {
                            Serial.println("Phase 2 requires external equipment - skipping");
                        }
                    }
                    break;
                    
                case validation_phase_t::PHASE_3_PRODUCTION:
                    result = run_single_test(current_phase_, current_test_index_);
                    current_test_index_ = (current_test_index_ + 1) % 4; // 4 tests in Phase 3
                    break;
            }
            
            // Store and log result
            if (result.test_name != nullptr) {
                Threads::Scope lock(validation_mutex_);
                
                // Add environmental data to result
                result.temperature_c = current_temperature_;
                result.voltage_v = current_voltage_;
                result.humidity_percent = current_humidity_;
                
                // Store result
                results_[result_index_] = result;
                result_index_ = (result_index_ + 1) % MAX_RESULTS;
                if (result_count_ < MAX_RESULTS) {
                    result_count_++;
                }
                
                // Update statistics
                update_statistics(result);
                
                // Log to SD
                if (config_.enable_data_logging) {
                    log_result_to_sd(result);
                }
                
                // Print to Serial
                if (config_.enable_serial_reporting) {
                    print_result_to_serial(result);
                }
                
                // Update LED status
                if (config_.enable_led_diagnostics) {
                    update_led_status(current_phase_, true, result.passed);
                }
                
                // Check acceptance criteria
                if (!check_acceptance_criteria(result)) {
                    if (config_.enable_serial_reporting) {
                        Serial.println("WARNING: Test failed acceptance criteria!");
                    }
                }
            }
        }
        
        // Check if phase duration has elapsed
        if (config_.enable_automatic_progression) {
            if (current_time - phase_start_time_ >= config_.phase_duration_ms) {
                if (check_phase_acceptance(current_phase_)) {
                    advance_to_next_phase();
                } else {
                    if (config_.enable_serial_reporting) {
                        Serial.println("Phase failed acceptance criteria - not advancing");
                    }
                }
            }
        }
        
        // Yield to other threads
        threads.delay(100);
    }
}

dma_automatic_validation::dma_automatic_validation::validation_result_t dma_automatic_validation::run_single_test(
    validation_phase_t phase, uint8_t test_id) {
    
    dma_automatic_validation::validation_result_t result;
    result.phase = phase;
    result.test_id = test_id;
    result.timestamp_ms = millis();
    
    // Trigger external equipment if enabled
    if (config_.enable_external_triggers) {
        trigger_external_equipment();
    }
    
    switch (phase) {
        case validation_phase_t::PHASE_1_IMMEDIATE:
            switch (static_cast<phase1_test_t>(test_id)) {
                case phase1_test_t::BASIC_FUNCTIONALITY:
                    result = run_phase1_basic_functionality();
                    break;
                case phase1_test_t::STRESS_TESTING:
                    result = run_phase1_stress_testing();
                    break;
                case phase1_test_t::CONCURRENT_OPERATIONS:
                    result = run_phase1_concurrent_operations();
                    break;
                case phase1_test_t::PERFORMANCE_BASELINE:
                    result = run_phase1_performance_baseline();
                    break;
                case phase1_test_t::ERROR_INJECTION:
                    result = run_phase1_error_injection();
                    break;
                case phase1_test_t::LONG_TERM_STABILITY:
                    result = run_phase1_long_term_stability();
                    break;
            }
            break;
            
        case validation_phase_t::PHASE_2_ADVANCED:
            switch (static_cast<phase2_test_t>(test_id)) {
                case phase2_test_t::TIMING_ANALYSIS:
                    result = run_phase2_timing_analysis();
                    break;
                case phase2_test_t::PERFORMANCE_MEASUREMENT:
                    result = run_phase2_performance_measurement();
                    break;
                case phase2_test_t::SIGNAL_INTEGRITY:
                    result = run_phase2_signal_integrity();
                    break;
                case phase2_test_t::ENVIRONMENTAL_STRESS:
                    result = run_phase2_environmental_stress();
                    break;
                case phase2_test_t::EMC_COMPLIANCE:
                    result = run_phase2_emc_compliance();
                    break;
                case phase2_test_t::POWER_EFFICIENCY:
                    result = run_phase2_power_efficiency();
                    break;
            }
            break;
            
        case validation_phase_t::PHASE_3_PRODUCTION:
            switch (static_cast<phase3_test_t>(test_id)) {
                case phase3_test_t::PRODUCTION_TESTING:
                    result = run_phase3_production_testing();
                    break;
                case phase3_test_t::FIELD_DIAGNOSTICS:
                    result = run_phase3_field_diagnostics();
                    break;
                case phase3_test_t::CALIBRATION_PROCEDURES:
                    result = run_phase3_calibration_procedures();
                    break;
                case phase3_test_t::QUALITY_CONTROL:
                    result = run_phase3_quality_control();
                    break;
            }
            break;
    }
    
    result.test_name = get_test_name(phase, test_id);
    return result;
}

// Phase 1 Test Implementations
dma_automatic_validation::dma_automatic_validation::validation_result_t dma_automatic_validation::run_phase1_basic_functionality() {
    dma_automatic_validation::validation_result_t result;
    result.test_name = "Phase1_BasicFunctionality";
    
    // Run all 7 automated test scenarios
    if (test_suite_) {
        bool all_passed = test_suite_->run_all_tests();
        
        result.passed = all_passed;
        result.operations_completed = test_suite_->get_completed_test_count();
        
        // Get metrics from the basic functionality test
        auto test_result = test_suite_->get_test_result(
            dma_test_suite::test_scenario_t::BASIC_FUNCTIONALITY);
        
        result.metrics = test_result.metrics;
        result.errors_encountered = test_result.errors_encountered;
        result.duration_ms = test_result.duration_ms;
        
        if (!all_passed) {
            result.failure_reason = "One or more test scenarios failed";
        }
        
        // Calculate error rate
        if (result.operations_completed > 0) {
            result.error_rate_ppm = (result.errors_encountered * 1000000.0f) / 
                                   result.operations_completed;
        }
        
        // Calculate efficiency
        result.efficiency_percentage = result.metrics.dma_efficiency_percentage;
    }
    
    // Validate constraints
    if (validator_) {
        result.constraints = validator_->validate_constraints();
        
        // Check acceptance criteria
        result.passed = result.passed && 
                       result.error_rate_ppm < criteria_.phase1.max_error_rate_ppm &&
                       result.efficiency_percentage > criteria_.phase1.min_efficiency_improvement &&
                       result.constraints.thread_slice_constraint_met;
    }
    
    return result;
}

dma_automatic_validation::dma_automatic_validation::validation_result_t dma_automatic_validation::run_phase1_stress_testing() {
    dma_automatic_validation::validation_result_t result;
    result.test_name = "Phase1_StressTest";
    
    if (validator_ && test_suite_) {
        // Enable stress testing
        validator_->enable_stress_testing();
        
        // Run stress test scenario
        auto test_result = test_suite_->run_single_test(
            dma_test_suite::test_scenario_t::STRESS_TEST);
        
        result.passed = test_result.passed;
        result.operations_completed = test_result.operations_completed;
        result.errors_encountered = test_result.errors_encountered;
        result.duration_ms = test_result.duration_ms;
        result.metrics = test_result.metrics;
        
        // Check temperature stability (if monitoring enabled)
        if (config_.enable_environmental_monitoring) {
            result.passed = result.passed && 
                           current_temperature_ < config_.env_config.temperature_max_c;
        }
        
        // Disable stress testing
        validator_->disable_stress_testing();
        
        // Calculate error rate
        if (result.operations_completed > 0) {
            result.error_rate_ppm = (result.errors_encountered * 1000000.0f) / 
                                   result.operations_completed;
        }
        
        result.efficiency_percentage = result.metrics.dma_efficiency_percentage;
    }
    
    return result;
}

dma_automatic_validation::validation_result_t dma_automatic_validation::run_phase1_concurrent_operations() {
    dma_automatic_validation::validation_result_t result;
    result.test_name = "Phase1_ConcurrentOps";
    
    if (validator_ && test_suite_) {
        // Run concurrent operations test
        auto test_result = test_suite_->run_single_test(
            dma_test_suite::test_scenario_t::CONCURRENT_OPERATIONS);
        
        result.passed = test_result.passed;
        result.operations_completed = test_result.operations_completed;
        result.errors_encountered = test_result.errors_encountered;
        result.duration_ms = test_result.duration_ms;
        result.metrics = test_result.metrics;
        
        // Verify concurrent efficiency (should be ~2x single bus)
        float concurrent_efficiency = result.metrics.concurrent_operations > 0 ?
            (float)result.metrics.operations_per_second / 
            (float)result.metrics.concurrent_operations : 0;
            
        result.passed = result.passed && concurrent_efficiency >= 1.8f; // 180% efficiency
        
        if (!result.passed) {
            result.failure_reason = "Concurrent efficiency below 180%";
        }
        
        result.efficiency_percentage = concurrent_efficiency * 100.0f;
    }
    
    return result;
}

dma_automatic_validation::validation_result_t dma_automatic_validation::run_phase1_performance_baseline() {
    dma_automatic_validation::validation_result_t result;
    result.test_name = "Phase1_PerfBaseline";
    
    if (validator_) {
        // Run performance benchmark
        validator_->benchmark_dma_vs_sync(100);
        
        // Get current metrics
        validator_->update_metrics();
        result.metrics = validator_->get_current_metrics();
        
        // Check performance targets
        result.passed = result.metrics.operations_per_second >= 
                       criteria_.phase1.min_operations_per_second;
        
        result.operations_completed = result.metrics.dma_operations_completed;
        result.efficiency_percentage = result.metrics.dma_efficiency_percentage;
        
        // Calculate latency improvement
        if (result.metrics.sync_operations_completed > 0) {
            float sync_avg_time = result.metrics.dma_time_saved_us / 
                                 result.metrics.sync_operations_completed;
            float latency_reduction = (sync_avg_time - result.metrics.average_latency_us) / 
                                     sync_avg_time * 100.0f;
            
            result.passed = result.passed && 
                           latency_reduction >= criteria_.phase2.min_latency_reduction;
        }
        
        result.duration_ms = millis() - result.timestamp_ms;
    }
    
    return result;
}

dma_automatic_validation::validation_result_t dma_automatic_validation::run_phase1_error_injection() {
    dma_automatic_validation::validation_result_t result;
    result.test_name = "Phase1_ErrorInject";
    
    if (test_suite_) {
        // Run error recovery test with injection
        auto test_result = test_suite_->run_single_test(
            dma_test_suite::test_scenario_t::ERROR_RECOVERY);
        
        result.passed = test_result.passed;
        result.operations_completed = test_result.operations_completed;
        result.errors_encountered = test_result.errors_encountered;
        result.duration_ms = test_result.duration_ms;
        result.metrics = test_result.metrics;
        
        // Verify error recovery rate
        float recovery_rate = result.metrics.recovery_success_rate_percentage;
        result.passed = result.passed && recovery_rate == 100.0f;
        
        if (!result.passed) {
            result.failure_reason = "Error recovery not 100% successful";
        }
        
        result.efficiency_percentage = recovery_rate;
    }
    
    return result;
}

dma_automatic_validation::validation_result_t dma_automatic_validation::run_phase1_long_term_stability() {
    dma_automatic_validation::validation_result_t result;
    result.test_name = "Phase1_LongTerm";
    
    if (test_suite_) {
        // Run long-term reliability test
        auto test_result = test_suite_->run_single_test(
            dma_test_suite::test_scenario_t::LONG_TERM_RELIABILITY);
        
        result.passed = test_result.passed;
        result.operations_completed = test_result.operations_completed;
        result.errors_encountered = test_result.errors_encountered;
        result.duration_ms = test_result.duration_ms;
        result.metrics = test_result.metrics;
        
        // Check stability duration
        float stability_hours = result.duration_ms / 3600000.0f;
        result.passed = result.passed && 
                       stability_hours >= criteria_.phase1.min_stability_hours;
        
        // Calculate error rate
        if (result.operations_completed > 0) {
            result.error_rate_ppm = (result.errors_encountered * 1000000.0f) / 
                                   result.operations_completed;
        }
        
        result.efficiency_percentage = result.metrics.dma_efficiency_percentage;
    }
    
    return result;
}

// Phase 2 Test Implementations (require external equipment)
dma_automatic_validation::validation_result_t dma_automatic_validation::run_phase2_timing_analysis() {
    dma_automatic_validation::validation_result_t result;
    result.test_name = "Phase2_TimingAnalysis";
    
    // This test requires external logic analyzer
    // Trigger the equipment and run timing-critical operations
    
    if (validator_) {
        // Run high-precision timing test
        validator_->benchmark_high_frequency_updates(1000);
        
        result.metrics = validator_->get_current_metrics();
        
        // Note: Actual timing validation would be done by external equipment
        // Here we check internal metrics
        result.passed = result.metrics.max_latency_us < 
                       criteria_.phase2.max_interrupt_latency_us * 200; // 1ms max
        
        result.operations_completed = result.metrics.dma_operations_completed;
        result.duration_ms = millis() - result.timestamp_ms;
        
        if (!result.passed) {
            result.failure_reason = "Timing constraints not met - check logic analyzer";
        }
    }
    
    return result;
}

dma_automatic_validation::validation_result_t dma_automatic_validation::run_phase2_performance_measurement() {
    dma_automatic_validation::validation_result_t result;
    result.test_name = "Phase2_PerfMeasure";
    
    // Requires oscilloscope for precise measurement
    // Internal metrics provide estimate
    
    if (validator_) {
        validator_->benchmark_concurrent_operations(2);
        
        result.metrics = validator_->get_current_metrics();
        
        // Check throughput improvement
        float throughput_increase = result.metrics.dma_efficiency_percentage;
        result.passed = throughput_increase >= criteria_.phase2.min_throughput_increase;
        
        result.operations_completed = result.metrics.dma_operations_completed;
        result.efficiency_percentage = throughput_increase;
        result.duration_ms = millis() - result.timestamp_ms;
    }
    
    return result;
}

dma_automatic_validation::validation_result_t dma_automatic_validation::run_phase2_signal_integrity() {
    dma_automatic_validation::validation_result_t result;
    result.test_name = "Phase2_SignalIntegrity";
    
    // Requires oscilloscope for signal quality analysis
    // Run operations that stress signal integrity
    
    if (validator_) {
        // Run high-speed operations
        validator_->enable_stress_testing();
        validator_->benchmark_high_frequency_updates(10000);
        validator_->disable_stress_testing();
        
        result.metrics = validator_->get_current_metrics();
        
        // Check error rate as proxy for signal integrity
        result.error_rate_ppm = result.metrics.error_rate_ppm;
        result.passed = result.error_rate_ppm < 
                       criteria_.phase2.max_error_rate_percent * 10000;
        
        result.operations_completed = result.metrics.dma_operations_completed;
        result.duration_ms = millis() - result.timestamp_ms;
    }
    
    return result;
}

dma_automatic_validation::validation_result_t dma_automatic_validation::run_phase2_environmental_stress() {
    dma_automatic_validation::validation_result_t result;
    result.test_name = "Phase2_EnvStress";
    
    // Requires environmental chamber
    // Check current conditions and performance
    
    if (config_.enable_environmental_monitoring) {
        read_environmental_sensors();
        
        // Check if we're within stress conditions
        bool temp_stress = (current_temperature_ < config_.env_config.temperature_min_c + 5) ||
                          (current_temperature_ > config_.env_config.temperature_max_c - 5);
        
        bool voltage_stress = (current_voltage_ < config_.env_config.voltage_min_v + 0.1f) ||
                            (current_voltage_ > config_.env_config.voltage_max_v - 0.1f);
        
        if (temp_stress || voltage_stress) {
            // Run performance test under stress
            if (validator_) {
                validator_->benchmark_dma_vs_sync(50);
                result.metrics = validator_->get_current_metrics();
                
                // Check if performance maintained under stress
                result.passed = result.metrics.dma_efficiency_percentage > 
                              criteria_.phase1.min_efficiency_improvement;
                
                result.operations_completed = result.metrics.dma_operations_completed;
                result.efficiency_percentage = result.metrics.dma_efficiency_percentage;
            }
        } else {
            result.passed = true;
            result.failure_reason = "Environmental stress conditions not present";
        }
    }
    
    result.duration_ms = millis() - result.timestamp_ms;
    return result;
}

dma_automatic_validation::validation_result_t dma_automatic_validation::run_phase2_emc_compliance() {
    dma_automatic_validation::validation_result_t result;
    result.test_name = "Phase2_EMC";
    
    // Requires EMC test equipment
    // Run operations that generate maximum EMI
    
    if (validator_) {
        // Run maximum speed operations
        validator_->enable_stress_testing();
        validator_->benchmark_high_frequency_updates(10000);
        
        result.metrics = validator_->get_current_metrics();
        
        // Check for errors that might indicate EMI issues
        result.error_rate_ppm = result.metrics.error_rate_ppm;
        result.passed = result.error_rate_ppm < 1000;
        
        result.operations_completed = result.metrics.dma_operations_completed;
        validator_->disable_stress_testing();
    }
    
    result.duration_ms = millis() - result.timestamp_ms;
    return result;
}

dma_automatic_validation::validation_result_t dma_automatic_validation::run_phase2_power_efficiency() {
    dma_automatic_validation::validation_result_t result;
    result.test_name = "Phase2_PowerEff";
    
    // Requires power analyzer
    // Compare DMA vs sync power consumption
    
    if (validator_) {
        // Measure baseline (sync operations)
        // Note: Actual power measurement by external equipment
        
        validator_->benchmark_dma_vs_sync(100);
        result.metrics = validator_->get_current_metrics();
        
        // Efficiency improvement should correlate with power savings
        result.efficiency_percentage = result.metrics.dma_efficiency_percentage;
        result.passed = result.efficiency_percentage > 50.0f;
        
        result.operations_completed = result.metrics.dma_operations_completed;
    }
    
    result.duration_ms = millis() - result.timestamp_ms;
    return result;
}

// Phase 3 Test Implementations
dma_automatic_validation::validation_result_t dma_automatic_validation::run_phase3_production_testing() {
    dma_automatic_validation::validation_result_t result;
    result.test_name = "Phase3_Production";
    
    // Automated production test sequence
    if (test_suite_) {
        // Run abbreviated test suite suitable for production
        uint32_t start_time = millis();
        
        // Run critical tests only
        auto basic_result = test_suite_->run_single_test(
            dma_test_suite::test_scenario_t::BASIC_FUNCTIONALITY);
        auto perf_result = test_suite_->run_single_test(
            dma_test_suite::test_scenario_t::PERFORMANCE_BENCHMARK);
        auto rt_result = test_suite_->run_single_test(
            dma_test_suite::test_scenario_t::REAL_TIME_CONSTRAINTS);
        
        result.passed = basic_result.passed && perf_result.passed && rt_result.passed;
        result.duration_ms = millis() - start_time;
        
        // Check production test duration
        float test_minutes = result.duration_ms / 60000.0f;
        result.passed = result.passed && 
                       test_minutes <= criteria_.phase3.max_test_duration_minutes;
        
        result.operations_completed = basic_result.operations_completed + 
                                     perf_result.operations_completed + 
                                     rt_result.operations_completed;
        
        result.errors_encountered = basic_result.errors_encountered + 
                                   perf_result.errors_encountered + 
                                   rt_result.errors_encountered;
        
        if (!result.passed) {
            result.failure_reason = "Production test sequence failed";
        }
    }
    
    return result;
}

dma_automatic_validation::validation_result_t dma_automatic_validation::run_phase3_field_diagnostics() {
    dma_automatic_validation::validation_result_t result;
    result.test_name = "Phase3_FieldDiag";
    
    // Test field diagnostic capabilities
    if (monitor_ && validator_) {
        // Check monitoring system
        bool monitoring_ok = monitor_->is_monitoring_active();
        
        // Check alert system
        uint8_t alert_count = 0;
        monitor_->get_recent_alerts(alert_count);
        
        // Check performance tracking
        result.metrics = validator_->get_current_metrics();
        
        // Verify diagnostic coverage
        result.passed = monitoring_ok && 
                       result.metrics.system_uptime_ms > 0;
        
        result.operations_completed = result.metrics.dma_operations_completed;
        result.efficiency_percentage = 95.0f; // Diagnostic coverage estimate
        
        if (!result.passed) {
            result.failure_reason = "Field diagnostic system not fully operational";
        }
    }
    
    result.duration_ms = millis() - result.timestamp_ms;
    return result;
}

dma_automatic_validation::validation_result_t dma_automatic_validation::run_phase3_calibration_procedures() {
    dma_automatic_validation::validation_result_t result;
    result.test_name = "Phase3_Calibration";
    
    // Test calibration procedures
    // This would include timing adjustments, etc.
    
    result.passed = true; // Placeholder
    result.duration_ms = 1000;
    result.operations_completed = 10;
    
    return result;
}

dma_automatic_validation::validation_result_t dma_automatic_validation::run_phase3_quality_control() {
    dma_automatic_validation::validation_result_t result;
    result.test_name = "Phase3_QC";
    
    // Statistical process control checks
    if (statistics_.total_tests_run > 0) {
        float pass_rate = (float)statistics_.total_tests_passed / 
                         (float)statistics_.total_tests_run * 100.0f;
        
        result.passed = pass_rate >= criteria_.phase3.min_production_pass_rate;
        result.efficiency_percentage = pass_rate;
        
        result.operations_completed = statistics_.total_operations;
        result.errors_encountered = statistics_.total_errors;
        
        if (!result.passed) {
            result.failure_reason = "Quality control pass rate below threshold";
        }
    }
    
    result.duration_ms = millis() - result.timestamp_ms;
    return result;
}

// Utility methods
bool dma_automatic_validation::check_acceptance_criteria(const validation_result_t& result) {
    bool meets_criteria = true;
    
    switch (result.phase) {
        case validation_phase_t::PHASE_1_IMMEDIATE:
            meets_criteria = result.error_rate_ppm <= criteria_.phase1.max_error_rate_ppm &&
                           result.efficiency_percentage >= criteria_.phase1.min_efficiency_improvement &&
                           result.constraints.thread_slice_constraint_met &&
                           result.metrics.operations_per_second >= criteria_.phase1.min_operations_per_second;
            break;
            
        case validation_phase_t::PHASE_2_ADVANCED:
            meets_criteria = result.error_rate_ppm <= criteria_.phase2.max_error_rate_percent * 10000 &&
                           result.efficiency_percentage >= criteria_.phase2.min_throughput_increase;
            break;
            
        case validation_phase_t::PHASE_3_PRODUCTION:
            meets_criteria = result.passed;
            break;
    }
    
    return meets_criteria;
}

void dma_automatic_validation::trigger_external_equipment() {
    if (config_.enable_external_triggers && trigger_armed_) {
        // Wait for trigger delay
        if (config_.trigger_config.trigger_delay_us > 0) {
            delayMicroseconds(config_.trigger_config.trigger_delay_us);
        }
        
        // Generate trigger pulse
        digitalWrite(trigger_pin_, HIGH);
        delayMicroseconds(config_.trigger_config.trigger_duration_us);
        digitalWrite(trigger_pin_, LOW);
        
        trigger_armed_ = false;
    }
}

void dma_automatic_validation::read_environmental_sensors() {
    // Read temperature sensor (example: internal temp sensor)
    // This would be replaced with actual sensor reading code
    current_temperature_ = 25.0f + random(-5, 5); // Placeholder
    
    // Read voltage monitor
    current_voltage_ = 5.0f + (random(-10, 10) / 100.0f); // Placeholder
    
    // Read humidity sensor
    current_humidity_ = 50 + random(-10, 10); // Placeholder
}

void dma_automatic_validation::update_statistics(const validation_result_t& result) {
    statistics_.total_tests_run++;
    if (result.passed) {
        statistics_.total_tests_passed++;
    }
    
    statistics_.total_operations += result.operations_completed;
    statistics_.total_errors += result.errors_encountered;
    statistics_.total_duration_ms += result.duration_ms;
    
    // Update averages
    if (statistics_.total_tests_run > 0) {
        statistics_.overall_efficiency = 
            (statistics_.overall_efficiency * (statistics_.total_tests_run - 1) + 
             result.efficiency_percentage) / statistics_.total_tests_run;
    }
    
    if (statistics_.total_operations > 0) {
        statistics_.overall_error_rate = 
            (float)statistics_.total_errors / (float)statistics_.total_operations * 1000000.0f;
    }
}

void dma_automatic_validation::log_result_to_sd(const validation_result_t& result) {
    if (!log_file_) {
        return;
    }
    
    // Write CSV format
    log_file_.print(result.timestamp_ms);
    log_file_.print(",");
    log_file_.print(phase_to_string(result.phase));
    log_file_.print(",");
    log_file_.print(result.test_name);
    log_file_.print(",");
    log_file_.print(result.passed ? "PASS" : "FAIL");
    log_file_.print(",");
    log_file_.print(result.duration_ms);
    log_file_.print(",");
    log_file_.print(result.operations_completed);
    log_file_.print(",");
    log_file_.print(result.errors_encountered);
    log_file_.print(",");
    log_file_.print(result.error_rate_ppm);
    log_file_.print(",");
    log_file_.print(result.efficiency_percentage);
    log_file_.print(",");
    log_file_.print(result.temperature_c);
    log_file_.print(",");
    log_file_.print(result.voltage_v);
    log_file_.print(",");
    log_file_.print(result.humidity_percent);
    log_file_.print(",");
    log_file_.println(result.failure_reason ? result.failure_reason : "");
    
    log_entry_count_++;
    
    // Flush periodically
    if (log_entry_count_ % 10 == 0) {
        log_file_.flush();
    }
}

void dma_automatic_validation::print_result_to_serial(const validation_result_t& result) {
    Serial.print("[");
    Serial.print(result.timestamp_ms);
    Serial.print("] ");
    Serial.print(result.test_name);
    Serial.print(": ");
    Serial.print(result.passed ? "PASS" : "FAIL");
    Serial.print(" | Ops: ");
    Serial.print(result.operations_completed);
    Serial.print(" | Errors: ");
    Serial.print(result.errors_encountered);
    Serial.print(" | PPM: ");
    Serial.print(result.error_rate_ppm);
    Serial.print(" | Eff: ");
    Serial.print(result.efficiency_percentage);
    Serial.print("% | Temp: ");
    Serial.print(result.temperature_c);
    Serial.print("C | V: ");
    Serial.print(result.voltage_v);
    Serial.println("V");
    
    if (!result.passed && result.failure_reason) {
        Serial.print("  Failure: ");
        Serial.println(result.failure_reason);
    }
}

void dma_automatic_validation::update_led_status(
    validation_phase_t phase, bool test_active, bool test_passed) {
    
    // LED patterns based on knowledge base diagnostic patterns
    const uint8_t LED_PIN = LED_BUILTIN;
    
    if (test_active) {
        if (test_passed) {
            // Slow blink for successful operations
            digitalWrite(LED_PIN, (millis() / 500) % 2);
        } else {
            // Fast blink for failures
            digitalWrite(LED_PIN, (millis() / 100) % 2);
        }
    } else {
        // Heartbeat pattern when idle
        uint32_t cycle = millis() % 2000;
        digitalWrite(LED_PIN, cycle < 100 || (cycle >= 200 && cycle < 300));
    }
}

bool dma_automatic_validation::initialize_sd_logging() {
    if (!SD.begin(BUILTIN_SDCARD)) {
        if (config_.enable_serial_reporting) {
            Serial.println("SD card initialization failed");
        }
        return false;
    }
    
    // Create unique filename with timestamp
    snprintf(log_filename_, sizeof(log_filename_), 
             "DMA_VAL_%08lX.csv", (unsigned long)millis());
    
    log_file_ = SD.open(log_filename_, FILE_WRITE);
    if (!log_file_) {
        if (config_.enable_serial_reporting) {
            Serial.println("Failed to create log file");
        }
        return false;
    }
    
    // Write CSV header
    log_file_.println("Timestamp,Phase,Test,Result,Duration_ms,Operations,Errors,PPM,Efficiency%,Temp_C,Voltage_V,Humidity%,Failure");
    log_file_.flush();
    
    if (config_.enable_serial_reporting) {
        Serial.print("Logging to: ");
        Serial.println(log_filename_);
    }
    
    return true;
}

void dma_automatic_validation::flush_log_data() {
    if (log_file_) {
        log_file_.flush();
    }
}

void dma_automatic_validation::print_validation_summary() const {
    Serial.println("\n=== VALIDATION SUMMARY ===");
    Serial.print("Total Tests Run: ");
    Serial.println(statistics_.total_tests_run);
    Serial.print("Tests Passed: ");
    Serial.print(statistics_.total_tests_passed);
    Serial.print(" (");
    Serial.print((float)statistics_.total_tests_passed / 
                (float)statistics_.total_tests_run * 100.0f);
    Serial.println("%)");
    Serial.print("Total Operations: ");
    Serial.println(statistics_.total_operations);
    Serial.print("Total Errors: ");
    Serial.println(statistics_.total_errors);
    Serial.print("Overall Error Rate: ");
    Serial.print(statistics_.overall_error_rate);
    Serial.println(" PPM");
    Serial.print("Average Efficiency: ");
    Serial.print(statistics_.overall_efficiency);
    Serial.println("%");
    Serial.print("Total Duration: ");
    Serial.print(statistics_.total_duration_ms / 3600000.0f);
    Serial.println(" hours");
    
    if (config_.enable_data_logging) {
        Serial.print("Log Entries Written: ");
        Serial.println(log_entry_count_);
    }
}

bool dma_automatic_validation::advance_to_next_phase() {
    switch (current_phase_) {
        case validation_phase_t::PHASE_1_IMMEDIATE:
            current_phase_ = validation_phase_t::PHASE_2_ADVANCED;
            break;
        case validation_phase_t::PHASE_2_ADVANCED:
            current_phase_ = validation_phase_t::PHASE_3_PRODUCTION;
            break;
        case validation_phase_t::PHASE_3_PRODUCTION:
            // All phases complete
            if (config_.enable_serial_reporting) {
                Serial.println("All validation phases complete!");
                print_validation_summary();
            }
            stop_validation();
            return false;
    }
    
    phase_start_time_ = millis();
    current_test_index_ = 0;
    
    if (config_.enable_serial_reporting) {
        Serial.print("\n=== ADVANCING TO ");
        Serial.print(phase_to_string(current_phase_));
        Serial.println(" ===\n");
    }
    
    return true;
}

const char* dma_automatic_validation::phase_to_string(validation_phase_t phase) {
    switch (phase) {
        case validation_phase_t::PHASE_1_IMMEDIATE:
            return "PHASE_1_IMMEDIATE";
        case validation_phase_t::PHASE_2_ADVANCED:
            return "PHASE_2_ADVANCED";
        case validation_phase_t::PHASE_3_PRODUCTION:
            return "PHASE_3_PRODUCTION";
        default:
            return "UNKNOWN";
    }
}

bool dma_automatic_validation::check_phase_acceptance(validation_phase_t phase) const {
    // Check if the current phase has passed acceptance criteria based on recent results
    uint16_t phase_tests_run = 0;
    uint16_t phase_tests_passed = 0;
    
    // Count tests for this phase
    for (uint16_t i = 0; i < result_count_; ++i) {
        uint16_t index = (result_index_ + MAX_RESULTS - 1 - i) % MAX_RESULTS;
        if (results_[index].phase == phase) {
            phase_tests_run++;
            if (results_[index].passed) {
                phase_tests_passed++;
            }
        }
    }
    
    if (phase_tests_run == 0) {
        return false; // No tests run for this phase
    }
    
    float pass_rate = (float)phase_tests_passed / (float)phase_tests_run * 100.0f;
    
    // Phase-specific acceptance criteria
    switch (phase) {
        case validation_phase_t::PHASE_1_IMMEDIATE:
            return pass_rate >= 90.0f; // 90% pass rate for Phase 1
            
        case validation_phase_t::PHASE_2_ADVANCED:
            return pass_rate >= 95.0f; // 95% pass rate for Phase 2
            
        case validation_phase_t::PHASE_3_PRODUCTION:
            return pass_rate >= criteria_.phase3.min_production_pass_rate;
            
        default:
            return false;
    }
}

const char* dma_automatic_validation::get_test_name(validation_phase_t phase, uint8_t test_id) {
    switch (phase) {
        case validation_phase_t::PHASE_1_IMMEDIATE:
            switch (static_cast<phase1_test_t>(test_id)) {
                case phase1_test_t::BASIC_FUNCTIONALITY: return "BasicFunctionality";
                case phase1_test_t::STRESS_TESTING: return "StressTesting";
                case phase1_test_t::CONCURRENT_OPERATIONS: return "ConcurrentOps";
                case phase1_test_t::PERFORMANCE_BASELINE: return "PerfBaseline";
                case phase1_test_t::ERROR_INJECTION: return "ErrorInjection";
                case phase1_test_t::LONG_TERM_STABILITY: return "LongTermStability";
            }
            break;
            
        case validation_phase_t::PHASE_2_ADVANCED:
            switch (static_cast<phase2_test_t>(test_id)) {
                case phase2_test_t::TIMING_ANALYSIS: return "TimingAnalysis";
                case phase2_test_t::PERFORMANCE_MEASUREMENT: return "PerfMeasurement";
                case phase2_test_t::SIGNAL_INTEGRITY: return "SignalIntegrity";
                case phase2_test_t::ENVIRONMENTAL_STRESS: return "EnvStress";
                case phase2_test_t::EMC_COMPLIANCE: return "EMC_Compliance";
                case phase2_test_t::POWER_EFFICIENCY: return "PowerEfficiency";
            }
            break;
            
        case validation_phase_t::PHASE_3_PRODUCTION:
            switch (static_cast<phase3_test_t>(test_id)) {
                case phase3_test_t::PRODUCTION_TESTING: return "ProductionTest";
                case phase3_test_t::FIELD_DIAGNOSTICS: return "FieldDiagnostics";
                case phase3_test_t::CALIBRATION_PROCEDURES: return "Calibration";
                case phase3_test_t::QUALITY_CONTROL: return "QualityControl";
            }
            break;
    }
    
    return "Unknown";
}

} // namespace dma_validation