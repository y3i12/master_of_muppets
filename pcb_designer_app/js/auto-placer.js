/**
 * Auto Placer - Intelligent component placement algorithm
 * Based on Master of Muppets optimization rules
 */

class AutoPlacer {
    constructor(renderer, footprintLibrary) {
        this.renderer = renderer;
        this.footprintLibrary = footprintLibrary;
        this.boardWidth = 100;
        this.boardHeight = 160;
        this.placementRules = this.initializePlacementRules();
    }

    initializePlacementRules() {
        return {
            // Zone definitions (mm from left edge)
            zones: {
                power: { x: 0, width: 20, y: 0, height: 160 },
                digital: { x: 20, width: 30, y: 0, height: 160 },
                analog: { x: 50, width: 30, y: 0, height: 160 },
                connectors: { x: 80, width: 20, y: 0, height: 160 }
            },

            // Critical constraints (from placement_optimization.json)
            constraints: {
                decoupling_distance: 3.0,  // mm from IC
                i2c_max_distance: 50.0,    // mm for I2C components
                jack_spacing: 19.05,       // mm standard Eurorack
                edge_clearance: 2.0,       // mm from board edge
                thermal_isolation: 5.0     // mm for hot components
            },

            // Component priorities (higher = place first)
            priorities: {
                microcontrollers: 10,
                ics: 9,
                power: 8,
                connectors: 7,
                passives: 3
            }
        };
    }

    autoPlace(components = null) {
        console.log('[AUTO-PLACE] Starting intelligent placement...');
        
        // Use Master of Muppets components if none provided
        if (!components) {
            components = this.footprintLibrary.getMasterOfMuppetsComponents();
        }

        // Clear existing components
        this.renderer.clearAll();

        // Convert to placement list with priorities
        const placementList = this.preparePlacementList(components);
        
        // Sort by priority (highest first)
        placementList.sort((a, b) => b.priority - a.priority);

        // Place components in priority order
        const placedComponents = [];
        
        for (const item of placementList) {
            const position = this.findOptimalPosition(item, placedComponents);
            
            if (position) {
                this.renderer.addComponent(
                    item.reference,
                    item.footprintId,
                    position.x,
                    position.y,
                    0, // rotation
                    position.layer || 1
                );
                
                placedComponents.push({
                    ...item,
                    x: position.x,
                    y: position.y,
                    placed: true
                });
                
                console.log(`[PLACED] ${item.reference} at (${position.x.toFixed(1)}, ${position.y.toFixed(1)})`);
            } else {
                console.warn(`[WARNING] Could not place ${item.reference}`);
            }
        }

        // Add decoupling capacitors near ICs
        this.addDecouplingCapacitors(placedComponents);

        console.log(`[AUTO-PLACE] Completed: ${placedComponents.length} components placed`);
        return placedComponents;
    }

    preparePlacementList(components) {
        const placementList = [];
        
        Object.entries(components).forEach(([ref, compData]) => {
            const footprint = this.footprintLibrary.getFootprint(compData.footprint);
            if (footprint) {
                placementList.push({
                    reference: ref,
                    footprintId: compData.footprint,
                    footprint: footprint,
                    priority: footprint.placement.priority,
                    zone: footprint.placement.zone,
                    preferredPosition: compData.position,
                    isEdgeComponent: footprint.placement.edge || false,
                    isThermal: footprint.placement.thermal || false
                });
            }
        });
        
        return placementList;
    }

    findOptimalPosition(item, placedComponents) {
        const { footprint, zone, isEdgeComponent, preferredPosition } = item;
        
        // Get zone boundaries
        const targetZone = this.getTargetZone(zone, isEdgeComponent);
        
        // Try preferred position first (if in valid zone)
        if (preferredPosition && this.isPositionValid(preferredPosition, footprint, targetZone, placedComponents)) {
            return preferredPosition;
        }

        // For edge components (like jacks), place along edge
        if (isEdgeComponent) {
            return this.findEdgePosition(item, placedComponents);
        }

        // For high-priority components, use zone center
        if (item.priority >= 8) {
            return this.findZoneCenterPosition(item, targetZone, placedComponents);
        }

        // For other components, find best available space
        return this.findAvailablePosition(item, targetZone, placedComponents);
    }

    getTargetZone(zoneName, isEdgeComponent) {
        if (isEdgeComponent) {
            return this.placementRules.zones.connectors;
        }
        
        return this.placementRules.zones[zoneName] || this.placementRules.zones.digital;
    }

    findEdgePosition(item, placedComponents) {
        const { footprint } = item;
        const zone = this.placementRules.zones.connectors;
        const spacing = this.placementRules.constraints.jack_spacing;
        
        // Place jacks vertically along right edge
        const baseX = zone.x + zone.width - footprint.width / 2 - this.placementRules.constraints.edge_clearance;
        
        // Find available Y position
        for (let i = 0; i < 16; i++) { // Max 16 jacks
            const y = 10 + i * (spacing * 0.8); // Slightly tighter than standard
            
            if (y + footprint.height / 2 > this.boardHeight - this.placementRules.constraints.edge_clearance) {
                break;
            }
            
            const position = { x: baseX, y: y };
            
            if (this.isPositionValid(position, footprint, zone, placedComponents)) {
                return position;
            }
        }
        
        return null;
    }

