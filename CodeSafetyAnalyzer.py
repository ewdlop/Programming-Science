import ast
import re
from typing import List, Dict, Set, Optional
from dataclasses import dataclass
from pathlib import Path
import logging

@dataclass
class CodePattern:
    """Represents a code pattern with associated risk metrics"""
    name: str
    description: str
    risk_level: str  # 'low', 'medium', 'high'
    remediation: str
    category: str

class CodeSafetyAnalyzer:
    def __init__(self):
        self.logger = self._setup_logger()
        self.patterns = self._initialize_patterns()

    def _setup_logger(self) -> logging.Logger:
        """Configure logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)

    def _initialize_patterns(self) -> Dict[str, CodePattern]:
        """Initialize known code patterns to check"""
        return {
            'hardcoded_credentials': CodePattern(
                name='Hardcoded Credentials',
                description='Credentials or secrets directly embedded in code',
                risk_level='high',
                remediation='Use environment variables or secure secret management',
                category='security'
            ),
            'unsafe_deserialization': CodePattern(
                name='Unsafe Deserialization',
                description='Direct deserialization of untrusted data',
                risk_level='high',
                remediation='Implement proper input validation and sanitization',
                category='security'
            ),
            'sql_concatenation': CodePattern(
                name='SQL String Concatenation',
                description='Direct string concatenation in SQL queries',
                risk_level='high',
                remediation='Use parameterized queries or ORM',
                category='security'
            ),
            'file_path_manipulation': CodePattern(
                name='Unsafe File Path Handling',
                description='Insufficient validation of file paths',
                risk_level='medium',
                remediation='Use path sanitization and access control',
                category='security'
            ),
            'debug_info': CodePattern(
                name='Debug Information',
                description='Debug/trace information in production code',
                risk_level='low',
                remediation='Remove or disable debug code in production',
                category='best_practice'
            ),
            'error_suppression': CodePattern(
                name='Broad Error Suppression',
                description='Catching all exceptions without proper handling',
                risk_level='medium',
                remediation='Catch specific exceptions and handle appropriately',
                category='reliability'
            )
        }

    def analyze_code(self, code: str) -> Dict:
        """
        Analyze code for potentially unsafe patterns
        
        Args:
            code: String containing source code to analyze
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            tree = ast.parse(code)
            
            results = {
                'findings': [],
                'metrics': self._calculate_metrics(tree),
                'recommendations': []
            }
            
            # Analyze AST
            visitor = CodeVisitor()
            visitor.visit(tree)
            
            # Process findings
            self._analyze_patterns(code, visitor, results)
            
            # Generate recommendations
            self._generate_recommendations(results)
            
            return results
            
        except SyntaxError as e:
            self.logger.error(f"Failed to parse code: {e}")
            return {'error': 'Invalid Python syntax'}
        except Exception as e:
            self.logger.error(f"Analysis error: {e}")
            return {'error': 'Analysis failed'}

    def _calculate_metrics(self, tree: ast.AST) -> Dict:
        """Calculate code complexity metrics"""
        metrics = {
            'cyclomatic_complexity': 0,
            'number_of_functions': 0,
            'number_of_classes': 0,
            'lines_of_code': 0,
            'comment_ratio': 0.0
        }
        
        # Count functions and classes
        metrics['number_of_functions'] = len([node for node in ast.walk(tree) 
                                            if isinstance(node, ast.FunctionDef)])
        metrics['number_of_classes'] = len([node for node in ast.walk(tree) 
                                          if isinstance(node, ast.ClassDef)])
        
        # Calculate cyclomatic complexity
        complexity_visitor = ComplexityVisitor()
        complexity_visitor.visit(tree)
        metrics['cyclomatic_complexity'] = complexity_visitor.complexity
        
        return metrics

    def _analyze_patterns(self, code: str, visitor: 'CodeVisitor', 
                         results: Dict) -> None:
        """Analyze code patterns based on AST visitor results"""
        
        # Check for hardcoded credentials
        if visitor.has_hardcoded_credentials:
            results['findings'].append({
                'pattern': self.patterns['hardcoded_credentials'],
                'locations': visitor.credential_locations
            })

        # Check for unsafe deserialization
        if visitor.has_unsafe_deserialization:
            results['findings'].append({
                'pattern': self.patterns['unsafe_deserialization'],
                'locations': visitor.deserialization_locations
            })

        # Check for SQL string concatenation
        if visitor.has_sql_concatenation:
            results['findings'].append({
                'pattern': self.patterns['sql_concatenation'],
                'locations': visitor.sql_locations
            })

        # Check for unsafe file operations
        if visitor.has_unsafe_file_ops:
            results['findings'].append({
                'pattern': self.patterns['file_path_manipulation'],
                'locations': visitor.file_op_locations
            })

        # Check for debug information
        if visitor.has_debug_info:
            results['findings'].append({
                'pattern': self.patterns['debug_info'],
                'locations': visitor.debug_locations
            })

        # Check error handling
        if visitor.has_broad_exception_handling:
            results['findings'].append({
                'pattern': self.patterns['error_suppression'],
                'locations': visitor.exception_locations
            })

    def _generate_recommendations(self, results: Dict) -> None:
        """Generate security recommendations based on findings"""
        for finding in results['findings']:
            pattern = finding['pattern']
            results['recommendations'].append({
                'title': f'Address {pattern.name}',
                'description': pattern.description,
                'remediation': pattern.remediation,
                'priority': pattern.risk_level
            })

        # Add general recommendations based on metrics
        metrics = results['metrics']
        if metrics['cyclomatic_complexity'] > 10:
            results['recommendations'].append({
                'title': 'Reduce Code Complexity',
                'description': 'High cyclomatic complexity detected',
                'remediation': 'Consider breaking down complex functions',
                'priority': 'medium'
            })

