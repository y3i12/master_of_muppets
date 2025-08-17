/**
 * PCB Router v1.0 - Intelligent PCB trace routing engine
 * Implements Lee algorithm with optimizations for PCB design
 */

class PCBRouter {
    constructor(renderer, footprintLibrary) {
        this.renderer = renderer;
        this.footprintLibrary = footprintLibrary;
        this.gridSize = 0.1; // 0.1mm grid resolution
        this.routingGrid = null;
        this.traces = [];
        this.vias = [];
        this.nets = new Map();
        
        // Design rules
        this.rules = {
            minTraceWidth: 0.1,     // mm
            minViaSize: 0.2,        // mm  
            minSpacing: 0.15,       // mm
            defaultTraceWidth: 0.2, // mm
            layerSpacing: 1.6       // mm between layers
        };
        
        this.initializeGrid();
    }

    initializeGrid() {
        const boardWidth = this.renderer.boardWidth || 100;
        const boardHeight = this.renderer.boardHeight || 160;
        
        this.gridWidth = Math.ceil(boardWidth / this.gridSize);
        this.gridHeight = Math.ceil(boardHeight / this.gridSize);
        
        // Initialize 4-layer routing grid
        this.routingGrid = {
            layers: [
                this.createEmptyGrid(), // Layer 1 (Top)
                this.createEmptyGrid(), // Layer 2 (Inner 1) 
                this.createEmptyGrid(), // Layer 3 (Inner 2)
                this.createEmptyGrid()  // Layer 4 (Bottom)
            ],
            obstacles: this.createEmptyGrid()
        };
        
        console.log(`[ROUTER] Grid initialized: ${this.gridWidth}×${this.gridHeight} (${this.gridSize}mm resolution)`);
    }

    createEmptyGrid() {
        const grid = [];
        for (let y = 0; y < this.gridHeight; y++) {
            grid[y] = [];
            for (let x = 0; x < this.gridWidth; x++) {
                grid[y][x] = {
                    occupied: false,
                    netId: null,
                    cost: 1,
                    distance: Infinity,
                    parent: null
                };
            }
        }
        return grid;
    }

    addObstacles(components) {
        // Clear existing obstacles
        this.routingGrid.obstacles = this.createEmptyGrid();
        
        components.forEach(component => {
            const footprint = this.footprintLibrary.getFootprint(component.footprint);
            if (!footprint) return;
            
            // Add component body as obstacle
            const x1 = Math.floor((component.x - footprint.width/2) / this.gridSize);
            const y1 = Math.floor((component.y - footprint.height/2) / this.gridSize);
            const x2 = Math.ceil((component.x + footprint.width/2) / this.gridSize);
            const y2 = Math.ceil((component.y + footprint.height/2) / this.gridSize);
            
            for (let y = Math.max(0, y1); y < Math.min(this.gridHeight, y2); y++) {
                for (let x = Math.max(0, x1); x < Math.min(this.gridWidth, x2); x++) {
                    this.routingGrid.obstacles[y][x].occupied = true;
                }
            }
        });
        
        console.log(`[ROUTER] Added obstacles for ${components.length} components`);
    }

    generateNetlist() {
        // Generate Master of Muppets netlist based on schematic
        const netlist = [
            {
                name: 'VCC',
                pins: [
                    { component: 'T1', pin: 'VIN' },
                    { component: 'DAC1', pin: 'VDD' },
                    { component: 'DAC2', pin: 'VDD' },
                    { component: 'U1', pin: 'VCC' },
                    { component: 'U2', pin: 'VCC' },
                    { component: 'U3', pin: 'VCC' },
                    { component: 'U4', pin: 'VCC' }
                ]
            },
            {
                name: 'GND',
                pins: [
                    { component: 'T1', pin: 'GND' },
                    { component: 'DAC1', pin: 'VSS' },
                    { component: 'DAC2', pin: 'VSS' },
                    { component: 'U1', pin: 'VSS' },
                    { component: 'U2', pin: 'VSS' },
                    { component: 'U3', pin: 'VSS' },
                    { component: 'U4', pin: 'VSS' }
                ]
            },
            {
                name: 'I2C_SDA',
                pins: [
                    { component: 'T1', pin: 'SDA' },
                    { component: 'DAC1', pin: 'SDA' },
                    { component: 'DAC2', pin: 'SDA' }
                ]
            },
            {
                name: 'I2C_SCL', 
                pins: [
                    { component: 'T1', pin: 'SCL' },
                    { component: 'DAC1', pin: 'SCL' },
                    { component: 'DAC2', pin: 'SCL' }
                ]
            }
        ];
        
        // Generate CV output nets (16 channels)
        for (let i = 0; i < 16; i++) {
            const dac = i < 8 ? 'DAC1' : 'DAC2';
            const dacPin = `OUT${(i % 8) + 1}`;
            const opAmp = `U${Math.floor(i / 4) + 1}`;
            const opAmpPin = `IN${(i % 4) + 1}`;
            const jack = `J${i + 2}`;
            
            netlist.push({
                name: `CV_${i + 1}`,
                pins: [
                    { component: dac, pin: dacPin },
                    { component: opAmp, pin: opAmpPin },
                    { component: opAmp, pin: `OUT${(i % 4) + 1}` },
                    { component: jack, pin: 'TIP' }
                ]
            });
        }
        
        return netlist;
    }

