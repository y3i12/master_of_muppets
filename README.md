# Master Of Muppets 
## In hard mode work in progress.... or *WIPPING HARD!!*
*Expect this repo to be under Buddhist impermanence: "transient, evanescent, inconstant". Currently under heavy development, everything can change at any moment.*

`USB MIDI to 16xCV interface, outputs 0-10v on the CV out according to the pitch bend sent on the respective MIDI channel.`

Similar to [Befaco MIDI Thing V2](https://www.befaco.org/midi-thing-v2/), [Der Mann mit der Maschine Droid Master 18](https://shop.dermannmitdermaschine.de/products/master18), [Expert Sleepers FH-2](https://www.expert-sleepers.co.uk/fh2.html), et al.
 - But open source...
 - And aiming to be done the DIY way (cheap and hacky)...
 - Done by a hobbyis producer, noob in electronics and old timer C++ addict...

The difference is that this fellow is not using [MAX11300](https://www.analog.com/media/en/technical-documentation/data-sheets/max11300.pdf), although it could support it. More details below.

At the moment Master Of Muppets only upscales MIDI pitch messages from their 14bit to framework common 16bit values and downscales it to the target DAC and sends them to different [AD5593R](https://www.analog.com/media/en/technical-documentation/data-sheets/ad5593r.pdf) (8x12 bit ADC/DAC) via I2C, one responsible for MIDI channels 1..8 and the other taking care of MIDI channels 9..16. 

The internally referenced DAC output ranges from 0V to 5V and is subsequently passed through a low pass filter and then amplified by 2 with OpAmps [TL074](https://www.ti.com/lit/ds/symlink/tl074-ep.pdf).

[This commit](https://github.com/y3i12/master_of_muppets/tree/7ddc9a420bcb24df1c32ecc6d5a23dffa7c8f9c1) has the prototype of it, running with 12 channesl using the [MCP4728](https://ww1.microchip.com/downloads/en/devicedoc/22187e.pdf). Not recommendable as the OpAmps need to be replaced by [LT1014](https://www.ti.com/lit/ds/symlink/lt1014d.pdf) (beatiful and expensive) due to a design flaw.... everywhere. Worked as a POC.


## Code Dependencies
 - Rob Tillaart's [AD5593R](https://github.com/RobTillaart/AD5593R) and [FunctionGenerator](https://github.com/RobTillaart/FunctionGenerator);
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
 - Claude AI is being used as aid;
   - The folder `claude` contains the context and the state of code analysis.


## Current Status
  - Starting to review schematics;
  - PCB is pending;
  - Firmware works, for 16 channels. Still need to benchmark.


## About GenAI `claude`

An iterative prompt is being used for big code changes:

```
Good day sir! It is time for another run. Let's update our project tracking and sync the reports.
In the context of the GitHub repository, I'd ask you to:
* Understand the README.md very well;
* Understand the current code base (no need to look in previous revisions);
* Understand the state of your control files in the folder `claude`;
* Clarify any possible uncertainty with me;
* Create or update the reports (they should be as much elaborated as possible for each finding in each topic) about the code, containing:
   * bugs & inconsistencies
   * static code analysis
   * design improvements
   * optimizations in the code
   * general remarks
   * feature propositions
* Analyze the KiCad schematics (disregard the PCB for the moment) and give me feedback about it's design, as OP (me) is unexperienced in the subject of electronics. Also consider this fact in your explanations. In case the files contain too many tokens, break them down before ingestion.
* Generate individual markdown files for each report;
* Generated code should follow rules described in `CODING_STYLE.md`;
* Keep the analysis context stored in the same folder so future iterations can happen easily;
```

On each smaller change/fix, the agent is activated again to uptade the context state;


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
