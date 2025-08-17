/**
 * Design Rule Checker (DRC) v1.0 - PCB design validation
 * Validates spacing, trace width, via size, and other design constraints
 */

class DesignRuleChecker {
    constructor(renderer, router) {
        this.renderer = renderer;
        this.router = router;
        this.violations = [];
        this.enabled = true;
        
        // Design rules (in mm)
        this.rules = {
            minTraceWidth: 0.1,
            maxTraceWidth: 10.0,
            minViaSize: 0.2,
            maxViaSize: 3.0,
            minSpacing: 0.15,
            minViaDrillSize: 0.1,
            minAnnularRing: 0.05,
            minCopperToEdge: 0.2,
            minHoleToHole: 0.15,
            minSilkToCopper: 0.1,
            maxAspectRatio: 8.0,
            minSolderMaskDam: 0.1
        };
        
        // Violation types
        this.violationTypes = {
            TRACE_WIDTH: 'Trace width violation',
            SPACING: 'Minimum spacing violation', 
            VIA_SIZE: 'Via size violation',
            ANNULAR_RING: 'Annular ring violation',
            EDGE_CLEARANCE: 'Edge clearance violation',
            DRILL_SIZE: 'Drill size violation',
            ASPECT_RATIO: 'Aspect ratio violation',
            COPPER_POUR: 'Copper pour violation'
        };
    }

    runFullDRC() {
        console.log('[DRC] Starting design rule check...');
        
        this.violations = [];
        const components = this.renderer.exportComponents();
        const routingData = this.router.exportRoutes();
        
        // Check all rules
        this.checkTraceWidths(routingData.traces);
        this.checkSpacing(components, routingData);
        this.checkViaSizes(routingData.vias);
        this.checkEdgeClearances(components);
        this.checkAnnularRings(routingData.vias);
        this.checkAspectRatios(routingData.vias);
        
        // Generate report
        const report = this.generateDRCReport();
        this.highlightViolations();
        
        console.log(`[DRC] Design rule check complete: ${this.violations.length} violations found`);
        return report;
    }

    checkTraceWidths(traces) {
        traces.forEach((trace, index) => {
            if (trace.width < this.rules.minTraceWidth) {
                this.addViolation({
                    type: this.violationTypes.TRACE_WIDTH,
                    severity: 'error',
                    description: `Trace width ${trace.width}mm below minimum ${this.rules.minTraceWidth}mm`,
                    location: trace.path[0],
                    layer: trace.layer,
                    netName: trace.netName,
                    object: `trace_${index}`,
                    suggested: `Increase trace width to ${this.rules.minTraceWidth}mm`
                });
            }
            
            if (trace.width > this.rules.maxTraceWidth) {
                this.addViolation({
                    type: this.violationTypes.TRACE_WIDTH,
                    severity: 'warning',
                    description: `Trace width ${trace.width}mm exceeds maximum ${this.rules.maxTraceWidth}mm`,
                    location: trace.path[0],
                    layer: trace.layer,
                    netName: trace.netName,
                    object: `trace_${index}`,
                    suggested: `Reduce trace width to below ${this.rules.maxTraceWidth}mm`
                });
            }
        });
    }

    checkSpacing(components, routingData) {
        // Check component to component spacing
        for (let i = 0; i < components.length; i++) {
            for (let j = i + 1; j < components.length; j++) {
                const comp1 = components[i];
                const comp2 = components[j];
                
                const distance = this.calculateDistance(comp1, comp2);
                const requiredClearance = this.getRequiredClearance(comp1, comp2);
                
                if (distance < requiredClearance) {
                    this.addViolation({
                        type: this.violationTypes.SPACING,
                        severity: 'error',
                        description: `Components ${comp1.reference} and ${comp2.reference} too close: ${distance.toFixed(2)}mm (min: ${requiredClearance}mm)`,
                        location: { x: (comp1.x + comp2.x) / 2, y: (comp1.y + comp2.y) / 2 },
                        layer: 1,
                        object: `${comp1.reference}_${comp2.reference}`,
                        suggested: `Increase spacing to ${requiredClearance}mm minimum`
                    });
                }
            }
        }
        
        // Check trace to trace spacing
        this.checkTraceSpacing(routingData.traces);
    }

