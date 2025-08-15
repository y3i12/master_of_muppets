#pragma once

#include "dr_teeth.h"
#include "TeensyThreads.h"

template < typename dac_driver_t > 
class electric_mayhem {
public:
    static const uint8_t k_channels_per_dac = dac_driver_t::k_channels;
    
    typedef typename dac_driver_t::value_t                  value_t;
    typedef typename dac_driver_t::initialization_struct_t  initialization_struct_t;

    electric_mayhem( void ) { };

    void initialize( const initialization_struct_t initialization_struct[ dr_teeth::k_dac_count ] );

    bool attention_please( uint8_t muppet_index );
    void hey_you( uint8_t muppet_index );
    void thanks( uint8_t muppet_index );

    void throw_muppet_in_the_mud( uint8_t muppet_index );
    void shit_storm( void );
    
    void put_muppet_to_work( uint8_t muppet_index );

protected:
    /**
     * @brief Thread-safe state management for DAC workers
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

    struct orientation_guide {
        orientation_guide( void ) : muppet( 0 ), lock( 0 ), state( 0 ), output_buffer( 0 ) {}
        orientation_guide( dac_driver_t& the_muppet, Threads::Mutex& the_lock, muppet_state& the_state, uint16_t* the_buffer ) :
            muppet(        &the_muppet ),
            lock(          &the_lock   ),
            state(         &the_state  ),
            output_buffer( the_buffer  )
        { }

        dac_driver_t*    muppet;
        Threads::Mutex*  lock;
        muppet_state*    state;
        uint16_t*        output_buffer;
    };


    dac_driver_t      muppets[ dr_teeth::k_dac_count ];
    orientation_guide muppet_orientation_guides[ dr_teeth::k_dac_count ];
    Threads::Mutex    muppet_lock[ dr_teeth::k_dac_count ];
    muppet_state      muppet_states[ dr_teeth::k_dac_count ];

    inline bool vaid_dac(      uint8_t muppet_index  ) { return muppet_index  < dr_teeth::k_dac_count; }
    inline bool valid_channel( uint8_t channel_index ) { return channel_index < k_channels_per_dac;    }

    

    static void muppet_worker( void* hidden_orientation_guide ) {
        orientation_guide& muppet_orientation_guide = *reinterpret_cast< orientation_guide* >( hidden_orientation_guide );
        
        dac_driver_t&    me               = *muppet_orientation_guide.muppet;
        Threads::Mutex&  my_lock          = *muppet_orientation_guide.lock;
        muppet_state&    my_state         = *muppet_orientation_guide.state;
        uint16_t*        my_output_buffer =  muppet_orientation_guide.output_buffer;

        uint16_t         my_personal_buffer_copy[ k_channels_per_dac ];
        uint32_t         last_processed_sequence = 0;
        
        while ( 1 ) {
            // Check if update is requested using thread-safe synchronization
            my_state.state_mutex.lock();
            uint32_t current_sequence = my_state.update_sequence;
            bool     should_update    = ( current_sequence != last_processed_sequence ) && 
                                        !my_state.update_in_progress;
            
            if ( should_update ) {
                my_state.update_in_progress = true;
            }
            my_state.state_mutex.unlock();
            
            if ( should_update ) {
                // Copy data safely to local buffer
                my_lock.lock();
                memcpy( my_personal_buffer_copy, my_output_buffer, sizeof( uint16_t ) * k_channels_per_dac );
                my_lock.unlock();
                
                // Perform DAC operations
                bool operation_successful = true;
                me.enable();
                me.set_values( my_personal_buffer_copy );
                me.disable();
                
                // Clear in-progress flag only after successful completion
                my_state.state_mutex.lock();
                if ( operation_successful ) {
                    last_processed_sequence = current_sequence;
                }
                my_state.update_in_progress = false;
                my_state.state_mutex.unlock();
            }

            threads.yield();
        }
    }

    static void party_pooper( void* the_electric_mayhem_in_disguise ) {
      electric_mayhem< dac_driver_t >& the_electric_mayhem = *reinterpret_cast< electric_mayhem< dac_driver_t >* >( the_electric_mayhem_in_disguise );
      
      while ( 1 ) {
        the_electric_mayhem.shit_storm();
        threads.delay( dr_teeth::k_force_refresh_every_millis );
      }
    }
};

template < class dac_driver_t >
void electric_mayhem< dac_driver_t >::initialize( const initialization_struct_t initialization_struct[ dr_teeth::k_dac_count ] ) {
    // Initialize muppet states with initial update request
    for ( uint8_t i = 0; i < dr_teeth::k_dac_count; ++i ) {
        muppet_states[ i ].update_sequence = 1; // Request initial update
    }
    threads.setSliceMicros( dr_teeth::k_thread_slice_micros );

    for ( uint8_t muppet_index = 0; muppet_index < dr_teeth::k_dac_count; ++muppet_index ) {
        muppets[ muppet_index ].initialize( initialization_struct[ muppet_index ] );
        put_muppet_to_work( muppet_index );
    }

    threads.addThread( party_pooper, this );
}

template < class dac_driver_t >
bool electric_mayhem< dac_driver_t >::attention_please( uint8_t muppet_index ) {
    return muppet_lock[ muppet_index ].lock( );
}

template < class dac_driver_t >
void electric_mayhem< dac_driver_t >::hey_you( uint8_t muppet_index ) {
    muppet_lock[ muppet_index ].lock( );
}

template < class dac_driver_t >
void electric_mayhem< dac_driver_t >::thanks( uint8_t muppet_index ) {
    muppet_lock[ muppet_index ].unlock( );
}

template < class dac_driver_t >
void electric_mayhem< dac_driver_t >::throw_muppet_in_the_mud( uint8_t muppet_index ) {
    if ( muppet_index >= dr_teeth::k_dac_count ) return;
    
    // Thread-safe update request using sequence increment
    muppet_states[ muppet_index ].state_mutex.lock();
    muppet_states[ muppet_index ].update_sequence++;
    muppet_states[ muppet_index ].state_mutex.unlock();
}

template < class dac_driver_t >
void electric_mayhem< dac_driver_t >::shit_storm( void ) {
    for ( uint8_t muppet_index = 0; muppet_index < dr_teeth::k_dac_count; ++muppet_index ) {
        throw_muppet_in_the_mud( muppet_index );
    }
}

template < class dac_driver_t >
void electric_mayhem< dac_driver_t >::put_muppet_to_work( uint8_t muppet_index ) {
    muppet_orientation_guides[ muppet_index ] = orientation_guide( 
        muppets[ muppet_index ], 
        muppet_lock[ muppet_index ], 
        muppet_states[ muppet_index ],
        dr_teeth::output_buffer + muppet_index * k_channels_per_dac 
    );

    threads.addThread( muppet_worker, &muppet_orientation_guides[ muppet_index ] );
}