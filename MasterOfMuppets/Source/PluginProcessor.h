/*
  ==============================================================================

    This file contains the basic framework code for a JUCE plugin processor.

  ==============================================================================
*/

#pragma once

#include <JuceHeader.h>
#include <vector>
#include <cmath>

#include "serial_port_libsp.h"
#include "dr_teeth.h"

typedef slip_encoded_serial_port_libsp serial_type_t;

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
        static uint8_t _channel;
        uint8_t channel;
        double accumulated_cv;
        double sample_counter;
        double last_transmitted_value;
        juce::AudioParameterFloat* param_cv;

        cv_state_t( juce::AudioParameterFloat* _param_cv ) :
            channel( _channel++ ),
            param_cv( _param_cv ),
            accumulated_cv( 0.0 ),
            sample_counter( 0.0 ),
            last_transmitted_value( std::nan("0") ) {
        }

        void tick( float samples ) { accumulated_cv += param_cv->get() * samples; sample_counter += samples; }
        void reset() { accumulated_cv = sample_counter = 0.0; }
    };
private:
    serial_type_t           serial;
    juce::AudioParameterChoice* serial_list;

    std::vector<cv_state_t>  cv_states;
    std::vector<cv_state_t*> cv_to_send;

    //==============================================================================
    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (MasterOfMuppetsAudioProcessor)
};
