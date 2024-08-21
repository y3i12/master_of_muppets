/*
  ==============================================================================

    This file contains the basic framework code for a JUCE plugin processor.

  ==============================================================================
*/

#pragma once

#include <JuceHeader.h>
#include <vector>
#include <cmath>
#include <thread>

#include "serial_port_libsp.h"
#include "serial_port_w32.h"
#include "dr_teeth.h"
#include "function_generator.h"

typedef slip_encoded_serial_port_libsp serial_type_t;
// typedef slip_encoded_serial_port_w32 serial_type_t;

//==============================================================================
/**
*/
class MasterOfMuppetsAudioProcessor  : public juce::AudioProcessor
{
public:
    //==============================================================================
    MasterOfMuppetsAudioProcessor();
    ~MasterOfMuppetsAudioProcessor() override;

    //==============================================================================
    void prepareToPlay (double sampleRate, int samplesPerBlock) override;
    void releaseResources() override;

   #ifndef JucePlugin_PreferredChannelConfigurations
    bool isBusesLayoutSupported (const BusesLayout& layouts) const override;
   #endif

    void processBlock (juce::AudioBuffer<float>&, juce::MidiBuffer&) override;

    //==============================================================================
    juce::AudioProcessorEditor* createEditor() override;
    bool hasEditor() const override;

    //==============================================================================
    const juce::String getName() const override;

    bool acceptsMidi() const override;
    bool producesMidi() const override;
    bool isMidiEffect() const override;
    double getTailLengthSeconds() const override;

    //==============================================================================
    int getNumPrograms() override;
    int getCurrentProgram() override;
    void setCurrentProgram (int index) override;
    const juce::String getProgramName (int index) override;
    void changeProgramName (int index, const juce::String& newName) override;

    //==============================================================================
    void getStateInformation (juce::MemoryBlock& destData) override;
    void setStateInformation (const void* data, int sizeInBytes) override;

private:
    struct cv_state_t {
        static uint8_t                      _channel;
        uint8_t                             channel;
        double                              cv_value;
        juce::AudioParameterFloat*          param_cv;

        cv_state_t( juce::AudioParameterFloat* _param_cv ) :
            channel( _channel++ ),
            param_cv( _param_cv ),
            cv_value( 0.0 ) { }

        void update_value( void ) { cv_value = param_cv->get( ); }
        void set_value( double the_value ) { *param_cv = static_cast< float >( cv_value = the_value ); }
    };

    static void sender( MasterOfMuppetsAudioProcessor* mop );
private:
    serial_type_t               serial;
    function_generator          the_function_generator;
    juce::AudioParameterChoice* serial_list;

    std::vector<cv_state_t>     cv_states;

    std::thread                 send_thread;
    std::mutex                  send_mutex;
    bool                        should_send;
    bool                        sender_active;

    //==============================================================================
    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (MasterOfMuppetsAudioProcessor)
};
