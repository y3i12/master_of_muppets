/**
 * Rendering Optimizer v1.0 - Performance improvements for PCB canvas
 * Created during autonomous learning cycle
 */

class RenderingOptimizer {
    constructor(renderer) {
        this.renderer = renderer;
        this.renderQueue = [];
        this.isRendering = false;
        this.performanceMetrics = {
            renderCount: 0,
            totalTime: 0,
            averageTime: 0
        };
    }
    
    queueRender(operation, priority = 0) {
        this.renderQueue.push({ operation, priority, timestamp: performance.now() });
        this.renderQueue.sort((a, b) => b.priority - a.priority);
        
        if (!this.isRendering) {
            this.processQueue();
        }
    }
    
    processQueue() {
        this.isRendering = true;
        const startTime = performance.now();
        
        requestAnimationFrame(() => {
            const batchStartTime = performance.now();
            let operationsProcessed = 0;
            
            // Process up to 10 operations per frame to maintain 60fps
            while (this.renderQueue.length > 0 && operationsProcessed < 10) {
                const { operation } = this.renderQueue.shift();
                operation();
                operationsProcessed++;
            }
            
            const batchTime = performance.now() - batchStartTime;
            this.updateMetrics(batchTime);
            
            if (this.renderQueue.length > 0) {
                // More operations pending, continue next frame
                this.processQueue();
            } else {
                this.isRendering = false;
            }
        });
    }
    
    updateMetrics(renderTime) {
        this.performanceMetrics.renderCount++;
        this.performanceMetrics.totalTime += renderTime;
        this.performanceMetrics.averageTime = 
            this.performanceMetrics.totalTime / this.performanceMetrics.renderCount;
    }
    
    getPerformanceReport() {
        return {
            ...this.performanceMetrics,
            efficiency: this.performanceMetrics.averageTime < 16 ? 'Excellent' : 
                       this.performanceMetrics.averageTime < 33 ? 'Good' : 'Needs Improvement'
        };
    }
    
    // Optimized component rendering
    optimizedComponentRender(component) {
        // Use DocumentFragment for batch DOM operations
        const fragment = document.createDocumentFragment();
        
        // Minimize SVG attribute updates
        const group = component.svgElement;
        const transform = `translate(${component.x}, ${component.y}) rotate(${component.rotation})`;
        
        if (group.getAttribute('transform') !== transform) {
            group.setAttribute('transform', transform);
        }
        
        return fragment;
    }
    
    // Viewport culling for better performance
    isComponentVisible(component, viewBox) {
        const margin = 10; // 10mm margin
        return (
            component.x + component.footprint.width/2 >= viewBox.x - margin &&
            component.x - component.footprint.width/2 <= viewBox.x + viewBox.width + margin &&
            component.y + component.footprint.height/2 >= viewBox.y - margin &&
            component.y - component.footprint.height/2 <= viewBox.y + viewBox.height + margin
        );
    }
}

// Integration with existing PCB renderer
if (typeof window !== 'undefined' && window.PCBRenderer) {
    const originalConstructor = window.PCBRenderer;
    
    window.PCBRenderer = function(svgElement, footprintLibrary) {
        const instance = new originalConstructor(svgElement, footprintLibrary);
        instance.optimizer = new RenderingOptimizer(instance);
        
        // Override moveComponent for optimized rendering
        const originalMoveComponent = instance.moveComponent;
        instance.moveComponent = function(reference, newX, newY) {
            this.optimizer.queueRender(() => {
                originalMoveComponent.call(this, reference, newX, newY);
            }, 1); // High priority for user interactions
        };
        
        return instance;
    };
}

window.RenderingOptimizer = RenderingOptimizer;