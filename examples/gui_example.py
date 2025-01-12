import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from tkinter import messagebox, ttk
from license_sdk.license_verifier import LicenseVerifier
import threading
import time

class LoginFrame(ttk.Frame):
    """登录界面"""
    def __init__(self, master, on_verify_success):
        super().__init__(master, padding="20")
        self.master = master
        self.on_verify_success = on_verify_success
        self.verifier = LicenseVerifier()
        self.create_widgets()
        
    def create_widgets(self):
        # 许可证输入框
        ttk.Label(self, text="许可证密钥:").pack(pady=5)
        self.license_entry = ttk.Entry(self, width=40)
        self.license_entry.pack(pady=5)
        
        # 验证按钮
        ttk.Button(self, text="验证许可证", command=self.verify_license).pack(pady=10)
        
        # 状态标签
        self.status_label = ttk.Label(self, text="")
        self.status_label.pack(pady=5)
        
        # 尝试加载已保存的许可证
        saved_info = self.verifier.load_license_info()
        if saved_info:
            self.license_entry.insert(0, saved_info['license_key'])
            self.verify_license()
            
    def verify_license(self):
        license_key = self.license_entry.get().strip()
        if not license_key:
            messagebox.showerror("错误", "请输入许可证密钥")
            return
            
        is_valid, error = self.verifier.verify_license(license_key)
        
        if is_valid:
            self.status_label.config(text="许可证有效", foreground="green")
            license_info = self.verifier.load_license_info()
            self.on_verify_success(license_info)
        else:
            self.status_label.config(text=f"验证失败: {error}", foreground="red")
            messagebox.showerror("错误", f"验证失败: {error}")

class MainPage(ttk.Frame):
    """主页面"""
    def __init__(self, master, license_info, on_logout):
        super().__init__(master, padding="20")
        self.master = master
        self.license_info = license_info
        self.on_logout = on_logout
        self.verifier = LicenseVerifier()
        self.is_running = True
        
        self.create_widgets()
        # 启动验证线程
        self.verify_thread = threading.Thread(target=self.auto_verify_loop, daemon=True)
        self.verify_thread.start()
        
    def create_widgets(self):
        # 欢迎信息
        welcome_frame = ttk.LabelFrame(self, text="许可证信息", padding="10")
        welcome_frame.pack(fill="x", padx=10, pady=5)
        
        # 显示许可证信息
        ttk.Label(welcome_frame, text=f"许可证密钥: {self.license_info['license_key']}").pack(anchor="w")
        ttk.Label(welcome_frame, text=f"机器码: {self.license_info['machine_code']}").pack(anchor="w")
        ttk.Label(welcome_frame, text=f"最后验证时间: {self.license_info['last_verify']}").pack(anchor="w")
        
        # 添加状态标签
        self.status_label = ttk.Label(welcome_frame, text="状态: 正常", foreground="green")
        self.status_label.pack(anchor="w")
        
        # 主程序内容区域
        content_frame = ttk.LabelFrame(self, text="主程序内容", padding="10")
        content_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        ttk.Label(content_frame, text="这里是您的主程序内容").pack()
        
        # 底部按钮
        button_frame = ttk.Frame(self)
        button_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(button_frame, text="刷新许可证", command=self.refresh_license).pack(side="left", padx=5)
        ttk.Button(button_frame, text="注销", command=self.logout).pack(side="right", padx=5)

    def auto_verify_loop(self):
        while self.is_running:
            try:
                is_valid, error = self.verifier.verify_license(self.license_info['license_key'])
                
                if is_valid:
                    self.after(0, lambda: self.status_label.config(
                        text="状态: 正常", 
                        foreground="green"
                    ))
                    self.license_info = self.verifier.load_license_info()
                else:
                    self.after(0, lambda: self.status_label.config(
                        text=f"状态: 验证失败 - {error}", 
                        foreground="red"
                    ))
                    self.after(0, lambda: self.handle_verification_failure(error))
                    break
                    
            except Exception as e:
                self.after(0, lambda: self.status_label.config(
                    text=f"状态: 验证错误 - {str(e)}", 
                    foreground="red"
                ))
            
            time.sleep(60)

    def handle_verification_failure(self, error):
        messagebox.showerror("许可证错误", f"许可证已失效: {error}\n请重新验证！")
        self.logout()
            
    def refresh_license(self):
        is_valid, error = self.verifier.verify_license(self.license_info['license_key'])
        
        if is_valid:
            messagebox.showinfo("成功", "许可证验证成功！")
            self.license_info = self.verifier.load_license_info()
            self.status_label.config(text="状态: 正常", foreground="green")
        else:
            messagebox.showerror("错误", f"许可证验证失败: {error}")
            self.logout()
            
    def logout(self):
        self.is_running = False
        self.verifier.clear_license()
        self.on_logout()

    def destroy(self):
        self.is_running = False
        super().destroy()

class LicenseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("许可证验证系统")
        self.root.geometry("500x400")
        
        self.current_frame = None
        self.show_login()
        
    def show_login(self):
        if self.current_frame:
            self.current_frame.destroy()
            
        self.current_frame = LoginFrame(self.root, self.on_verify_success)
        self.current_frame.pack(fill="both", expand=True)
        
    def show_main_page(self, license_info):
        if self.current_frame:
            self.current_frame.destroy()
            
        self.current_frame = MainPage(self.root, license_info, self.on_logout)
        self.current_frame.pack(fill="both", expand=True)
        
    def on_verify_success(self, license_info):
        self.show_main_page(license_info)
        
    def on_logout(self):
        self.show_login()

if __name__ == '__main__':
    root = tk.Tk()
    app = LicenseApp(root)
    root.mainloop()