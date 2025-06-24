"""
Vosk-API 项目代码调用关系分析脚本
"""
import os
import sys
import ast
import networkx as nx
import matplotlib.pyplot as plt
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# 设置调试输出
DEBUG = True
def debug_print(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)

debug_print(f"项目根目录: {project_root}")
debug_print(f"Python路径: {sys.path}")

class CodeAnalyzer:
    """代码分析器"""
    def __init__(self, root_dir):
        self.root_dir = Path(root_dir)
        self.call_graph = nx.DiGraph()
        self.signal_connections = {}
        
    def analyze_file(self, file_path):
        """分析单个Python文件"""
        try:
            debug_print(f"\n正在分析文件: {file_path}")
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            debug_print(f"文件大小: {len(content)} 字节")
            tree = ast.parse(content)
            analyzer = CallGraphVisitor()
            analyzer.visit(tree)
            
            # 添加到调用图
            debug_print(f"找到 {len(analyzer.calls)} 个调用关系:")
            for caller, callee in analyzer.calls:
                debug_print(f"  {caller} -> {callee}")
                self.call_graph.add_edge(caller, callee)
                
            return analyzer.calls
        except Exception as e:
            debug_print(f"分析文件失败 {file_path}: {e}")
            return []
          def analyze_file(self, file_path):
        """分析单个Python文件"""
        try:
            debug_print(f"\n正在分析文件: {file_path}")
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            debug_print(f"文件大小: {len(content)} 字节")
            tree = ast.parse(content)
            analyzer = CallGraphVisitor()
            analyzer.visit(tree)
            
            # 添加到调用图
            debug_print(f"找到 {len(analyzer.calls)} 个调用关系:")
            for caller, callee in analyzer.calls:
                debug_print(f"  {caller} -> {callee}")
                self.call_graph.add_edge(caller, callee)
                
            return analyzer.calls
        except Exception as e:
            print(f"分析文件失败 {file_path}: {e}")
            return []
            
    def analyze_directory(self, dir_path=None):
        """分析目录下的所有Python文件"""
        if dir_path is None:
            dir_path = self.root_dir
            
        for file_path in Path(dir_path).rglob('*.py'):
            if '__pycache__' not in str(file_path):
                self.analyze_file(file_path)
                
    def draw_call_graph(self, output_file='call_graph.png'):
        """绘制调用关系图"""
        plt.figure(figsize=(15, 10))
        pos = nx.spring_layout(self.call_graph)
        nx.draw(self.call_graph, pos, with_labels=True, 
                node_color='lightblue', node_size=2000, 
                font_size=8, font_weight='bold')
        plt.savefig(output_file)
        plt.close()

class CallGraphVisitor(ast.NodeVisitor):
    """AST访问器，用于收集函数调用信息"""
    def __init__(self):
        self.calls = []
        self.current_function = None
        
    def visit_FunctionDef(self, node):
        """访问函数定义"""
        old_function = self.current_function
        self.current_function = node.name
        self.generic_visit(node)
        self.current_function = old_function
        
    def visit_Call(self, node):
        """访问函数调用"""
        if self.current_function:
            if isinstance(node.func, ast.Name):
                self.calls.append((self.current_function, node.func.id))
            elif isinstance(node.func, ast.Attribute):
                self.calls.append((self.current_function, node.func.attr))
        self.generic_visit(node)

