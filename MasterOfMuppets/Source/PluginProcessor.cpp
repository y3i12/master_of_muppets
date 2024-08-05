/*
  ==============================================================================

    This file contains the basic framework code for a JUCE plugin processor.

  ==============================================================================
*/

#include "PluginProcessor.h"

#include <algorithm>
#include <limits>
#include <sstream>

#include "master_of_muppets.hpp"

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
    std::stringstream ss;
    for ( int i = 0; i < dr_teeth::k_total_channels; ++i ) {
        ss.str("");
        ss.clear();
        ss << "cv_" << i;
        auto param = new juce::AudioParameterFloat( { ss.str(), 1}, ss.str( ), 0.0f, 100.0f, 0.0f );
        cv_states.push_back(cv_state_t( param ));
        addParameter( param );
    }
    juce::StringArray ports;
    std::list<serial_device> vec_ports;

    // List available ports for user choice
    vec_ports = serial_type_t::get_devices( );

    for ( auto itr = vec_ports.begin( ); itr != vec_ports.end( ); ++itr ) {
        ports.add(itr->first);
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

    cv_to_send.reserve( dr_teeth::k_total_channels );
}

MasterOfMuppetsAudioProcessor::~MasterOfMuppetsAudioProcessor( ) {
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
    // Use this method as the place to do any pre-playback
    // initialisation that you need..
}

void MasterOfMuppetsAudioProcessor::releaseResources( ) {
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

void MasterOfMuppetsAudioProcessor::processBlock( juce::AudioBuffer<float>& buffer, juce::MidiBuffer& midiMessages ) {
    juce::ScopedNoDenormals noDenormals;
    auto totalNumInputChannels  = getTotalNumInputChannels( );
    auto totalNumOutputChannels = getTotalNumOutputChannels( );

    // In case we have more outputs than inputs, this code clears any output
    // channels that didn't contain input data, (because these aren't
    // guaranteed to be empty - they may contain garbage).
    // This is here to avoid people getting screaming feedback
    // when they first compile a plugin, but obviously you don't need to keep
    // this code if your algorithm always overwrites all the output channels.
    for ( auto i = totalNumInputChannels; i < totalNumOutputChannels; ++i )
        buffer.clear( i, 0, buffer.getNumSamples( ) );

    // This is the place where you'd normally do the guts of your plugin's
    // audio processing...
    // Make sure to reset the state if your inner loop is processing
    // the samples and the outer loop is handling the channels.
    // Alternatively, you can process the samples with the channels
    // interleaved by keeping the same state.
    // for ( int channel = 0; channel < totalNumInputChannels; ++channel ) {
    //     auto* channelData = buffer.getWritePointer( channel );

    //     // ..do something to the data...
    // }


    int samples           = buffer.getNumSamples( );
    double sample_rate    = getSampleRate();
    cv_to_send.clear();

    std::for_each(
        cv_states.begin(),
        cv_states.end(),
        [&]( cv_state_t& n ) {
            n.tick( samples );
            if ( n.sample_counter > sample_rate / 1000 * 2.5 ) { // Current HW doesn't update faster than 2.5ms
                double value = n.accumulated_cv / 100.0 / n.sample_counter;
                n.accumulated_cv = n.sample_counter = 0;
                if ( n.last_transmitted_value != value ) {
                    n.last_transmitted_value = value;
                    cv_to_send.push_back( &n );
                }
            }
        }
    );

    if ( !cv_to_send.empty() ) {
        cv_state_t* cv_state = cv_to_send.front( );

        message_set_dac_value_t::instance->message.type = message_t::k_set_dac_value;
        message_set_dac_value_t::instance->count        = static_cast<uint8_t>( cv_to_send.size() );

        message_attribute_address_value_t* av = &message_set_dac_value_t::instance->first_address_value;

        std::for_each(
            cv_to_send.begin( ),
            cv_to_send.end( ),
            [&]( cv_state_t* cvs ) {
                av->address = cvs->channel;
                av->value   = static_cast< uint16_t >( std::numeric_limits< uint16_t >::max() * cvs->last_transmitted_value );
                ++av;
            }
        );

        serial.begin_packet( );
        serial.write( reinterpret_cast< uint8_t* >( message_set_dac_value_t::instance ), ( sizeof( message_set_dac_value_t ) + sizeof( message_attribute_address_value_t ) * ( message_set_dac_value_t::instance->count - 1 ) ) );
        serial.end_packet();
    }
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
