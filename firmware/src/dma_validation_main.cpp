/**
 * @file dma_validation_main.cpp
 * @brief Main integration file for DMA automatic validation system
 * 
 * This file demonstrates how to integrate and use the comprehensive
 * DMA automatic validation system with the Master of Muppets firmware.
 * 
 * Based on Season 04 DMA Hardware Testing Plan Knowledge Base.
 */

#include <Arduino.h>
#include "dma_automatic_validation.h"
#include "dma_performance_validator.h"
#include "dma_error_handler.h"
#include "electric_mayhem_dma.h"
#include "dr_teeth.h"

// Global validation system instance
dma_validation::dma_automatic_validation* g_auto_validator = nullptr;
dma_validation::dma_performance_validator* g_perf_validator = nullptr;
dma_validation::dma_test_suite* g_test_suite = nullptr;
dma_validation::dma_realtime_monitor* g_monitor = nullptr;
dma_diagnostics::dma_error_handler* g_error_handler = nullptr;

// Validation mode flag (set via compile flag or runtime)
bool g_validation_mode_enabled = false;

// External trigger pins (for test equipment)
const uint8_t LOGIC_ANALYZER_TRIGGER_PIN = 32;
const uint8_t OSCILLOSCOPE_TRIGGER_PIN = 33;

/**
 * @brief Initialize the DMA validation system
 * 
 * Sets up all components required for comprehensive DMA validation
 * including performance monitoring, error handling, and test automation.
 */
void initialize_dma_validation_system() {
    Serial.println("Initializing DMA Validation System...");
    
    // Initialize error handler
    dma_diagnostics::dma_error_handler::error_config_t error_config;
    error_config.enable_led_diagnostics = true;
    error_config.enable_serial_logging = true;
    error_config.enable_automatic_recovery = true;
    error_config.max_retry_count = 3;
    error_config.retry_delay_ms = 10;
    
    g_error_handler = new dma_diagnostics::dma_error_handler(error_config);
    
    // Initialize performance validator
    dma_validation::dma_performance_validator::test_config_t perf_config;
    perf_config.test_duration_ms = 30000;          // 30 seconds per test
    perf_config.measurement_interval_ms = 1000;     // 1 second intervals
    perf_config.enable_stress_testing = true;
    perf_config.enable_concurrent_testing = true;
    perf_config.enable_error_injection = true;
    perf_config.target_operations_per_second = 1000;
    perf_config.max_acceptable_latency_us = 1000;   // 1ms max latency
    perf_config.thread_slice_limit_us = 10;         // 10μs thread slice
    
    g_perf_validator = new dma_validation::dma_performance_validator(perf_config);
    
    // Initialize test suite
    g_test_suite = new dma_validation::dma_test_suite(g_perf_validator, g_error_handler);
    
    // Initialize real-time monitor
    dma_validation::dma_realtime_monitor::monitor_config_t monitor_config;
    monitor_config.monitoring_interval_ms = 5000;   // 5 second monitoring
    monitor_config.enable_automatic_alerts = true;
    monitor_config.enable_performance_logging = true;
    monitor_config.enable_constraint_checking = true;
    monitor_config.alert_threshold_latency_us = 2000;  // 2ms alert threshold
    monitor_config.alert_threshold_error_rate = 1.0f;  // 1% error rate alert
    
    g_monitor = new dma_validation::dma_realtime_monitor(g_perf_validator, monitor_config);
    
    // Initialize automatic validation system
    dma_validation::dma_automatic_validation::validation_config_t val_config;
    val_config.current_phase = dma_validation::dma_automatic_validation::validation_phase_t::PHASE_1_IMMEDIATE;
    val_config.enable_automatic_progression = true;
    val_config.enable_data_logging = true;
    val_config.enable_serial_reporting = true;
    val_config.enable_led_diagnostics = true;
    val_config.enable_external_triggers = false;  // Set to true if equipment connected
    val_config.enable_environmental_monitoring = true;
    val_config.phase_duration_ms = 3600000;      // 1 hour per phase for testing
    val_config.test_interval_ms = 60000;         // 1 minute between tests
    
    // Configure external triggers if equipment is connected
    val_config.trigger_config.trigger_pin = LOGIC_ANALYZER_TRIGGER_PIN;
    val_config.trigger_config.enable_logic_analyzer = false;
    val_config.trigger_config.enable_oscilloscope = false;
    val_config.trigger_config.trigger_delay_us = 100;
    val_config.trigger_config.trigger_duration_us = 10;
    
    // Configure environmental monitoring
    val_config.env_config.enable_temperature_monitoring = true;
    val_config.env_config.enable_voltage_monitoring = true;
    val_config.env_config.enable_humidity_monitoring = false;
    val_config.env_config.temperature_min_c = -20.0f;
    val_config.env_config.temperature_max_c = 70.0f;
    val_config.env_config.voltage_min_v = 4.5f;
    val_config.env_config.voltage_max_v = 5.5f;
    
    g_auto_validator = new dma_validation::dma_automatic_validation(
        g_perf_validator, g_test_suite, g_monitor, g_error_handler, val_config);
    
    // Configure acceptance criteria (from knowledge base)
    dma_validation::dma_automatic_validation::acceptance_criteria_t criteria;
    
    // Phase 1 criteria
    criteria.phase1.min_efficiency_improvement = 50.0f;     // >50% improvement
    criteria.phase1.max_error_rate_ppm = 1000;             // <0.1% error rate
    criteria.phase1.max_thread_slice_us = 10;              // 10μs max
    criteria.phase1.min_operations_per_second = 1000;      // >1000 ops/sec
    criteria.phase1.min_stability_hours = 8;               // 8+ hours stability
    
    // Phase 2 criteria (requires external equipment)
    criteria.phase2.min_latency_reduction = 90.0f;         // >90% reduction
    criteria.phase2.min_throughput_increase = 100.0f;      // >100% increase
    criteria.phase2.max_interrupt_latency_us = 5;          // <5μs interrupt
    criteria.phase2.max_timing_jitter_us = 1.0f;          // <1μs jitter
    criteria.phase2.max_error_rate_percent = 0.1f;        // <0.1% errors
    
    // Phase 3 criteria
    criteria.phase3.min_production_pass_rate = 99.0f;      // >99% pass rate
    criteria.phase3.max_test_duration_minutes = 10;        // <10 min test
    criteria.phase3.max_false_positive_rate = 0.1f;       // <0.1% false positives
    criteria.phase3.min_diagnostic_coverage = 95;          // >95% coverage
    
    g_auto_validator->set_acceptance_criteria(criteria);
    
    Serial.println("DMA Validation System initialized successfully!");
}