class SignalSlotAnalyzer(ast.NodeVisitor):
    """Qt信号槽分析器"""
    def __init__(self):
        self.signals = {}  # {class_name: [signal_name]}
        self.slots = {}    # {class_name: [slot_name]}
        self.connections = []  # [(source, signal, target, slot)]
        self.current_class = None
        
    def visit_ClassDef(self, node):
        """访问类定义"""
        old_class = self.current_class
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = old_class
        
    def visit_Assign(self, node):
        """访问变量赋值，查找信号定义"""
        if self.current_class:
            for target in node.targets:
                if isinstance(target, ast.Name):
                    if isinstance(node.value, ast.Call):
                        if isinstance(node.value.func, ast.Name):
                            if node.value.func.id == 'pyqtSignal':
                                if self.current_class not in self.signals:
                                    self.signals[self.current_class] = []
                                self.signals[self.current_class].append(target.id)
        self.generic_visit(node)
        
    def visit_FunctionDef(self, node):
        """访问函数定义，查找槽函数"""
        if self.current_class:
            for decorator in node.decorator_list:
                if isinstance(decorator, ast.Name) and decorator.id == 'pyqtSlot':
                    if self.current_class not in self.slots:
                        self.slots[self.current_class] = []
                    self.slots[self.current_class].append(node.name)
        self.generic_visit(node)

def main():
    """主函数"""
    print("开始分析代码...\n")
    
    # 初始化分析器
    analyzer = CodeAnalyzer(project_root)
    
    # 分析核心组件
    core_components = {
        'AudioProcessor': str(project_root / 'src' / 'core' / 'audio' / 'audio_processor.py'),
        'FileTranscriber': str(project_root / 'src' / 'core' / 'audio' / 'file_transcriber.py'),
        'SubtitleWidget': str(project_root / 'src' / 'ui' / 'widgets' / 'subtitle_widget.py'),
        'PluginManager': str(project_root / 'src' / 'core' / 'plugins' / 'base' / 'plugin_manager.py')
    }
    
    for component, file_path in core_components.items():
        print(f"\n分析组件: {component}")
        if os.path.exists(file_path):
            calls = analyzer.analyze_file(file_path)
            print(f"找到 {len(calls)} 个调用关系:")
            for caller, callee in calls:
                print(f"  {caller} -> {callee}")
        else:
            print(f"文件不存在: {file_path}")
    
    # 生成调用图
    analyzer.draw_call_graph('core_components_calls.png')
    print("\n核心组件调用图已保存到 core_components_calls.png")
    
    # 分析信号槽
    mainwindow_path = str(project_root / 'src' / 'ui' / 'main_window.py')
    if os.path.exists(mainwindow_path):
        print("\n分析 MainWindow 信号槽...")
        with open(mainwindow_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())
            
        signal_analyzer = SignalSlotAnalyzer()
        signal_analyzer.visit(tree)
        
        print("\n信号定义:")
        for class_name, signals in signal_analyzer.signals.items():
            print(f"{class_name}: {signals}")
            
        print("\n槽函数:")
        for class_name, slots in signal_analyzer.slots.items():
            print(f"{class_name}: {slots}")
            
        # 生成信号槽连接图
        signal_graph = nx.DiGraph()
        
        for class_name, signals in signal_analyzer.signals.items():
            for signal in signals:
                signal_graph.add_node(f"{class_name}.{signal}", node_type="signal")
                
        for class_name, slots in signal_analyzer.slots.items():
            for slot in slots:
                signal_graph.add_node(f"{class_name}.{slot}", node_type="slot")
                
        # 根据命名约定添加可能的连接
        for src_class, signals in signal_analyzer.signals.items():
            for signal in signals:
                for dst_class, slots in signal_analyzer.slots.items():
                    for slot in slots:
                        if signal.replace('signal', '') in slot.lower():
                            signal_graph.add_edge(f"{src_class}.{signal}", 
                                               f"{dst_class}.{slot}")
        
        plt.figure(figsize=(15, 10))
        pos = nx.spring_layout(signal_graph)
        nx.draw(signal_graph, pos, with_labels=True,
                node_color=['lightblue' if attr['node_type']=='signal' else 'lightgreen'
                           for _, attr in signal_graph.nodes(data=True)],
                node_size=2000, font_size=8)
        plt.savefig('signal_slot_connections.png')
        plt.close()
        
        print("\n信号槽连接图已保存到 signal_slot_connections.png")
    else:
        print(f"\n主窗口文件不存在: {mainwindow_path}")

if __name__ == "__main__":
    main()
