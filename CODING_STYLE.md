# Master of Muppets Coding Style Rules

## Naming Conventions
- **Classes/Types**: `snake_case` (e.g., `electric_mayhem`, `muppet_clock`, `rob_tillaart_ad_5993r`)
- **Constants**: `k_` prefix with `snake_case` (e.g., `k_dac_count`, `k_channels_per_dac`, `k_max_value`)
- **Variables/Functions**: `snake_case` (e.g., `input_buffer`, `attention_please`, `throw_muppet_in_the_mud`)
- **Static members**: `snake_case` (e.g., `global_time_f`, `tick_time`)
- **Namespaces**: `snake_case` (e.g., `drivers`)

## File Organization
- **Headers**: `.h` extension with `#pragma once`
- **Implementations**: `.cpp` extension
- **Driver separation**: Driver classes in `drivers/` subdirectory
- **Include order**: Standard libraries first, then project headers

## Code Structure
- **Template definitions**: In header files with implementation
- **Class layout**: Public members first, protected/private last
- **Static functions**: Used for thread workers and utilities
- **Inline functions**: Small utility functions marked `inline`

## Formatting
- **Indentation**: 4 spaces (no tabs)
- **Braces**: Opening brace on same line for functions/classes, new line for control structures
- **Spacing**: Space around operators, after commas, around template brackets
- **Line length**: Reasonable wrapping for readability
- **Alignment**: Function parameters and array initializers aligned

## Vertical Alignment Rules
- **Variable declarations**: Align variable types, names and assignment operators when declaring multiple related variables. Use spacing to separate type from variable name for readability.
  ```cpp
  static constexpr uint8_t  k_dac_count                   = 2;
  static constexpr uint8_t  k_channels_per_dac            = 8;
  static constexpr uint8_t  k_total_channels              = k_dac_count * k_channels_per_dac;
  static constexpr uint16_t k_max_value                   = 64 * 1024 - 1;
  static constexpr int      k_thread_slice_micros         = 10;
  static constexpr int      k_force_refresh_every_millis  = 100;
  ```
- **Member variable declarations**: Use consistent spacing between type and variable name to improve readability
  ```cpp
  static float    global_time_f;
  static uint32_t tick_time;
  static uint32_t last_tick_time;
  static uint32_t last_tick_delta;
  ```
- **Member declarations**: Align pointer/reference operators and member names in structs/classes
  ```cpp
  dac_driver_t*    muppet;
  Threads::Mutex*  lock;
  uint8_t*         dirty;
  uint16_t*        output_buffer;
  ```
- **Array declarations**: Align brackets and array names for consistency
  ```cpp
  static uint16_t           input_buffer[  k_total_channels ];
  static uint16_t           output_buffer[ k_total_channels ];
  ```
- **Constructor initialization lists**: Align member initializers vertically
  ```cpp
  orientation_guide( dac_driver_t& the_muppet, Threads::Mutex& the_lock, uint8_t& the_dirty_flag, uint16_t* the_buffer ) :
      muppet(        &the_muppet     ),
      lock(          &the_lock       ),
      dirty(         &the_dirty_flag ),
      output_buffer( the_buffer      )
  {}
  ```
- **Array initializers**: Align elements in multi-line array initialization
  ```cpp
  dac_driver_t::initialization_struct_t initialization_structs[ dr_teeth::k_dac_count ] = {
      dac_driver_t::initialization_struct_t( &Wire2 ),
      dac_driver_t::initialization_struct_t( &Wire1 ),
  };
  ```
- **Array values**: Align values in lookup tables and data arrays for readability
  ```cpp
  static constexpr int16_t k_heartbeat_lut[ k_heartbeat_lut_size ] = {
       2000,  4000,  6000,  8000, 10000, 12000, 14000, 16000,
      18000, 20000, 22000, 24000, 26000, 28000, 30000, 32000,
      30000, 28000, 26000, 24000, 22000, 20000, 18000, 16000,
      14000, 12000, 10000,  8000,  6000,  4000,  2000,     0
  };
  ```
- **Template declarations**: Space between angle brackets and typename
  ```cpp
  template< typename T >
  ```
- **Function parameters**: Align parameters in multi-line function declarations
- **Assignment operators**: Align `=` operators when declaring related constants or variables
- **Closing brackets alignment**: Align closing brackets, parentheses, and braces vertically when they appear in related lines
  ```cpp
  int16_t value1 = k_heartbeat_lut[ index     ];
  int16_t value2 = k_heartbeat_lut[ index + 1 ];
  
  function_call( parameter1 );
  function_call( parameter2 );
  ```

## Memory Management
- **Static arrays**: Used for buffers with compile-time sizes
- **Stack allocation**: Preferred for small, temporary buffers
- **No dynamic allocation**: Embedded-friendly approach
- **Const correctness**: Constants properly marked

## Types and Constants
- **Explicit types**: `uint8_t`, `uint16_t`, `uint32_t` instead of `int`
- **Static constexpr**: For compile-time constants
- **Typedef usage**: Type aliases for template parameters and value types
- **Template constraints**: Explicit template parameter naming

## Arduino/Embedded Specifics
- **Pin configuration**: Explicit pinMode and digitalWrite calls
- **Wire interface**: Standard I2C initialization patterns
- **Thread integration**: TeensyThreads library usage
- **Hardware abstraction**: Driver wrapper classes

## Comments and Documentation
- **Minimal comments**: Code should be self-documenting
- **Section dividers**: `////////////////////////////////////////////////////////////////////////////////`
- **Inline explanations**: Only for complex logic or hardware-specific operations

## Error Handling
- **Bounds checking**: Explicit range validation before array access
- **Retry logic**: Hardware initialization with retry counters
- **Graceful degradation**: Return early on invalid inputs

## Template Usage
- **Generic interfaces**: Template classes for hardware abstraction
- **Type safety**: Strong typing with typedef aliases
- **Compile-time polymorphism**: Preferred over runtime polymorphism