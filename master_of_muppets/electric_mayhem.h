#pragma once

#include "dr_teeth.h"
#include "TeensyThreads.h"

template < typename dac_driver_t > 
class electric_mayhem {
public:
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
    struct orientation_guide {
        orientation_guide( void ) : muppet( 0 ), lock( 0 ), dirty( 0 ), output_buffer( 0 ) {}
        orientation_guide( dac_driver_t& the_muppet, Threads::Mutex& the_lock, uint8_t& the_dirty_flag, uint16_t* the_buffer ) :
            muppet( &the_muppet ),
            lock( &the_lock ),
            dirty( &the_dirty_flag ),
            output_buffer( the_buffer )
        {}

        dac_driver_t*    muppet;
        Threads::Mutex*  lock;
        uint8_t*         dirty;
        uint16_t*        output_buffer;
    };


    dac_driver_t      muppets[ dr_teeth::k_dac_count ];
    orientation_guide muppet_orientation_guides[ dr_teeth::k_dac_count ];
    Threads::Mutex    muppet_lock[ dr_teeth::k_dac_count ];
    uint8_t           is_muppet_dirty[ dr_teeth::k_dac_count ];

    inline bool vaid_dac(      uint8_t muppet_index     ) { return muppet_index     < dr_teeth::k_dac_count;        }
    inline bool valid_channel( uint8_t channel_index ) { return channel_index < dr_teeth::k_channels_per_dac; }

    

    static void muppet_worker( void* hidden_orientation_guide ) {
        orientation_guide& muppet_orientation_guide = *reinterpret_cast< orientation_guide* >( hidden_orientation_guide );
        
        dac_driver_t&    me               = *muppet_orientation_guide.muppet;
        Threads::Mutex&  my_lock          = *muppet_orientation_guide.lock;
        uint8_t&         am_i_dirty       = *muppet_orientation_guide.dirty;
        uint16_t*        my_output_buffer  =  muppet_orientation_guide.output_buffer;

        uint16_t         my_personal_buffer_copy[ dr_teeth::k_channels_per_dac ];
        
        while ( 1 ) {
            if ( am_i_dirty ) {
                my_lock.lock( );
                memcpy( my_personal_buffer_copy, my_output_buffer, sizeof( uint16_t ) * dr_teeth::k_channels_per_dac );
                am_i_dirty = 0; 
                my_lock.unlock( );

                me.enable( );
                me.set_values( my_personal_buffer_copy );
                me.disable( );

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
    memset( is_muppet_dirty, 1, dr_teeth::k_dac_count );
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
        is_muppet_dirty[ muppet_index ] = 1;
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
        is_muppet_dirty[ muppet_index ],
        dr_teeth::output_buffer + muppet_index * dr_teeth::k_dac_count 
    );

    threads.addThread( muppet_worker, &muppet_orientation_guides[ muppet_index ] );
}