#pragma once

#include "drivers/rob_tillaart_ad_5993r.h"
#include "drivers/dma_i2c_hal.h"
#include "TeensyThreads.h"

namespace drivers {

/**
 * @brief Asynchronous extension of the AD5593R driver
 * 
 * Extends the synchronous rob_tillaart_ad_5993r driver with DMA-based asynchronous operations.
 * Maintains full backward compatibility while adding non-blocking I2C transfer capabilities.
 */
class rob_tillaart_ad_5993r_async : public rob_tillaart_ad_5993r {
public:
    // Async operation completion callback type
    typedef void (*async_completion_callback_t)( bool success, dma_i2c_hal::error_code_t error, void* user_data );
    
    // Async operation status
    enum class async_status_t : uint8_t {
        READY = 0,          // Ready for new operation
        IN_PROGRESS,        // Async operation in progress
        COMPLETED,          // Last operation completed successfully
        ERROR_OCCURRED      // Last operation failed
    };
    
    // Statistics for monitoring async operations
    struct async_stats_t {
        uint32_t total_operations;
        uint32_t successful_operations;
        uint32_t failed_operations;
        uint32_t timeout_errors;
        uint32_t nak_errors;
        uint32_t dma_errors;
        uint32_t average_transfer_time_us;
        uint32_t max_transfer_time_us;
        
        async_stats_t() : 
            total_operations( 0 ), successful_operations( 0 ), failed_operations( 0 ),
            timeout_errors( 0 ), nak_errors( 0 ), dma_errors( 0 ),
            average_transfer_time_us( 0 ), max_transfer_time_us( 0 ) {}
    };

private:
    dma_i2c_hal dma_hal_;
    
    // Async operation state
    volatile async_status_t async_status_;
    async_completion_callback_t current_callback_;
    void* current_user_data_;
    Threads::Mutex async_mutex_;
    
    // Internal buffer for DMA operations (must be DMA-safe)
    uint8_t dma_write_buffer_[32] __attribute__((aligned(32)));
    
    // Statistics tracking
    async_stats_t stats_;
    uint32_t transfer_start_time_;
    
    // Static callback for DMA completion
    static void dma_completion_callback( dma_i2c_hal::transfer_state_t state, 
                                       dma_i2c_hal::error_code_t error, 
                                       void* user_data );
    
    // Helper functions
    void update_statistics( bool success, dma_i2c_hal::error_code_t error, uint32_t duration_us );
    bool prepare_dac_write_buffer( const value_t values[], uint8_t num_channels );
    void set_async_status( async_status_t status );

public:
    rob_tillaart_ad_5993r_async();
    virtual ~rob_tillaart_ad_5993r_async();
    
    // Enhanced initialization with DMA support
    void initialize_async( const initialization_struct_t& initialization_struct, 
                         uint8_t dma_channel = 0 );
    
    // Asynchronous operations (non-blocking)
    dma_i2c_hal::error_code_t set_values_async( const value_t values[], 
                                               async_completion_callback_t callback, 
                                               void* user_data = nullptr );
    
    dma_i2c_hal::error_code_t set_channel_value_async( uint8_t channel_index, 
                                                      value_t value,
                                                      async_completion_callback_t callback, 
                                                      void* user_data = nullptr );
    
    dma_i2c_hal::error_code_t set_all_channels_same_value_async( value_t value_for_all_channels,
                                                                async_completion_callback_t callback,
                                                                void* user_data = nullptr );
    
    // Status and monitoring operations
    async_status_t get_async_status() const;
    bool is_async_operation_complete() const;
    dma_i2c_hal::error_code_t get_last_async_error() const;
    
    // Blocking wait operations (with timeout)
    dma_i2c_hal::error_code_t wait_for_async_completion( uint32_t timeout_ms = 100 );
    
    // Abort ongoing async operation
    dma_i2c_hal::error_code_t abort_async_operation();
    
    // Statistics and diagnostics
    const async_stats_t& get_async_statistics() const { return stats_; }
    void reset_async_statistics();
    uint32_t get_current_transfer_duration_us() const;
    
    // Configuration and control
    void enable_async_mode() { /* DMA is always available when initialized */ }
    void disable_async_mode() { /* Falls back to sync operations */ }
    bool is_async_mode_available() const;
    
    // Thread safety utilities
    bool try_lock_async_operation( uint32_t timeout_ms = 10 );
    void unlock_async_operation();
};

} // namespace drivers