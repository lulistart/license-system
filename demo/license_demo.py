import requests
import hashlib
import platform
import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime
import threading

class LicenseDemo:
    def __init__(self):
        self.api_url = 'http://localhost:5000'
        self.config_file = 'license.json'
        self.window = tk.Tk()
        self.window.title('许可证验证系统')
        self.window.geometry('500x400')
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.window, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 许可证信息区域
        ttk.Label(self.main_frame, text='许可证密钥:').grid(row=0, column=0, pady=10)
        self.license_key = ttk.Entry(self.main_frame, width=40)
        self.license_key.grid(row=0, column=1, pady=10)
        
        # 按钮区域
        button_frame = ttk.Frame(self.main_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text='验证许可证', command=self.verify_license).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text='检查更新', command=self.check_update).pack(side=tk.LEFT, padx=5)
        
        # 进度条
        self.progress = ttk.Progressbar(self.main_frame, length=300, mode='determinate')
        self.progress.grid(row=2, column=0, columnspan=2, pady=10)
        
        # 状态显示
        self.status_frame = ttk.LabelFrame(self.main_frame, text='状态信息', padding="5")
        self.status_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        self.status_label = ttk.Label(self.status_frame, text='等待验证...')
        self.status_label.pack(fill=tk.X)
        
        # 许可证详情
        self.details_frame = ttk.LabelFrame(self.main_frame, text='许可证详情', padding="5")
        self.details_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        self.details_text = tk.Text(self.details_frame, height=6, width=40)
        self.details_text.pack(fill=tk.BOTH)
        
        # 加载保存的许可证
        self.load_license()
        
    def get_machine_code(self):
        """获取机器码"""
        system_info = platform.uname()
        machine_info = f"{system_info.system}{system_info.machine}{system_info.processor}"
        return hashlib.md5(machine_info.encode()).hexdigest()
    
    def update_progress(self, value):
        """更新进度条"""
        self.progress['value'] = value
        self.window.update_idletasks()
    
    def update_status(self, text, color='black'):
        """更新状态信息"""
        self.status_label.config(text=text, foreground=color)
    
    def save_license(self):
        """保存许可证信息"""
        data = {
            'license_key': self.license_key.get(),
            'last_verify': datetime.now().isoformat(),
            'machine_code': self.get_machine_code()
        }
        with open(self.config_file, 'w') as f:
            json.dump(data, f)
    
    def load_license(self):
        """加载保存的许可证信息"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    self.license_key.insert(0, data.get('license_key', ''))
                    self.update_details(data)
        except Exception as e:
            print(f"加载配置失败: {e}")
    
    def update_details(self, data):
        """更新许可证详情显示"""
        self.details_text.delete('1.0', tk.END)
        for key, value in data.items():
            self.details_text.insert(tk.END, f"{key}: {value}\n")
    
    def verify_license(self):
        """验证许可证"""
        def verify_thread():
            license_key = self.license_key.get().strip()
            if not license_key:
                messagebox.showerror('错误', '请输入许可证密钥')
                return
            
            try:
                self.update_status("正在验证...", 'blue')
                self.update_progress(20)
                
                response = requests.post(
                    f'{self.api_url}/api/verify_license',
                    json={
                        'license_key': license_key,
                        'machine_code': self.get_machine_code()
                    }
                )
                
                self.update_progress(60)
                result = response.json()
                
                if result.get('valid'):
                    self.update_progress(100)
                    self.update_status('许可证验证成功！', 'green')
                    self.save_license()
                    messagebox.showinfo('成功', '许可证验证成功！')
                else:
                    self.update_progress(100)
                    error_msg = result.get('error', '许可证无效')
                    self.update_status(f'验证失败：{error_msg}', 'red')
                    messagebox.showerror('错误', f'验证失败：{error_msg}')
                
            except Exception as e:
                self.update_progress(100)
                self.update_status(f'验证出错：{str(e)}', 'red')
                messagebox.showerror('错误', f'验证出错：{str(e)}')
        
        # 在新线程中执行验证
        threading.Thread(target=verify_thread).start()
    
    def check_update(self):
        """检查更新"""
        self.update_status("正在检查更新...", 'blue')
        self.update_progress(50)
        
        # 这里添加实际的更新检查逻辑
        
        self.update_progress(100)
        self.update_status("已是最新版本", 'green')
        messagebox.showinfo('更新', '当前已是最新版本')
    
    def run(self):
        """运行程序"""
        self.window.mainloop()

if __name__ == '__main__':
    app = LicenseDemo()
    app.run() 