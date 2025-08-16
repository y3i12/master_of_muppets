/**
 * Main Application Controller - PCB Designer
 * Integrates all modules and handles UI interactions
 */

class PCBDesignerApp {
    constructor() {
        this.footprintLibrary = new FootprintLibrary();
        this.renderer = null;
        this.autoPlacer = null;
        this.currentTool = 'select';
        this.isDragging = false;
        this.dragTarget = null;
        
        this.init();
    }

    init() {
        console.log('[APP] Initializing PCB Designer...');
        
        // Initialize modules
        this.initializeRenderer();
        this.initializeAutoPlacer();
        this.setupEventHandlers();
        this.populateComponentLibrary();
        this.setupLayerControls();
        
        console.log('[APP] PCB Designer ready!');
        this.updateStatus('Ready - Click Auto Place to start');
    }

    initializeRenderer() {
        const svgElement = document.getElementById('pcb-canvas');
        this.renderer = new PCBRenderer(svgElement, this.footprintLibrary);
        
        // Set up component selection events
        svgElement.addEventListener('componentSelected', (e) => {
            this.onComponentSelected(e.detail);
        });
        
        svgElement.addEventListener('componentDeselected', () => {
            this.onComponentDeselected();
        });
    }

    initializeAutoPlacer() {
        this.autoPlacer = new AutoPlacer(this.renderer, this.footprintLibrary);
    }

