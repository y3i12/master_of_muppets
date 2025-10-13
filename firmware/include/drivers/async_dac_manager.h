#pragma once

#include "drivers/rob_tillaart_ad_5993r_async.h"
#include "drivers/dma_i2c_hal.h"
#include "TeensyThreads.h"

namespace drivers {

/**
 * @brief Thread-safe async operation manager for integration with electric_mayhem
 * 
 * Provides a higher-level interface for managing async DAC operations within
 * the Master of Muppets threading architecture.
 */
class async_dac_manager {
public:
    // Operation completion state for thread communication
    struct operation_state_t {
        volatile bool operation_pending;
        volatile bool operation_completed;
        volatile dma_i2c_hal::error_code_t last_error;
        volatile uint32_t completion_sequence;
        Threads::Mutex state_mutex;
        
        operation_state_t() :
            operation_pending( false ),
            operation_completed( false ),
            last_error( dma_i2c_hal::error_code_t::SUCCESS ),
            completion_sequence( 0 )
        {}
    };

private:
    rob_tillaart_ad_5993r_async* async_driver_;
    operation_state_t operation_state_;
    uint32_t next_operation_sequence_;
    
    // Static callback for async driver completion
    static void async_operation_callback( bool success, dma_i2c_hal::error_code_t error, void* user_data );
    
public:
    async_dac_manager( rob_tillaart_ad_5993r_async* driver );
    ~async_dac_manager();
    
    // High-level async operations for worker threads
    bool initiate_async_update( const rob_tillaart_ad_5993r::value_t values[] );
    bool is_operation_pending() const;
    bool is_operation_completed() const;
    uint32_t get_completion_sequence() const;
    dma_i2c_hal::error_code_t get_operation_result();
    
    // Integration with muppet_state sequence tracking
    bool check_and_clear_completion( uint32_t expected_sequence );
    void reset_operation_state();
    
    // Error handling and recovery
    bool has_operation_error() const;
    void force_operation_completion(); // For error recovery
};

} // namespace drivers