/**
 * PCB Renderer - Handles component rendering and layer management
 */

class PCBRenderer {
    constructor(svgElement, footprintLibrary) {
        this.svg = svgElement;
        this.footprintLibrary = footprintLibrary;
        this.components = new Map();
        this.selectedComponent = null;
        this.currentLayer = 1;
        this.layerCount = 2; // Default 2-layer board
        
        this.initializeLayers();
        this.setupEventHandlers();
    }

    initializeLayers() {
        // Configure layers based on board type
        this.layers = {
            0: { name: 'Grid/Outline', visible: true, color: '#4CAF50' },
            1: { name: 'Top Layer', visible: true, color: '#ff0000' },
            2: { name: 'Inner 1', visible: false, color: '#00ff00' },
            3: { name: 'Inner 2', visible: false, color: '#0000ff' },
            4: { name: 'Bottom Layer', visible: false, color: '#ffff00' }
        };
        
        this.updateLayerVisibility();
    }

    setLayerCount(count) {
        this.layerCount = count;
        
        // Show/hide layers based on count
        const layer2 = this.svg.querySelector('#layer-2');
        const layer3 = this.svg.querySelector('#layer-3');
        const layer4 = this.svg.querySelector('#layer-4');
        
        switch(count) {
            case 1:
                layer2.style.display = 'none';
                layer3.style.display = 'none';
                layer4.style.display = 'none';
                break;
            case 2:
                layer2.style.display = 'none';
                layer3.style.display = 'none';
                layer4.style.display = 'block';
                this.layers[4].visible = true;
                break;
            case 4:
                layer2.style.display = 'block';
                layer3.style.display = 'block';
                layer4.style.display = 'block';
                this.layers[2].visible = true;
                this.layers[3].visible = true;
                this.layers[4].visible = true;
                break;
        }
        
        this.updateLayerVisibility();
    }

    updateLayerVisibility() {
        Object.entries(this.layers).forEach(([layerId, layer]) => {
            const layerElement = this.svg.querySelector(`#layer-${layerId}`);
            if (layerElement) {
                layerElement.style.display = layer.visible ? 'block' : 'none';
            }
        });
    }

    addComponent(reference, footprintId, x, y, rotation = 0, layer = 1) {
        const footprint = this.footprintLibrary.getFootprint(footprintId);
        if (!footprint) {
            console.error(`Footprint not found: ${footprintId}`);
            return null;
        }

        const component = {
            reference,
            footprintId,
            footprint,
            x,
            y,
            rotation,
            layer,
            selected: false
        };

        // Create SVG group for component
        const componentGroup = this.createComponentSVG(component);
        
        // Add to appropriate layer
        const layerElement = this.svg.querySelector(`#layer-${layer}`);
        layerElement.appendChild(componentGroup);
        
        // Store component
        this.components.set(reference, component);
        
        return component;
    }

    createComponentSVG(component) {
        const { reference, footprint, x, y, rotation } = component;
        
        // Create main group
        const group = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        group.setAttribute('id', `comp-${reference}`);
        group.setAttribute('data-ref', reference);
        group.classList.add('component');
        group.setAttribute('transform', `translate(${x}, ${y}) rotate(${rotation})`);

        // Create component body
        const body = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        body.setAttribute('x', -footprint.width / 2);
        body.setAttribute('y', -footprint.height / 2);
        body.setAttribute('width', footprint.width);
        body.setAttribute('height', footprint.height);
        body.setAttribute('fill', footprint.color);
        body.setAttribute('stroke', '#000');
        body.setAttribute('stroke-width', '0.1');
        body.classList.add('component-body');

        // Create pads
        const padsGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        padsGroup.classList.add('component-pads');
        
        if (footprint.pads) {
            footprint.pads.forEach(pad => {
                const padElement = this.createPadSVG(pad);
                padsGroup.appendChild(padElement);
            });
        }

        // Create reference text
        const refText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        refText.setAttribute('x', 0);
        refText.setAttribute('y', 0);
        refText.setAttribute('text-anchor', 'middle');
        refText.setAttribute('dominant-baseline', 'central');
        refText.setAttribute('font-size', '2');
        refText.setAttribute('fill', 'white');
        refText.classList.add('component-label');
        refText.textContent = reference;

        // Assemble component
        group.appendChild(body);
        group.appendChild(padsGroup);
        group.appendChild(refText);

        return group;
    }

