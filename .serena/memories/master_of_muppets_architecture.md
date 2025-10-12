# Master of Muppets - System Architecture

## Project Overview
Teensy 4.1 firmware for multi-channel DAC control with DMA support. Used for audio/CV generation with MIDI or LFO input.

## Hardware Configuration
- **Platform**: Teensy 4.1 microcontroller
- **DACs**: 2 DACs × 8 channels = 16 total output channels
  - DAC 0: Wire2, address 11, channels 0-7
  - DAC 1: Wire1, address 37, channels 8-15
- **Supported DAC chips**:
  - AD5593R (primary, DMA-capable, 16-bit)
  - MCP4728 (alternative, sync only, 12-bit)

## Core Architecture

### Entry Point: firmware/src/main.cpp

**setup() initialization sequence:**
1. Initialize I2C buses (Wire1, Wire2)
2. Configure DAC drivers with DMA channels
3. Set DMA mode (ENABLED/REQUIRED/DISABLED)
4. Configure MIDI handler: `usbMIDI.setHandlePitchChange(set_channel_value)`
5. Set thread slicing: 10μs cooperative multitasking
6. Spawn two worker threads
7. [Optional] Initialize DMA validation system

**loop() behavior:**
- Simply calls `threads.yield()` 
- Handles validation commands if DMA validation enabled
- All real work happens in spawned threads

### Thread Architecture

**Thread 1: `the_voice_from_beyond` (Input)**
- Infinite loop that:
  1. Calls `muppet_clock::tick()` for timing
  2. Locks `inspiration` mutex
  3. Reads input (MIDI or LFO) into `dr_teeth::input_buffer[16]`
  4. Unlocks mutex
