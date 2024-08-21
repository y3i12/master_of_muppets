/*
  ==============================================================================

    This file contains the basic framework code for a JUCE plugin processor.

  ==============================================================================
*/

#include "PluginProcessor.h"

#include <algorithm>
#include <limits>
#include <sstream>
#include <chrono>

#include "master_of_muppets.hpp"


#define LFO_FREQUENCY 20    // comment to disable lfo
#define LFO_SHAPE triangle // triangle square stair sawtooth sinus sinusRectified sinusDiode trapezium1 trapezium2 heartBeat

#ifdef max
#undef max
#endif

uint8_t MasterOfMuppetsAudioProcessor::cv_state_t::_channel = 0;

//==============================================================================
MasterOfMuppetsAudioProcessor::MasterOfMuppetsAudioProcessor( )
#ifndef JucePlugin_PreferredChannelConfigurations
    : AudioProcessor( BusesProperties( )
#if ! JucePlugin_IsMidiEffect
#if ! JucePlugin_IsSynth
                      .withInput( "Input", juce::AudioChannelSet::stereo( ), true )
#endif
                      .withOutput( "Output", juce::AudioChannelSet::stereo( ), true )
#endif
    )
#endif
{
    #ifdef LFO_FREQUENCY
        the_function_generator.setFrequency( LFO_FREQUENCY );
        the_function_generator.setAmplitude( 0.5f );
    #endif

    sender_active = true;
    should_send = false;

    std::stringstream ss;
    for ( int i = 0; i < dr_teeth::k_total_channels; ++i ) {
        ss.str("");
        ss.clear();
        ss << "cv_" << i;
        auto param = new juce::AudioParameterFloat( { ss.str(), 1}, ss.str( ), 0.0f, 1.0f, 0.0f );
        cv_states.push_back(cv_state_t( param ));
        addParameter( param );
    }
    juce::StringArray ports;
    std::list<serial_device> vec_ports;

    // List available ports for user choice
    vec_ports = serial_type_t::get_devices( );

    for ( auto itr = vec_ports.begin( ); itr != vec_ports.end( ); ++itr ) {
        if ( strstr( itr->second.c_str(), "USB" ) ) {
            ports.add(itr->first);
        }
    }

    // TODO: y3i12- device selection
    serial_list = new juce::AudioParameterChoice( { "serial_port", 1 },
                                                    "Serial Port",
                                                    ports,
                                                    0 );

    addParameter( serial_list );

    if ( vec_ports.size( ) != 0 ) {
      // Attempt to open the selected port
        if ( !serial.open_port( vec_ports.front( ).first, 50 ) ) {
            std::cout << "Error oppening port" << std::endl;
            // TODO: y3i12- exception
        }
    }
    send_thread = std::thread( sender, this );
}

MasterOfMuppetsAudioProcessor::~MasterOfMuppetsAudioProcessor( ) {
    sender_active = false;
    send_thread.join();
}

void MasterOfMuppetsAudioProcessor::sender( MasterOfMuppetsAudioProcessor* mop ) {
    bool&                       sender_active(  mop->sender_active  );
    bool&                       should_send(    mop->should_send    );
    std::mutex&                 send_mutex(     mop->send_mutex     );
    std::vector< cv_state_t >&  cv_states(      mop->cv_states      );
    serial_type_t&              serial(         mop->serial         );

    while ( 1 ) {
        while ( sender_active && !should_send ) {
            std::this_thread::yield();
        }

         if ( !sender_active ) return;

        message_set_dac_value_t::instance->message.type = message_t::k_set_dac_value;
        message_set_dac_value_t::instance->count        = 0;

        message_attribute_address_value_t* av           = &message_set_dac_value_t::instance->first_address_value;

        send_mutex.lock( );
        std::for_each(
            cv_states.begin( ),
            cv_states.end( ),
            [&]( cv_state_t& n ) {
                if ( n.cv_value >= 0 ) {
                    av->address = n.channel;
                    av->value = static_cast<uint16_t>( std::numeric_limits< uint16_t >::max( ) * n.cv_value );
                    ++message_set_dac_value_t::instance->count;
                    ++av;
                    n.cv_value = -1.0;
                }
            }
        );
        send_mutex.unlock( );

        if ( message_set_dac_value_t::instance->count ) {
            serial.send_packet( reinterpret_cast< uint8_t* >( message_set_dac_value_t::instance ), reinterpret_cast< size_t >( av ) - reinterpret_cast< size_t >( message_set_dac_value_t::instance  ) );
        }

        should_send = false;
    }
}

