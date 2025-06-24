"""测试配置文件
根据测试路径自动选择加载原有代码或新代码的组件
"""
import os
import sys
import pytest
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

def is_src_update_test(request):
    """检查是否是新代码的测试"""
    if request and request.module and request.module.__file__:
        test_path = Path(request.module.__file__)
        return "src_update" in str(test_path) or "unit/core" in str(test_path)
    return False

# 根据测试路径导入相应的组件
def import_components(request):
    if is_src_update_test(request):
        # 新代码的测试，不需要导入旧组件
        return None, None, None
    else:
        # 原有代码的测试，导入所需的组件
        from src.utils.config_manager import config_manager
        from src.core.asr.model_manager import ASRModelManager
        from src.core.translation import TranslationManager
        return config_manager, ASRModelManager, TranslationManager

@pytest.fixture
def config_manager(request):
    """配置管理器实例"""
    old_config_manager, _, _ = import_components(request)
    if old_config_manager:
        return old_config_manager
    # 新代码的测试会使用自己的 ConfigManager
    return None

@pytest.fixture
def model_manager(request):
    """ASR模型管理器实例"""
    _, ASRModelManager, _ = import_components(request)
    if ASRModelManager:
        return ASRModelManager()
    # 新代码的测试会使用自己的模型管理器
    return None

@pytest.fixture
def translation_manager(request):
    """创建翻译管理器实例"""
    _, _, TranslationManager = import_components(request)
    if TranslationManager:
        # 使用测试专用的模型目录
        config = {
            'opus_mt': {
                'model_dir': os.path.join('tests', 'models', 'translation', 'opus-mt', 'en-zh')
            },
            'argos': {
                'model_dir': os.path.join('tests', 'models', 'translation', 'argos')
            }
        }
        return TranslationManager(config)
    # 新代码的测试会使用自己的翻译管理器
    return None

@pytest.fixture
def test_text():
    """测试用的文本"""
    return "Hello, how are you?"

@pytest.fixture
def test_audio_path(tmp_path):
    """创建测试音频文件路径"""
    return tmp_path / "test.wav"

@pytest.fixture
def test_model_path(tmp_path):
    """创建测试模型目录路径"""
    model_dir = tmp_path / "models" / "asr" / "test_model"
    model_dir.mkdir(parents=True)
    return model_dir

@pytest.fixture
def test_data_dir():
    """测试数据目录"""
    data_dir = Path(__file__).parent / "data"
    data_dir.mkdir(exist_ok=True)
    return data_dir