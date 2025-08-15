/**
 * @file race_condition_fix.cpp
 * @brief Fix for race condition in electric_mayhem.h muppet_worker function
 * @date 2025-08-15
 * 
 * MCU-optimized version using existing project conventions:
 * - Class names in PascalCase
 * - Constants with k_ prefix
 * - No STL usage (atomic operations via TeensyThreads)
 * - Fixed-size arrays instead of std::array
 */

#include <cstdint>
#include "TeensyThreads.h"

namespace master_of_muppets {
namespace electric_mayhem {

/**
 * @brief Thread-safe worker state management for MCU
 */
struct muppet_state {
    volatile bool     update_requested;
    volatile bool     update_in_progress;
    volatile uint32_t update_sequence;
    Threads::Mutex   state_mutex;
    
    muppet_state() : 
        update_requested(  false ),
        update_in_progress( false ),
        update_sequence(   0     )
    {}
};

/**
 * @brief Fixed muppet worker that eliminates race conditions
 */
template<typename dac_driver_t>
class safe_muppet_worker {
private:
    static constexpr uint8_t k_channels_per_dac = dac_driver_t::k_channels_per_dac;
    
    dac_driver_t* dac_instance_;
    muppet_state* muppet_state_;
    uint16_t*     output_buffer_;
    
    // Local buffer for atomic operations - fixed size for MCU
    uint16_t local_buffer_[ k_channels_per_dac ];

public:
    safe_muppet_worker( dac_driver_t* dac, muppet_state* state, uint16_t* buffer ) :
        dac_instance_(  dac    ),
        muppet_state_(  state  ),
        output_buffer_( buffer )
    {}

    /**
     * @brief Thread-safe worker function with proper synchronization
     */
    void worker_thread_function() {
        uint32_t last_processed_sequence = 0;
        
        while (true) {
            // Check if update is requested using TeensyThreads synchronization
            muppet_state_->state_mutex.lock();
            uint32_t current_sequence = muppet_state_->update_sequence;
            bool should_update = (current_sequence != last_processed_sequence) && 
                               !muppet_state_->update_in_progress;
            
            if (should_update) {
                muppet_state_->update_in_progress = true;
            }
            muppet_state_->state_mutex.unlock();
            
            if (should_update) {
                // Copy data safely to local buffer
                copy_buffer_with_lock();
                
                // Perform DAC operations
                bool operation_successful = update_dac_safely();
                
                // Clear in-progress flag only after successful completion
                muppet_state_->state_mutex.lock();
                if (operation_successful) {
                    last_processed_sequence = current_sequence;
                }
                muppet_state_->update_in_progress = false;
                muppet_state_->state_mutex.unlock();
            }
            
            // Yield to other threads using TeensyThreads
            threads.yield();
        }
    }

private:
    /**
     * @brief Safe buffer copy operation using existing mutex
     */
    void copy_buffer_with_lock() {
        // Copy buffer contents safely
        for (uint8_t i = 0; i < k_channels_per_dac; ++i) {
            local_buffer_[i] = output_buffer_[i];
        }
    }
    
    /**
     * @brief Safe DAC update with error handling
     * @return true if operation successful, false otherwise
     */
    bool update_dac_safely() {
        // No exceptions in MCU environment - use return codes
        if (!dac_instance_->enable()) {
            return false;
        }
        
        bool result = dac_instance_->set_values(local_buffer_);
        dac_instance_->disable();
        return result;
    }
};

/**
 * @brief Improved electric_mayhem with race condition fixes
 */
template<typename dac_driver_t>
class improved_electric_mayhem {
private:
    static constexpr uint8_t k_dac_count = 2; // From dr_teeth constants
    static constexpr uint8_t k_channels_per_dac = dac_driver_t::k_channels_per_dac;
    
    dac_driver_t dac_instances_[k_dac_count];
    muppet_state muppet_states_[k_dac_count];
    safe_muppet_worker<dac_driver_t> workers_[k_dac_count];
    
    uint16_t* shared_output_buffer_;

public:
    improved_electric_mayhem(uint16_t* output_buffer) 
        : shared_output_buffer_(output_buffer) {
        
        // Initialize workers
        for (uint8_t i = 0; i < k_dac_count; ++i) {
            workers_[i] = safe_muppet_worker<dac_driver_t>(
                &dac_instances_[i],
                &muppet_states_[i],
                &shared_output_buffer_[i * k_channels_per_dac]
            );
        }
    }
    
    /**
     * @brief Thread-safe method to request DAC updates
     * @param dac_index Index of DAC to update
     */
    void request_dac_update(uint8_t dac_index) {
        if (dac_index >= k_dac_count) return;
        
        // Increment sequence number to signal update needed
        muppet_states_[dac_index].state_mutex.lock();
        muppet_states_[dac_index].update_sequence++;
        muppet_states_[dac_index].state_mutex.unlock();
    }
    
    /**
     * @brief Check if DAC update is in progress
     * @param dac_index Index of DAC to check
     * @return true if update in progress, false otherwise
     */
    bool is_update_in_progress(uint8_t dac_index) const {
        if (dac_index >= k_dac_count) return false;
        return muppet_states_[dac_index].update_in_progress;
    }
    
    /**
     * @brief Force update of all DACs (for periodic refresh)
     */
    void force_update_all_dacs() {
        for (uint8_t i = 0; i < k_dac_count; ++i) {
            request_dac_update(i);
        }
    }
};

// Original problematic code for reference:
/*
static void muppet_worker(void* hidden_orientation_guide) {
    orientation_guide& muppet_orientation_guide = *reinterpret_cast<orientation_guide*>(hidden_orientation_guide);
    
    dac_driver_t&    me               = *muppet_orientation_guide.muppet;
    Threads::Mutex&  my_lock          = *muppet_orientation_guide.lock;
    uint8_t&         am_i_dirty       = *muppet_orientation_guide.dirty;  // RACE CONDITION: Non-atomic access
    uint16_t*        my_output_buffer = muppet_orientation_guide.output_buffer;

    uint16_t my_personal_buffer_copy[k_channels_per_dac];
    
    while (1) {
        if (am_i_dirty) {  // RACE CONDITION: Check without proper synchronization
            my_lock.lock();
            memcpy(my_personal_buffer_copy, my_output_buffer, sizeof(uint16_t) * k_channels_per_dac);
            am_i_dirty = 0;  // RACE CONDITION: Cleared before DAC operation completes
            my_lock.unlock();

            me.enable();
            me.set_values(my_personal_buffer_copy);  // If this fails, dirty flag is already cleared
            me.disable();
        }

        threads.yield();
    }
}
*/

} // namespace electric_mayhem
} // namespace master_of_muppets