# Master Of Muppets **Hard mode WIP.... or WIPPING HARD!!**
*Expect this repo to be under Buddhist impermanence: "transient, evanescent, inconstant". Currently under heavy development, everything can change at any moment.*

`USB MIDI to 16xCV interface, outputs 0-10v on the CV out according to the pitch bend sent on the respective MIDI channel.`

Similar to [Befaco MIDI Thing V2](https://www.befaco.org/midi-thing-v2/), [Der Mann mit der Maschine Droid Master 18](https://shop.dermannmitdermaschine.de/products/master18), [Expert Sleepers FH-2](https://www.expert-sleepers.co.uk/fh2.html), et al.
But open source...
And aiming to be done the DIY way (cheap)...
Done by a noob in electronics, but old time C++ addict...

The difference is that this fellow is not using [MAX11300](https://www.analog.com/media/en/technical-documentation/data-sheets/max11300.pdf), although it could support it. More details below.

At the moment Master Of Muppets only translates MIDI pitch messages from 0..65k (16 bit) downscales it to 0..4k (12 bit) and sends them to different [AD5593R](https://www.analog.com/media/en/technical-documentation/data-sheets/ad5593r.pdf) (8x12 bit ADC/DAC) via I2C, one responsible for MIDI channels 1..8 and the other taking care of MIDI channels 9..16. 

The internally referenced DAC output ranges from 0V to 5V and is subsequently passed through a low pass filter and then amplified by 2 with OpAmps [TL074](https://www.ti.com/lit/ds/symlink/tl074-ep.pdf).

[This commit](https://github.com/y3i12/master_of_muppets/tree/7ddc9a420bcb24df1c32ecc6d5a23dffa7c8f9c1) has the prototype of it, running with 12 channesl using the [MCP4728](https://ww1.microchip.com/downloads/en/devicedoc/22187e.pdf).


## Code Dependencies
 - Rob Tillaart's [AD5593R](https://github.com/RobTillaart/AD5593R);
 - Fernando Trias' [TeensyThreads](https://github.com/ftrias/TeensyThreads)
 - Adafruit's [MCP4728](https://github.com/adafruit/Adafruit_MCP4728) and [BusIO](https://github.com/adafruit/Adafruit_BusIO)
 - The Muppets

All dependencies are incorporated in the project - for hackability... and trouble updating them.


## Code Disclaimer
 - The code was done in a way that it would be fun to read, knowing that it won't make it more maintainable. It references The Muppets, Dr. Teeth and The Electric Mayhem.
 - Expect puns.
 - It is asynchronous, but simple:
   - One thread reads MIDI and copies it to a buffer (`dr_teeth`);
   - The other updates the DACs (`electric_mayhem`);
 - Makes somewhat extensive use of templating, which still can be improved;
 - Supports drivers for different DACs, currently AD5593R and MCP4728, both via I2C:
   - Enables mingling different buses and DACs;
   - Enables easy expansion of the hardware by using a chip select pin (possibly with the cost of lower refresh rate).
 - On Windows it is currently limited by the update frequency of the USB stack which is about 1KHz;
   - An alternative would be ethernet, *probably it is a terrible idea*.


## Current Status
  - Starting to review schematics;
  - PCB is pending;
  - Firmware works, for 16 channels. Still need to benchmark.


## To explore in the future
  - Some sort of documentation;
  - Expand Master of Muppets to also send data back to the host:
    - Read 0..10V, downscale to 0-5V into the same terminal that is amplified to the output using another set of OpAmps;
    - Make use of AD5593R ADC to read through the same ports;
    - Might need leds to indicate I/O;
    - Might need specific messaging or more GPIO (there's a lot free) to get I/O direction;
  - Experiment with [AD5592R](https://www.analog.com/media/en/technical-documentation/data-sheets/ad5592r.pdf) (the SPI version of AD5593R) if I2C DAC isn't fast enough;
  - Different boards with different features - same firmware with different compilation flags;
  - Physical modular assembly with flat cables or pin headers, using modules divided hierarchically like (but not exactly) in the schematics;
  - Enhance the firmware, having something like Droid Master 18 (which is awesome), but a bit more flexible, maybe with a small uploadable bytecode, but mostly for mapping - check for embedded scripting languages;
  - MIDI over Ethernet instead of USB, maybe with a crossover cable? It wouldn't be as plug and play. Maybe MIDI2;


## What didn't work
  - A VST converting MIDI to serial over USB, using the same threaded design.
    - The plugin was finicky;
    - The protocol was getting complex;
    - The code was (even more) convoluted;
    - There was the 1KHz limit;
