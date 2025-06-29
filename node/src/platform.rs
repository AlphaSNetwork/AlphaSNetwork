//! 跨平台支持模块
//! 
//! 处理不同操作系统的特定配置和路径

use std::env;
use std::fs;
use std::path::PathBuf;
use std::io::Result as IoResult;

/// 获取平台信息
pub fn get_platform_info() -> String {
    format!("{}-{}", env::consts::OS, env::consts::ARCH)
}

/// 获取默认数据目录
pub fn get_default_data_dir() -> PathBuf {
    match env::consts::OS {
        "windows" => {
            // Windows: %APPDATA%\AlphaNode
            let appdata = env::var("APPDATA")
                .unwrap_or_else(|_| env::var("USERPROFILE").unwrap_or_else(|_| ".".to_string()));
            PathBuf::from(appdata).join("AlphaNode")
        },
        "macos" => {
            // macOS: ~/Library/Application Support/AlphaNode
            let home = env::var("HOME").unwrap_or_else(|_| ".".to_string());
            PathBuf::from(home).join("Library").join("Application Support").join("AlphaNode")
        },
        _ => {
            // Linux and others: ~/.local/share/alpha-node
            let home = env::var("HOME").unwrap_or_else(|_| ".".to_string());
            PathBuf::from(home).join(".local").join("share").join("alpha-node")
        }
    }
}

/// 获取默认配置文件路径
pub fn get_default_config_path() -> PathBuf {
    get_default_data_dir().join("config.toml")
}

/// 获取默认日志目录
pub fn get_default_log_dir() -> PathBuf {
    get_default_data_dir().join("logs")
}

/// 获取默认数据库目录
pub fn get_default_db_dir() -> PathBuf {
    get_default_data_dir().join("db")
}

/// 获取默认密钥存储目录
pub fn get_default_keystore_dir() -> PathBuf {
    get_default_data_dir().join("keystore")
}

/// 确保数据目录存在
pub fn ensure_data_directory() -> IoResult<()> {
    let data_dir = get_default_data_dir();
    let log_dir = get_default_log_dir();
    let db_dir = get_default_db_dir();
    let keystore_dir = get_default_keystore_dir();
    
    fs::create_dir_all(&data_dir)?;
    fs::create_dir_all(&log_dir)?;
    fs::create_dir_all(&db_dir)?;
    fs::create_dir_all(&keystore_dir)?;
    
    println!("📁 Data directory: {}", data_dir.display());
    println!("📁 Log directory: {}", log_dir.display());
    println!("📁 Database directory: {}", db_dir.display());
    println!("📁 Keystore directory: {}", keystore_dir.display());
    
    Ok(())
}

/// 获取系统资源信息
pub fn get_system_info() -> SystemInfo {
    SystemInfo {
        os: env::consts::OS.to_string(),
        arch: env::consts::ARCH.to_string(),
        cpu_count: num_cpus::get(),
        available_memory: get_available_memory(),
        available_disk_space: get_available_disk_space(),
    }
}

/// 系统信息结构体
#[derive(Debug, Clone)]
pub struct SystemInfo {
    pub os: String,
    pub arch: String,
    pub cpu_count: usize,
    pub available_memory: u64, // MB
    pub available_disk_space: u64, // MB
}

/// 获取可用内存（MB）
fn get_available_memory() -> u64 {
    #[cfg(target_os = "linux")]
    {
        use std::fs::File;
        use std::io::{BufRead, BufReader};
        
        if let Ok(file) = File::open("/proc/meminfo") {
            let reader = BufReader::new(file);
            for line in reader.lines() {
                if let Ok(line) = line {
                    if line.starts_with("MemAvailable:") {
                        let parts: Vec<&str> = line.split_whitespace().collect();
                        if parts.len() >= 2 {
                            if let Ok(kb) = parts[1].parse::<u64>() {
                                return kb / 1024; // Convert KB to MB
                            }
                        }
                    }
                }
            }
        }
    }
    
    #[cfg(target_os = "macos")]
    {
        use std::process::Command;
        
        if let Ok(output) = Command::new("sysctl")
            .args(&["-n", "hw.memsize"])
            .output() 
        {
            if let Ok(mem_str) = String::from_utf8(output.stdout) {
                if let Ok(bytes) = mem_str.trim().parse::<u64>() {
                    return bytes / 1024 / 1024; // Convert bytes to MB
                }
            }
        }
    }
    
    #[cfg(target_os = "windows")]
    {
        // Windows memory detection would require additional dependencies
        // For now, return a default value
        return 8192; // 8GB default
    }
    
    4096 // 4GB default fallback
}

/// 获取可用磁盘空间（MB）
fn get_available_disk_space() -> u64 {
    use std::fs;
    
    let data_dir = get_default_data_dir();
    
    // Try to get disk space for the data directory
    if let Ok(metadata) = fs::metadata(&data_dir.parent().unwrap_or(&data_dir)) {
        // This is a simplified approach
        // In a real implementation, you'd use platform-specific APIs
        return 50000; // 50GB default
    }
    
    50000 // 50GB default fallback
}

/// 检查系统是否满足运行要求
pub fn check_system_requirements(node_type: &str) -> Result<(), String> {
    let system_info = get_system_info();
    
    println!("🔍 System Information:");
    println!("   OS: {} ({})", system_info.os, system_info.arch);
    println!("   CPU Cores: {}", system_info.cpu_count);
    println!("   Available Memory: {} MB", system_info.available_memory);
    println!("   Available Disk Space: {} MB", system_info.available_disk_space);
    
    match node_type {
        "validator" => {
            if system_info.cpu_count < 4 {
                return Err("Validator node requires at least 4 CPU cores".to_string());
            }
            if system_info.available_memory < 8192 {
                return Err("Validator node requires at least 8GB RAM".to_string());
            }
            if system_info.available_disk_space < 100000 {
                return Err("Validator node requires at least 100GB disk space".to_string());
            }
        },
        "full" => {
            if system_info.cpu_count < 2 {
                return Err("Full node requires at least 2 CPU cores".to_string());
            }
            if system_info.available_memory < 4096 {
                return Err("Full node requires at least 4GB RAM".to_string());
            }
            if system_info.available_disk_space < 50000 {
                return Err("Full node requires at least 50GB disk space".to_string());
            }
        },
        "light" => {
            if system_info.available_memory < 1024 {
                return Err("Light node requires at least 1GB RAM".to_string());
            }
            if system_info.available_disk_space < 1000 {
                return Err("Light node requires at least 1GB disk space".to_string());
            }
        },
        _ => {}
    }
    
    println!("✅ System requirements check passed for {} node", node_type);
    Ok(())
}

