import ast
from typing import Dict, List, Set, Optional
from dataclasses import dataclass
import logging
from pathlib import Path

@dataclass
class ComplexityMetric:
    """Represents complexity metrics for a code unit"""
    name: str
    complexity: int
    line_number: int
    type: str  # 'function' or 'class'
    nested_depth: int
    decision_points: List[Dict]

class CyclomaticComplexityAnalyzer:
    def __init__(self, threshold_warning: int = 10, threshold_critical: int = 15):
        """
        Initialize the analyzer with complexity thresholds
        
        Args:
            threshold_warning: Complexity level that triggers a warning
            threshold_critical: Complexity level that triggers a critical alert
        """
        self.threshold_warning = threshold_warning
        self.threshold_critical = threshold_critical
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """Configure logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)

    def analyze_code(self, code: str) -> Dict:
        """
        Analyze code for cyclomatic complexity
        
        Args:
            code: String containing source code to analyze
            
        Returns:
            Dictionary containing complexity metrics and hotspots
        """
        try:
            tree = ast.parse(code)
            visitor = ComplexityVisitor()
            visitor.visit(tree)
            
            # Calculate overall metrics
            metrics = {
                'overall_complexity': visitor.total_complexity,
                'average_function_complexity': self._calculate_average(
                    [m.complexity for m in visitor.metrics if m.type == 'function']
                ),
                'max_complexity': max(m.complexity for m in visitor.metrics) if visitor.metrics else 0,
                'total_decision_points': len(visitor.all_decision_points),
                'unique_decision_types': len(set(d['type'] for d in visitor.all_decision_points))
            }
            
            # Identify complexity hotspots
            hotspots = self._identify_hotspots(visitor.metrics)
            
            # Generate detailed analysis
            analysis = {
                'metrics': metrics,
                'hotspots': hotspots,
                'recommendations': self._generate_recommendations(metrics, hotspots),
                'details': self._generate_detailed_report(visitor.metrics),
                'decision_point_summary': self._summarize_decision_points(
                    visitor.all_decision_points
                )
            }
            
            return analysis
            
        except SyntaxError as e:
            self.logger.error(f"Failed to parse code: {e}")
            return {'error': 'Invalid Python syntax'}
        except Exception as e:
            self.logger.error(f"Analysis error: {e}")
            return {'error': 'Analysis failed'}

    def _calculate_average(self, values: List[int]) -> float:
        """Calculate average of values, handling empty lists"""
        return sum(values) / len(values) if values else 0.0

    def _identify_hotspots(self, metrics: List[ComplexityMetric]) -> List[Dict]:
        """Identify code areas with high complexity"""
        hotspots = []
        
        for metric in metrics:
            severity = self._determine_severity(metric.complexity)
            if severity != 'normal':
                hotspots.append({
                    'name': metric.name,
                    'complexity': metric.complexity,
                    'line_number': metric.line_number,
                    'type': metric.type,
                    'severity': severity,
                    'nested_depth': metric.nested_depth,
                    'decision_points': metric.decision_points
                })
        
        return sorted(hotspots, key=lambda x: (-x['complexity'], x['line_number']))

    def _determine_severity(self, complexity: int) -> str:
        """Determine severity level based on complexity"""
        if complexity >= self.threshold_critical:
            return 'critical'
        elif complexity >= self.threshold_warning:
            return 'warning'
        return 'normal'

    def _generate_recommendations(self, metrics: Dict, hotspots: List[Dict]) -> List[Dict]:
        """Generate specific recommendations for complexity reduction"""
        recommendations = []
        
        # Check overall complexity
        if metrics['overall_complexity'] > self.threshold_critical * 2:
            recommendations.append({
                'type': 'critical',
                'message': 'Overall code complexity is very high',
                'suggestion': 'Consider breaking down the code into smaller modules'
            })
        
        # Check average function complexity
        if metrics['average_function_complexity'] > self.threshold_warning:
            recommendations.append({
                'type': 'warning',
                'message': 'Average function complexity is high',
                'suggestion': 'Review functions for potential simplification'
            })
        
        # Generate specific recommendations for hotspots
        for hotspot in hotspots:
            if hotspot['severity'] == 'critical':
                recommendations.append(self._generate_hotspot_recommendation(hotspot))
        
        return recommendations

    def _generate_hotspot_recommendation(self, hotspot: Dict) -> Dict:
        """Generate specific recommendation for a complexity hotspot"""
        base_message = f"High complexity in {hotspot['type']} '{hotspot['name']}'"
        
        # Analyze decision points to give more specific recommendations
        decision_types = [d['type'] for d in hotspot['decision_points']]
        
        if len(set(decision_types)) == 1:
            # Single type of complexity
            d_type = decision_types[0]
            if d_type == 'if':
                suggestion = 'Consider using strategy pattern or lookup tables'
            elif d_type == 'loop':
                suggestion = 'Consider breaking loop body into smaller functions'
            else:
                suggestion = 'Consider breaking down into smaller functions'
        else:
            # Mixed types of complexity
            suggestion = ('Break down the code into smaller, focused functions '
                        'handling specific cases')
        
        return {
            'type': 'critical',
            'message': base_message,
            'suggestion': suggestion,
            'location': f"Line {hotspot['line_number']}"
        }

    def _generate_detailed_report(self, metrics: List[ComplexityMetric]) -> List[Dict]:
        """Generate detailed complexity report for each code unit"""
        return [{
            'name': m.name,
            'type': m.type,
            'complexity': m.complexity,
            'line_number': m.line_number,
            'nested_depth': m.nested_depth,
            'severity': self._determine_severity(m.complexity),
            'decision_points': self._format_decision_points(m.decision_points)
        } for m in metrics]

    def _format_decision_points(self, decision_points: List[Dict]) -> List[Dict]:
        """Format decision points for reporting"""
        return [{
            'type': d['type'],
            'line': d['line'],
            'description': self._get_decision_description(d)
        } for d in decision_points]

    def _get_decision_description(self, decision: Dict) -> str:
        """Generate human-readable description of decision point"""
        type_descriptions = {
            'if': 'Conditional branch',
            'loop': 'Loop construct',
            'except': 'Exception handler',
            'boolean_op': 'Boolean operation',
            'return': 'Early return statement'
        }
        return type_descriptions.get(decision['type'], 'Unknown decision point')

    def _summarize_decision_points(self, decision_points: List[Dict]) -> Dict:
        """Summarize all decision points in the code"""
        summary = {}
        
        # Count by type
        type_counts = {}
        for point in decision_points:
            type_counts[point['type']] = type_counts.get(point['type'], 0) + 1
        
        # Calculate distributions
        total = len(decision_points)
        distributions = {
            t: {'count': c, 'percentage': (c / total) * 100}
            for t, c in type_counts.items()
        }
        
        # Find clusters
        clusters = self._find_decision_clusters(decision_points)
        
        return {
            'total_points': total,
            'distributions': distributions,
            'clusters': clusters
        }

    def _find_decision_clusters(self, decision_points: List[Dict]) -> List[Dict]:
        """Identify clusters of decision points"""
        clusters = []
        window_size = 5
        min_cluster_size = 3
        
        # Sort by line number
        sorted_points = sorted(decision_points, key=lambda x: x['line'])
        
        current_cluster = []
        for i, point in enumerate(sorted_points):
            if not current_cluster or (
                point['line'] - current_cluster[-1]['line'] <= window_size
            ):
                current_cluster.append(point)
            else:
                if len(current_cluster) >= min_cluster_size:
                    clusters.append({
                        'start_line': current_cluster[0]['line'],
                        'end_line': current_cluster[-1]['line'],
                        'size': len(current_cluster),
                        'types': [p['type'] for p in current_cluster]
                    })
                current_cluster = [point]
        
        # Handle last cluster
        if len(current_cluster) >= min_cluster_size:
            clusters.append({
                'start_line': current_cluster[0]['line'],
                'end_line': current_cluster[-1]['line'],
                'size': len(current_cluster),
                'types': [p['type'] for p in current_cluster]
            })
        
        return clusters

class ComplexityVisitor(ast.NodeVisitor):
    """AST visitor to calculate cyclomatic complexity"""
    
    def __init__(self):
        self.metrics = []
        self.total_complexity = 1  # Base complexity
        self.current_function = None
        self.current_class = None
        self.nested_depth = 0
        self.all_decision_points = []
        self.current_decision_points = []

    def visit_ClassDef(self, node):
        """Visit class definition"""
        previous_class = self.current_class
        self.current_class = node.name
        self.nested_depth += 1
        
        # Visit all nodes in the class
        self.generic_visit(node)
        
        self.nested_depth -= 1
        self.current_class = previous_class

    def visit_FunctionDef(self, node):
        """Visit function definition"""
        previous_function = self.current_function
        previous_points = self.current_decision_points
        
        self.current_function = node.name
        self.current_decision_points = []
        start_complexity = self.total_complexity
        self.nested_depth += 1
        
        # Visit all nodes in the function
        self.generic_visit(node)
        
        # Calculate function complexity
        function_complexity = self.total_complexity - start_complexity + 1
        
        # Record metrics
        self.metrics.append(ComplexityMetric(
            name=node.name,
            complexity=function_complexity,
            line_number=node.lineno,
            type='function',
            nested_depth=self.nested_depth,
            decision_points=self.current_decision_points.copy()
        ))
        
        self.nested_depth -= 1
        self.current_function = previous_function
        self.current_decision_points = previous_points

    def _add_decision_point(self, node: ast.AST, decision_type: str):
        """Record a decision point"""
        point = {
            'type': decision_type,
            'line': node.lineno
        }
        self.current_decision_points.append(point)
        self.all_decision_points.append(point)
        self.total_complexity += 1

    def visit_If(self, node):
        """Visit if statement"""
        self._add_decision_point(node, 'if')
        self.generic_visit(node)

    def visit_While(self, node):
        """Visit while loop"""
        self._add_decision_point(node, 'loop')
        self.generic_visit(node)

    def visit_For(self, node):
        """Visit for loop"""
        self._add_decision_point(node, 'loop')
        self.generic_visit(node)

    def visit_ExceptHandler(self, node):
        """Visit exception handler"""
        self._add_decision_point(node, 'except')
        self.generic_visit(node)

    def visit_Return(self, node):
        """Visit return statement"""
        if self.current_function:  # Only count returns inside functions
            self._add_decision_point(node, 'return')
        self.generic_visit(node)

    def visit_BoolOp(self, node):
        """Visit boolean operation"""
        if isinstance(node.op, (ast.And, ast.Or)):
            self._add_decision_point(node, 'boolean_op')
        self.generic_visit(node)

# Example usage
if __name__ == "__main__":
    analyzer = CyclomaticComplexityAnalyzer()
    
    # Example code to analyze
    sample_code = """
    def process_data(data):
        if not data:
            return None
            
        result = []
        for item in data:
            if item.get('active'):
                if item.get('type') == 'A':
                    result.append(item['value'] * 2)
                elif item.get('type') == 'B':
                    if item.get('value') > 0:
                        result.append(item['value'] / 2)
                else:
                    try:
                        result.append(float(item['value']))
                    except ValueError:
                        continue
        
        return result if result else None
    
    class DataProcessor:
        def clean_data(self, items):
            cleaned = []
            for item in items:
                if item and (item.get('valid') or item.get('force')):
                    cleaned.append(item)
            return cleaned
    """
    
    # Analyze the code
    results = analyzer.analyze_code(sample_code)
    
    # Print results
    print("\nComplexity Analysis:")
    print("-" * 50)
    
    print("\nOverall Metrics:")
    for metric, value in results['metrics'].items():
        print(f"- {metric}: {value}")
    
    print("\nHotspots:")
    for hotspot in results['hotspots']:
        print(f"\n- {hotspot['name']} ({hotspot['type']})")
        print(f"  Complexity: {hotspot['complexity']}")
        print(f"  Line: {hotspot['line_number']}")
        print(f"  Severity: {hotspot['severity']}")
    
    print("\nRecommendations:")
    for rec in results['recommendations']:
        print(f"\n- {rec['message']}")
        print(f"  Suggestion: {rec['suggestion']}")