    checkTraceSpacing(traces) {
        for (let i = 0; i < traces.length; i++) {
            for (let j = i + 1; j < traces.length; j++) {
                const trace1 = traces[i];
                const trace2 = traces[j];
                
                // Skip traces on different nets (they need spacing)
                if (trace1.netName === trace2.netName) continue;
                
                // Check if traces are on same layer
                if (trace1.layer === trace2.layer) {
                    const minDistance = this.getMinimumTraceDistance(trace1, trace2);
                    
                    if (minDistance < this.rules.minSpacing) {
                        this.addViolation({
                            type: this.violationTypes.SPACING,
                            severity: 'error',
                            description: `Traces too close: ${minDistance.toFixed(2)}mm (min: ${this.rules.minSpacing}mm)`,
                            location: this.getClosestPoint(trace1, trace2),
                            layer: trace1.layer,
                            netName: `${trace1.netName} / ${trace2.netName}`,
                            object: `trace_spacing_${i}_${j}`,
                            suggested: `Increase spacing to ${this.rules.minSpacing}mm minimum`
                        });
                    }
                }
            }
        }
    }

    checkViaSizes(vias) {
        vias.forEach((via, index) => {
            if (via.size < this.rules.minViaSize) {
                this.addViolation({
                    type: this.violationTypes.VIA_SIZE,
                    severity: 'error',
                    description: `Via size ${via.size}mm below minimum ${this.rules.minViaSize}mm`,
                    location: { x: via.x, y: via.y },
                    layer: 'all',
                    object: `via_${index}`,
                    suggested: `Increase via size to ${this.rules.minViaSize}mm`
                });
            }
            
            if (via.size > this.rules.maxViaSize) {
                this.addViolation({
                    type: this.violationTypes.VIA_SIZE,
                    severity: 'warning',
                    description: `Via size ${via.size}mm exceeds recommended maximum ${this.rules.maxViaSize}mm`,
                    location: { x: via.x, y: via.y },
                    layer: 'all',
                    object: `via_${index}`,
                    suggested: `Consider reducing via size`
                });
            }
        });
    }

    checkEdgeClearances(components) {
        const boardWidth = this.renderer.boardWidth || 100;
        const boardHeight = this.renderer.boardHeight || 160;
        
        components.forEach(component => {
            const footprint = this.renderer.footprintLibrary.getFootprint(component.footprint);
            if (!footprint) return;
            
            // Check distance to board edges
            const leftEdge = component.x - footprint.width / 2;
            const rightEdge = component.x + footprint.width / 2;
            const topEdge = component.y - footprint.height / 2;
            const bottomEdge = component.y + footprint.height / 2;
            
            if (leftEdge < this.rules.minCopperToEdge) {
                this.addViolation({
                    type: this.violationTypes.EDGE_CLEARANCE,
                    severity: 'error',
                    description: `Component ${component.reference} too close to left edge: ${leftEdge.toFixed(2)}mm`,
                    location: { x: component.x, y: component.y },
                    layer: component.layer,
                    object: component.reference,
                    suggested: `Move component ${this.rules.minCopperToEdge}mm from edge`
                });
            }
            
            if (rightEdge > boardWidth - this.rules.minCopperToEdge) {
                this.addViolation({
                    type: this.violationTypes.EDGE_CLEARANCE,
                    severity: 'error',
                    description: `Component ${component.reference} too close to right edge`,
                    location: { x: component.x, y: component.y },
                    layer: component.layer,
                    object: component.reference,
                    suggested: `Move component ${this.rules.minCopperToEdge}mm from edge`
                });
            }
            
            if (topEdge < this.rules.minCopperToEdge) {
                this.addViolation({
                    type: this.violationTypes.EDGE_CLEARANCE,
                    severity: 'error',
                    description: `Component ${component.reference} too close to top edge`,
                    location: { x: component.x, y: component.y },
                    layer: component.layer,
                    object: component.reference,
                    suggested: `Move component ${this.rules.minCopperToEdge}mm from edge`
                });
            }
            
            if (bottomEdge > boardHeight - this.rules.minCopperToEdge) {
                this.addViolation({
                    type: this.violationTypes.EDGE_CLEARANCE,
                    severity: 'error',
                    description: `Component ${component.reference} too close to bottom edge`,
                    location: { x: component.x, y: component.y },
                    layer: component.layer,
                    object: component.reference,
                    suggested: `Move component ${this.rules.minCopperToEdge}mm from edge`
                });
            }
        });
    }

