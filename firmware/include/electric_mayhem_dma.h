#pragma once

#include "dr_teeth.h"
#include "TeensyThreads.h"
#include "drivers/rob_tillaart_ad_5993r_async.h"
#include "drivers/rob_tillaart_ad_5993r.h"

/**
 * @brief Enhanced electric_mayhem controller with DMA support
 * 
 * Extends the original electric_mayhem template class to support both synchronous
 * and asynchronous DMA-based DAC operations. Maintains backward compatibility
 * while providing significant performance improvements.
 */
template < typename dac_driver_t > 
class electric_mayhem_dma {
public:
    static const uint8_t k_channels_per_dac = dac_driver_t::k_channels;
    
    typedef typename dac_driver_t::value_t                  value_t;
    typedef typename dac_driver_t::initialization_struct_t  initialization_struct_t;
    
    // DMA operation modes
    enum class dma_mode_t : uint8_t {
        DISABLED = 0,       // Use synchronous operations only
        ENABLED,           // Use DMA when available, fallback to sync
        REQUIRED           // DMA required, fail if not available
    };
    
    // Enhanced statistics for DMA operations
    struct dma_statistics_t {
        uint32_t total_dma_operations;
        uint32_t successful_dma_operations;
        uint32_t fallback_to_sync_operations;
        uint32_t dma_errors;
        uint32_t average_dma_time_us;
        uint32_t max_dma_time_us;
        uint32_t thread_blocking_time_saved_us;
        
        dma_statistics_t() :
            total_dma_operations(0), successful_dma_operations(0),
            fallback_to_sync_operations(0), dma_errors(0),
            average_dma_time_us(0), max_dma_time_us(0),
            thread_blocking_time_saved_us(0) {}
    };
    
    electric_mayhem_dma(dma_mode_t mode = dma_mode_t::ENABLED);
    
    void initialize(const initialization_struct_t initialization_struct[ dr_teeth::k_dac_count ],
                   const uint8_t dma_channels[ dr_teeth::k_dac_count ] = nullptr);

    bool attention_please( uint8_t muppet_index );
    void hey_you( uint8_t muppet_index );
    void thanks( uint8_t muppet_index );

    void throw_muppet_in_the_mud( uint8_t muppet_index );
    void shit_storm( void );
    
    void put_muppet_to_work( uint8_t muppet_index );
    
    // DMA-specific operations
    void set_dma_mode(dma_mode_t mode) { dma_mode_ = mode; }
    dma_mode_t get_dma_mode() const { return dma_mode_; }
    bool is_dma_available() const;
    
    // Statistics and monitoring
    const dma_statistics_t& get_dma_statistics() const { return dma_stats_; }
    void reset_dma_statistics();

protected:
    /**
     * @brief Enhanced thread-safe state management with DMA support
     */
    struct muppet_state_dma {
        // Original synchronization fields
        volatile bool     update_requested;
        volatile bool     update_in_progress;
        volatile uint32_t update_sequence;
        Threads::Mutex    state_mutex;
        
        // DMA-specific fields
        volatile bool     dma_operation_pending;
        volatile bool     dma_operation_completed;
        volatile uint32_t dma_completion_sequence;
        volatile uint32_t dma_error_count;
        volatile uint32_t last_dma_duration_us;
        
        // Async DAC manager for high-level DMA operations
        drivers::async_dac_manager* async_manager;
        
        muppet_state_dma() : 
            update_requested(false),
            update_in_progress(false),
            update_sequence(0),
            dma_operation_pending(false),
            dma_operation_completed(false),
            dma_completion_sequence(0),
            dma_error_count(0),
            last_dma_duration_us(0),
            async_manager(nullptr)
        {}
    };

    struct orientation_guide_dma {
        orientation_guide_dma( void ) : 
            muppet(nullptr), lock(nullptr), state(nullptr), output_buffer(nullptr), 
            async_driver(nullptr), manager_instance(nullptr) {}
            
        orientation_guide_dma( dac_driver_t& the_muppet, 
                              Threads::Mutex& the_lock, 
                              muppet_state_dma& the_state, 
                              uint16_t* the_buffer,
                              drivers::rob_tillaart_ad_5993r_async* the_async_driver = nullptr ) :
            muppet(&the_muppet),
            lock(&the_lock),
            state(&the_state),
            output_buffer(the_buffer),
            async_driver(the_async_driver),
            manager_instance(nullptr)
        { }

        dac_driver_t*                                  muppet;
        Threads::Mutex*                               lock;
        muppet_state_dma*                             state;
        uint16_t*                                     output_buffer;
        drivers::rob_tillaart_ad_5993r_async*         async_driver;
        electric_mayhem_dma<dac_driver_t>*            manager_instance;
    };

