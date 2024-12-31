import sys
from pathlib import Path

# Platform-specific considerations
platform = sys.platform
if platform == 'win32':
    deploy_lib_path = Path(sys.executable).parent / 'Lib' / 'site-packages' / 'PySide6' / 'scripts' / 'deploy_lib' / 'dependency_util.py'
else:
    deploy_lib_path = Path(sys.executable).parent / 'lib' / f'python{sys.version_info.major}.{sys.version_info.minor}' / 'site-packages' / 'PySide6' / 'scripts' / 'deploy_lib' / 'dependency_util.py'

# Apply the patch
if deploy_lib_path.exists():
    content = deploy_lib_path.read_text()
    patched_content = content.replace(
        'if main_mod_name.startswith(\"PySide6\"):',
        'if main_mod_name and main_mod_name.startswith(\"PySide6\"):'
    )
    deploy_lib_path.write_text(patched_content)