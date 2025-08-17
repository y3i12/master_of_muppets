/**
 * Raster Net Visualizer v1.0 - Visual net connectivity display
 * Shows unrouted connections (ratsnest) and net relationships
 */

class RasterNetVisualizer {
    constructor(renderer, router) {
        this.renderer = renderer;
        this.router = router;
        this.rasterLines = [];
        this.showRatsnest = true;
        this.showNetLabels = true;
        this.netColors = new Map();
        
        this.initializeNetColors();
    }

    initializeNetColors() {
        // Predefined colors for different net types
        this.netColorPalette = [
            '#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', 
            '#feca57', '#ff9ff3', '#54a0ff', '#5f27cd',
            '#00d2d3', '#ff9f43', '#10ac84', '#ee5a24',
            '#0abde3', '#3742fa', '#2f3542', '#40407a'
        ];
        
        // Special colors for power/ground
        this.specialNetColors = {
            'VCC': '#ff0000',
            'GND': '#000000',
            'I2C_SDA': '#00ff00',
            'I2C_SCL': '#0000ff'
        };
    }

    getNetColor(netName) {
        if (this.specialNetColors[netName]) {
            return this.specialNetColors[netName];
        }
        
        if (!this.netColors.has(netName)) {
            const colorIndex = this.netColors.size % this.netColorPalette.length;
            this.netColors.set(netName, this.netColorPalette[colorIndex]);
        }
        
        return this.netColors.get(netName);
    }

    generateRatsnest() {
        console.log('[RASTER] Generating ratsnest visualization...');
        
        // Clear existing ratsnest
        this.clearRatsnest();
        
        // Get netlist from router
        const netlist = this.router.generateNetlist();
        const components = this.renderer.exportComponents();
        
        // Create component position lookup
        const componentPositions = new Map();
        components.forEach(comp => {
            componentPositions.set(comp.reference, { x: comp.x, y: comp.y });
        });
        
        // Generate unrouted connections
        netlist.forEach(net => {
            const netColor = this.getNetColor(net.name);
            const connections = this.calculateNetConnections(net, componentPositions);
            
            connections.forEach(connection => {
                this.addRasterLine(connection, netColor, net.name);
            });
        });
        
        this.renderRatsnest();
        console.log(`[RASTER] Generated ${this.rasterLines.length} ratsnest connections`);
    }

    calculateNetConnections(net, componentPositions) {
        const connections = [];
        
        if (net.pins.length < 2) return connections;
        
        // For star topology, connect all pins to first pin
        const centerPin = net.pins[0];
        const centerPos = componentPositions.get(centerPin.component);
        
        if (!centerPos) return connections;
        
        for (let i = 1; i < net.pins.length; i++) {
            const pin = net.pins[i];
            const pinPos = componentPositions.get(pin.component);
            
            if (pinPos) {
                connections.push({
                    start: { x: centerPos.x, y: centerPos.y, component: centerPin.component, pin: centerPin.pin },
                    end: { x: pinPos.x, y: pinPos.y, component: pin.component, pin: pin.pin },
                    netName: net.name
                });
            }
        }
        
        return connections;
    }

    addRasterLine(connection, color, netName) {
        this.rasterLines.push({
            start: connection.start,
            end: connection.end,
            color: color,
            netName: netName,
            routed: false // Will be updated when traces are routed
        });
    }

    renderRatsnest() {
        // Get or create ratsnest layer
        let ratsnestLayer = document.getElementById('ratsnest-layer');
        if (!ratsnestLayer) {
            ratsnestLayer = document.createElementNS('http://www.w3.org/2000/svg', 'g');
            ratsnestLayer.setAttribute('id', 'ratsnest-layer');
            ratsnestLayer.classList.add('ratsnest-layer');
            
            // Insert before interaction layer
            const interactionLayer = document.getElementById('interaction-layer');
            if (interactionLayer) {
                interactionLayer.parentNode.insertBefore(ratsnestLayer, interactionLayer);
            } else {
                this.renderer.svg.appendChild(ratsnestLayer);
            }
        }
        
        // Clear existing lines
        ratsnestLayer.innerHTML = '';
        
        // Render each ratsnest line
        this.rasterLines.forEach((line, index) => {
            if (!line.routed && this.showRatsnest) {
                const lineElement = this.createRatsnestLine(line, index);
                ratsnestLayer.appendChild(lineElement);
            }
        });
        
        // Add net labels if enabled
        if (this.showNetLabels) {
            this.addNetLabels(ratsnestLayer);
        }
    }

