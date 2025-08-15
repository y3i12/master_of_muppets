/**
 * @file configuration_manager.cpp
 * @brief Centralized configuration management system with EEPROM persistence
 * @date 2025-08-15
 * 
 * MCU-optimized version using existing project conventions:
 * - Class names in PascalCase
 * - Constants with k_ prefix
 * - No STL usage (fixed C-style arrays)
 * - EEPROM library for Teensy
 */

#include <cstdint>
#include <cstring>
#include <EEPROM.h>

namespace master_of_muppets {
namespace configuration {

/**
 * @brief System configuration structure with k_ constants
 */
struct system_config {
    // Hardware configuration
    uint8_t k_dac_count = 2;
    uint8_t k_channels_per_dac = 8;
    uint16_t k_max_refresh_rate_hz = 1000;
    uint8_t k_i2c_addresses[4] = {0x10, 0x11, 0x12, 0x13};
    
    // MIDI settings
    bool k_enable_velocity_to_cv = false;
    bool k_enable_aftertouch_to_cv = false;
    bool k_enable_cc_to_cv = false;
    uint8_t k_pitch_bend_range_semitones = 12;
    uint8_t k_midi_input_channel = 0; // 0 = omni, 1-16 = specific channel
    
    // Hardware settings  
    bool k_enable_ldac_synchronization = true;
    uint8_t k_ldac_pins[4] = {2, 3, 4, 5};
    
    // Calibration settings
    bool k_auto_calibration_enabled = false;
    float k_channel_offset_volts[16]; // Per-channel offset - initialized to 0 in constructor
    float k_channel_scale_factor[16]; // Per-channel scaling - initialized to 1.0 in constructor
    
    // Performance settings
    uint8_t k_thread_priority_midi = 99;
    uint8_t k_thread_priority_dac = 80;
    uint16_t k_i2c_clock_speed_khz = 400;
    
    // Version and validation
    uint32_t k_config_version = 1;
    uint32_t k_checksum = 0;
    
    // Constructor to initialize arrays
    system_config() {
        for (uint8_t i = 0; i < 16; ++i) {
            k_channel_offset_volts[i] = 0.0f;
            k_channel_scale_factor[i] = 1.0f;
        }
    }
};

/**
 * @brief Channel mapping configuration for advanced MIDI processing
 */
struct channel_mapping {
    enum class CvMode : uint8_t {
        k_pitch_bend = 0,
        k_note_velocity = 1,
        k_cc_value = 2,
        k_aftertouch = 3,
        k_gate_trigger = 4,
        k_lfo_output = 5
    };
    
    uint8_t k_midi_channel = 1;        // 1-16, 0 = disabled
    CvMode k_mode = CvMode::k_pitch_bend;
    uint8_t k_cc_number = 1;           // For CC_VALUE mode
    float k_scale_factor = 1.0f;       // Output scaling
    float k_offset_volts = 0.0f;       // Output offset
    bool k_invert_output = false;      // Invert signal
    
    // Range limiting
    float k_min_output_volts = 0.0f;
    float k_max_output_volts = 10.0f;
};

/**
 * @brief Comprehensive configuration_manager with persistence
 */
class configuration_manager {
private:
    static constexpr uint16_t k_eeprom_config_address = 0x00;
    static constexpr uint16_t k_eeprom_mapping_address = 0x100;
    static constexpr uint32_t k_config_magic_number = 0x4D555050; // "MUPP" in hex - Muppet theme!
    static constexpr uint8_t k_max_channels = 16;
    
    system_config current_config_;
    channel_mapping channel_mappings_[k_max_channels];
    bool config_dirty_ = false;
    
public:
    configuration_manager() {
        initialize_default_config();
    }
    
    /**
     * @brief Load configuration from EEPROM with validation
     * @return true if valid configuration loaded, false if defaults used
     */
    bool load_from_eeprom() {
        system_config loaded_config;
        
        // Read configuration structure from EEPROM
        if (!read_eeprom_block(k_eeprom_config_address, 
                              reinterpret_cast<uint8_t*>(&loaded_config),
                              sizeof(system_config))) {
            return false;
        }
        
        // Validate configuration
        if (!validate_configuration(loaded_config)) {
            initialize_default_config();
            return false;
        }
        
        // Load channel mappings
        if (!read_eeprom_block(k_eeprom_mapping_address,
                              reinterpret_cast<uint8_t*>(channel_mappings_),
                              sizeof(channel_mappings_))) {
            initialize_default_mappings();
        }
        
        current_config_ = loaded_config;
        config_dirty_ = false;
        return true;
    }
    