    createPadSVG(pad) {
        const padElement = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        padElement.setAttribute('x', pad.x - pad.width / 2);
        padElement.setAttribute('y', pad.y - pad.height / 2);
        padElement.setAttribute('width', pad.width);
        padElement.setAttribute('height', pad.height);
        
        // Style based on pad type
        if (pad.type === 'smd') {
            padElement.setAttribute('fill', '#c0c0c0');
            padElement.setAttribute('stroke', '#808080');
        } else { // tht
            padElement.setAttribute('fill', '#ffd700');
            padElement.setAttribute('stroke', '#cc9900');
        }
        
        padElement.setAttribute('stroke-width', '0.05');
        padElement.classList.add('component-pad');
        padElement.setAttribute('data-pad', pad.number);

        return padElement;
    }

    moveComponent(reference, newX, newY) {
        const component = this.components.get(reference);
        if (!component) return;

        component.x = newX;
        component.y = newY;

        const componentElement = this.svg.querySelector(`#comp-${reference}`);
        if (componentElement) {
            componentElement.setAttribute('transform', 
                `translate(${newX}, ${newY}) rotate(${component.rotation})`);
        }
    }

    rotateComponent(reference, rotation) {
        const component = this.components.get(reference);
        if (!component) return;

        component.rotation = rotation;

        const componentElement = this.svg.querySelector(`#comp-${reference}`);
        if (componentElement) {
            componentElement.setAttribute('transform', 
                `translate(${component.x}, ${component.y}) rotate(${rotation})`);
        }
    }

    selectComponent(reference) {
        // Deselect previous
        if (this.selectedComponent) {
            const prevElement = this.svg.querySelector(`#comp-${this.selectedComponent}`);
            if (prevElement) {
                prevElement.classList.remove('selected');
            }
        }

        // Select new
        this.selectedComponent = reference;
        if (reference) {
            const componentElement = this.svg.querySelector(`#comp-${reference}`);
            if (componentElement) {
                componentElement.classList.add('selected');
            }
        }

        return this.components.get(reference);
    }

    removeComponent(reference) {
        const componentElement = this.svg.querySelector(`#comp-${reference}`);
        if (componentElement) {
            componentElement.remove();
        }
        
        this.components.delete(reference);
        
        if (this.selectedComponent === reference) {
            this.selectedComponent = null;
        }
    }

    clearAll() {
        this.components.clear();
        this.selectedComponent = null;
        
        // Clear all component layers
        [1, 2, 3, 4].forEach(layerId => {
            const layer = this.svg.querySelector(`#layer-${layerId}`);
            layer.innerHTML = '';
        });
    }

    setupEventHandlers() {
        this.svg.addEventListener('click', (e) => {
            if (e.target.closest('.component')) {
                const componentElement = e.target.closest('.component');
                const reference = componentElement.getAttribute('data-ref');
                this.selectComponent(reference);
                
                // Dispatch custom event
                this.svg.dispatchEvent(new CustomEvent('componentSelected', {
                    detail: { reference, component: this.components.get(reference) }
                }));
            } else {
                this.selectComponent(null);
                this.svg.dispatchEvent(new CustomEvent('componentDeselected'));
            }
        });
    }

    getComponentAt(x, y) {
        // Find component at coordinates
        for (const [ref, comp] of this.components) {
            const dx = Math.abs(comp.x - x);
            const dy = Math.abs(comp.y - y);
            
            if (dx < comp.footprint.width / 2 && dy < comp.footprint.height / 2) {
                return comp;
            }
        }
        return null;
    }

    getComponent(reference) {
        return this.components.get(reference);
    }

    exportComponents() {
        const components = [];
        for (const [ref, comp] of this.components) {
            components.push({
                reference: ref,
                footprint: comp.footprintId,
                x: comp.x,
                y: comp.y,
                rotation: comp.rotation,
                layer: comp.layer
            });
        }
        return components;
    }

    importComponents(componentsData) {
        this.clearAll();
        
        componentsData.forEach(compData => {
            this.addComponent(
                compData.reference,
                compData.footprint,
                compData.x,
                compData.y,
                compData.rotation || 0,
                compData.layer || 1
            );
        });
    }
}

// Export for use in other modules
window.PCBRenderer = PCBRenderer;