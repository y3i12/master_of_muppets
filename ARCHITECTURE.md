# Architecture Overview

## System Design Philosophy

Master Of Muppets implements a real-time embedded system architecture optimized for low-latency MIDI-to-CV conversion. The design emphasizes thread safety, template flexibility, and deterministic performance.

## Threading Model

### Overview
The system uses **TeensyThreads** cooperative multitasking to separate concerns between MIDI input processing and DAC output management.

### Thread Architecture

```
┌─────────────────┐     ┌──────────────────┐
│   USB MIDI IN   │────▶│   dr_teeth       │
└─────────────────┘     │   (Main Thread)  │
                        └────────┬─────────┘
                                 │
                        ┌────────▼─────────┐
                        │  Input Buffer    │
                        │   [16 channels]  │
                        └────────┬─────────┘
                                 │
                ┌────────────────┼────────────────┐
                │                │                │
       ┌────────▼────────┐ ┌────▼──────┐ ┌──────▼──────┐
       │ electric_mayhem │ │ electric_  │ │   Future    │
       │   <AD5593R>     │ │  mayhem    │ │   Workers   │
       │   (Thread 1)    │ │ <AD5593R>  │ │             │
       └────────┬────────┘ │ (Thread 2) │ └─────────────┘
                │          └─────┬──────┘
       ┌────────▼────────┐ ┌─────▼──────┐
       │   DAC 1 (I2C)   │ │ DAC 2 (I2C)│
       │  Channels 1-8   │ │Channels 9-16│
       └─────────────────┘ └─────────────┘
```

### Thread Responsibilities

#### dr_teeth (Main Thread)
- **Purpose**: Central MIDI processor and buffer manager
- **Responsibilities**:
  - Read USB MIDI events
  - Process pitch bend messages (14-bit to 16-bit conversion)
  - Update input buffer with thread-safe access
  - Trigger DAC worker updates via `go_muppets()`
- **Timing**: Event-driven, processes on MIDI reception

#### electric_mayhem Workers
- **Purpose**: DAC output management
- **Responsibilities**:
  - Copy data from input buffer to local buffer
  - Perform I2C communication with DACs
  - Implement sequence tracking for update consistency
- **Timing**: ~500μs per DAC update cycle
- **Instances**: One per physical DAC

### Synchronization Mechanisms

#### Mutex Protection
```cpp
struct muppet_state {
    value_t           buffer[k_channels];
    std::atomic<bool> update_requested;
    uint32_t          sequence_number;
    std::mutex        mutex;
};
```

#### Sequence Tracking
Prevents race conditions during concurrent updates:
1. Main thread increments sequence before update request
2. Worker captures sequence at update start
3. Worker validates sequence before applying changes
4. Discards stale updates if sequence mismatch

### Thread Safety Guarantees
- **No dynamic allocation**: All buffers statically sized
- **Lock-free reads**: Workers use local buffer copies
- **Atomic flags**: Update requests via atomic booleans
- **Minimal critical sections**: Mutex held only during buffer copy

## Template Architecture

### Design Pattern
The system uses C++ templates to abstract DAC hardware differences while maintaining type safety and zero-overhead abstraction.

### Core Template: electric_mayhem<T>

```cpp
template< typename T >
class electric_mayhem {
public:
    using value_t = typename T::value_t;
    using initialization_struct_t = typename T::initialization_struct_t;
    
    static constexpr uint8_t k_channels = T::k_channels;
    
    // Thread-safe interface
    void set_value(uint8_t channel, value_t value);
    void request_update();
    
private:
    T driver;  // Concrete DAC driver instance
    muppet_state state;
    threads::thread_id worker_thread;
};
```

### DAC Driver Interface

Required typedefs and methods for any DAC driver:

```cpp
class dac_driver {
public:
    // Required type definitions
    using value_t = uint16_t;  // Or appropriate type
    using initialization_struct_t = /* I2C config struct */;
    
    // Required constant
    static constexpr uint8_t k_channels = 8;  // Or 4, etc.
    
    // Required methods
    void begin(initialization_struct_t config);
    void set_value(uint8_t channel, value_t value);
    void update();  // Physically update DAC outputs
};
```

### Supported Drivers

#### AD5593R Driver
- **Channels**: 8
- **Resolution**: 12-bit
- **Interface**: I2C with dynamic chip select
- **Special Features**: A0 pin for address expansion

#### MCP4728 Driver (Legacy)
- **Channels**: 4
- **Resolution**: 12-bit
- **Interface**: I2C
- **Status**: Maintained for compatibility

## Data Flow

### MIDI to CV Pipeline

