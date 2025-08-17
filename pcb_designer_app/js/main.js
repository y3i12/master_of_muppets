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
        this.isPanning = false;
        this.panStart = { x: 0, y: 0 };
        this.zoomLevel = 1.0;
        
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
        this.updateZoomDisplay('100');
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
        this.router = new PCBRouter(this.renderer, this.footprintLibrary);
        this.rasterVisualizer = new RasterNetVisualizer(this.renderer, this.router);
        this.drc = new DesignRuleChecker(this.renderer, this.router);
    }

    setupEventHandlers() {
        // Header buttons
        document.getElementById('auto-place').addEventListener('click', () => {
            this.runAutoPlacement();
        });
        
        document.getElementById('auto-route').addEventListener('click', () => {
            this.startRouting();
        });
        
        document.getElementById('run-drc').addEventListener('click', () => {
            this.runDRC();
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
                
                // Special handling for route tool
                if (e.target.dataset.tool === 'route') {
                    this.startRouting();
                }
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
        
        // Mouse wheel zoom
        svg.addEventListener('wheel', (e) => this.onMouseWheel(e));
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => this.onKeyDown(e));
        
        // Net visualization toggles
        document.getElementById('toggle-ratsnest').addEventListener('click', () => {
            const isVisible = this.rasterVisualizer.toggleRatsnest();
            this.updateToggleButton('toggle-ratsnest', isVisible);
            this.updateStatus(`Ratsnest ${isVisible ? 'shown' : 'hidden'}`);
        });
        
        document.getElementById('toggle-net-labels').addEventListener('click', () => {
            const isVisible = this.rasterVisualizer.toggleNetLabels();
            this.updateToggleButton('toggle-net-labels', isVisible);
            this.updateStatus(`Net labels ${isVisible ? 'shown' : 'hidden'}`);
        });
        
        document.getElementById('toggle-drc-markers').addEventListener('click', () => {
            const isVisible = this.drc.toggleDRC();
            this.updateToggleButton('toggle-drc-markers', isVisible);
            this.updateStatus(`DRC markers ${isVisible ? 'shown' : 'hidden'}`);
        });
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
            
            // Generate ratsnest after placement
            this.rasterVisualizer.generateRatsnest();
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
        if (e.button === 1 || (e.button === 0 && e.ctrlKey)) {
            // Middle mouse or Ctrl+left mouse for panning
            this.isPanning = true;
            const coords = this.getSVGCoordinates(e);
            this.panStart = { x: coords.x, y: coords.y };
            e.preventDefault();
        } else if (this.currentTool === 'select' && e.target.closest('.component')) {
            this.isDragging = true;
            this.dragTarget = e.target.closest('.component').dataset.ref;
        }
    }

    onMouseMove(e) {
        if (this.isPanning) {
            const coords = this.getSVGCoordinates(e);
            const deltaX = this.panStart.x - coords.x;
            const deltaY = this.panStart.y - coords.y;
            
            const svg = document.getElementById('pcb-canvas');
            const viewBox = svg.viewBox.baseVal;
            
            svg.setAttribute('viewBox', 
                `${viewBox.x + deltaX} ${viewBox.y + deltaY} ${viewBox.width} ${viewBox.height}`);
        } else if (this.isDragging && this.dragTarget) {
            const coords = this.getSVGCoordinates(e);
            this.renderer.moveComponent(this.dragTarget, coords.x, coords.y);
            this.updateSelectionPosition(coords);
        }
    }

    onMouseUp(e) {
        this.isDragging = false;
        this.dragTarget = null;
        this.isPanning = false;
    }

    onMouseWheel(e) {
        e.preventDefault();
        
        const zoomFactor = e.deltaY > 0 ? 0.9 : 1.1;
        const coords = this.getSVGCoordinates(e);
        
        this.zoomAtPoint(coords.x, coords.y, zoomFactor);
    }

    onKeyDown(e) {
        switch(e.key) {
            case '+':
            case '=':
                this.zoomIn();
                break;
            case '-':
                this.zoomOut();
                break;
            case '0':
                this.zoomFit();
                break;
            case 'f':
                if (e.ctrlKey) {
                    e.preventDefault();
                    this.zoomFit();
                }
                break;
        }
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
        this.adjustZoom(1.25);
    }

    zoomOut() {
        this.adjustZoom(0.8);
    }

    zoomFit() {
        this.fitToView();
    }

    adjustZoom(factor) {
        const svg = document.getElementById('pcb-canvas');
        const viewBox = svg.viewBox.baseVal;
        
        const centerX = viewBox.x + viewBox.width / 2;
        const centerY = viewBox.y + viewBox.height / 2;
        
        const newWidth = viewBox.width / factor;
        const newHeight = viewBox.height / factor;
        
        // Limit zoom to reasonable bounds
        if (newWidth < 10 || newWidth > 1000) return;
        
        const newX = centerX - newWidth / 2;
        const newY = centerY - newHeight / 2;
        
        svg.setAttribute('viewBox', `${newX} ${newY} ${newWidth} ${newHeight}`);
        
        this.zoomLevel = 100 / newWidth;
        const zoomPercent = (this.zoomLevel * 100).toFixed(0);
        this.updateZoomDisplay(zoomPercent);
    }

    fitToView() {
        const svg = document.getElementById('pcb-canvas');
        const boardWidth = this.renderer.boardWidth || 100;
        const boardHeight = this.renderer.boardHeight || 160;
        
        // Add 10% margin
        const margin = Math.max(boardWidth, boardHeight) * 0.1;
        const viewX = -margin;
        const viewY = -margin;
        const viewWidth = boardWidth + 2 * margin;
        const viewHeight = boardHeight + 2 * margin;
        
        svg.setAttribute('viewBox', `${viewX} ${viewY} ${viewWidth} ${viewHeight}`);
        this.zoomLevel = 100 / viewWidth;
        this.updateStatus('Zoomed to fit');
    }

    zoomAtPoint(x, y, factor) {
        const svg = document.getElementById('pcb-canvas');
        const viewBox = svg.viewBox.baseVal;
        
        const newWidth = viewBox.width / factor;
        const newHeight = viewBox.height / factor;
        
        // Limit zoom to reasonable bounds
        if (newWidth < 5 || newWidth > 2000) return;
        
        // Calculate new position to keep point under cursor
        const newX = x - (x - viewBox.x) / factor;
        const newY = y - (y - viewBox.y) / factor;
        
        svg.setAttribute('viewBox', `${newX} ${newY} ${newWidth} ${newHeight}`);
        
        this.zoomLevel = 100 / newWidth;
        const zoomPercent = (this.zoomLevel * 100).toFixed(0);
        this.updateZoomDisplay(zoomPercent);
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

    updateZoomDisplay(zoomPercent) {
        const zoomElement = document.getElementById('zoom-level');
        if (zoomElement) {
            zoomElement.textContent = `${zoomPercent}%`;
        }
        this.updateStatus(`Zoom: ${zoomPercent}%`);
    }

    startRouting() {
        this.updateStatus('Starting auto-routing...');
        
        try {
            const result = this.router.autoRouteAll();
            this.updateStatus(`Routing complete: ${result.success}/${result.total} nets (${result.percentage}%)`);
            
            // Update design rules panel with routing stats
            this.updateRoutingStats(result);
            
            // Update ratsnest to show routed connections
            this.rasterVisualizer.updateRoutedConnections(this.router.traces);
        } catch (error) {
            console.error('[ERROR] Auto-routing failed:', error);
            this.updateStatus('Auto-routing failed');
        }
    }

    updateRoutingStats(result) {
        // Future: Update design rules panel with routing statistics
        console.log(`[ROUTING] ${result.success}/${result.total} nets routed (${result.percentage}%)`);
    }

    updateToggleButton(buttonId, isActive) {
        const button = document.getElementById(buttonId);
        if (button) {
            button.classList.toggle('active', isActive);
        }
    }

    runDRC() {
        this.updateStatus('Running design rule check...');
        
        try {
            const report = this.drc.runFullDRC();
            
            const message = report.summary.passed 
                ? 'DRC passed - No violations found!'
                : `DRC complete: ${report.summary.errors} errors, ${report.summary.warnings} warnings`;
            
            this.updateStatus(message);
            this.showDRCResults(report);
        } catch (error) {
            console.error('[ERROR] DRC failed:', error);
            this.updateStatus('DRC check failed');
        }
    }

    showDRCResults(report) {
        // Simple console output for now
        console.log('[DRC] Design Rule Check Results:');
        console.log(`Total violations: ${report.summary.total}`);
        console.log(`Errors: ${report.summary.errors}`);
        console.log(`Warnings: ${report.summary.warnings}`);
        
        if (report.violations.length > 0) {
            console.log('\nViolations:');
            report.violations.forEach((v, i) => {
                console.log(`${i + 1}. ${v.type}: ${v.description}`);
            });
        }
        
        // Future: Create proper DRC results panel
    }
}

// Initialize application when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.pcbApp = new PCBDesignerApp();
});