    checkAnnularRings(vias) {
        vias.forEach((via, index) => {
            const drillSize = via.size * 0.6; // Assume 60% drill to via ratio
            const annularRing = (via.size - drillSize) / 2;
            
            if (annularRing < this.rules.minAnnularRing) {
                this.addViolation({
                    type: this.violationTypes.ANNULAR_RING,
                    severity: 'error',
                    description: `Via annular ring ${annularRing.toFixed(2)}mm below minimum ${this.rules.minAnnularRing}mm`,
                    location: { x: via.x, y: via.y },
                    layer: 'all',
                    object: `via_${index}`,
                    suggested: `Increase via size or reduce drill size`
                });
            }
        });
    }

    checkAspectRatios(vias) {
        const boardThickness = 1.6; // Standard PCB thickness
        
        vias.forEach((via, index) => {
            const drillSize = via.size * 0.6;
            const aspectRatio = boardThickness / drillSize;
            
            if (aspectRatio > this.rules.maxAspectRatio) {
                this.addViolation({
                    type: this.violationTypes.ASPECT_RATIO,
                    severity: 'warning',
                    description: `Via aspect ratio ${aspectRatio.toFixed(1)}:1 exceeds recommended ${this.rules.maxAspectRatio}:1`,
                    location: { x: via.x, y: via.y },
                    layer: 'all',
                    object: `via_${index}`,
                    suggested: `Increase drill size or use buried vias`
                });
            }
        });
    }

    addViolation(violation) {
        violation.id = `drc_${this.violations.length}`;
        violation.timestamp = new Date().toISOString();
        this.violations.push(violation);
    }

    calculateDistance(comp1, comp2) {
        const footprint1 = this.renderer.footprintLibrary.getFootprint(comp1.footprint);
        const footprint2 = this.renderer.footprintLibrary.getFootprint(comp2.footprint);
        
        if (!footprint1 || !footprint2) return Infinity;
        
        // Calculate edge-to-edge distance
        const dx = Math.max(0, Math.abs(comp1.x - comp2.x) - (footprint1.width + footprint2.width) / 2);
        const dy = Math.max(0, Math.abs(comp1.y - comp2.y) - (footprint1.height + footprint2.height) / 2);
        
        return Math.sqrt(dx * dx + dy * dy);
    }

    getRequiredClearance(comp1, comp2) {
        // Base clearance
        let clearance = this.rules.minSpacing;
        
        // Increase clearance for power components
        const powerComponents = ['PSU', 'REG', 'VREG'];
        if (powerComponents.some(type => comp1.reference.includes(type) || comp2.reference.includes(type))) {
            clearance *= 2;
        }
        
        return clearance;
    }

    getMinimumTraceDistance(trace1, trace2) {
        let minDistance = Infinity;
        
        // Simplified: check distance between first points of each trace
        // Real implementation would check all segment combinations
        for (const point1 of trace1.path) {
            for (const point2 of trace2.path) {
                const distance = Math.sqrt(
                    Math.pow(point1.x - point2.x, 2) + 
                    Math.pow(point1.y - point2.y, 2)
                );
                minDistance = Math.min(minDistance, distance);
            }
        }
        
        return minDistance;
    }

    getClosestPoint(trace1, trace2) {
        // Return midpoint between closest trace points
        let minDistance = Infinity;
        let closestPoints = { p1: null, p2: null };
        
        for (const point1 of trace1.path) {
            for (const point2 of trace2.path) {
                const distance = Math.sqrt(
                    Math.pow(point1.x - point2.x, 2) + 
                    Math.pow(point1.y - point2.y, 2)
                );
                if (distance < minDistance) {
                    minDistance = distance;
                    closestPoints = { p1: point1, p2: point2 };
                }
            }
        }
        
        return {
            x: (closestPoints.p1.x + closestPoints.p2.x) / 2,
            y: (closestPoints.p1.y + closestPoints.p2.y) / 2
        };
    }

    highlightViolations() {
        // Clear existing violation markers
        this.clearViolationMarkers();
        
        // Create violation layer
        let violationLayer = document.getElementById('violation-layer');
        if (!violationLayer) {
            violationLayer = document.createElementNS('http://www.w3.org/2000/svg', 'g');
            violationLayer.setAttribute('id', 'violation-layer');
            violationLayer.classList.add('violation-layer');
            this.renderer.svg.appendChild(violationLayer);
        }
        
        // Add markers for each violation
        this.violations.forEach(violation => {
            const marker = this.createViolationMarker(violation);
            violationLayer.appendChild(marker);
        });
    }