    // Member variables
    dac_driver_t                                     muppets_[ dr_teeth::k_dac_count ];
    drivers::rob_tillaart_ad_5993r_async*           async_muppets_[ dr_teeth::k_dac_count ];
    drivers::async_dac_manager*                     async_managers_[ dr_teeth::k_dac_count ];
    orientation_guide_dma                           muppet_orientation_guides_[ dr_teeth::k_dac_count ];
    Threads::Mutex                                  muppet_lock_[ dr_teeth::k_dac_count ];
    muppet_state_dma                                muppet_states_[ dr_teeth::k_dac_count ];
    
    dma_mode_t                                      dma_mode_;
    dma_statistics_t                                dma_stats_;
    Threads::Mutex                                  stats_mutex_;

    inline bool valid_dac(     uint8_t muppet_index  ) { return muppet_index  < dr_teeth::k_dac_count; }
    inline bool valid_channel( uint8_t channel_index ) { return channel_index < k_channels_per_dac;    }

    // Enhanced worker thread with DMA support
    static void muppet_worker_dma( void* hidden_orientation_guide ) {
        orientation_guide_dma& guide = *reinterpret_cast< orientation_guide_dma* >( hidden_orientation_guide );
        
        dac_driver_t&                                  me = *guide.muppet;
        Threads::Mutex&                               my_lock = *guide.lock;
        muppet_state_dma&                             my_state = *guide.state;
        uint16_t*                                     my_output_buffer = guide.output_buffer;
        drivers::rob_tillaart_ad_5993r_async*         async_me = guide.async_driver;
        electric_mayhem_dma<dac_driver_t>*            manager = guide.manager_instance;

        uint16_t                                      my_personal_buffer_copy[ k_channels_per_dac ];
        uint32_t                                      last_processed_sequence = 0;
        uint32_t                                      operation_start_time = 0;
        bool                                          use_dma = false;
        
        while ( 1 ) {
            // Check for pending DMA completion first
            if (my_state.dma_operation_pending && async_me && my_state.async_manager) {
                if (my_state.async_manager->is_operation_completed()) {
                    // Handle DMA completion
                    uint32_t completion_time = micros();
                    uint32_t operation_duration = completion_time - operation_start_time;
                    
                    my_state.state_mutex.lock();
                    my_state.dma_operation_pending = false;
                    my_state.dma_operation_completed = true;
                    my_state.last_dma_duration_us = operation_duration;
                    my_state.update_in_progress = false;
                    
                    bool success = !my_state.async_manager->has_operation_error();
                    if (success) {
                        last_processed_sequence = my_state.update_sequence;
                        my_state.dma_completion_sequence = last_processed_sequence;
                    } else {
                        my_state.dma_error_count++;
                    }
                    
                    my_state.state_mutex.unlock();
                    
                    // Update statistics
                    if (manager) {
                        manager->update_dma_statistics(success, operation_duration);
                    }
                    
                    // Clear the completion state for next operation
                    my_state.async_manager->reset_operation_state();
                }
            }
            
            // Check if new update is requested using thread-safe synchronization
            my_state.state_mutex.lock();
            uint32_t current_sequence = my_state.update_sequence;
            bool should_update = (current_sequence != last_processed_sequence) && 
                                !my_state.update_in_progress &&
                                !my_state.dma_operation_pending;
            
            if (should_update) {
                my_state.update_in_progress = true;
                // Determine if we should use DMA based on availability and mode
                use_dma = async_me && my_state.async_manager && 
                         (manager && manager->get_dma_mode() != dma_mode_t::DISABLED) &&
                         async_me->is_async_mode_available();
            }
            my_state.state_mutex.unlock();
            
            if (should_update) {
                // Copy data safely to local buffer (this part remains the same)
                my_lock.lock();
                memcpy(my_personal_buffer_copy, my_output_buffer, sizeof(uint16_t) * k_channels_per_dac);
                my_lock.unlock();
                
                operation_start_time = micros();
                bool operation_successful = false;
                
                if (use_dma) {
                    // Attempt DMA operation
                    me.enable();
                    
                    // Convert to value_t array for async driver
                    typename dac_driver_t::value_t async_values[k_channels_per_dac];
                    for (uint8_t i = 0; i < k_channels_per_dac; ++i) {
                        async_values[i] = static_cast<typename dac_driver_t::value_t>(my_personal_buffer_copy[i]);
                    }
                    
                    // Initiate async operation
                    bool async_started = my_state.async_manager->initiate_async_update(async_values);
                    
                    if (async_started) {
                        // DMA operation started successfully
                        my_state.state_mutex.lock();
                        my_state.dma_operation_pending = true;
                        my_state.dma_operation_completed = false;
                        my_state.state_mutex.unlock();
                        
                        operation_successful = true; // Will be validated on completion
                        
                        // Update statistics for DMA attempt
                        if (manager) {
                            manager->increment_dma_operation_count();
                        }
                    } else {
                        // DMA failed to start, fall back to synchronous operation
                        me.set_values(my_personal_buffer_copy);
                        me.disable();
                        operation_successful = true;
                        
                        // Update statistics for fallback
                        if (manager) {
                            manager->increment_sync_fallback_count();
                        }
                        
                        // Clear in-progress flag immediately for sync operation
                        my_state.state_mutex.lock();
                        my_state.update_in_progress = false;
                        last_processed_sequence = current_sequence;
                        my_state.state_mutex.unlock();
                    }
                } else {
                    // Use synchronous operation (original behavior)
                    me.enable();
                    me.set_values(my_personal_buffer_copy);
                    me.disable();
                    operation_successful = true;
                    
                    // Clear in-progress flag for sync operation
                    my_state.state_mutex.lock();
                    if (operation_successful) {
                        last_processed_sequence = current_sequence;
                    }
                    my_state.update_in_progress = false;
                    my_state.state_mutex.unlock();
                    
                    // Update statistics
                    if (manager) {
                        uint32_t sync_duration = micros() - operation_start_time;
                        manager->increment_sync_fallback_count();
                    }
                }
            }

            threads.yield();
        }
    }