```
MIDI Input (14-bit pitch bend)
    │
    ▼
[Offset Correction]
value - 8192 (center to zero)
    │
    ▼
[Scale to 16-bit]
value * 4 (14-bit to 16-bit)
    │
    ▼
[Re-center]
value + 32768 (0-65535 range)
    │
    ▼
[Buffer Update]
input_buffer[channel] = value
    │
    ▼
[Worker Copy]
local_buffer = input_buffer
    │
    ▼
[DAC Scaling]
value >> 4 (16-bit to 12-bit)
    │
    ▼
[I2C Transfer]
Wire.write(value)
    │
    ▼
[Hardware Output]
0-5V from DAC
    │
    ▼
[OpAmp Amplification]
2× gain → 0-10V CV
```

### Buffer Management

#### Double Buffering Strategy
- **Input Buffer**: Written by MIDI thread, read by workers
- **Output Buffer**: Currently unused, reserved for future features
- **Local Buffers**: Per-worker copies for I2C operations

#### Memory Layout
```cpp
static value_t input_buffer[16];   // Global input
static value_t output_buffer[16];  // Reserved
value_t local_buffer[8];           // Per-worker
```

## Performance Characteristics

### Latency Budget

| Component | Latency | Notes |
|-----------|---------|-------|
| USB MIDI | ~1ms | Windows USB stack limitation |
| MIDI Processing | <10μs | Simple arithmetic operations |
| Thread Switch | ~5μs | Cooperative scheduling |
| Buffer Copy | <5μs | 16 values, local memory |
| I2C Transfer | ~500μs | Primary bottleneck |
| OpAmp Response | <10μs | Analog settling time |
| **Total** | **~2-3ms** | End-to-end latency |

### Optimization Opportunities

#### Implemented
- Parallel I2C buses (Wire1, Wire2)
- Local buffer copies (no blocking during I2C)
- Template-based zero-overhead abstraction
- Static memory allocation

#### Future Improvements
- **I2C Batching**: Reduce per-transaction overhead (60-70% improvement potential)
- **Lock-free Structures**: Eliminate mutex contention (40% improvement potential)
- **SIMD Operations**: ARM DSP instructions for batch processing
- **DMA Transfers**: Hardware-accelerated I2C

### Resource Usage

#### Memory
- **Stack**: 256 bytes per thread
- **Heap**: 0 bytes (no dynamic allocation)
- **Static**: ~1KB for buffers and state
- **Code**: ~50KB firmware size

#### CPU
- **MIDI Thread**: <1% average
- **Worker Threads**: ~5% during updates
- **System Overhead**: <2%
- **Available Headroom**: >90%

## Real-Time Guarantees

### Design Constraints
- **No Dynamic Memory**: Prevents allocation failures
- **Bounded Execution**: All operations have known upper bounds
- **Priority Inversion Protection**: Mutex with timeout
- **Watchdog Safety**: Heartbeat on channel 15

### Timing Analysis
- **Worst Case Execution**: 3ms
- **Average Case**: 2ms
- **Best Case**: 1.5ms
- **Jitter**: ±0.5ms

## System Integration

### Hardware Abstraction Layer

```
Application Layer (main.cpp)
    │
    ▼
Framework Layer (dr_teeth, electric_mayhem)
    │
    ▼
Driver Layer (AD5593R, MCP4728)
    │
    ▼
HAL Layer (Wire, TeensyThreads)
    │
    ▼
Hardware (I2C, GPIO, USB)
```

### I2C Bus Architecture

#### Bus Allocation
- **Wire1**: DAC 1 (channels 1-8)
- **Wire2**: DAC 2 (channels 9-16)
- **SDA/SCL Pins**: Teensy 4.1 default assignments

#### Addressing Scheme
- **Base Address**: 0x10 (AD5593R default)
- **Chip Select**: Pin 11 (DAC 1), Pin 37 (DAC 2)
- **Dynamic Selection**: A0 pin control

## Error Handling

### Fault Detection
- I2C communication timeouts
- Invalid MIDI data detection
- Buffer overflow protection
- Sequence mismatch detection

### Recovery Strategies
- Automatic I2C bus reset
- Skipped update on sequence mismatch
- Default value fallback
- Heartbeat verification

## Testing & Validation

### Unit Testing
- Template instantiation validation
- Thread safety verification
- Conversion accuracy testing
- Timing measurement

### Integration Testing
- End-to-end latency measurement
- Multi-channel stress testing
- Long-duration stability
- Power cycle recovery

### Hardware Testing
- Oscilloscope verification (0-10V output)
- Multimeter calibration
- MIDI controller validation
- Thermal stability testing

---

*For implementation details, see the [source code](src/). For hardware specifications, see [HARDWARE.md](HARDWARE.md).*