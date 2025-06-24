"""
Vosk-API 项目代码调用关系分析脚本
"""
import os
import sys
import ast
import logging
from datetime import datetime
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# 设置调试输出
DEBUG = True
def debug_print(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs, flush=True)

debug_print(f"项目根目录: {project_root}")
debug_print(f"Python路径: {sys.path}")

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

class CodeAnalyzer:
    """代码分析器"""
    def __init__(self, root_dir):
        self.root_dir = Path(root_dir)
        self.call_graph = nx.DiGraph()
        
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
            
    def analyze_directory(self, dir_path=None):
        """分析目录下的所有Python文件"""
        if dir_path is None:
            dir_path = self.root_dir
            
        debug_print(f"\n分析目录: {dir_path}")
        for file_path in Path(dir_path).rglob('*.py'):
            if '__pycache__' not in str(file_path):
                self.analyze_file(file_path)
                
    def draw_call_graph(self, output_file='call_graph.png'):
        """绘制调用关系图"""
        debug_print(f"\n生成调用图: {output_file}")
        plt.figure(figsize=(15, 10))
        pos = nx.spring_layout(self.call_graph)
        nx.draw(self.call_graph, pos, with_labels=True, 
                node_color='lightblue', node_size=2000, 
                font_size=8, font_weight='bold')
        plt.savefig(output_file)
        plt.close()
        debug_print(f"调用图已保存到: {output_file}")

def main():
    """主函数"""
    # 分析核心组件
    core_components = {
        'AudioProcessor': project_root / 'src' / 'core' / 'audio' / 'audio_processor.py',
        'FileTranscriber': project_root / 'src' / 'core' / 'audio' / 'file_transcriber.py',
        'SubtitleWidget': project_root / 'src' / 'ui' / 'widgets' / 'subtitle_widget.py',
        'PluginManager': project_root / 'src' / 'core' / 'plugins' / 'base' / 'plugin_manager.py'
    }

    analyzer = CodeAnalyzer(project_root)
    
    # 分析每个核心组件
    for component, file_path in core_components.items():
        debug_print(f"\n分析组件: {component}")
        if file_path.exists():
            calls = analyzer.analyze_file(file_path)
            debug_print(f"找到 {len(calls)} 个调用关系:")
            for caller, callee in calls:
                debug_print(f"  {caller} -> {callee}")
        else:
            debug_print(f"文件不存在: {file_path}")

    # 生成调用图
    analyzer.draw_call_graph('core_components_calls.png')
    debug_print("\n分析完成！调用图已保存到 core_components_calls.png")

if __name__ == "__main__":
    main()
