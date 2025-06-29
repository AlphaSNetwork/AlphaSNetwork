#!/usr/bin/env python3
"""
Alpha Blockchain Node Manager
跨平台节点管理工具，提供图形化界面管理Alpha区块链节点
"""

import os
import sys
import json
import subprocess
import threading
import time
import platform
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import webbrowser

class AlphaNodeManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Alpha Blockchain Node Manager")
        self.root.geometry("800x600")
        
        # 获取平台信息
        self.platform = platform.system().lower()
        self.setup_paths()
        
        # 节点进程
        self.node_process = None
        self.node_running = False
        
        # 创建界面
        self.create_widgets()
        
        # 启动状态检查
        self.check_node_status()
    
    def setup_paths(self):
        """设置平台相关的路径"""
        if self.platform == "windows":
            self.data_dir = Path(os.environ.get("LOCALAPPDATA", "")) / "AlphaNode"
            self.binary_name = "alpha-node.exe"
        elif self.platform == "darwin":  # macOS
            self.data_dir = Path.home() / "Library" / "Application Support" / "AlphaNode"
            self.binary_name = "alpha-node"
        else:  # Linux
            self.data_dir = Path.home() / ".local" / "share" / "alpha-node"
            self.binary_name = "alpha-node"
        
        # 创建数据目录
        self.data_dir.mkdir(parents=True, exist_ok=True)
        (self.data_dir / "logs").mkdir(exist_ok=True)
        (self.data_dir / "db").mkdir(exist_ok=True)
        (self.data_dir / "keystore").mkdir(exist_ok=True)
        
        # 查找二进制文件
        self.binary_path = self.find_binary()
    
    def find_binary(self):
        """查找Alpha节点二进制文件"""
        # 可能的路径
        possible_paths = [
            Path("/usr/local/bin") / self.binary_name,
            Path.home() / ".local" / "bin" / self.binary_name,
            Path("./target/release") / self.binary_name,
            Path(".") / self.binary_name,
        ]
        
        if self.platform == "windows":
            possible_paths.extend([
                Path(os.environ.get("LOCALAPPDATA", "")) / "AlphaNode" / self.binary_name,
                Path(os.environ.get("PROGRAMFILES", "")) / "AlphaNode" / self.binary_name,
            ])
        
        for path in possible_paths:
            if path.exists():
                return path
        
        return None
    
    def create_widgets(self):
        """创建界面组件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text="Alpha Blockchain Node Manager", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 节点状态
        status_frame = ttk.LabelFrame(main_frame, text="Node Status", padding="10")
        status_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        status_frame.columnconfigure(1, weight=1)
        
        ttk.Label(status_frame, text="Status:").grid(row=0, column=0, sticky=tk.W)
        self.status_label = ttk.Label(status_frame, text="Stopped", foreground="red")
        self.status_label.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        ttk.Label(status_frame, text="Binary:").grid(row=1, column=0, sticky=tk.W)
        binary_text = str(self.binary_path) if self.binary_path else "Not found"
        self.binary_label = ttk.Label(status_frame, text=binary_text)
        self.binary_label.grid(row=1, column=1, sticky=tk.W, padx=(10, 0))
        
        ttk.Label(status_frame, text="Data Dir:").grid(row=2, column=0, sticky=tk.W)
        self.data_dir_label = ttk.Label(status_frame, text=str(self.data_dir))
        self.data_dir_label.grid(row=2, column=1, sticky=tk.W, padx=(10, 0))
        
        # 节点配置
        config_frame = ttk.LabelFrame(main_frame, text="Node Configuration", padding="10")
        config_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        config_frame.columnconfigure(1, weight=1)
        
        ttk.Label(config_frame, text="Node Type:").grid(row=0, column=0, sticky=tk.W)
        self.node_type = tk.StringVar(value="full")
        node_type_combo = ttk.Combobox(config_frame, textvariable=self.node_type,
                                      values=["light", "full", "validator"], state="readonly")
        node_type_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0))
        
        ttk.Label(config_frame, text="Node Name:").grid(row=1, column=0, sticky=tk.W)
        self.node_name = tk.StringVar(value=f"AlphaNode-{platform.node()}")
        node_name_entry = ttk.Entry(config_frame, textvariable=self.node_name)
        node_name_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0))
        
        ttk.Label(config_frame, text="Chain:").grid(row=2, column=0, sticky=tk.W)
        self.chain = tk.StringVar(value="local")
        chain_combo = ttk.Combobox(config_frame, textvariable=self.chain,
                                  values=["local", "dev", "testnet"], state="readonly")
        chain_combo.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(10, 0))
        
        # 控制按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=(0, 10))
        
        self.start_button = ttk.Button(button_frame, text="Start Node", 
                                      command=self.start_node)
        self.start_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.stop_button = ttk.Button(button_frame, text="Stop Node", 
                                     command=self.stop_node, state="disabled")
        self.stop_button.pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(button_frame, text="Generate Keys", 
                  command=self.generate_keys).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(button_frame, text="Open Data Dir", 
                  command=self.open_data_dir).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(button_frame, text="View Logs", 
                  command=self.view_logs).pack(side=tk.LEFT, padx=(0, 5))
        
        # 日志输出
        log_frame = ttk.LabelFrame(main_frame, text="Node Output", padding="10")
        log_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, state="disabled")
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 状态栏
        self.status_bar = ttk.Label(main_frame, text="Ready", relief=tk.SUNKEN)
        self.status_bar.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def log_message(self, message):
        """添加日志消息"""
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, f"{time.strftime('%H:%M:%S')} - {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")
    
    def update_status(self, status, color="black"):
        """更新状态显示"""
        self.status_label.config(text=status, foreground=color)
        self.status_bar.config(text=status)
    
    def start_node(self):
        """启动节点"""
        if not self.binary_path or not self.binary_path.exists():
            messagebox.showerror("Error", "Alpha node binary not found!")
            return
        
        if self.node_running:
            messagebox.showwarning("Warning", "Node is already running!")
            return
        
        # 构建命令
        cmd = [
            str(self.binary_path),
            "--chain", self.chain.get(),
            "--base-path", str(self.data_dir),
            "--name", self.node_name.get(),
            "--rpc-port", "9933",
            "--ws-port", "9944",
            "--rpc-cors", "all"
        ]
        
        if self.node_type.get() == "light":
            cmd.append("--light")
        elif self.node_type.get() == "validator":
            cmd.append("--validator")
        
        # 启动节点进程
        try:
            self.log_message(f"Starting node with command: {' '.join(cmd)}")
            self.node_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            self.node_running = True
            self.update_status("Starting...", "orange")
            self.start_button.config(state="disabled")
            self.stop_button.config(state="normal")
            
            # 启动输出读取线程
            threading.Thread(target=self.read_node_output, daemon=True).start()
            
        except Exception as e:
            self.log_message(f"Failed to start node: {e}")
            messagebox.showerror("Error", f"Failed to start node: {e}")
    
    def stop_node(self):
        """停止节点"""
        if self.node_process and self.node_running:
            self.log_message("Stopping node...")
            self.node_process.terminate()
            
            # 等待进程结束
            try:
                self.node_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.log_message("Force killing node...")
                self.node_process.kill()
            
            self.node_running = False
            self.update_status("Stopped", "red")
            self.start_button.config(state="normal")
            self.stop_button.config(state="disabled")
            self.log_message("Node stopped")
    
    def read_node_output(self):
        """读取节点输出"""
        try:
            for line in iter(self.node_process.stdout.readline, ''):
                if not self.node_running:
                    break
                
                line = line.strip()
                if line:
                    self.root.after(0, self.log_message, line)
                    
                    # 检查特定状态
                    if "Idle" in line or "Imported" in line:
                        self.root.after(0, self.update_status, "Running", "green")
                    elif "Error" in line or "Failed" in line:
                        self.root.after(0, self.update_status, "Error", "red")
            
        except Exception as e:
            self.root.after(0, self.log_message, f"Output reading error: {e}")
        
        # 进程结束
        if self.node_running:
            self.node_running = False
            self.root.after(0, self.update_status, "Stopped", "red")
            self.root.after(0, lambda: self.start_button.config(state="normal"))
            self.root.after(0, lambda: self.stop_button.config(state="disabled"))
    
    def generate_keys(self):
        """生成验证者密钥"""
        if not self.binary_path or not self.binary_path.exists():
            messagebox.showerror("Error", "Alpha node binary not found!")
            return
        
        try:
            cmd = [str(self.binary_path), "key", "generate"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                messagebox.showinfo("Keys Generated", f"Keys generated successfully:\n\n{result.stdout}")
                self.log_message("Validator keys generated")
            else:
                messagebox.showerror("Error", f"Failed to generate keys:\n{result.stderr}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate keys: {e}")
    
    def open_data_dir(self):
        """打开数据目录"""
        try:
            if self.platform == "windows":
                os.startfile(self.data_dir)
            elif self.platform == "darwin":
                subprocess.run(["open", str(self.data_dir)])
            else:
                subprocess.run(["xdg-open", str(self.data_dir)])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open data directory: {e}")
    
    def view_logs(self):
        """查看日志文件"""
        log_file = self.data_dir / "logs" / "alpha-node.log"
        if log_file.exists():
            try:
                if self.platform == "windows":
                    os.startfile(log_file)
                elif self.platform == "darwin":
                    subprocess.run(["open", str(log_file)])
                else:
                    subprocess.run(["xdg-open", str(log_file)])
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open log file: {e}")
        else:
            messagebox.showinfo("Info", "No log file found")
    
    def check_node_status(self):
        """定期检查节点状态"""
        # 这里可以添加更复杂的状态检查逻辑
        # 比如检查RPC端口是否可用等
        
        # 每5秒检查一次
        self.root.after(5000, self.check_node_status)
    
    def on_closing(self):
        """窗口关闭事件"""
        if self.node_running:
            if messagebox.askokcancel("Quit", "Node is still running. Stop it and quit?"):
                self.stop_node()
                self.root.destroy()
        else:
            self.root.destroy()
    
    def run(self):
        """运行应用"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

def main():
    """主函数"""
    try:
        app = AlphaNodeManager()
        app.run()
    except Exception as e:
        print(f"Failed to start Alpha Node Manager: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

