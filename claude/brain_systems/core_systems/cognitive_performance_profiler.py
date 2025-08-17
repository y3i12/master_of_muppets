#!/usr/bin/env python3
"""
Cognitive Performance Profiler v1.0 - Real-time cognitive efficiency monitoring
Tracks decision-making speed, accuracy, and identifies cognitive bottlenecks
"""

import time
import json
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from collections import defaultdict, deque
from dataclasses import dataclass, asdict
import statistics
import functools

@dataclass
class CognitiveMetric:
    """Single cognitive performance measurement"""
    timestamp: str
    operation: str
    duration_ms: float
    accuracy_score: float  # 0.0 - 1.0
    context_complexity: int  # 1-10
    cognitive_load: float  # 0.0 - 1.0
    outcome: str  # success/error/partial
    memory_usage: int  # bytes
    confidence: float  # 0.0 - 1.0

@dataclass
class CognitiveBottleneck:
    """Identified performance bottleneck"""
    operation: str
    avg_duration: float
    frequency: int
    severity: float  # 0.0 - 1.0
    suggested_optimization: str
    hot_path_candidate: bool

class CognitivePerformanceProfiler:
    """Real-time cognitive performance monitoring and optimization"""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.metrics_file = self.project_root / 'claude' / 'brain_systems' / 'cognitive_metrics.json'
        self.hot_paths_file = self.project_root / 'claude' / 'brain_systems' / 'cognitive_hot_paths.json'
        
        # Performance tracking
        self.metrics: deque[CognitiveMetric] = deque(maxlen=10000)
        self.operation_stats = defaultdict(list)
        self.hot_paths = {}
        self.bottlenecks = []
        
        # Real-time monitoring
        self.monitoring_active = False
        self.monitor_thread = None
        self.real_time_stats = defaultdict(lambda: {'count': 0, 'total_time': 0, 'errors': 0})
        
        # Learning parameters
        self.performance_thresholds = {
            'slow_operation_ms': 1000,
            'high_complexity': 7,
            'low_accuracy': 0.7,
            'hot_path_frequency': 10
        }
        
        self.load_existing_data()
        
    def load_existing_data(self):
        """Load existing performance data"""
        if self.metrics_file.exists():
            with open(self.metrics_file, 'r') as f:
                data = json.load(f)
                # Convert to CognitiveMetric objects
                for metric_data in data.get('metrics', [])[-1000:]:  # Last 1000
                    metric = CognitiveMetric(**metric_data)
                    self.metrics.append(metric)
                    
        if self.hot_paths_file.exists():
            with open(self.hot_paths_file, 'r') as f:
                self.hot_paths = json.load(f)
                
    def save_performance_data(self):
        """Save performance data to disk"""
        # Save metrics
        metrics_data = {
            'timestamp': datetime.now().isoformat(),
            'metrics': [asdict(metric) for metric in list(self.metrics)[-1000:]],  # Last 1000
            'performance_summary': self.get_performance_summary()
        }
        
        self.metrics_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.metrics_file, 'w') as f:
            json.dump(metrics_data, f, indent=2)
            
        # Save hot paths
        with open(self.hot_paths_file, 'w') as f:
            json.dump(self.hot_paths, f, indent=2)
            
    def cognitive_profiler(self, operation_name: str, context_complexity: int = 5):
        """Decorator for profiling cognitive operations"""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                start_memory = self._get_memory_usage()
                
                try:
                    result = func(*args, **kwargs)
                    outcome = 'success'
                    accuracy = self._calculate_accuracy(result, func.__name__)
                    confidence = self._calculate_confidence(result, outcome)
                except Exception as e:
                    result = None
                    outcome = 'error'
                    accuracy = 0.0
                    confidence = 0.0
                    
                end_time = time.time()
                duration_ms = (end_time - start_time) * 1000
                end_memory = self._get_memory_usage()
                memory_delta = end_memory - start_memory
                
                # Calculate cognitive load based on duration and complexity
                cognitive_load = min(1.0, (duration_ms / 1000.0) * (context_complexity / 10.0))
                
                # Record metric
                metric = CognitiveMetric(
                    timestamp=datetime.now().isoformat(),
                    operation=operation_name,
                    duration_ms=duration_ms,
                    accuracy_score=accuracy,
                    context_complexity=context_complexity,
                    cognitive_load=cognitive_load,
                    outcome=outcome,
                    memory_usage=memory_delta,
                    confidence=confidence
                )
                
                self.record_metric(metric)
                
                if outcome == 'error':
                    raise
                    
                return result
            return wrapper
        return decorator
        
    def record_metric(self, metric: CognitiveMetric):
        """Record a cognitive performance metric"""
        self.metrics.append(metric)
        self.operation_stats[metric.operation].append(metric)
        
        # Update real-time stats
        self.real_time_stats[metric.operation]['count'] += 1
        self.real_time_stats[metric.operation]['total_time'] += metric.duration_ms
        if metric.outcome == 'error':
            self.real_time_stats[metric.operation]['errors'] += 1
            
        # Check for hot path candidates
        if self.real_time_stats[metric.operation]['count'] >= self.performance_thresholds['hot_path_frequency']:
            self._mark_as_hot_path(metric.operation)
            
    def _calculate_accuracy(self, result: Any, operation: str) -> float:
        """Calculate accuracy score for operation result"""
        if result is None:
            return 0.0
            
        # Simple heuristics - can be enhanced per operation type
        if isinstance(result, bool):
            return 1.0 if result else 0.5
        elif isinstance(result, (list, dict)):
            return min(1.0, len(str(result)) / 100.0)  # Normalize by content size
        elif isinstance(result, str):
            return min(1.0, len(result) / 50.0)  # Normalize by string length
        else:
            return 0.8  # Default decent accuracy
            
    def _calculate_confidence(self, result: Any, outcome: str) -> float:
        """Calculate confidence in the result"""
        if outcome == 'error':
            return 0.0
        elif result is None:
            return 0.3
        else:
            # Higher confidence for non-empty results
            return 0.9 if result else 0.5
            
    def _get_memory_usage(self) -> int:
        """Get current memory usage (simplified)"""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss
        except ImportError:
            # Fallback to basic memory approximation
            import sys
            return sys.getsizeof(self.metrics) + sys.getsizeof(self.operation_stats)
        except:
            return 0
            
    def _mark_as_hot_path(self, operation: str):
        """Mark operation as cognitive hot path"""
        stats = self.real_time_stats[operation]
        avg_time = stats['total_time'] / stats['count']
        error_rate = stats['errors'] / stats['count']
        
        self.hot_paths[operation] = {
            'frequency': stats['count'],
            'avg_duration_ms': avg_time,
            'error_rate': error_rate,
            'marked_at': datetime.now().isoformat(),
            'optimization_priority': self._calculate_optimization_priority(avg_time, stats['count'], error_rate)
        }
        
        print(f"[COGNITIVE_PROFILER] Hot path identified: {operation} (freq: {stats['count']}, avg: {avg_time:.1f}ms)")
        
    def _calculate_optimization_priority(self, avg_time: float, frequency: int, error_rate: float) -> float:
        """Calculate optimization priority for hot path"""
        # Higher priority for slow, frequent, error-prone operations
        time_factor = min(1.0, avg_time / 1000.0)  # Normalize to 1s
        frequency_factor = min(1.0, frequency / 100.0)  # Normalize to 100 calls
        error_factor = error_rate
        
        return (time_factor * 0.4) + (frequency_factor * 0.4) + (error_factor * 0.2)
        
    def identify_bottlenecks(self) -> List[CognitiveBottleneck]:
        """Identify cognitive performance bottlenecks"""
        bottlenecks = []
        
        for operation, metrics_list in self.operation_stats.items():
            if len(metrics_list) < 3:  # Need minimum data
                continue
                
            durations = [m.duration_ms for m in metrics_list]
            accuracies = [m.accuracy_score for m in metrics_list]
            cognitive_loads = [m.cognitive_load for m in metrics_list]
            
            avg_duration = statistics.mean(durations)
            avg_accuracy = statistics.mean(accuracies)
            avg_cognitive_load = statistics.mean(cognitive_loads)
            frequency = len(metrics_list)
            
            # Calculate severity based on multiple factors
            severity = 0.0
            suggested_optimizations = []
            
            if avg_duration > self.performance_thresholds['slow_operation_ms']:
                severity += 0.3
                suggested_optimizations.append("Speed optimization needed")
                
            if avg_accuracy < self.performance_thresholds['low_accuracy']:
                severity += 0.2
                suggested_optimizations.append("Accuracy improvement needed")
                
            if avg_cognitive_load > 0.7:
                severity += 0.2
                suggested_optimizations.append("Cognitive load reduction needed")
                
            if frequency > self.performance_thresholds['hot_path_frequency']:
                severity += 0.3
                suggested_optimizations.append("Create specialized brain/cache")
                
            if severity > 0.3:  # Threshold for bottleneck
                bottleneck = CognitiveBottleneck(
                    operation=operation,
                    avg_duration=avg_duration,
                    frequency=frequency,
                    severity=severity,
                    suggested_optimization="; ".join(suggested_optimizations),
                    hot_path_candidate=frequency > self.performance_thresholds['hot_path_frequency']
                )
                bottlenecks.append(bottleneck)
                
        # Sort by severity
        bottlenecks.sort(key=lambda x: x.severity, reverse=True)
        self.bottlenecks = bottlenecks
        return bottlenecks
        
    def optimize_hot_paths(self) -> Dict[str, str]:
        """Generate optimization strategies for hot paths"""
        optimizations = {}
        
        for operation, hot_path_data in self.hot_paths.items():
            priority = hot_path_data['optimization_priority']
            
            if priority > 0.5:  # High priority
                if hot_path_data['avg_duration_ms'] > 500:
                    optimizations[operation] = "Create cached specialized brain"
                elif hot_path_data['frequency'] > 50:
                    optimizations[operation] = "Pre-compile decision tree"
                elif hot_path_data['error_rate'] > 0.1:
                    optimizations[operation] = "Create error-prevention wrapper"
                else:
                    optimizations[operation] = "General performance optimization"
                    
        return optimizations
        
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        if not self.metrics:
            return {'status': 'no_data'}
            
        recent_metrics = list(self.metrics)[-100:]  # Last 100 operations
        
        # Calculate aggregate statistics
        avg_duration = statistics.mean([m.duration_ms for m in recent_metrics])
        avg_accuracy = statistics.mean([m.accuracy_score for m in recent_metrics])
        avg_cognitive_load = statistics.mean([m.cognitive_load for m in recent_metrics])
        success_rate = len([m for m in recent_metrics if m.outcome == 'success']) / len(recent_metrics)
        
        # Performance trends
        first_half = recent_metrics[:len(recent_metrics)//2]
        second_half = recent_metrics[len(recent_metrics)//2:]
        
        if first_half and second_half:
            speed_trend = statistics.mean([m.duration_ms for m in first_half]) - statistics.mean([m.duration_ms for m in second_half])
            accuracy_trend = statistics.mean([m.accuracy_score for m in second_half]) - statistics.mean([m.accuracy_score for m in first_half])
        else:
            speed_trend = 0
            accuracy_trend = 0
            
        return {
            'status': 'active',
            'metrics_count': len(self.metrics),
            'avg_duration_ms': avg_duration,
            'avg_accuracy': avg_accuracy,
            'avg_cognitive_load': avg_cognitive_load,
            'success_rate': success_rate,
            'speed_trend': speed_trend,  # Positive = getting faster
            'accuracy_trend': accuracy_trend,  # Positive = getting more accurate
            'hot_paths_count': len(self.hot_paths),
            'bottlenecks_count': len(self.bottlenecks),
            'performance_grade': self._calculate_performance_grade(avg_duration, avg_accuracy, success_rate)
        }
        
    def _calculate_performance_grade(self, avg_duration: float, avg_accuracy: float, success_rate: float) -> str:
        """Calculate overall performance grade"""
        # Scoring based on speed, accuracy, and reliability
        speed_score = max(0, 100 - (avg_duration / 10))  # Penalty for slow operations
        accuracy_score = avg_accuracy * 100
        reliability_score = success_rate * 100
        
        overall_score = (speed_score * 0.3) + (accuracy_score * 0.4) + (reliability_score * 0.3)
        
        if overall_score >= 90:
            return 'A+'
        elif overall_score >= 80:
            return 'A'
        elif overall_score >= 70:
            return 'B'
        elif overall_score >= 60:
            return 'C'
        else:
            return 'D'
            
    def generate_performance_report(self) -> str:
        """Generate comprehensive performance analysis report"""
        summary = self.get_performance_summary()
        bottlenecks = self.identify_bottlenecks()
        optimizations = self.optimize_hot_paths()
        
        report = f"""# Cognitive Performance Analysis Report
Generated: {datetime.now().isoformat()}

## Performance Summary
- **Overall Grade**: {summary.get('performance_grade', 'N/A')}
- **Metrics Collected**: {summary.get('metrics_count', 0)}
- **Average Duration**: {summary.get('avg_duration_ms', 0):.1f}ms
- **Average Accuracy**: {summary.get('avg_accuracy', 0):.1%}
- **Success Rate**: {summary.get('success_rate', 0):.1%}
- **Cognitive Load**: {summary.get('avg_cognitive_load', 0):.1%}

## Performance Trends
- **Speed Trend**: {"🚀 Getting Faster" if summary.get('speed_trend', 0) > 0 else "🐌 Getting Slower" if summary.get('speed_trend', 0) < 0 else "➡️ Stable"}
- **Accuracy Trend**: {"📈 Improving" if summary.get('accuracy_trend', 0) > 0 else "📉 Declining" if summary.get('accuracy_trend', 0) < 0 else "➡️ Stable"}

## Cognitive Hot Paths ({len(self.hot_paths)})
"""
        
        for operation, data in sorted(self.hot_paths.items(), key=lambda x: x[1]['optimization_priority'], reverse=True):
            report += f"- **{operation}**: {data['frequency']} calls, {data['avg_duration_ms']:.1f}ms avg, {data['error_rate']:.1%} errors\n"
            report += f"  - Priority: {data['optimization_priority']:.2f}\n"
            
        report += f"\n## Performance Bottlenecks ({len(bottlenecks)})\n"
        for bottleneck in bottlenecks[:5]:  # Top 5
            report += f"- **{bottleneck.operation}** (Severity: {bottleneck.severity:.2f})\n"
            report += f"  - Avg Duration: {bottleneck.avg_duration:.1f}ms\n"
            report += f"  - Frequency: {bottleneck.frequency}\n"
            report += f"  - Optimization: {bottleneck.suggested_optimization}\n"
            
        report += f"\n## Optimization Strategies ({len(optimizations)})\n"
        for operation, strategy in optimizations.items():
            report += f"- **{operation}**: {strategy}\n"
            
        return report
        
    def start_real_time_monitoring(self):
        """Start real-time performance monitoring"""
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        print("[COGNITIVE_PROFILER] Real-time monitoring started")
        
    def _monitor_loop(self):
        """Real-time monitoring loop"""
        while self.monitoring_active:
            time.sleep(5)  # Check every 5 seconds
            
            # Save data periodically
            self.save_performance_data()
            
            # Check for critical performance issues
            summary = self.get_performance_summary()
            if summary.get('performance_grade') in ['D', 'C']:
                print(f"[COGNITIVE_PROFILER] ⚠️ Performance degradation detected: Grade {summary['performance_grade']}")
                
    def stop_monitoring(self):
        """Stop real-time monitoring"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join()
        print("[COGNITIVE_PROFILER] Monitoring stopped")

def main():
    """Test cognitive performance profiler"""
    profiler = CognitivePerformanceProfiler()
    
    print("[COGNITIVE_PROFILER] ===== COGNITIVE PERFORMANCE PROFILER =====")
    
    # Test the profiler with some mock operations
    @profiler.cognitive_profiler("file_search", context_complexity=6)
    def mock_file_search(pattern: str):
        time.sleep(0.1)  # Simulate work
        return [f"file_{i}.py" for i in range(5)]
        
    @profiler.cognitive_profiler("path_resolution", context_complexity=4)
    def mock_path_resolution(path: str):
        time.sleep(0.05)  # Simulate work
        return f"/resolved/{path}"
        
    @profiler.cognitive_profiler("pattern_analysis", context_complexity=8)
    def mock_pattern_analysis(data):
        time.sleep(0.2)  # Simulate complex work
        return {"patterns": ["p1", "p2"], "confidence": 0.85}
        
    # Run some operations
    for i in range(15):
        mock_file_search(f"*.{['py', 'json', 'cc'][i % 3]}")
        mock_path_resolution(f"file_{i}")
        if i % 3 == 0:
            mock_pattern_analysis([1, 2, 3, 4, 5])
            
    # Generate analysis
    bottlenecks = profiler.identify_bottlenecks()
    report = profiler.generate_performance_report()
    
    # Save results
    profiler.save_performance_data()
    
    report_path = profiler.project_root / 'cognitive_performance_report.md'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
        
    print(f"[COGNITIVE_PROFILER] Performance report saved to: {report_path}")
    print(f"[COGNITIVE_PROFILER] Bottlenecks identified: {len(bottlenecks)}")
    print(f"[COGNITIVE_PROFILER] Hot paths detected: {len(profiler.hot_paths)}")
    
    # Show key metrics
    summary = profiler.get_performance_summary()
    print(f"[COGNITIVE_PROFILER] Performance Grade: {summary.get('performance_grade', 'N/A')}")
    
    return profiler

if __name__ == "__main__":
    main()