    findZoneCenterPosition(item, zone, placedComponents) {
        const { footprint } = item;
        
        // Start from zone center
        const centerX = zone.x + zone.width / 2;
        const centerY = zone.y + zone.height / 2;
        
        // Try center first
        let position = { x: centerX, y: centerY };
        if (this.isPositionValid(position, footprint, zone, placedComponents)) {
            return position;
        }
        
        // Spiral outward from center
        const stepSize = 5; // mm
        for (let radius = stepSize; radius < Math.min(zone.width, zone.height) / 2; radius += stepSize) {
            const candidates = [
                { x: centerX - radius, y: centerY },
                { x: centerX + radius, y: centerY },
                { x: centerX, y: centerY - radius },
                { x: centerX, y: centerY + radius }
            ];
            
            for (const candidate of candidates) {
                if (this.isPositionValid(candidate, footprint, zone, placedComponents)) {
                    return candidate;
                }
            }
        }
        
        return null;
    }

    findAvailablePosition(item, zone, placedComponents) {
        const { footprint } = item;
        const stepSize = 2.54; // Grid step
        
        // Scan zone from top-left
        for (let y = zone.y + footprint.height / 2; y < zone.y + zone.height - footprint.height / 2; y += stepSize) {
            for (let x = zone.x + footprint.width / 2; x < zone.x + zone.width - footprint.width / 2; x += stepSize) {
                const position = { x, y };
                
                if (this.isPositionValid(position, footprint, zone, placedComponents)) {
                    return position;
                }
            }
        }
        
        return null;
    }

    isPositionValid(position, footprint, zone, placedComponents) {
        const { x, y } = position;
        
        // Check zone boundaries
        if (x - footprint.width / 2 < zone.x || x + footprint.width / 2 > zone.x + zone.width) {
            return false;
        }
        if (y - footprint.height / 2 < zone.y || y + footprint.height / 2 > zone.y + zone.height) {
            return false;
        }
        
        // Check board boundaries
        if (x - footprint.width / 2 < 0 || x + footprint.width / 2 > this.boardWidth) {
            return false;
        }
        if (y - footprint.height / 2 < 0 || y + footprint.height / 2 > this.boardHeight) {
            return false;
        }
        
        // Check clearance from other components
        for (const placed of placedComponents) {
            if (this.componentsOverlap(position, footprint, placed)) {
                return false;
            }
        }
        
        return true;
    }

    componentsOverlap(pos1, footprint1, placed) {
        const clearance = 1.0; // mm minimum clearance
        
        const dx = Math.abs(pos1.x - placed.x);
        const dy = Math.abs(pos1.y - placed.y);
        
        const minDx = (footprint1.width + placed.footprint.width) / 2 + clearance;
        const minDy = (footprint1.height + placed.footprint.height) / 2 + clearance;
        
        return dx < minDx && dy < minDy;
    }

    addDecouplingCapacitors(placedComponents) {
        const ics = placedComponents.filter(comp => 
            comp.footprint.category === 'ics' || comp.footprint.category === 'microcontrollers'
        );
        
        let capCount = 1;
        
        ics.forEach(ic => {
            // Find position near IC for decoupling cap
            const capPosition = this.findDecouplingPosition(ic, placedComponents);
            
            if (capPosition) {
                const capRef = `C${capCount}`;
                this.renderer.addComponent(
                    capRef,
                    'C_0603',
                    capPosition.x,
                    capPosition.y,
                    0,
                    1
                );
                
                placedComponents.push({
                    reference: capRef,
                    footprintId: 'C_0603',
                    footprint: this.footprintLibrary.getFootprint('C_0603'),
                    x: capPosition.x,
                    y: capPosition.y,
                    placed: true,
                    isDecoupling: true
                });
                
                capCount++;
                console.log(`[DECOUPLING] Added ${capRef} near ${ic.reference}`);
            }
        });
    }

    findDecouplingPosition(ic, placedComponents) {
        const maxDistance = this.placementRules.constraints.decoupling_distance;
        const capFootprint = this.footprintLibrary.getFootprint('C_0603');
        
        // Try positions around the IC
        const candidates = [
            { x: ic.x - maxDistance, y: ic.y },
            { x: ic.x + maxDistance, y: ic.y },
            { x: ic.x, y: ic.y - maxDistance },
            { x: ic.x, y: ic.y + maxDistance }
        ];
        
        for (const candidate of candidates) {
            // Use a flexible zone for decoupling caps
            const flexZone = {
                x: 0, y: 0,
                width: this.boardWidth,
                height: this.boardHeight
            };
            
            if (this.isPositionValid(candidate, capFootprint, flexZone, placedComponents)) {
                return candidate;
            }
        }
        
        return null;
    }

    // Optimization functions
    optimizePlacement(placedComponents) {
        // Future: Implement placement optimization
        // - Minimize wire length
        // - Improve thermal distribution
        // - Reduce EMI
        console.log('[OPTIMIZE] Placement optimization not yet implemented');
    }
}

// Export for use in other modules
window.AutoPlacer = AutoPlacer;