    /**
     * @brief Save current configuration to EEPROM
     * @return true if successfully saved
     */
    bool save_to_eeprom() {
        // Calculate and update checksum
        current_config_.checksum = calculate_checksum(current_config_);
        
        // Write configuration
        bool config_saved = write_eeprom_block(k_eeprom_config_address,
                                              reinterpret_cast<const uint8_t*>(&current_config_),
                                              sizeof(system_config));
        
        // Write channel mappings
        bool mappings_saved = write_eeprom_block(k_eeprom_mapping_address,
                                                reinterpret_cast<const uint8_t*>(channel_mappings_),
                                                sizeof(channel_mappings_));
        
        if (config_saved && mappings_saved) {
            config_dirty_ = false;
            return true;
        }
        
        return false;
    }
    
    /**
     * @brief Apply configuration changes at runtime
     * @param new_config Configuration to apply
     * @return true if successfully applied
     */
    bool apply_runtime_config(const system_config& new_config) {
        if (!validate_configuration(new_config)) {
            return false;
        }
        
        // Check what needs to be reconfigured
        bool need_i2c_reconfig = (new_config.i2c_clock_speed_khz != current_config_.i2c_clock_speed_khz);
        bool need_dac_reconfig = (new_config.dac_count != current_config_.dac_count);
        bool need_thread_reconfig = (new_config.thread_priority_midi != current_config_.thread_priority_midi);
        
        // Apply changes in safe order
        current_config_ = new_config;
        config_dirty_ = true;
        
        // Reconfigure subsystems as needed
        if (need_i2c_reconfig) {
            reconfigure_i2c_bus();
        }
        
        if (need_dac_reconfig) {
            reconfigure_dac_system();
        }
        
        if (need_thread_reconfig) {
            reconfigure_thread_priorities();
        }
        
        return true;
    }
    
    /**
     * @brief Get current system configuration
     */
    const system_config& get_system_config() const {
        return current_config_;
    }
    
    /**
     * @brief Set channel mapping for specific channel
     * @param channel_index Channel number (0-15)
     * @param mapping New channel mapping configuration
     */
    void set_channel_mapping(uint8_t channel_index, const channel_mapping& mapping) {
        if (channel_index < k_max_channels) {
            channel_mappings_[channel_index] = mapping;
            config_dirty_ = true;
        }
    }
    
    /**
     * @brief Get channel mapping for specific channel
     */
    const channel_mapping& get_channel_mapping(uint8_t channel_index) const {
        if (channel_index < k_max_channels) {
            return channel_mappings_[channel_index];
        }
        static const channel_mapping default_mapping = {};
        return default_mapping;
    }
    
    /**
     * @brief Check if configuration has unsaved changes
     */
    bool is_config_dirty() const {
        return config_dirty_;
    }
    
    /**
     * @brief Reset to factory defaults
     */
    void reset_to_defaults() {
        initialize_default_config();
        initialize_default_mappings();
        config_dirty_ = true;
    }
    
    /**
     * @brief Export configuration as JSON string (for web interface)
     * @param buffer Output buffer for JSON string
     * @param buffer_size Size of output buffer
     * @return true if successfully exported
     */
    bool export_to_json(char* buffer, size_t buffer_size) const {
        // Implementation would serialize configuration to JSON
        // This is a placeholder for the concept - would use sprintf for MCU
        if (buffer_size > 50) {
            strcpy(buffer, "{\"version\":1,\"config\":{...}}");
            return true;
        }
        return false;
    }
    
    /**
     * @brief Import configuration from JSON string
     * @param json_data JSON string to parse
     * @return true if successfully imported
     */
    bool import_from_json(const char* json_data) {
        // Implementation would parse JSON and update configuration
        // This is a placeholder for the concept - would use custom parser for MCU
        return false;
    }

private:
    /**
     * @brief Initialize default system configuration
     */
    void initialize_default_config() {
        current_config_ = SystemConfig{}; // Use default values from struct
        current_config_.config_version = 1;
        current_config_.checksum = calculate_checksum(current_config_);
    }
    