    static void party_pooper( void* the_electric_mayhem_in_disguise ) {
        electric_mayhem_dma< dac_driver_t >& the_electric_mayhem = 
            *reinterpret_cast< electric_mayhem_dma< dac_driver_t >* >( the_electric_mayhem_in_disguise );
        
        while ( 1 ) {
            the_electric_mayhem.shit_storm();
            threads.delay( dr_teeth::k_force_refresh_every_millis );
        }
    }
    
    // Statistics update methods
    void update_dma_statistics(bool success, uint32_t duration_us);
    void increment_dma_operation_count();
    void increment_sync_fallback_count();
    
    // Template specialization for async driver initialization
    void initialize_async_driver(uint8_t muppet_index, const initialization_struct_t& init_struct, uint8_t dma_channel);
};

// Template method implementations

template < class dac_driver_t >
electric_mayhem_dma< dac_driver_t >::electric_mayhem_dma(dma_mode_t mode) :
    dma_mode_(mode)
{
    // Initialize async driver pointers
    for (uint8_t i = 0; i < dr_teeth::k_dac_count; ++i) {
        async_muppets_[i] = nullptr;
        async_managers_[i] = nullptr;
    }
}

template < class dac_driver_t >
void electric_mayhem_dma< dac_driver_t >::initialize( const initialization_struct_t initialization_struct[ dr_teeth::k_dac_count ],
                                                      const uint8_t dma_channels[ dr_teeth::k_dac_count ] ) {
    // Initialize muppet states with initial update request
    for ( uint8_t i = 0; i < dr_teeth::k_dac_count; ++i ) {
        muppet_states_[ i ].update_sequence = 1; // Request initial update
    }
    threads.setSliceMicros( dr_teeth::k_thread_slice_micros );

    for ( uint8_t muppet_index = 0; muppet_index < dr_teeth::k_dac_count; ++muppet_index ) {
        // Initialize base synchronous driver
        muppets_[ muppet_index ].initialize( initialization_struct[ muppet_index ] );
        
        // Initialize DMA driver if requested and available
        if (dma_mode_ != dma_mode_t::DISABLED && dma_channels) {
            initialize_async_driver(muppet_index, initialization_struct[muppet_index], dma_channels[muppet_index]);
        }
        
        put_muppet_to_work( muppet_index );
    }

    threads.addThread( party_pooper, this );
}

template < class dac_driver_t >
bool electric_mayhem_dma< dac_driver_t >::attention_please( uint8_t muppet_index ) {
    return muppet_lock_[ muppet_index ].lock( );
}

template < class dac_driver_t >
void electric_mayhem_dma< dac_driver_t >::hey_you( uint8_t muppet_index ) {
    muppet_lock_[ muppet_index ].lock( );
}

template < class dac_driver_t >
void electric_mayhem_dma< dac_driver_t >::thanks( uint8_t muppet_index ) {
    muppet_lock_[ muppet_index ].unlock( );
}

