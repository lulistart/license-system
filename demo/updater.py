import requests
import os
import sys
import hashlib
import json
from datetime import datetime

class Updater:
    def __init__(self):
        self.version_file = 'version.json'
        self.current_version = '1.0.0'
        self.update_url = 'http://localhost:5000/api/check_update'
    
    def get_file_hash(self, filename):
        """获取文件的MD5哈希值"""
        if not os.path.exists(filename):
            return None
        
        with open(filename, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    
    def check_update(self):
        """检查更新"""
        try:
            response = requests.get(self.update_url)
            update_info = response.json()
            
            if update_info['version'] > self.current_version:
                return True, update_info
            return False, None
        except Exception as e:
            print(f"检查更新失败: {e}")
            return False, None
    
    def download_update(self, update_info):
        """下载更新"""
        try:
            response = requests.get(update_info['download_url'])
            with open('temp_update.exe', 'wb') as f:
                f.write(response.content)
            
            # 验证下载文件的完整性
            if self.get_file_hash('temp_update.exe') == update_info['file_hash']:
                return True
            return False
        except Exception as e:
            print(f"下载更新失败: {e}")
            return False
    
    def apply_update(self):
        """应用更新"""
        if os.path.exists('temp_update.exe'):
            try:
                # 备份当前文件
                os.rename(sys.argv[0], f"{sys.argv[0]}.bak")
                # 替换为新文件
                os.rename('temp_update.exe', sys.argv[0])
                return True
            except Exception as e:
                print(f"应用更新失败: {e}")
                # 恢复备份
                if os.path.exists(f"{sys.argv[0]}.bak"):
                    os.rename(f"{sys.argv[0]}.bak", sys.argv[0])
        return False 