/**
 * @brief Start the automatic validation process
 * 
 * Begins the three-phase validation methodology automatically
 * progressing through all test scenarios.
 */
void start_dma_validation() {
    if (!g_auto_validator) {
        Serial.println("ERROR: Validation system not initialized!");
        return;
    }
    
    Serial.println("\n========================================");
    Serial.println("STARTING DMA AUTOMATIC VALIDATION");
    Serial.println("========================================");
    Serial.println("This will run the complete three-phase");
    Serial.println("validation methodology as specified in");
    Serial.println("the Season 04 Knowledge Base.");
    Serial.println("========================================\n");
    
    // Initialize SD card logging
    if (!g_auto_validator->initialize_sd_logging()) {
        Serial.println("WARNING: SD logging failed to initialize");
        Serial.println("Results will only be displayed on Serial");
    }
    
    // Start the validation
    if (g_auto_validator->start_validation()) {
        Serial.println("Validation started successfully!");
        Serial.println("Tests will run automatically at configured intervals.");
        Serial.println("Press 's' to stop validation at any time.");
        Serial.println("Press 'r' to show current results.");
        Serial.println("Press 'p' to show progress.");
    } else {
        Serial.println("ERROR: Failed to start validation!");
    }
}

/**
 * @brief Stop the validation process
 */
