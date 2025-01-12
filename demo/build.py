import PyInstaller.__main__
import os

def build():
    """打包程序"""
    # 确保在正确的目录
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # GUI版本
    PyInstaller.__main__.run([
        'license_demo.py',
        '--onefile',
        '--windowed',
        '--name=LicenseVerifier',
        '--add-data=version.json;.',
        '--noconsole'
    ])
    
    # 命令行版本
    PyInstaller.__main__.run([
        'cli_demo.py',
        '--onefile',
        '--name=license-cli',
        '--add-data=version.json;.'
    ])

if __name__ == '__main__':
    # 安装依赖
    os.system('pip install -r requirements.txt')
    build() 