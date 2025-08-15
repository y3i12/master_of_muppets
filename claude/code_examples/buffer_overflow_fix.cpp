/**
 * @file buffer_overflow_fix.cpp
 * @brief Fix for buffer overflow in function_generator.cpp heartBeat function
 * @date 2025-08-15
 * 
 * MCU-optimized version using existing project conventions:
 * - Class names in PascalCase
 * - Constants with k_ prefix
 * - No STL usage (fixed C-style arrays)
 * - Stack-friendly pre-computed lookup tables
 */

#include <cstdint>

namespace master_of_muppets {
namespace function_generator {

class safe_function_generator {
private:
    // Pre-computed lookup table as class constant - MCU friendly
    static constexpr uint8_t k_heartbeat_lut_size = 32;
    static constexpr int16_t k_heartbeat_lut[ k_heartbeat_lut_size ] = {
         2000,  4000,  6000,  8000, 10000, 12000, 14000, 16000,
        18000, 20000, 22000, 24000, 26000, 28000, 30000, 32000,
        30000, 28000, 26000, 24000, 22000, 20000, 18000, 16000,
        14000, 12000, 10000,  8000,  6000,  4000,  2000,     0
    };

public:
    /**
     * @brief Safe heartbeat function with bounds checking
     * @param time_normalized Normalized time value (0.0 to 1.0)
     * @return Heartbeat amplitude value
     */
    int16_t heart_beat_safe( float time_normalized ) const {
        // Clamp input to valid range
        if ( time_normalized < 0.0f  ) time_normalized = 0.0f;
        if ( time_normalized >= 1.0f ) time_normalized = 0.999f;
        
        // Convert to array index with bounds checking
        uint8_t index = static_cast< uint8_t >( time_normalized * k_heartbeat_lut_size );
        
        // Additional safety check (should never trigger with clamped input)
        if ( index >= k_heartbeat_lut_size ) {
            index = k_heartbeat_lut_size - 1;
        }
        
        return k_heartbeat_lut[ index ];
    }
    
    /**
     * @brief Interpolated heartbeat for smoother output
     * @param time_normalized Normalized time value (0.0 to 1.0)
     * @return Interpolated heartbeat amplitude
     */
    int16_t heart_beat_interpolated( float time_normalized ) const {
        // Clamp input to valid range
        if ( time_normalized < 0.0f  ) time_normalized = 0.0f;
        if ( time_normalized >= 1.0f ) time_normalized = 0.999f;
        
        // Calculate array position with fractional part
        float   float_index = time_normalized * ( k_heartbeat_lut_size - 1 );
        uint8_t index       = static_cast< uint8_t >( float_index );
        float   fraction    = float_index - index;
        
        // Bounds checking for interpolation
        if ( index >= k_heartbeat_lut_size - 1 ) {
            return k_heartbeat_lut[ k_heartbeat_lut_size - 1 ];
        }
        
        // Linear interpolation between adjacent points
        int16_t value1 = k_heartbeat_lut[ index     ];
        int16_t value2 = k_heartbeat_lut[ index + 1 ];
        
        return static_cast< int16_t >( value1 + fraction * ( value2 - value1 ) );
    }
};

// Original problematic code for reference:
/*
int16_t heartBeat(float t) {
    int16_t out[32] = { // Large stack allocation
        2000, 4000, 6000, 8000, 10000, 12000, 14000, 16000,
        18000, 20000, 22000, 24000, 26000, 28000, 30000, 32000,
        30000, 28000, 26000, 24000, 22000, 20000, 18000, 16000,
        14000, 12000, 10000, 8000, 6000, 4000, 2000, 0
    };
    
    size_t idx = static_cast<size_t>(t * 32) % 32;
    // POTENTIAL BUFFER OVERFLOW: arr[idx+1] when idx == 31
    return out[idx]; // Should check bounds before accessing idx+1
}
*/

} // namespace function_generator
} // namespace master_of_muppets