void stop_dma_validation() {
    if (g_auto_validator && g_auto_validator->is_validation_active()) {
        Serial.println("\nStopping validation...");
        g_auto_validator->stop_validation();
        
        // Print final summary
        g_auto_validator->print_validation_summary();
        
        // Export results to CSV
        g_auto_validator->export_results_to_csv();
        
        Serial.println("\nValidation stopped.");
    }
}

/**
 * @brief Handle user commands during validation
 */
void handle_validation_commands() {
    if (!Serial.available()) {
        return;
    }
    
    char cmd = Serial.read();
    
    switch (cmd) {
        case 's':
        case 'S':
            stop_dma_validation();
            break;
            
        case 'r':
        case 'R':
            if (g_auto_validator) {
                Serial.println("\n=== CURRENT RESULTS ===");
                g_auto_validator->print_validation_summary();
                
                // Show latest result
                auto latest = g_auto_validator->get_latest_result();
                Serial.print("\nLatest test: ");
                Serial.print(latest.test_name);
                Serial.print(" - ");
                Serial.println(latest.passed ? "PASS" : "FAIL");
            }
            break;
            
        case 'p':
        case 'P':
            if (g_auto_validator) {
                Serial.println("\n=== VALIDATION PROGRESS ===");
                Serial.print("Current Phase: ");
                Serial.println(dma_validation::dma_automatic_validation::phase_to_string(
                    g_auto_validator->get_current_phase()));
                Serial.print("Progress: ");
                Serial.print(g_auto_validator->get_progress_percentage());
                Serial.println("%");
                Serial.print("Estimated completion: ");
                Serial.print(g_auto_validator->get_estimated_completion_time() / 3600000);
                Serial.println(" hours");
                
                auto stats = g_auto_validator->get_statistics();
                Serial.print("Tests run: ");
                Serial.println(stats.total_tests_run);
                Serial.print("Pass rate: ");
                Serial.print((float)stats.total_tests_passed / 
                           (float)stats.total_tests_run * 100.0f);
                Serial.println("%");
            }
            break;
            
        case 'a':
        case 'A':
            if (g_auto_validator) {
                // Advance to next phase manually
                Serial.println("\nAdvancing to next phase...");
                if (g_auto_validator->advance_to_next_phase()) {
                    Serial.println("Advanced successfully!");
                } else {
                    Serial.println("Cannot advance - all phases complete or criteria not met");
                }
            }
            break;
            
        case 't':
        case 'T':
            if (g_auto_validator) {
                // Trigger external equipment manually
                Serial.println("\nTriggering external equipment...");
                g_auto_validator->manual_trigger();
            }
            break;
            
        case 'e':
        case 'E':
            if (g_auto_validator) {
                // Show environmental conditions
                float temp, voltage;
                uint8_t humidity;
                g_auto_validator->get_environmental_conditions(temp, voltage, humidity);
                Serial.println("\n=== ENVIRONMENTAL CONDITIONS ===");
                Serial.print("Temperature: ");
                Serial.print(temp);
                Serial.println(" C");
                Serial.print("Voltage: ");
                Serial.print(voltage);
                Serial.println(" V");
                Serial.print("Humidity: ");
                Serial.print(humidity);
                Serial.println(" %");
            }
            break;
            
        case 'h':
        case 'H':
        case '?':
            Serial.println("\n=== VALIDATION COMMANDS ===");
            Serial.println("s - Stop validation");
            Serial.println("r - Show current results");
            Serial.println("p - Show progress");
            Serial.println("a - Advance to next phase");
            Serial.println("t - Trigger external equipment");
            Serial.println("e - Show environmental conditions");
            Serial.println("h - Show this help");
            break;
    }
}

/**
 * @brief Run a specific validation phase
 * 
 * This function can be called to run a specific phase without
 * automatic progression.
 */
void run_validation_phase(dma_validation::dma_automatic_validation::validation_phase_t phase) {
    if (!g_auto_validator) {
        Serial.println("ERROR: Validation system not initialized!");
        return;
    }
    
    Serial.print("Running validation phase: ");
    Serial.println(dma_validation::dma_automatic_validation::phase_to_string(phase));
    
    g_auto_validator->set_validation_phase(phase);
    
    if (g_auto_validator->run_current_phase_tests()) {
        Serial.println("Phase tests completed successfully!");
        
        // Check if phase passed acceptance criteria
        if (g_auto_validator->check_phase_acceptance(phase)) {
            Serial.println("Phase PASSED acceptance criteria!");
        } else {
            Serial.println("Phase FAILED acceptance criteria!");
        }
    } else {
        Serial.println("ERROR: Phase tests failed to complete!");
    }
}

