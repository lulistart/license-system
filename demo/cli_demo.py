import requests
import hashlib
import platform
import sys

def get_machine_code():
    """获取机器码"""
    system_info = platform.uname()
    machine_info = f"{system_info.system}{system_info.machine}{system_info.processor}"
    machine_code = hashlib.md5(machine_info.encode()).hexdigest()
    print(f"机器码: {machine_code}")
    return machine_code

def verify_license(license_key):
    """验证许可证"""
    try:
        machine_code = get_machine_code()
        print(f"正在验证许可证: {license_key}")
        
        url = 'http://localhost:5000/api/verify_license'
        data = {
            'license_key': license_key,
            'machine_code': machine_code
        }
        print(f"发送请求到: {url}")
        print(f"请求数据: {data}")
        
        response = requests.post(url, json=data)
        print(f"服务器响应状态码: {response.status_code}")
        
        result = response.json()
        print(f"服务器响应内容: {result}")
        
        if result.get('valid'):
            print('许可证验证成功！')
            return True
        else:
            print(f'验证失败：{result.get("error", "许可证无效")}')
            return False
            
    except Exception as e:
        print(f'验证出错：{str(e)}')
        print(f'错误类型：{type(e).__name__}')
        return False

def main():
    """主函数"""
    print("许可证验证工具")
    print("-" * 50)
    
    # 如果提供了命令行参数，使用参数中的许可证密钥
    if len(sys.argv) > 1:
        license_key = sys.argv[1]
    else:
        # 否则提示用户输入
        license_key = input("请输入许可证密钥: ").strip()
    
    if not license_key:
        print("错误：许可证密钥不能为空")
        return False
    
    print("\n开始验证...")
    return verify_license(license_key)

if __name__ == '__main__':
    try:
        success = main()
        if success:
            print("\n验证成功，程序正常退出")
            sys.exit(0)
        else:
            print("\n验证失败，程序异常退出")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n程序被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n程序出错：{str(e)}")
        sys.exit(1) 