    setupEventHandlers() {
        // Header buttons
        document.getElementById('auto-place').addEventListener('click', () => {
            this.runAutoPlacement();
        });
        
        document.getElementById('layer-toggle').addEventListener('click', () => {
            this.toggleLayerPanel();
        });
        
        document.getElementById('export').addEventListener('click', () => {
            this.exportLayout();
        });

        // Canvas toolbar
        document.getElementById('zoom-in').addEventListener('click', () => this.zoomIn());
        document.getElementById('zoom-out').addEventListener('click', () => this.zoomOut());
        document.getElementById('zoom-fit').addEventListener('click', () => this.zoomFit());

        // Tool selection
        document.querySelectorAll('.tool-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.selectTool(e.target.dataset.tool);
            });
        });

        // Board size selection
        document.getElementById('board-size').addEventListener('change', (e) => {
            this.changeBoardSize(e.target.value);
        });

        // Mouse tracking on canvas
        const svg = document.getElementById('pcb-canvas');
        svg.addEventListener('mousemove', (e) => this.updateMouseCoordinates(e));
        
        // Drag and drop
        svg.addEventListener('mousedown', (e) => this.onMouseDown(e));
        svg.addEventListener('mousemove', (e) => this.onMouseMove(e));
        svg.addEventListener('mouseup', (e) => this.onMouseUp(e));
    }

    populateComponentLibrary() {
        const categoriesElement = document.getElementById('component-categories');
        const categories = this.footprintLibrary.getAllCategories();
        
        categories.forEach(category => {
            const categoryDiv = document.createElement('div');
            categoryDiv.innerHTML = `<h4>${category.charAt(0).toUpperCase() + category.slice(1)}</h4>`;
            
            const components = this.footprintLibrary.getCategoryComponents(category);
            components.forEach(component => {
                const componentDiv = document.createElement('div');
                componentDiv.className = 'component-item';
                componentDiv.textContent = `${component.name} (${component.package})`;
                componentDiv.dataset.footprint = component.id;
                
                componentDiv.addEventListener('click', () => {
                    this.selectComponentType(component.id);
                });
                
                categoryDiv.appendChild(componentDiv);
            });
            
            categoriesElement.appendChild(categoryDiv);
        });
    }

    setupLayerControls() {
        const layerControl = document.getElementById('layer-control');
        const layers = [
            { id: 1, name: 'Top Layer', color: '#ff0000' },
            { id: 2, name: 'Inner 1', color: '#00ff00' },
            { id: 3, name: 'Inner 2', color: '#0000ff' },
            { id: 4, name: 'Bottom Layer', color: '#ffff00' }
        ];
        
        layers.forEach(layer => {
            const layerDiv = document.createElement('div');
            layerDiv.className = 'layer-item';
            layerDiv.innerHTML = `
                <input type="checkbox" id="layer-${layer.id}" ${layer.id === 1 || layer.id === 4 ? 'checked' : ''}>
                <div class="layer-color" style="background-color: ${layer.color}"></div>
                <label for="layer-${layer.id}">${layer.name}</label>
            `;
            
            const checkbox = layerDiv.querySelector('input');
            checkbox.addEventListener('change', () => {
                this.toggleLayer(layer.id, checkbox.checked);
            });
            
            layerControl.appendChild(layerDiv);
        });
    }

    // Event handlers
    runAutoPlacement() {
        this.updateStatus('Running auto-placement...');
        
        try {
            const placed = this.autoPlacer.autoPlace();
            this.updateStatus(`Auto-placement complete: ${placed.length} components placed`);
        } catch (error) {
            console.error('[ERROR] Auto-placement failed:', error);
            this.updateStatus('Auto-placement failed');
        }
    }

    onComponentSelected(detail) {
        const { reference, component } = detail;
        
        // Update selection info panel
        document.getElementById('sel-ref').textContent = reference;
        document.getElementById('sel-package').textContent = component.footprint.package;
        document.getElementById('sel-position').textContent = `(${component.x.toFixed(1)}, ${component.y.toFixed(1)})`;
        
        const rotationInput = document.getElementById('sel-rotation');
        rotationInput.value = component.rotation;
        rotationInput.disabled = false;
        
        rotationInput.onchange = () => {
            this.renderer.rotateComponent(reference, parseInt(rotationInput.value));
        };
    }

    onComponentDeselected() {
        document.getElementById('sel-ref').textContent = '-';
        document.getElementById('sel-package').textContent = '-';
        document.getElementById('sel-position').textContent = '-';
        document.getElementById('sel-rotation').disabled = true;
    }

    onMouseDown(e) {
        if (this.currentTool === 'select' && e.target.closest('.component')) {
            this.isDragging = true;
            this.dragTarget = e.target.closest('.component').dataset.ref;
        }
    }

    onMouseMove(e) {
        if (this.isDragging && this.dragTarget) {
            const coords = this.getSVGCoordinates(e);
            this.renderer.moveComponent(this.dragTarget, coords.x, coords.y);
            this.updateSelectionPosition(coords);
        }
    }

    onMouseUp(e) {
        this.isDragging = false;
        this.dragTarget = null;
    }

    getSVGCoordinates(event) {
        const svg = document.getElementById('pcb-canvas');
        const rect = svg.getBoundingClientRect();
        const viewBox = svg.viewBox.baseVal;
        
        const x = ((event.clientX - rect.left) / rect.width) * viewBox.width;
        const y = ((event.clientY - rect.top) / rect.height) * viewBox.height;
        
        return { x, y };
    }

    updateMouseCoordinates(event) {
        const coords = this.getSVGCoordinates(event);
        document.getElementById('mouse-coords').textContent = 
            `${coords.x.toFixed(1)}, ${coords.y.toFixed(1)}`;
    }

    updateSelectionPosition(coords) {
        document.getElementById('sel-position').textContent = 
            `(${coords.x.toFixed(1)}, ${coords.y.toFixed(1)})`;
    }

    selectTool(tool) {
        this.currentTool = tool;
        
        document.querySelectorAll('.tool-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.tool === tool);
        });
        
        const svg = document.getElementById('pcb-canvas');
        svg.style.cursor = tool === 'select' ? 'default' : 'crosshair';
    }

    selectComponentType(footprintId) {
        document.querySelectorAll('.component-item').forEach(item => {
            item.classList.toggle('selected', item.dataset.footprint === footprintId);
        });
        
        this.selectedFootprintType = footprintId;
        this.updateStatus(`Selected: ${this.footprintLibrary.getFootprint(footprintId).name}`);
    }

    changeBoardSize(size) {
        if (size === '100x160') {
            this.renderer.boardWidth = 100;
            this.renderer.boardHeight = 160;
        } else if (size === '100x100') {
            this.renderer.boardWidth = 100;
            this.renderer.boardHeight = 100;
        }
        // Update SVG viewBox would go here
        this.updateStatus(`Board size: ${size}mm`);
    }

    toggleLayer(layerId, visible) {
        this.renderer.layers[layerId].visible = visible;
        this.renderer.updateLayerVisibility();
    }

    toggleLayerPanel() {
        // Future: Implement layer panel toggle
        console.log('[INFO] Layer panel toggle not yet implemented');
    }

    zoomIn() {
        // Future: Implement zoom functionality
        console.log('[INFO] Zoom functionality not yet implemented');
    }

    zoomOut() {
        console.log('[INFO] Zoom functionality not yet implemented');
    }

    zoomFit() {
        console.log('[INFO] Zoom fit functionality not yet implemented');
    }

    exportLayout() {
        const components = this.renderer.exportComponents();
        
        const exportData = {
            board: {
                width: this.renderer.boardWidth || 100,
                height: this.renderer.boardHeight || 160,
                layers: this.renderer.layerCount || 2
            },
            components: components,
            timestamp: new Date().toISOString()
        };
        
        const blob = new Blob([JSON.stringify(exportData, null, 2)], 
            { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = 'pcb_layout.json';
        a.click();
        
        URL.revokeObjectURL(url);
        this.updateStatus('Layout exported');
    }

    updateStatus(message) {
        document.getElementById('status').textContent = message;
        console.log(`[STATUS] ${message}`);
    }
}

// Initialize application when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.pcbApp = new PCBDesignerApp();
});