    /**
     * @brief Initialize default channel mappings
     */
    void initialize_default_mappings() {
        for (uint8_t i = 0; i < k_max_channels; ++i) {
            channel_mappings_[i] = channel_mapping{};
            channel_mappings_[i].k_midi_channel = static_cast<uint8_t>(i + 1); // Channels 1-16
        }
    }
    
    /**
     * @brief Validate configuration structure
     */
    bool validate_configuration(const system_config& config) const {
        // Check version compatibility
        if (config.k_config_version > 1) {
            return false;
        }
        
        // Validate ranges
        if (config.k_dac_count > 4 || config.k_dac_count == 0) return false;
        if (config.k_channels_per_dac > 8 || config.k_channels_per_dac == 0) return false;
        if (config.k_max_refresh_rate_hz > 10000 || config.k_max_refresh_rate_hz < 100) return false;
        if (config.k_pitch_bend_range_semitones > 24) return false;
        if (config.k_i2c_clock_speed_khz > 1000 || config.k_i2c_clock_speed_khz < 100) return false;
        
        // Validate checksum
        uint32_t calculated_checksum = calculate_checksum(config);
        if (calculated_checksum != config.k_checksum) {
            return false;
        }
        
        return true;
    }
    
    /**
     * @brief Calculate CRC32 checksum for configuration
     */
    uint32_t calculate_checksum(const system_config& config) const {
        // Simple CRC32 calculation (placeholder implementation)
        uint32_t crc = 0xFFFFFFFF;
        const uint8_t* data = reinterpret_cast<const uint8_t*>(&config);
        size_t length = sizeof(system_config) - sizeof(config.k_checksum);
        
        for (size_t i = 0; i < length; ++i) {
            crc ^= data[i];
            for (int j = 0; j < 8; ++j) {
                crc = (crc >> 1) ^ (0xEDB88320 * (crc & 1));
            }
        }
        
        return ~crc;
    }
    
    /**
     * @brief Platform-specific EEPROM read operation
     */
    bool read_eeprom_block(uint16_t address, uint8_t* data, size_t length) {
        // Teensy EEPROM read implementation
        for (size_t i = 0; i < length; ++i) {
            data[i] = EEPROM.read(address + i);
        }
        return true;
    }
    
    /**
     * @brief Platform-specific EEPROM write operation
     */
    bool write_eeprom_block(uint16_t address, const uint8_t* data, size_t length) {
        // Teensy EEPROM write implementation with wear leveling awareness
        for (size_t i = 0; i < length; ++i) {
            EEPROM.update(address + i, data[i]); // update() only writes if different
        }
        return true;
    }
    
    /**
     * @brief Reconfigure I2C bus with new settings
     */
    void reconfigure_i2c_bus() {
        // Implementation would reconfigure I2C clock speed
    }
    
    /**
     * @brief Reconfigure DAC system with new settings
     */
    void reconfigure_dac_system() {
        // Implementation would reinitialize DAC drivers
    }
    
    /**
     * @brief Reconfigure thread priorities
     */
    void reconfigure_thread_priorities() {
        // Implementation would update thread priorities
    }
};

/**
 * @brief Global configuration manager instance
 */
extern configuration_manager g_config_manager;

/**
 * @brief Convenience functions for common configuration operations
 */
namespace config_helpers {

/**
 * @brief Get number of active channels based on configuration
 */
inline uint8_t get_total_channels() {
    const system_config& config = g_config_manager.get_system_config();
    return config.k_dac_count * config.k_channels_per_dac;
}

/**
 * @brief Get I2C address for specific DAC
 */
inline uint8_t get_dac_i2c_address(uint8_t dac_index) {
    const system_config& config = g_config_manager.get_system_config();
    if (dac_index < 4) { // Max 4 DACs supported
        return config.k_i2c_addresses[dac_index];
    }
    return 0x10; // Default address
}

/**
 * @brief Check if LDAC synchronization is enabled
 */
inline bool is_ldac_sync_enabled() {
    return g_config_manager.get_system_config().k_enable_ldac_synchronization;
}

} // namespace config_helpers

} // namespace configuration
} // namespace master_of_muppets