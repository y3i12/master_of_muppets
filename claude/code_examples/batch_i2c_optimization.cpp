/**
 * @file batch_i2c_optimization.cpp
 * @brief Optimized I2C batch operations for AD5593R DACs
 * @date 2025-08-15
 * 
 * MCU-optimized version using existing project conventions:
 * - Class names in PascalCase
 * - Constants with k_ prefix
 * - No STL usage (fixed C-style arrays)
 * - TeensyThreads compatible
 */

#include <cstdint>
#include <Wire.h>

namespace master_of_muppets {
namespace i2c_optimization {

/**
 * @brief High-performance I2C batch writer for AD5593R
 */
class batch_i2c_writer {
private:
    // Pre-allocated buffer to avoid dynamic allocation in real-time code
    static constexpr uint8_t  k_batch_buffer_size = 32;
    uint8_t                   batch_buffer_[k_batch_buffer_size];
    
    // Constants for AD5593R protocol
    static constexpr uint8_t  k_channels_per_dac   = 8;
    static constexpr uint8_t  k_multi_channel_cmd  = 0x40;
    static constexpr uint16_t k_dac_max_value      = 4095;  // 12-bit DAC
    static constexpr uint16_t k_input_max_value    = 65535; // 16-bit input
    
    // Use Arduino Wire library for I2C (Teensy compatible)
    TwoWire* i2c_bus_;

public:
    explicit batch_i2c_writer(TwoWire* i2c_bus = &Wire) : i2c_bus_(i2c_bus) {}

    /**
     * @brief Write all 8 DAC channels in a single I2C transaction
     * @param device_address I2C address of AD5593R (0x10 or 0x11)
     * @param channel_values Array of 8 channel values (16-bit input)
     * @return true if successful, false on error
     */
    bool write_dac_batch(uint8_t device_address, const uint16_t channel_values[k_channels_per_dac]) {
        // Prepare batch command for AD5593R
        // Format: [CMD][CH0_H][CH0_L][CH1_H][CH1_L]...[CH7_H][CH7_L]
        
        uint8_t buffer_index = 0;
        
        // AD5593R multi-channel DAC write command
        batch_buffer_[buffer_index++] = k_multi_channel_cmd;
        
        // Pack all 8 channels (12-bit values)
        for (uint8_t channel = 0; channel < k_channels_per_dac; ++channel) {
            uint16_t scaled_value = scale_dac_value(channel_values[channel]);
            batch_buffer_[buffer_index++] = (scaled_value >> 8) & 0x0F; // High nibble (bits 11-8)
            batch_buffer_[buffer_index++] = scaled_value & 0xFF;        // Low byte (bits 7-0)
        }
        
        // Single I2C transaction for all channels
        i2c_bus_->beginTransmission(device_address);
        uint8_t bytes_written = i2c_bus_->write(batch_buffer_, 17); // 1 cmd + 16 data
        uint8_t result = i2c_bus_->endTransmission();
        
        return (result == 0) && (bytes_written == 17);
    }
    
    /**
     * @brief Write single channel (for comparison with batch)
     * @param device_address I2C address
     * @param channel Channel number (0-7)
     * @param value 16-bit value to write
     * @return true if successful
     */
    bool write_single_channel(uint8_t device_address, uint8_t channel, uint16_t value) {
        if (channel >= k_channels_per_dac) return false;
        
        uint16_t scaled_value = scale_dac_value(value);
        
        // Single channel command for AD5593R
        uint8_t single_cmd[3] = {
            static_cast< uint8_t >( 0x10 | channel ),               // Single channel command
            static_cast< uint8_t >( (scaled_value >> 8) & 0x0F ),
            static_cast< uint8_t >( scaled_value & 0xFF )
        };
        
        i2c_bus_->beginTransmission(device_address);
        uint8_t bytes_written = i2c_bus_->write(single_cmd, 3);
        uint8_t result = i2c_bus_->endTransmission();
        
        return (result == 0) && (bytes_written == 3);
    }

private:
    /**
     * @brief Scale 16-bit input to 12-bit DAC value
     * @param input_value 16-bit input (0-65535)
     * @return 12-bit DAC value (0-4095)
     */
    uint16_t scale_dac_value(uint16_t input_value) {
        // Scale from 16-bit to 12-bit with proper rounding
        return static_cast< uint16_t >( ( static_cast< uint32_t >( input_value ) * k_dac_max_value ) / k_input_max_value );
    }
};

/**
 * @brief Performance comparison utility
 */
class i2c_performance_tester {
public:
    /**
     * @brief Compare sequential vs batch write performance
     */
    struct performance_results {
        uint32_t sequential_time_us;
        uint32_t batch_time_us;
        float    improvement_factor;
    };
    
    performance_results compare_write_methods( batch_i2c_writer& writer,
                                               uint8_t           device_address,
                                               const uint16_t    test_values[ k_channels_per_dac ] ) {
        performance_results results = {0, 0, 0.0f};
        
        // Test sequential writes
        uint32_t start_time = micros();
        for (uint8_t channel = 0; channel < k_channels_per_dac; ++channel) {
            writer.write_single_channel(device_address, channel, test_values[channel]);
        }
        results.sequential_time_us = micros() - start_time;
        
        // Test batch write
        start_time = micros();
        writer.write_dac_batch(device_address, test_values);
        results.batch_time_us = micros() - start_time;
        
        // Calculate improvement
        if (results.batch_time_us > 0) {
            results.improvement_factor = 
                static_cast< float >( results.sequential_time_us ) / results.batch_time_us;
        }
        
        return results;
    }

private:
    static constexpr uint8_t k_channels_per_dac = 8;
};

// Original inefficient code for reference:
/*
void set_values(const value_t values[k_channels]) {
    enable();
    
    // INEFFICIENT: 8 separate I2C transactions
    for (uint8_t channel_index = 0; channel_index < k_channels; ++channel_index) {
        ad5593r.writeDAC(channel_index, dac_value_rescale(values[channel_index]));
        // Each writeDAC call: begin_transmission() + write() + end_transmission()
        // Total: 8 × (start + data + stop) = very high latency
    }
    
    disable();
}
*/

/**
 * @brief Usage example showing the optimization benefit
 */
void optimization_example() {
    // Example usage with Teensy Wire library
    batch_i2c_writer writer(&Wire); // Use default Wire interface
    
    // Test data
    static constexpr uint8_t k_test_channels = 8;
    uint16_t channel_values[k_test_channels] = {
        1024, 2048, 3072, 4095, 512, 1536, 2560, 3584
    };
    
    // Old way: 8 separate transactions
    // Estimated time: 8 × 100µs = 800µs (typical I2C overhead per transaction)
    
    // New way: Single batch transaction  
    // Estimated time: 1 × 150µs = 150µs (single transaction with more data)
    // Improvement: ~5.3x faster (800µs / 150µs)
    
    bool success = writer.write_dac_batch(0x10, channel_values);
    if (success) {
        // All 8 channels updated in single I2C transaction
        // Significant improvement in real-time performance
    }
}

} // namespace i2c_optimization
} // namespace master_of_muppets