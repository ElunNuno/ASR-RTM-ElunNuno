"""
Vosk-API 项目代码调用关系分析工具
分析项目中的代码调用关系并生成报告
"""
import os
import sys
import ast
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Set

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# 设置日志
log_file = project_root / 'reports' / f'code_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class CallGraphVisitor(ast.NodeVisitor):
    """AST访问器，用于收集函数调用信息"""
    def __init__(self):
        self.calls: List[Tuple[str, str]] = []  # (caller, callee)
        self.imports: Set[str] = set()  # 导入的模块
        self.current_class: str = None
        self.current_function: str = None
        self.qt_signals: Dict[str, List[str]] = {}  # {class_name: [signal_names]}
        self.qt_slots: Dict[str, List[str]] = {}    # {class_name: [slot_names]}
        
    def visit_ClassDef(self, node):
        """访问类定义"""
        old_class = self.current_class
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = old_class
        
    def visit_FunctionDef(self, node):
        """访问函数定义"""
        old_function = self.current_function
        self.current_function = node.name
        
        # 检查是否是Qt槽函数
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name) and decorator.id == 'pyqtSlot':
                if self.current_class not in self.qt_slots:
                    self.qt_slots[self.current_class] = []
                self.qt_slots[self.current_class].append(node.name)
                
        self.generic_visit(node)
        self.current_function = old_function
        
    def visit_Assign(self, node):
        """访问变量赋值，查找Qt信号定义"""
        if self.current_class:
            for target in node.targets:
                if isinstance(target, ast.Name):
                    if isinstance(node.value, ast.Call):
                        if isinstance(node.value.func, ast.Name):
                            if node.value.func.id == 'pyqtSignal':
                                if self.current_class not in self.qt_signals:
                                    self.qt_signals[self.current_class] = []
                                self.qt_signals[self.current_class].append(target.id)
        self.generic_visit(node)
        
    def visit_Call(self, node):
        """访问函数调用"""
        if self.current_function:
            if isinstance(node.func, ast.Name):
                self.calls.append((
                    f"{self.current_class}.{self.current_function}" if self.current_class else self.current_function,
                    node.func.id
                ))
            elif isinstance(node.func, ast.Attribute):
                self.calls.append((
                    f"{self.current_class}.{self.current_function}" if self.current_class else self.current_function,
                    node.func.attr
                ))
        self.generic_visit(node)
        
    def visit_Import(self, node):
        """访问导入语句"""
        for name in node.names:
            self.imports.add(name.name)
        self.generic_visit(node)
        
    def visit_ImportFrom(self, node):
        """访问from导入语句"""
        if node.module:
            self.imports.add(node.module)
        for name in node.names:
            self.imports.add(f"{node.module}.{name.name}" if node.module else name.name)
        self.generic_visit(node)

class CodeAnalyzer:
    """代码分析器"""
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.results: Dict = {
            'files_analyzed': [],
            'component_calls': {},
            'qt_signals': {},
            'qt_slots': {},
            'imports': {},
            'errors': []
        }
        
    def analyze_file(self, file_path: Path) -> None:
        """分析单个Python文件"""
        try:
            logger.info(f"分析文件: {file_path.relative_to(self.root_dir)}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            visitor = CallGraphVisitor()
            visitor.visit(tree)
            
            rel_path = file_path.relative_to(self.root_dir)
            self.results['files_analyzed'].append(str(rel_path))
            self.results['component_calls'][str(rel_path)] = visitor.calls
            self.results['qt_signals'].update(visitor.qt_signals)
            self.results['qt_slots'].update(visitor.qt_slots)
            self.results['imports'][str(rel_path)] = list(visitor.imports)
            
            logger.info(f"找到 {len(visitor.calls)} 个调用关系")
            logger.info(f"找到 {len(visitor.imports)} 个导入")
            if visitor.qt_signals:
                logger.info(f"找到 Qt 信号: {visitor.qt_signals}")
            if visitor.qt_slots:
                logger.info(f"找到 Qt 槽: {visitor.qt_slots}")
                
        except Exception as e:
            error_msg = f"分析文件 {file_path} 失败: {str(e)}"
            logger.error(error_msg)
            self.results['errors'].append(error_msg)
    
    def analyze_core_components(self) -> None:
        """分析核心组件"""
        core_components = {
            'AudioProcessor': self.root_dir / 'src' / 'core' / 'audio' / 'audio_processor.py',
            'FileTranscriber': self.root_dir / 'src' / 'core' / 'audio' / 'file_transcriber.py',
            'SubtitleWidget': self.root_dir / 'src' / 'ui' / 'widgets' / 'subtitle_widget.py',
            'PluginManager': self.root_dir / 'src' / 'core' / 'plugins' / 'base' / 'plugin_manager.py',
            'MainWindow': self.root_dir / 'src' / 'ui' / 'main_window.py'
        }
        
        logger.info("开始分析核心组件...")
        for component, file_path in core_components.items():
            if file_path.exists():
                logger.info(f"\n分析组件: {component}")
                self.analyze_file(file_path)
            else:
                error_msg = f"组件文件不存在: {file_path}"
                logger.error(error_msg)
                self.results['errors'].append(error_msg)
    
    def save_results(self) -> None:
        """保存分析结果"""
        report_file = self.root_dir / 'reports' / f'code_analysis_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        logger.info(f"\n分析报告已保存到: {report_file}")

def main():
    """主函数"""
    logger.info("开始代码分析...")
    analyzer = CodeAnalyzer(project_root)
    analyzer.analyze_core_components()
    analyzer.save_results()
    logger.info("代码分析完成!")

if __name__ == "__main__":
    main()