    routeNet(net) {
        console.log(`[ROUTER] Routing net: ${net.name} (${net.pins.length} pins)`);
        
        if (net.pins.length < 2) return [];
        
        const routes = [];
        const startPin = net.pins[0];
        
        // Route from first pin to all other pins (star topology)
        for (let i = 1; i < net.pins.length; i++) {
            const endPin = net.pins[i];
            const route = this.routeTwoPoints(startPin, endPin, net.name);
            
            if (route.length > 0) {
                routes.push(route);
                this.markRouteAsOccupied(route, net.name);
            } else {
                console.warn(`[ROUTER] Failed to route ${startPin.component}:${startPin.pin} to ${endPin.component}:${endPin.pin}`);
            }
        }
        
        return routes;
    }

    routeTwoPoints(startPin, endPin, netName) {
        // Get component positions
        const startComp = this.renderer.getComponent(startPin.component);
        const endComp = this.renderer.getComponent(endPin.component);
        
        if (!startComp || !endComp) {
            console.warn(`[ROUTER] Component not found: ${startPin.component} or ${endPin.component}`);
            return [];
        }
        
        // Convert to grid coordinates
        const start = {
            x: Math.round(startComp.x / this.gridSize),
            y: Math.round(startComp.y / this.gridSize),
            layer: 1 // Start on top layer
        };
        
        const end = {
            x: Math.round(endComp.x / this.gridSize),
            y: Math.round(endComp.y / this.gridSize),
            layer: 1 // End on top layer
        };
        
        // Use Lee algorithm (maze routing)
        return this.leeRoute(start, end, netName);
    }

    leeRoute(start, end, netName) {
        // Reset distance field
        for (let layer = 0; layer < 4; layer++) {
            for (let y = 0; y < this.gridHeight; y++) {
                for (let x = 0; x < this.gridWidth; x++) {
                    this.routingGrid.layers[layer][y][x].distance = Infinity;
                    this.routingGrid.layers[layer][y][x].parent = null;
                }
            }
        }
        
        // Initialize start point
        const queue = [{ x: start.x, y: start.y, layer: start.layer - 1, distance: 0 }];
        this.routingGrid.layers[start.layer - 1][start.y][start.x].distance = 0;
        
        // Wave expansion
        while (queue.length > 0) {
            const current = queue.shift();
            
            // Check if we reached the target
            if (current.x === end.x && current.y === end.y && current.layer === end.layer - 1) {
                return this.backtrackPath(start, end);
            }
            
            // Explore neighbors
            const neighbors = this.getNeighbors(current);
            
            for (const neighbor of neighbors) {
                if (this.isValidMove(current, neighbor, netName)) {
                    const newDistance = current.distance + this.getMoveCost(current, neighbor);
                    
                    if (newDistance < this.routingGrid.layers[neighbor.layer][neighbor.y][neighbor.x].distance) {
                        this.routingGrid.layers[neighbor.layer][neighbor.y][neighbor.x].distance = newDistance;
                        this.routingGrid.layers[neighbor.layer][neighbor.y][neighbor.x].parent = current;
                        
                        queue.push({ ...neighbor, distance: newDistance });
                        queue.sort((a, b) => a.distance - b.distance); // Priority queue
                    }
                }
            }
        }
        
        return []; // No route found
    }

    getNeighbors(point) {
        const neighbors = [];
        const directions = [
            { dx: 0, dy: 1 },   // Up
            { dx: 1, dy: 0 },   // Right  
            { dx: 0, dy: -1 },  // Down
            { dx: -1, dy: 0 }   // Left
        ];
        
        // Same layer neighbors
        for (const dir of directions) {
            const newX = point.x + dir.dx;
            const newY = point.y + dir.dy;
            
            if (newX >= 0 && newX < this.gridWidth && newY >= 0 && newY < this.gridHeight) {
                neighbors.push({ x: newX, y: newY, layer: point.layer });
            }
        }
        
        // Via to other layers
        for (let layer = 0; layer < 4; layer++) {
            if (layer !== point.layer) {
                neighbors.push({ x: point.x, y: point.y, layer: layer });
            }
        }
        
        return neighbors;
    }

    isValidMove(from, to, netName) {
        // Check bounds
        if (to.x < 0 || to.x >= this.gridWidth || to.y < 0 || to.y >= this.gridHeight) {
            return false;
        }
        
        // Check obstacles
        if (this.routingGrid.obstacles[to.y][to.x].occupied) {
            return false;
        }
        
        // Check if already occupied by different net
        const cell = this.routingGrid.layers[to.layer][to.y][to.x];
        if (cell.occupied && cell.netId !== netName) {
            return false;
        }
        
        return true;
    }

    getMoveCost(from, to) {
        // Same layer move
        if (from.layer === to.layer) {
            return 1;
        }
        
        // Via cost (expensive to discourage unnecessary layer changes)
        return 10;
    }