- Input modes:
  - **MIDI Mode** (default): USB MIDI pitch bend → 16-bit channel values
  - **LFO Mode** (#define LFO_FREQUENCY): Generated waveforms from `function_generator`

**Thread 2: `the_muppet_show` (Output)**
- Infinite loop that:
  1. Locks `inspiration` mutex
  2. Calls `dr_teeth::go_muppets(the_muppets)`:
     - For each DAC: check ready, copy input→output buffers, request update
  3. Unlocks mutex
- Triggers DAC hardware updates via `electric_mayhem`

**Synchronization:**
- Mutex: `inspiration` (Threads::Mutex) - protects dr_teeth buffers
- Thread slice: 10μs per thread (cooperative multitasking)

### Data Flow
```
MIDI/LFO Input → input_buffer[16] → (mutex copy) → output_buffer[16] → DAC Hardware
```

## Key Components

### 1. dr_teeth (firmware/include/dr_teeth.h:4-51)
**Role**: Central data structure and constants

**Static buffers:**
- `input_buffer[k_total_channels]` - uint16_t[16], written by input thread
- `output_buffer[k_total_channels]` - uint16_t[16], read by output thread

**Key constants:**
- `k_dac_count = 2`
- `k_channels_per_dac = 8`
- `k_total_channels = 16`
- `k_thread_slice_micros = 10`
- `k_audio_half_scale = 32768` (for bipolar signals)

**Core method:**
- `go_muppets<T>(T& muppets)` - Template function that:
  - Iterates through DACs
  - Checks readiness via `attention_please()`
  - Copies 8 channels from input→output buffer
  - Triggers update via `throw_muppet_in_the_mud()`
  - Acknowledges via `thanks()`

### 2. electric_mayhem (firmware/include/electric_mayhem.h:15-306)
**Role**: DAC controller with DMA support

**Template parameter**: `dac_driver_t` (AD5593R or MCP4728)

**DMA Modes** (set via `set_dma_mode()`):
- `DISABLED` - Synchronous I2C only
- `ENABLED` - DMA with automatic fallback on error
- `REQUIRED` - DMA only, fails if unavailable

**Key fields:**
- `async_muppets_*` - Async driver array for DMA operations
- `async_managers_*` - DMA manager array
- `dma_mode_` - Current DMA operating mode
- `dma_stats_` - Performance statistics
- `muppet_states_[]` - Per-DAC state with update sequences

**Key methods:**
- `attention_please(muppet_index)` - Check if DAC ready for update
- `throw_muppet_in_the_mud(muppet_index)` - Request DAC update (increments sequence)
- `thanks(muppet_index)` - Acknowledge completion
- `muppet_worker_dma()` - DMA worker thread (one per DAC)

**DMA Workers:**
- Background threads monitor `muppet_states_[].update_sequence`
- When sequence changes, perform async I2C transfer via DMA
- Use `async_dac_manager` for hardware interfacing

### 3. Hardware Drivers (firmware/lib/)
**Primary**: `AD5593R/` 
- Driver: `rob_tillaart_ad_5993r_async`
- 16-bit mixed-signal I/O chip
- Supports DMA async operations

**Alternative**: `Adafruit MCP4728/`
- Driver: `adafruit_mcp_4728`
- 12-bit quad DAC
- Synchronous I2C only (no DMA)

**Threading**: `TeensyThreads/`
- Provides cooperative multitasking
- `Threads::Mutex` for synchronization

**Signal Generation**: `FunctionGenerator/`
- Waveforms: sine, triangle, square, sawtooth, trapezium, heartbeat, etc.
- Used in LFO mode

### 4. DMA Validation System (firmware/include/dma_*.h)
**Status**: Optional (#ifdef ENABLE_DMA_VALIDATION)

**Components:**
- `dma_performance_validator` - Latency/throughput metrics
- `dma_test_suite` - Automated test scenarios  
- `dma_realtime_monitor` - Live performance tracking (5s intervals)
- `dma_error_handler` - Retry logic with peripheral reset
- `dma_automatic_validation` - Phase progression controller

**Three-Phase Testing Methodology:**
1. **Phase 1 - Immediate**: 8hr stability, >50% efficiency improvement, <0.1% error rate
2. **Phase 2 - Advanced**: Logic analyzer integration, <5μs interrupt latency, <1μs jitter
3. **Phase 3 - Production**: Automated testing, >99% pass rate, <10min test duration

**Validation Commands** (via Serial):
- `v` - Toggle validation on/off
- `r` - Show validation results
- `s` - Show system status (DMA mode, performance)
- `h` - Help

## Important File Locations

**Main Firmware:**
- `firmware/src/main.cpp` - Main entry point (always compiled)
- `firmware/src/dma_validation_main.cpp` - Standalone validation mode (#ifdef STANDALONE_VALIDATION)

**Headers:**
- `firmware/include/dr_teeth.h` - Core data structures
- `firmware/include/electric_mayhem.h` - DAC controller
- `firmware/include/dma_automatic_validation.h` - Validation framework
- `firmware/include/dma_performance_validator.h`
- `firmware/include/dma_error_handler.h`

**Implementation:**
- `firmware/src/master_of_muppets.hpp` - Buffer instantiation

## Typical Execution Flow

```
T=0: setup()
  ├─ Initialize I2C (Wire1, Wire2)
  ├─ electric_mayhem::initialize(init_structs, dma_channels)
  ├─ electric_mayhem::set_dma_mode(ENABLED)
  ├─ Register MIDI callback
  ├─ threads.setSliceMicros(10)
  ├─ threads.addThread(the_muppet_show)
  ├─ threads.addThread(the_voice_from_beyond)
  └─ [Optional] initialize_dma_validation_system()

T=0+: Concurrent execution
  ├─ loop() - yields, handles validation commands
  ├─ Thread: the_voice_from_beyond
  │   └─ Loop: tick → lock → MIDI/LFO→input_buffer → unlock
  ├─ Thread: the_muppet_show  
  │   └─ Loop: lock → go_muppets(copy+trigger) → unlock
  └─ [If DMA enabled] Per-DAC workers
      └─ Loop: wait sequence → async I2C via DMA → ack
```

## Design Patterns

**Mutex-Protected Buffers**: Input/output threads synchronize via `inspiration` mutex around shared `dr_teeth` buffers

**Template-Based HAL**: `electric_mayhem<dac_driver_t>` allows compile-time driver selection

**Async with Fallback**: DMA mode ENABLED allows automatic fallback to sync I2C on errors

**Cooperative Threading**: 10μs time slices with explicit yield points prevent starvation

**Sequence-Based Updates**: DAC workers monitor update sequence counters to detect new data

## Configuration Options

**Compile-time flags:**
- `MASTER_OF_MUPPETS_AD5593R` - Use AD5593R driver (default)
- `MASTER_OF_MUPPETS_MCP4728` - Use MCP4728 driver (alternative)
- `ENABLE_DMA_VALIDATION` - Include validation system
- `STANDALONE_VALIDATION` - Compile dma_validation_main.cpp as standalone
- `LFO_FREQUENCY` - Enable LFO mode instead of MIDI
- `DEBUG_LED` - Enable LED status indicators
- `DEBUG_CHANNEL` - Show specific channel on LED

**Runtime configuration:**
- DMA mode: Set via `the_muppets.set_dma_mode()` in setup()
- LFO shape/frequency: Configure `function_generator` parameters
- Thread slice: Adjustable via `threads.setSliceMicros()`

## Notes

- Both `main.cpp` and `dma_validation_main.cpp` provide setup()/loop() but with different compilation guards
- Default configuration: AD5593R drivers, DMA enabled with fallback, MIDI input mode
- DMA validation system is comprehensive but optional - adds ~1500 lines of validation code
- System supports 16 simultaneous channels with independent control
- Channel mapping is direct: Channel N → DAC(N/8), Channel(N%8)