/**
 * @brief Example of how to integrate validation into main firmware
 * 
 * This would be called from the main setup() and loop() functions
 * when validation mode is enabled.
 */
void validation_setup() {
    // Check if validation mode is enabled (via jumper, switch, or compile flag)
    #ifdef ENABLE_DMA_VALIDATION
        g_validation_mode_enabled = true;
    #endif
    
    // Could also check a hardware jumper
    // pinMode(VALIDATION_MODE_PIN, INPUT_PULLUP);
    // g_validation_mode_enabled = (digitalRead(VALIDATION_MODE_PIN) == LOW);
    
    if (g_validation_mode_enabled) {
        Serial.println("\n========================================");
        Serial.println("DMA VALIDATION MODE ENABLED");
        Serial.println("========================================");
        
        // Initialize the validation system
        initialize_dma_validation_system();
        
        // Wait for user input
        Serial.println("\nPress ENTER to start validation or 'h' for help...");
        while (!Serial.available()) {
            delay(100);
        }
        
        char cmd = Serial.read();
        if (cmd == 'h' || cmd == 'H') {
            Serial.println("\n=== VALIDATION OPTIONS ===");
            Serial.println("1 - Run Phase 1 (Immediate Validation)");
            Serial.println("2 - Run Phase 2 (Advanced with Equipment)");
            Serial.println("3 - Run Phase 3 (Production Testing)");
            Serial.println("A - Run All Phases Automatically");
            Serial.println("Press corresponding key to continue...");
            
            while (!Serial.available()) {
                delay(100);
            }
            cmd = Serial.read();
        }
        
        switch (cmd) {
            case '1':
                run_validation_phase(
                    dma_validation::dma_automatic_validation::validation_phase_t::PHASE_1_IMMEDIATE);
                break;
            case '2':
                run_validation_phase(
                    dma_validation::dma_automatic_validation::validation_phase_t::PHASE_2_ADVANCED);
                break;
            case '3':
                run_validation_phase(
                    dma_validation::dma_automatic_validation::validation_phase_t::PHASE_3_PRODUCTION);
                break;
            case 'A':
            case 'a':
            default:
                start_dma_validation();
                break;
        }
    }
}

void validation_loop() {
    if (g_validation_mode_enabled && g_auto_validator) {
        // Handle user commands
        handle_validation_commands();
        
        // The validation runs in its own thread, so we just need to
        // keep the main loop alive and handle commands
        delay(10);
    }
}

/**
 * @brief Clean up validation system
 */
void cleanup_validation_system() {
    if (g_auto_validator) {
        if (g_auto_validator->is_validation_active()) {
            g_auto_validator->stop_validation();
        }
        delete g_auto_validator;
        g_auto_validator = nullptr;
    }
    
    if (g_monitor) {
        if (g_monitor->is_monitoring_active()) {
            g_monitor->stop_monitoring();
        }
        delete g_monitor;
        g_monitor = nullptr;
    }
    
    if (g_test_suite) {
        delete g_test_suite;
        g_test_suite = nullptr;
    }
    
    if (g_perf_validator) {
        delete g_perf_validator;
        g_perf_validator = nullptr;
    }
    
    if (g_error_handler) {
        delete g_error_handler;
        g_error_handler = nullptr;
    }
}

// Example integration with main firmware
#ifdef STANDALONE_VALIDATION

void setup() {
    Serial.begin(115200);
    while (!Serial) {
        delay(10);
    }
    
    Serial.println("Master of Muppets DMA Validation System");
    Serial.println("Season 04 - Comprehensive Hardware Validation");
    
    validation_setup();
}

void loop() {
    validation_loop();
}

#endif // STANDALONE_VALIDATION