class CodeVisitor(ast.NodeVisitor):
    """AST visitor to identify code patterns"""
    
    def __init__(self):
        self.has_hardcoded_credentials = False
        self.has_unsafe_deserialization = False
        self.has_sql_concatenation = False
        self.has_unsafe_file_ops = False
        self.has_debug_info = False
        self.has_broad_exception_handling = False
        
        self.credential_locations = []
        self.deserialization_locations = []
        self.sql_locations = []
        self.file_op_locations = []
        self.debug_locations = []
        self.exception_locations = []

    def visit_Assign(self, node: ast.Assign):
        """Visit assignment nodes"""
        # Check for potential hardcoded credentials
        for target in node.targets:
            if isinstance(target, ast.Name):
                name = target.id.lower()
                if any(cred in name for cred in ['password', 'secret', 'key', 'token']):
                    if isinstance(node.value, (ast.Str, ast.Constant)):
                        self.has_hardcoded_credentials = True
                        self.credential_locations.append(node.lineno)

        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        """Visit function call nodes"""
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
            
            # Check for unsafe deserialization
            if func_name in ['pickle.loads', 'yaml.load']:
                self.has_unsafe_deserialization = True
                self.deserialization_locations.append(node.lineno)
            
            # Check for debug info
            if func_name in ['print', 'logging.debug']:
                self.has_debug_info = True
                self.debug_locations.append(node.lineno)

        self.generic_visit(node)

    def visit_BinOp(self, node: ast.BinOp):
        """Visit binary operation nodes"""
        # Check for string concatenation in SQL queries
        if isinstance(node.op, ast.Add):
            if any(isinstance(n, ast.Str) for n in [node.left, node.right]):
                if self._is_sql_string(node):
                    self.has_sql_concatenation = True
                    self.sql_locations.append(node.lineno)

        self.generic_visit(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler):
        """Visit exception handler nodes"""
        # Check for broad exception handling
        if node.type is None or (isinstance(node.type, ast.Name) and 
                               node.type.id == 'Exception'):
            self.has_broad_exception_handling = True
            self.exception_locations.append(node.lineno)

        self.generic_visit(node)

    def _is_sql_string(self, node: ast.AST) -> bool:
        """Check if a string contains SQL keywords"""
        sql_keywords = {'select', 'insert', 'update', 'delete', 'where', 'from'}
        
        def get_string_value(n):
            if isinstance(n, ast.Str):
                return n.s
            elif isinstance(n, ast.Constant) and isinstance(n.value, str):
                return n.value
            return ''
        
        if isinstance(node, ast.BinOp):
            left_str = get_string_value(node.left)
            right_str = get_string_value(node.right)
            combined = f"{left_str} {right_str}".lower()
            return any(keyword in combined for keyword in sql_keywords)
            
        return False

class ComplexityVisitor(ast.NodeVisitor):
    """AST visitor to calculate cyclomatic complexity"""
    
    def __init__(self):
        self.complexity = 1
    
    def visit_If(self, node):
        self.complexity += 1
        self.generic_visit(node)
    
    def visit_While(self, node):
        self.complexity += 1
        self.generic_visit(node)
    
    def visit_For(self, node):
        self.complexity += 1
        self.generic_visit(node)
    
    def visit_And(self, node):
        self.complexity += 1
        self.generic_visit(node)
    
    def visit_Or(self, node):
        self.complexity += 1
        self.generic_visit(node)

# Example usage
if __name__ == "__main__":
    analyzer = CodeSafetyAnalyzer()
    
    # Example code to analyze
    sample_code = """
    def process_user_data(user_input):
        try:
            # Unsafe string concatenation
            query = "SELECT * FROM users WHERE id = " + user_input
            
            # Hardcoded credential
            api_key = "1234secret"
            
            # Debug info
            print("Processing user:", user_input)
            
            # Unsafe file operation
            with open(user_input + ".txt", "r") as f:
                data = f.read()
                
        except Exception:  # Broad exception handling
            pass
    """
    
    # Analyze the code
    results = analyzer.analyze_code(sample_code)
    
    # Print results
    print("\nAnalysis Results:")
    print("-" * 50)
    
    print("\nFindings:")
    for finding in results['findings']:
        pattern = finding['pattern']
        print(f"\n- {pattern.name} (Risk Level: {pattern.risk_level})")
        print(f"  Description: {pattern.description}")
        print(f"  Locations: {finding['locations']}")
        print(f"  Remediation: {pattern.remediation}")
    
    print("\nMetrics:")
    for metric, value in results['metrics'].items():
        print(f"- {metric}: {value}")
    
    print("\nRecommendations:")
    for rec in results['recommendations']:
        print(f"\n- {rec['title']} (Priority: {rec['priority']})")
        print(f"  {rec['description']}")
        print(f"  Remediation: {rec['remediation']}")