template < class dac_driver_t >
void electric_mayhem_dma< dac_driver_t >::throw_muppet_in_the_mud( uint8_t muppet_index ) {
    if ( muppet_index >= dr_teeth::k_dac_count ) return;
    
    // Thread-safe update request using sequence increment
    muppet_states_[ muppet_index ].state_mutex.lock();
    muppet_states_[ muppet_index ].update_sequence++;
    muppet_states_[ muppet_index ].state_mutex.unlock();
}

template < class dac_driver_t >
void electric_mayhem_dma< dac_driver_t >::shit_storm( void ) {
    for ( uint8_t muppet_index = 0; muppet_index < dr_teeth::k_dac_count; ++muppet_index ) {
        throw_muppet_in_the_mud( muppet_index );
    }
}

template < class dac_driver_t >
void electric_mayhem_dma< dac_driver_t >::put_muppet_to_work( uint8_t muppet_index ) {
    muppet_orientation_guides_[ muppet_index ] = orientation_guide_dma( 
        muppets_[ muppet_index ], 
        muppet_lock_[ muppet_index ], 
        muppet_states_[ muppet_index ],
        dr_teeth::output_buffer + muppet_index * k_channels_per_dac,
        async_muppets_[ muppet_index ]
    );
    
    muppet_orientation_guides_[ muppet_index ].manager_instance = this;

    threads.addThread( muppet_worker_dma, &muppet_orientation_guides_[ muppet_index ] );
}

template < class dac_driver_t >
bool electric_mayhem_dma< dac_driver_t >::is_dma_available() const {
    for (uint8_t i = 0; i < dr_teeth::k_dac_count; ++i) {
        if (async_muppets_[i] && async_muppets_[i]->is_async_mode_available()) {
            return true;
        }
    }
    return false;
}

template < class dac_driver_t >
void electric_mayhem_dma< dac_driver_t >::reset_dma_statistics() {
    stats_mutex_.lock();
    dma_stats_ = dma_statistics_t();
    stats_mutex_.unlock();
}

template < class dac_driver_t >
void electric_mayhem_dma< dac_driver_t >::update_dma_statistics(bool success, uint32_t duration_us) {
    stats_mutex_.lock();
    
    dma_stats_.total_dma_operations++;
    
    if (success) {
        dma_stats_.successful_dma_operations++;
        
        // Update timing statistics
        if (duration_us > dma_stats_.max_dma_time_us) {
            dma_stats_.max_dma_time_us = duration_us;
        }
        
        // Rolling average
        if (dma_stats_.successful_dma_operations == 1) {
            dma_stats_.average_dma_time_us = duration_us;
        } else {
            dma_stats_.average_dma_time_us = 
                (dma_stats_.average_dma_time_us * 7 + duration_us) / 8;
        }
        
        // Estimate time saved vs synchronous operation (assume ~160us for sync)
        if (duration_us < 160) {
            dma_stats_.thread_blocking_time_saved_us += (160 - duration_us);
        }
    } else {
        dma_stats_.dma_errors++;
    }
    
    stats_mutex_.unlock();
}

template < class dac_driver_t >
void electric_mayhem_dma< dac_driver_t >::increment_dma_operation_count() {
    stats_mutex_.lock();
    dma_stats_.total_dma_operations++;
    stats_mutex_.unlock();
}

template < class dac_driver_t >
void electric_mayhem_dma< dac_driver_t >::increment_sync_fallback_count() {
    stats_mutex_.lock();
    dma_stats_.fallback_to_sync_operations++;
    stats_mutex_.unlock();
}

// Template specialization for rob_tillaart_ad_5993r driver
template<>
void electric_mayhem_dma<drivers::rob_tillaart_ad_5993r>::initialize_async_driver(
    uint8_t muppet_index, 
    const drivers::rob_tillaart_ad_5993r::initialization_struct_t& init_struct, 
    uint8_t dma_channel) {
    
    // Create and initialize async version of rob_tillaart_ad_5993r
    async_muppets_[muppet_index] = new drivers::rob_tillaart_ad_5993r_async();
    async_muppets_[muppet_index]->initialize_async(init_struct, dma_channel);
    
    // Create async manager
    async_managers_[muppet_index] = new drivers::async_dac_manager(async_muppets_[muppet_index]);
    muppet_states_[muppet_index].async_manager = async_managers_[muppet_index];
}

// Generic template implementation for drivers without async support
template < class dac_driver_t >
void electric_mayhem_dma< dac_driver_t >::initialize_async_driver(
    uint8_t muppet_index, 
    const typename dac_driver_t::initialization_struct_t& init_struct, 
    uint8_t dma_channel) {
    
    // No async support available for this driver type
    // DMA operations will automatically fall back to sync operations
    async_muppets_[muppet_index] = nullptr;
    async_managers_[muppet_index] = nullptr;
    muppet_states_[muppet_index].async_manager = nullptr;
}