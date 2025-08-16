/**
 * Footprint Library - Real component footprints for PCB design
 * Based on Master of Muppets component analysis
 */

class FootprintLibrary {
    constructor() {
        this.footprints = this.initializeFootprints();
        this.categories = this.organizeByCategory();
    }

    initializeFootprints() {
        return {
            // Microcontrollers
            'Teensy41': {
                name: 'Teensy 4.1',
                package: 'DIP-48',
                width: 61.0,
                height: 17.78,
                pins: 48,
                pinPitch: 2.54,
                category: 'microcontrollers',
                pads: this.generateDIPPads(48, 2.54, 61.0, 17.78),
                color: '#4a90e2',
                description: 'Teensy 4.1 microcontroller',
                placement: { priority: 10, zone: 'digital' }
            },

            // DACs
            'AD5593R': {
                name: 'AD5593R DAC',
                package: 'TSSOP-16',
                width: 4.4,
                height: 5.0,
                pins: 16,
                pinPitch: 0.65,
                category: 'ics',
                pads: this.generateTSSOP16Pads(),
                color: '#e24a4a',
                description: '12-bit DAC/ADC with I2C',
                placement: { priority: 9, zone: 'analog' }
            },

            // OpAmps
            'TL074': {
                name: 'TL074 Quad OpAmp',
                package: 'SOIC-14',
                width: 3.9,
                height: 8.7,
                pins: 14,
                pinPitch: 1.27,
                category: 'ics',
                pads: this.generateSOIC14Pads(),
                color: '#e24a4a',
                description: 'Quad JFET OpAmp',
                placement: { priority: 8, zone: 'analog' }
            },

            // Connectors
            'Jack_3.5mm_TRS': {
                name: '3.5mm TRS Jack',
                package: 'TRS_Jack',
                width: 15.8,
                height: 15.8,
                pins: 3,
                pinPitch: 5.08,
                category: 'connectors',
                pads: this.generateJackPads(),
                color: '#e2a04a',
                description: '3.5mm stereo jack',
                placement: { priority: 7, zone: 'connectors', edge: true }
            },

            // Passives
            'R_0603': {
                name: '0603 Resistor',
                package: '0603',
                width: 1.6,
                height: 0.8,
                pins: 2,
                category: 'passives',
                pads: this.generate0603Pads(),
                color: '#e2e24a',
                description: '0603 SMD resistor',
                placement: { priority: 3, zone: 'any' }
            },

            'C_0603': {
                name: '0603 Capacitor',
                package: '0603',
                width: 1.6,
                height: 0.8,
                pins: 2,
                category: 'passives',
                pads: this.generate0603Pads(),
                color: '#4ae24a',
                description: '0603 SMD capacitor',
                placement: { priority: 4, zone: 'any' }
            },

            'C_0805': {
                name: '0805 Capacitor',
                package: '0805',
                width: 2.0,
                height: 1.25,
                pins: 2,
                category: 'passives',
                pads: this.generate0805Pads(),
                color: '#4ae24a',
                description: '0805 SMD capacitor',
                placement: { priority: 4, zone: 'any' }
            },

            // Power
            'LD1117': {
                name: 'LD1117 Regulator',
                package: 'TO-220',
                width: 10.0,
                height: 4.5,
                pins: 3,
                pinPitch: 2.54,
                category: 'power',
                pads: this.generateTO220Pads(),
                color: '#ff6b6b',
                description: '3.3V/5V regulator',
                placement: { priority: 6, zone: 'power', thermal: true }
            }
        };
    }

    // Pad generation methods
    generateDIPPads(pinCount, pitch, width, height) {
        const pads = [];
        const pinsPerSide = pinCount / 2;
        const padWidth = 1.6;
        const padHeight = 1.6;
        
        // Left side (pins 1 to n/2)
        for (let i = 0; i < pinsPerSide; i++) {
            pads.push({
                number: i + 1,
                x: -width/2,
                y: -height/2 + pitch/2 + i * pitch,
                width: padWidth,
                height: padHeight,
                type: 'tht'
            });
        }
        
        // Right side (pins n/2+1 to n)
        for (let i = 0; i < pinsPerSide; i++) {
            pads.push({
                number: pinsPerSide + i + 1,
                x: width/2,
                y: height/2 - pitch/2 - i * pitch,
                width: padWidth,
                height: padHeight,
                type: 'tht'
            });
        }
        
        return pads;
    }

