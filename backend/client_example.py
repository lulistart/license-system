import requests
import platform
import hashlib

def get_machine_code():
    """获取机器码"""
    system_info = platform.uname()
    machine_info = f"{system_info.system}{system_info.machine}{system_info.processor}"
    return hashlib.md5(machine_info.encode()).hexdigest()

def verify_license(license_key):
    """验证许可证"""
    machine_code = get_machine_code()
    response = requests.post(
        'http://localhost:5000/api/verify_license',
        json={
            'license_key': license_key,
            'machine_code': machine_code
        }
    )
    return response.json()

if __name__ == '__main__':
    # 测试许可证验证
    license_key = "your-license-key"  # 替换为实际的许可证密钥
    result = verify_license(license_key)
    
    if result.get('valid'):
        print("许可证验证成功！")
    else:
        print(f"许可证验证失败：{result.get('error', '未知错误')}") 