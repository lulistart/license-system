import requests
import platform
import hashlib
import json
import os
from datetime import datetime
from typing import Tuple, Optional, Dict

class LicenseVerifier:
    """许可证验证类"""
    
    def __init__(self, server_url: str = 'http://localhost:5000', config_path: str = None):
        """
        初始化许可证验证器
        
        Args:
            server_url: 验证服务器地址
            config_path: 配置文件保存路径，默认为当前目录
        """
        self.server_url = server_url.rstrip('/')
        self.config_path = config_path or os.path.join(os.path.expanduser('~'), '.license')
        self.config_file = os.path.join(self.config_path, 'license.json')
        
        # 确保配置目录存在
        os.makedirs(self.config_path, exist_ok=True)
        
    def get_machine_code(self) -> str:
        """
        获取机器唯一标识码
        
        Returns:
            str: 机器码的MD5哈希值
        """
        system_info = platform.uname()
        machine_info = f"{system_info.system}{system_info.machine}{system_info.processor}"
        return hashlib.md5(machine_info.encode()).hexdigest()
        
    def verify_license(self, license_key: str) -> Tuple[bool, Optional[str]]:
        """验证许可证"""
        try:
            machine_code = self.get_machine_code()
            
            response = requests.post(
                f'{self.server_url}/api/verify_license',
                json={
                    'license_key': license_key,
                    'machine_code': machine_code
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('valid'):
                    self.save_license_info(license_key)
                return result.get('valid'), result.get('error')
            else:
                return False, f"服务器错误: {response.status_code}"
            
        except requests.RequestException as e:
            return False, f"网络错误: {str(e)}"
        except Exception as e:
            return False, f"验证失败: {str(e)}"
            
    def save_license_info(self, license_key: str) -> None:
        """
        保存许可证信息到本地
        
        Args:
            license_key: 许可证密钥
        """
        data = {
            'license_key': license_key,
            'machine_code': self.get_machine_code(),
            'last_verify': datetime.now().isoformat(),
            'server_url': self.server_url
        }
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"保存许可证信息失败: {e}")
            
    def load_license_info(self) -> Optional[Dict]:
        """
        加载本地许可证信息
        
        Returns:
            Optional[Dict]: 许可证信息字典，如果不存在则返回 None
        """
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"加载许可证信息失败: {e}")
        return None
        
    def clear_license(self) -> None:
        """清除本地保存的许可证信息"""
        try:
            if os.path.exists(self.config_file):
                os.remove(self.config_file)
        except Exception as e:
            print(f"清除许可证信息失败: {e}") 