    generateTSSOP16Pads() {
        const pads = [];
        const pitch = 0.65;
        const padWidth = 0.3;
        const padHeight = 1.5;
        const bodyWidth = 4.4;
        
        // Generate 8 pads on each side
        for (let i = 0; i < 8; i++) {
            // Left side
            pads.push({
                number: i + 1,
                x: -bodyWidth/2 - padWidth/2,
                y: -pitch * 3.5 + i * pitch,
                width: padWidth,
                height: padHeight,
                type: 'smd'
            });
            
            // Right side
            pads.push({
                number: 16 - i,
                x: bodyWidth/2 + padWidth/2,
                y: pitch * 3.5 - i * pitch,
                width: padWidth,
                height: padHeight,
                type: 'smd'
            });
        }
        
        return pads;
    }

    generateSOIC14Pads() {
        const pads = [];
        const pitch = 1.27;
        const padWidth = 0.6;
        const padHeight = 1.5;
        const bodyWidth = 3.9;
        
        for (let i = 0; i < 7; i++) {
            // Left side
            pads.push({
                number: i + 1,
                x: -bodyWidth/2 - padWidth/2,
                y: -pitch * 3 + i * pitch,
                width: padWidth,
                height: padHeight,
                type: 'smd'
            });
            
            // Right side
            pads.push({
                number: 14 - i,
                x: bodyWidth/2 + padWidth/2,
                y: pitch * 3 - i * pitch,
                width: padWidth,
                height: padHeight,
                type: 'smd'
            });
        }
        
        return pads;
    }

    generateJackPads() {
        return [
            { number: 1, x: -5.08, y: 0, width: 2.0, height: 2.0, type: 'tht' },
            { number: 2, x: 0, y: 0, width: 2.0, height: 2.0, type: 'tht' },
            { number: 3, x: 5.08, y: 0, width: 2.0, height: 2.0, type: 'tht' }
        ];
    }

    generate0603Pads() {
        return [
            { number: 1, x: -0.8, y: 0, width: 0.8, height: 0.95, type: 'smd' },
            { number: 2, x: 0.8, y: 0, width: 0.8, height: 0.95, type: 'smd' }
        ];
    }

    generate0805Pads() {
        return [
            { number: 1, x: -1.0, y: 0, width: 1.0, height: 1.25, type: 'smd' },
            { number: 2, x: 1.0, y: 0, width: 1.0, height: 1.25, type: 'smd' }
        ];
    }

    generateTO220Pads() {
        return [
            { number: 1, x: -2.54, y: 0, width: 1.8, height: 1.8, type: 'tht' },
            { number: 2, x: 0, y: 0, width: 1.8, height: 1.8, type: 'tht' },
            { number: 3, x: 2.54, y: 0, width: 1.8, height: 1.8, type: 'tht' }
        ];
    }

    organizeByCategory() {
        const categories = {};
        
        Object.entries(this.footprints).forEach(([id, footprint]) => {
            const category = footprint.category;
            if (!categories[category]) {
                categories[category] = [];
            }
            categories[category].push({ id, ...footprint });
        });
        
        return categories;
    }

    getFootprint(id) {
        return this.footprints[id];
    }

    getCategoryComponents(category) {
        return this.categories[category] || [];
    }

    getAllCategories() {
        return Object.keys(this.categories);
    }

    // Master of Muppets specific component set
    getMasterOfMuppetsComponents() {
        return {
            'T1': { footprint: 'Teensy41', position: { x: 20, y: 70 } },
            'DAC1': { footprint: 'AD5593R', position: { x: 25, y: 45 } },
            'DAC2': { footprint: 'AD5593R', position: { x: 25, y: 100 } },
            'U1': { footprint: 'TL074', position: { x: 60, y: 30 } },
            'U2': { footprint: 'TL074', position: { x: 70, y: 30 } },
            'U3': { footprint: 'TL074', position: { x: 60, y: 110 } },
            'U4': { footprint: 'TL074', position: { x: 70, y: 110 } },
            'REG1': { footprint: 'LD1117', position: { x: 10, y: 20 } }
        };
    }
}

// Export for use in other modules
window.FootprintLibrary = FootprintLibrary;