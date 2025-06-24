import os
import sys
import pytest

# 添加项目根目录到 PYTHONPATH
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, project_root)

# 打印当前的 Python 路径
print("Python path:")
for path in sys.path:
    print(f"  {path}")

# 运行测试
pytest.main(["-v", "test_config.py"])