    backtrackPath(start, end) {
        const path = [];
        let current = { x: end.x, y: end.y, layer: end.layer - 1 };
        
        while (current) {
            path.unshift({
                x: current.x * this.gridSize,
                y: current.y * this.gridSize,
                layer: current.layer + 1
            });
            
            current = this.routingGrid.layers[current.layer][current.y][current.x].parent;
        }
        
        return path;
    }

    markRouteAsOccupied(route, netName) {
        for (const point of route) {
            const gridX = Math.round(point.x / this.gridSize);
            const gridY = Math.round(point.y / this.gridSize);
            const layer = point.layer - 1;
            
            if (gridX >= 0 && gridX < this.gridWidth && gridY >= 0 && gridY < this.gridHeight) {
                this.routingGrid.layers[layer][gridY][gridX].occupied = true;
                this.routingGrid.layers[layer][gridY][gridX].netId = netName;
            }
        }
    }

    autoRouteAll() {
        console.log('[ROUTER] Starting auto-routing...');
        
        // Clear existing routes
        this.traces = [];
        this.vias = [];
        
        // Add component obstacles
        const components = this.renderer.exportComponents();
        this.addObstacles(components);
        
        // Generate netlist
        const netlist = this.generateNetlist();
        
        let successfulRoutes = 0;
        let totalNets = netlist.length;
        
        // Route each net
        for (const net of netlist) {
            const routes = this.routeNet(net);
            
            if (routes.length > 0) {
                successfulRoutes++;
                
                // Convert routes to traces
                for (const route of routes) {
                    this.traces.push({
                        netName: net.name,
                        path: route,
                        width: this.rules.defaultTraceWidth,
                        layer: route[0].layer
                    });
                }
            }
        }
        
        console.log(`[ROUTER] Auto-routing complete: ${successfulRoutes}/${totalNets} nets routed`);
        
        // Render traces
        this.renderTraces();
        
        return {
            success: successfulRoutes,
            total: totalNets,
            percentage: (successfulRoutes / totalNets * 100).toFixed(1)
        };
    }

    renderTraces() {
        // Clear existing traces
        const existingTraces = document.querySelectorAll('.pcb-trace');
        existingTraces.forEach(trace => trace.remove());
        
        const layerColors = {
            1: '#ff0000', // Top layer - Red
            2: '#00ff00', // Inner 1 - Green  
            3: '#0000ff', // Inner 2 - Blue
            4: '#ffff00'  // Bottom - Yellow
        };
        
        for (const trace of this.traces) {
            const pathData = this.generateSVGPath(trace.path);
            const layerGroup = document.getElementById(`layer-${trace.layer}`);
            
            if (layerGroup && pathData) {
                const pathElement = document.createElementNS('http://www.w3.org/2000/svg', 'path');
                pathElement.setAttribute('d', pathData);
                pathElement.setAttribute('stroke', layerColors[trace.layer]);
                pathElement.setAttribute('stroke-width', trace.width);
                pathElement.setAttribute('fill', 'none');
                pathElement.setAttribute('stroke-linecap', 'round');
                pathElement.setAttribute('stroke-linejoin', 'round');
                pathElement.classList.add('pcb-trace');
                pathElement.setAttribute('data-net', trace.netName);
                
                layerGroup.appendChild(pathElement);
            }
        }
        
        console.log(`[ROUTER] Rendered ${this.traces.length} traces`);
    }

    generateSVGPath(route) {
        if (route.length < 2) return '';
        
        let pathData = `M ${route[0].x} ${route[0].y}`;
        
        for (let i = 1; i < route.length; i++) {
            const point = route[i];
            const prevPoint = route[i - 1];
            
            // Add via if layer changes
            if (point.layer !== prevPoint.layer) {
                this.addVia(prevPoint.x, prevPoint.y, prevPoint.layer, point.layer);
            }
            
            pathData += ` L ${point.x} ${point.y}`;
        }
        
        return pathData;
    }

    addVia(x, y, fromLayer, toLayer) {
        this.vias.push({
            x: x,
            y: y,
            fromLayer: fromLayer,
            toLayer: toLayer,
            size: this.rules.minViaSize
        });
        
        // Render via
        const viaGroup = document.getElementById('layer-1'); // Vias visible on all layers
        if (viaGroup) {
            const viaElement = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            viaElement.setAttribute('cx', x);
            viaElement.setAttribute('cy', y);
            viaElement.setAttribute('r', this.rules.minViaSize / 2);
            viaElement.setAttribute('fill', '#666');
            viaElement.setAttribute('stroke', '#333');
            viaElement.setAttribute('stroke-width', '0.05');
            viaElement.classList.add('pcb-via');
            
            viaGroup.appendChild(viaElement);
        }
    }

    exportRoutes() {
        return {
            traces: this.traces,
            vias: this.vias,
            rules: this.rules,
            stats: {
                totalTraces: this.traces.length,
                totalVias: this.vias.length,
                gridSize: this.gridSize
            }
        };
    }
}

window.PCBRouter = PCBRouter;