    createViolationMarker(violation) {
        const group = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        group.classList.add('violation-marker');
        group.setAttribute('data-violation-id', violation.id);
        group.setAttribute('data-severity', violation.severity);
        
        // Create error icon (circle with X)
        const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        circle.setAttribute('cx', violation.location.x);
        circle.setAttribute('cy', violation.location.y);
        circle.setAttribute('r', '1');
        circle.setAttribute('fill', violation.severity === 'error' ? '#ff4444' : '#ffaa00');
        circle.setAttribute('stroke', '#ffffff');
        circle.setAttribute('stroke-width', '0.2');
        circle.classList.add('violation-circle');
        
        // Create X mark
        const x1 = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        x1.setAttribute('x1', violation.location.x - 0.5);
        x1.setAttribute('y1', violation.location.y - 0.5);
        x1.setAttribute('x2', violation.location.x + 0.5);
        x1.setAttribute('y2', violation.location.y + 0.5);
        x1.setAttribute('stroke', '#ffffff');
        x1.setAttribute('stroke-width', '0.2');
        
        const x2 = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        x2.setAttribute('x1', violation.location.x - 0.5);
        x2.setAttribute('y1', violation.location.y + 0.5);
        x2.setAttribute('x2', violation.location.x + 0.5);
        x2.setAttribute('y2', violation.location.y - 0.5);
        x2.setAttribute('stroke', '#ffffff');
        x2.setAttribute('stroke-width', '0.2');
        
        // Add hover tooltip
        group.addEventListener('mouseenter', () => {
            this.showViolationTooltip(violation, group);
        });
        
        group.addEventListener('mouseleave', () => {
            this.hideViolationTooltip();
        });
        
        group.appendChild(circle);
        group.appendChild(x1);
        group.appendChild(x2);
        
        return group;
    }

    showViolationTooltip(violation, element) {
        // Simple tooltip implementation
        console.log(`[DRC] ${violation.type}: ${violation.description}`);
        // Future: Create proper tooltip UI
    }

    hideViolationTooltip() {
        // Future: Hide tooltip UI
    }

    clearViolationMarkers() {
        const violationLayer = document.getElementById('violation-layer');
        if (violationLayer) {
            violationLayer.innerHTML = '';
        }
    }

    generateDRCReport() {
        const errorCount = this.violations.filter(v => v.severity === 'error').length;
        const warningCount = this.violations.filter(v => v.severity === 'warning').length;
        
        const report = {
            summary: {
                total: this.violations.length,
                errors: errorCount,
                warnings: warningCount,
                passed: this.violations.length === 0
            },
            violations: this.violations,
            rules: this.rules,
            timestamp: new Date().toISOString()
        };
        
        return report;
    }

    getViolationsByType() {
        const byType = {};
        
        this.violations.forEach(violation => {
            if (!byType[violation.type]) {
                byType[violation.type] = [];
            }
            byType[violation.type].push(violation);
        });
        
        return byType;
    }

    exportDRCReport(format = 'json') {
        const report = this.generateDRCReport();
        
        if (format === 'json') {
            return JSON.stringify(report, null, 2);
        } else if (format === 'csv') {
            return this.generateCSVReport(report);
        }
        
        return report;
    }

    generateCSVReport(report) {
        const headers = ['Type', 'Severity', 'Description', 'Location', 'Layer', 'Suggestion'];
        const rows = [headers.join(',')];
        
        report.violations.forEach(violation => {
            const row = [
                violation.type,
                violation.severity,
                `"${violation.description}"`,
                `"(${violation.location.x.toFixed(2)}, ${violation.location.y.toFixed(2)})"`,
                violation.layer,
                `"${violation.suggested}"`
            ];
            rows.push(row.join(','));
        });
        
        return rows.join('\n');
    }

    toggleDRC() {
        this.enabled = !this.enabled;
        
        if (!this.enabled) {
            this.clearViolationMarkers();
        }
        
        return this.enabled;
    }
}

window.DesignRuleChecker = DesignRuleChecker;