#include "MasterOfMuppets.h"
#include "IControls.h"
#include "IPlug_include_in_plug_src.h"

#include "serial_messages.h"


MasterOfMuppets::MasterOfMuppets(const InstanceInfo& info)
  : Plugin(info, MakeConfig(theNumberOfMCP, kNumPresets))
{
  dac_outputs.fill(Output());
  mMakeGraphicsFunc = [&]() { return MakeGraphics(*this, PLUG_WIDTH, PLUG_HEIGHT, PLUG_FPS, GetScaleForScreen(PLUG_WIDTH, PLUG_HEIGHT)); };

  mLayoutFunc = [&](IGraphics* pGraphics) {
    pGraphics->AttachCornerResizer(EUIResizerMode::Scale, false);
    pGraphics->AttachPanelBackground(COLOR_GRAY);
    pGraphics->LoadFont("Roboto-Regular", ROBOTO_FN);

    const IRECT b = pGraphics->GetBounds();

    // pGraphics->AttachControl(new ITextControl(b.GetMidVPadded(50), std::string(vec_ports.at(0).name.begin(), vec_ports.at(0).name.end()).c_str(), IText(50)), kConnectionLabel);
    std::ostringstream oss;
    for (size_t i = 0; i < theNumberOfMCP; ++i)
    {
      oss << "CV " << i;

      GetParam(i)->InitDouble(oss.str().c_str(), 0, 0, 1, 0.001);
      pGraphics->AttachControl(new IVKnobControl(b.GetCentredInside(75).GetHShifted((-100.0f * theNumberOfMCP / 2 + i * 100) + 75), i));

      oss.str("");
    }
  };

  // INTERFACE_CLASS enum_ports;
  std::list<serial_device> vec_ports;

  // List available ports for user choice
  vec_ports = serial_type_t::get_devices();

  // TODO: y3i12- device selection
  if (vec_ports.size() != 0)
  {
    // Attempt to open the selected port
    int sres = serial.open_port(vec_ports.front().first, 50);
    if (sres < 0)
    {
      // TODO: y3i12- exception
    }
  }
}

void MasterOfMuppets::ProcessBlock(sample** inputs, sample** outputs, int sampleCount)
{
  for (size_t i = 0; i < dac_outputs.size(); ++i)
  {
    Output& dac_output = dac_outputs[i];
    dac_output.sample_counter += sampleCount;

    if (dac_output.status == Output::Accumulating)
    {
      dac_output.value_sum += GetParam(i)->Value();

      if (dac_output.sample_counter > dac_output.last_send + GetSampleRate() / 50)
      {
        unsigned short value = static_cast<unsigned short>( dac_output.average() * 40.95 );
        dac_output.value_to_send = value;
        dac_output.status = Output::WaitingToSend;
      }
    }

    if (dac_output.status == Output::SendRetry)
    {
      unsigned int samples_since_last_send = dac_output.sample_counter - dac_output.last_send;
      if (samples_since_last_send > GetSampleRate() / 10)
      {
        dac_output.status = Output::WaitingToSend;
        dac_output.retries += 1;
      }

      if (dac_output.retries > 3 )
      {
        dac_output = Output();
        continue;
      }
    }

    if ( dac_output.status == Output::WaitingToSend )
    {
      message_set_dac_value_t message(i, dac_output.value_to_send);
      int nout = serial.send_packet(message);
      dac_output.last_send = dac_output.sample_counter;

      if (nout > 0)
      {
        dac_output = Output();
      }
      else
      {
        dac_output.status = Output::SendRetry;
      }
    }
  }

  // pass_by
  const int nChans = NOutChansConnected();
  for (int c = 0; c < nChans; c++)
  {
    memcpy(outputs[c], inputs[c], sizeof(sample) * sampleCount);
  }
}