    createRatsnestLine(line, index) {
        const group = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        group.classList.add('ratsnest-connection');
        group.setAttribute('data-net', line.netName);
        group.setAttribute('data-index', index);
        
        // Create dashed line
        const pathElement = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        pathElement.setAttribute('x1', line.start.x);
        pathElement.setAttribute('y1', line.start.y);
        pathElement.setAttribute('x2', line.end.x);
        pathElement.setAttribute('y2', line.end.y);
        pathElement.setAttribute('stroke', line.color);
        pathElement.setAttribute('stroke-width', '0.1');
        pathElement.setAttribute('stroke-dasharray', '0.5,0.3');
        pathElement.setAttribute('opacity', '0.6');
        pathElement.classList.add('ratsnest-line');
        
        // Add connection dots at endpoints
        const startDot = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        startDot.setAttribute('cx', line.start.x);
        startDot.setAttribute('cy', line.start.y);
        startDot.setAttribute('r', '0.2');
        startDot.setAttribute('fill', line.color);
        startDot.classList.add('ratsnest-dot');
        
        const endDot = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        endDot.setAttribute('cx', line.end.x);
        endDot.setAttribute('cy', line.end.y);
        endDot.setAttribute('r', '0.2');
        endDot.setAttribute('fill', line.color);
        endDot.classList.add('ratsnest-dot');
        
        // Add hover effects
        group.addEventListener('mouseenter', () => this.highlightNet(line.netName));
        group.addEventListener('mouseleave', () => this.unhighlightNet(line.netName));
        
        group.appendChild(pathElement);
        group.appendChild(startDot);
        group.appendChild(endDot);
        
        return group;
    }

    addNetLabels(ratsnestLayer) {
        const netMidpoints = new Map();
        
        // Calculate midpoint for each net
        this.rasterLines.forEach(line => {
            if (!line.routed) {
                const midX = (line.start.x + line.end.x) / 2;
                const midY = (line.start.y + line.end.y) / 2;
                
                if (!netMidpoints.has(line.netName)) {
                    netMidpoints.set(line.netName, { x: midX, y: midY, color: line.color });
                }
            }
        });
        
        // Add labels
        netMidpoints.forEach((pos, netName) => {
            const label = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            label.setAttribute('x', pos.x);
            label.setAttribute('y', pos.y);
            label.setAttribute('text-anchor', 'middle');
            label.setAttribute('dominant-baseline', 'central');
            label.setAttribute('font-size', '1.5');
            label.setAttribute('fill', pos.color);
            label.setAttribute('stroke', '#000');
            label.setAttribute('stroke-width', '0.1');
            label.classList.add('net-label');
            label.textContent = netName;
            
            ratsnestLayer.appendChild(label);
        });
    }

    highlightNet(netName) {
        // Highlight all connections for this net
        const connections = document.querySelectorAll(`[data-net="${netName}"]`);
        connections.forEach(conn => {
            conn.style.opacity = '1.0';
            const lines = conn.querySelectorAll('.ratsnest-line');
            lines.forEach(line => {
                line.setAttribute('stroke-width', '0.2');
            });
        });
        
        // Show net info in status
        const netInfo = this.getNetInfo(netName);
        this.updateNetStatus(netInfo);
    }

    unhighlightNet(netName) {
        const connections = document.querySelectorAll(`[data-net="${netName}"]`);
        connections.forEach(conn => {
            conn.style.opacity = '0.6';
            const lines = conn.querySelectorAll('.ratsnest-line');
            lines.forEach(line => {
                line.setAttribute('stroke-width', '0.1');
            });
        });
    }

    getNetInfo(netName) {
        const netConnections = this.rasterLines.filter(line => line.netName === netName);
        const routedCount = netConnections.filter(line => line.routed).length;
        const totalCount = netConnections.length;
        
        return {
            name: netName,
            connections: totalCount,
            routed: routedCount,
            unrouted: totalCount - routedCount,
            completion: totalCount > 0 ? (routedCount / totalCount * 100).toFixed(1) : 0
        };
    }

    updateNetStatus(netInfo) {
        // Future: Update status panel with net information
        console.log(`[NET] ${netInfo.name}: ${netInfo.routed}/${netInfo.connections} routed (${netInfo.completion}%)`);
    }

    clearRatsnest() {
        this.rasterLines = [];
        const ratsnestLayer = document.getElementById('ratsnest-layer');
        if (ratsnestLayer) {
            ratsnestLayer.innerHTML = '';
        }
    }

    updateRoutedConnections(traces) {
        // Mark connections as routed when traces exist
        traces.forEach(trace => {
            this.rasterLines.forEach(line => {
                if (line.netName === trace.netName) {
                    line.routed = true;
                }
            });
        });
        
        this.renderRatsnest();
    }

    toggleRatsnest() {
        this.showRatsnest = !this.showRatsnest;
        this.renderRatsnest();
        
        return this.showRatsnest;
    }

    toggleNetLabels() {
        this.showNetLabels = !this.showNetLabels;
        this.renderRatsnest();
        
        return this.showNetLabels;
    }

    getNetStatistics() {
        const netStats = new Map();
        
        this.rasterLines.forEach(line => {
            if (!netStats.has(line.netName)) {
                netStats.set(line.netName, { total: 0, routed: 0 });
            }
            
            const stats = netStats.get(line.netName);
            stats.total++;
            if (line.routed) stats.routed++;
        });
        
        const results = [];
        netStats.forEach((stats, netName) => {
            results.push({
                name: netName,
                total: stats.total,
                routed: stats.routed,
                completion: stats.total > 0 ? (stats.routed / stats.total * 100).toFixed(1) : 0
            });
        });
        
        return results.sort((a, b) => b.completion - a.completion);
    }

    exportRatsnest() {
        return {
            ratsnestLines: this.rasterLines,
            netColors: Object.fromEntries(this.netColors),
            statistics: this.getNetStatistics(),
            settings: {
                showRatsnest: this.showRatsnest,
                showNetLabels: this.showNetLabels
            }
        };
    }
}

window.RasterNetVisualizer = RasterNetVisualizer;