void MasterOfMuppetsAudioProcessor::processBlock( juce::AudioBuffer<float>& buffer, juce::MidiBuffer& midiMessages ) {
    juce::ScopedNoDenormals noDenormals;
    auto totalNumInputChannels  = getTotalNumInputChannels( );
    auto totalNumOutputChannels = getTotalNumOutputChannels( );

    for ( auto i = totalNumInputChannels; i < totalNumOutputChannels; ++i ) {
        buffer.clear( i, 0, buffer.getNumSamples( ) );
    }

    
    send_mutex.lock( );
    std::for_each(
        cv_states.begin( ),
        cv_states.end( ),
        [&]( cv_state_t& n ) {
            #ifdef LFO_FREQUENCY
                n.set_value( the_function_generator.LFO_SHAPE( static_cast< float >( juce::Time::getMillisecondCounterHiRes( ) * 10000 ) ) + 0.5f );
            #else
                n.update_value( );
            #endif
            should_send = true;
        }
    );
    send_mutex.unlock( );
 }

//==============================================================================
bool MasterOfMuppetsAudioProcessor::hasEditor( ) const {
    return true; // (change this to false if you choose to not supply an editor)
}

juce::AudioProcessorEditor* MasterOfMuppetsAudioProcessor::createEditor( ) {
    return new juce::GenericAudioProcessorEditor( *this );
    //return new MasterOfMuppetsAudioProcessorEditor( *this );
}

//==============================================================================
void MasterOfMuppetsAudioProcessor::getStateInformation( juce::MemoryBlock& destData ) {
    // You should use this method to store your parameters in the memory block.
    // You could do that either as raw data, or use the XML or ValueTree classes
    // as intermediaries to make it easy to save and load complex data.
}

void MasterOfMuppetsAudioProcessor::setStateInformation( const void* data, int sizeInBytes ) {
    // You should use this method to restore your parameters from this memory block,
    // whose contents will have been created by the getStateInformation() call.
}

//==============================================================================
// This creates new instances of the plugin..
juce::AudioProcessor* JUCE_CALLTYPE createPluginFilter( ) {
    return new MasterOfMuppetsAudioProcessor( );
}


//==============================================================================
const juce::String MasterOfMuppetsAudioProcessor::getName( ) const {
    return JucePlugin_Name;
}

bool MasterOfMuppetsAudioProcessor::acceptsMidi( ) const {
#if JucePlugin_WantsMidiInput
    return true;
#else
    return false;
#endif
}

bool MasterOfMuppetsAudioProcessor::producesMidi( ) const {
#if JucePlugin_ProducesMidiOutput
    return true;
#else
    return false;
#endif
}

bool MasterOfMuppetsAudioProcessor::isMidiEffect( ) const {
#if JucePlugin_IsMidiEffect
    return true;
#else
    return false;
#endif
}

double MasterOfMuppetsAudioProcessor::getTailLengthSeconds( ) const {
    return 0.0;
}

int MasterOfMuppetsAudioProcessor::getNumPrograms( ) {
    return 1;   // NB: some hosts don't cope very well if you tell them there are 0 programs,
                // so this should be at least 1, even if you're not really implementing programs.
}

int MasterOfMuppetsAudioProcessor::getCurrentProgram( ) {
    return 0;
}

void MasterOfMuppetsAudioProcessor::setCurrentProgram( int index ) {
}

const juce::String MasterOfMuppetsAudioProcessor::getProgramName( int index ) {
    return {};
}

void MasterOfMuppetsAudioProcessor::changeProgramName( int index, const juce::String& newName ) {
}

//==============================================================================
void MasterOfMuppetsAudioProcessor::prepareToPlay( double sampleRate, int samplesPerBlock ) {
    // y3i12- TODO:
    // Use this method as the place to do any pre-playback
    // initialisation that you need..
}

void MasterOfMuppetsAudioProcessor::releaseResources( ) {
    // y3i12- TODO:
    // When playback stops, you can use this as an opportunity to free up any
    // spare memory, etc.
}

#ifndef JucePlugin_PreferredChannelConfigurations
bool MasterOfMuppetsAudioProcessor::isBusesLayoutSupported( const BusesLayout& layouts ) const {
#if JucePlugin_IsMidiEffect
    juce::ignoreUnused( layouts );
    return true;
#else
  // This is the place where you check if the layout is supported.
  // In this template code we only support mono or stereo.
  // Some plugin hosts, such as certain GarageBand versions, will only
  // load plugins that support stereo bus layouts.
    if ( layouts.getMainOutputChannelSet( ) != juce::AudioChannelSet::mono( )
         && layouts.getMainOutputChannelSet( ) != juce::AudioChannelSet::stereo( ) )
        return false;

    // This checks if the input layout matches the output layout
#if ! JucePlugin_IsSynth
    if ( layouts.getMainOutputChannelSet( ) != layouts.getMainInputChannelSet( ) )
        return false;
#endif

    return true;
#endif
}
#endif
