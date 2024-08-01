#pragma once

#include "IPlug_include_in_plug_hdr.h"
#include "serial_port_libsp.h"

#include <array>
#include <limits>

// Constants
// theNumberOfMCP sets the total number of MCP4725 instances
// for the moment, only 3 are supported.
// @see MCP

#define theNumberOfMCP 8
// valueLimit sets the maximum value to be received from the host computer via serial
#define valueLimit 4096

const int kNumPresets = 0;

using namespace iplug;
using namespace igraphics;

typedef slip_encoded_serial_port_libsp serial_type_t;

class MasterOfMuppets final : public Plugin
{
public:
  MasterOfMuppets(const InstanceInfo& info);
  
  struct Output
  {
    enum Status
    {
      Accumulating,
      WaitingToSend,
      SendRetry,
    };

    Output()
      : status(Accumulating)
      , sample_counter(0)
      , last_send(0)
      , value_sum(0.0)
      , value_to_send(0)
      , retries(0)
    {
    }

    double average() { return value_sum / sample_counter; }
    Status status;
    unsigned int sample_counter;
    unsigned int last_send;
    double value_sum;
    unsigned short value_to_send;
    uint8_t retries;
  };

#if IPLUG_DSP // http://bit.ly/2S64BDd
  void ProcessBlock(sample** inputs, sample** outputs, int nFrames) override;
#endif

  std::array<Output, theNumberOfMCP> dac_outputs;
  serial_type_t serial;
  
};
