import requests
import platform
import hashlib
import json
import os
from datetime import datetime

class LicenseClient:
    def __init__(self, server_url='http://localhost:5000'):
        self.server_url = server_url
        self.config_file = 'license.json'
        
    def get_machine_code(self):
        """获取机器码"""
        system_info = platform.uname()
        machine_info = f"{system_info.system}{system_info.machine}{system_info.processor}"
        return hashlib.md5(machine_info.encode()).hexdigest()
        
    def verify_license(self, license_key):
        """验证许可证"""
        try:
            machine_code = self.get_machine_code()
            
            response = requests.post(
                f'{self.server_url}/api/verify_license',
                json={
                    'license_key': license_key,
                    'machine_code': machine_code
                }
            )
            
            result = response.json()
            
            # 如果验证成功，保存许可证信息
            if result.get('valid'):
                self.save_license_info(license_key)
                
            return result.get('valid'), result.get('error')
            
        except Exception as e:
            return False, str(e)
            
    def save_license_info(self, license_key):
        """保存许可证信息到本地"""
        data = {
            'license_key': license_key,
            'machine_code': self.get_machine_code(),
            'last_verify': datetime.now().isoformat()
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(data, f)
            
    def load_license_info(self):
        """加载本地许可证信息"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return None

def main():
    client = LicenseClient()
    
    # 尝试加载已保存的许可证
    saved_info = client.load_license_info()
    if saved_info:
        print(f"发现已保存的许可证: {saved_info['license_key']}")
        license_key = saved_info['license_key']
    else:
        # 提示输入许可证
        license_key = input("请输入许可证密钥: ").strip()
    
    # 验证许可证
    print("\n正在验证许可证...")
    is_valid, error = client.verify_license(license_key)
    
    if is_valid:
        print("许可证验证成功！")
    else:
        print(f"验证失败：{error}")

if __name__ == '__main__':
    main() 