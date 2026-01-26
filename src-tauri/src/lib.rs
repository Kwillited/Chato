// Learn more about Tauri commands at https://tauri.app/develop/calling-rust/
use std::env;
use std::fs;
use std::path::Path;
use std::process::Command;
use std::time::SystemTime;
// 添加编码转换支持
use encoding::all::GBK;
use encoding::{DecoderTrap, Encoding};
// UUID生成
use uuid::Uuid;

#[tauri::command]
fn execute_command(command: &str) -> Result<String, String> {
    // 特殊处理cd命令
    if command.to_lowercase().starts_with("cd ") {
        let path = &command[3..].trim();
        return match env::set_current_dir(path) {
            Ok(_) => {
                // 返回新的当前目录
                match env::current_dir() {
                    Ok(current) => Ok(format!("当前目录为: {}", current.display())),
                    Err(e) => Err(format!("无法获取当前目录: {}", e)),
                }
            }
            Err(e) => Err(format!("无法切换到目录 '{}': {}", path, e)),
        };
    }
    // 特殊处理单独的cd命令（显示当前目录）
    else if command.trim().to_lowercase() == "cd" {
        return match env::current_dir() {
            Ok(current) => Ok(format!("当前目录为: {}", current.display())),
            Err(e) => Err(format!("无法获取当前目录: {}", e)),
        };
    }

    // 对于其他命令，使用cmd.exe执行
    let output = Command::new("cmd")
        .args(["/c", command])
        .output()
        .map_err(|e| format!("执行命令失败: {}", e))?;

    // 处理命令输出的编码问题（Windows命令行通常使用GBK编码）
    let decode_output = |bytes: &[u8]| -> String {
        if bytes.is_empty() {
            return String::new();
        }

        // 尝试以UTF-8解码
        if let Ok(utf8_str) = String::from_utf8(bytes.to_vec()) {
            return utf8_str;
        }

        // 如果UTF-8解码失败，尝试以GBK解码
        match GBK.decode(bytes, DecoderTrap::Replace) {
            Ok(gbk_str) => gbk_str,
            Err(_) => {
                // 如果GBK解码也失败，使用损失最小的方式解码
                String::from_utf8_lossy(bytes).to_string()
            }
        }
    };

    let stdout = decode_output(&output.stdout);
    let stderr = decode_output(&output.stderr);

    let mut result = String::new();
    if !stdout.is_empty() {
        result.push_str(&stdout);
    }
    if !stderr.is_empty() {
        if !result.is_empty() {
            result.push_str("\n");
        }
        result.push_str(&stderr);
    }

    // 如果命令执行失败，返回错误信息
    if !output.status.success() {
        return Err(format!("命令执行失败: {}", result));
    }

    Ok(result.trim().to_string())
}

#[tauri::command]
fn start_python_server() -> Result<String, String> {
    // 获取当前可执行文件所在目录
    let exe_path = env::current_exe().map_err(|e| format!("无法获取可执行文件路径: {}", e))?;
    let exe_dir = exe_path.parent().ok_or("无法获取可执行文件所在目录")?;

    // 尝试不同的Python脚本路径（main.py）
    let mut python_script_path = exe_dir.join("python").join("main.py");

    // 如果在当前目录找不到，尝试在其他可能的位置
    if !python_script_path.exists() {
        // 尝试在可执行文件同级目录的resources子目录中查找（Tauri打包后的资源位置）
        python_script_path = exe_dir.join("resources").join("python").join("main.py");
    }

    // 如果仍找不到，尝试在应用数据目录中查找
    if !python_script_path.exists() {
        python_script_path = exe_dir.join("data").join("python").join("main.py");
    }

    // 作为最后的备选，尝试原始开发路径（当前项目路径）
    if !python_script_path.exists() {
        let current_dir = env::current_dir().map_err(|e| format!("无法获取当前目录: {}", e))?;
        let absolute_path = current_dir.join("src-tauri").join("python").join("main.py");
        if absolute_path.exists() {
            python_script_path = absolute_path.to_path_buf();
        }
    }

    if !python_script_path.exists() {
        return Err(format!("找不到Python脚本: {:?}", python_script_path));
    }

    println!("使用Python脚本路径: {:?}", python_script_path);

    // 启动Python进程
    match start_python_process(&python_script_path) {
        Ok(pid) => Ok(format!("Python服务器启动成功，进程ID: {}", pid)),
        Err(e) => Err(format!("启动Python服务器失败: {}", e)),
    }
}

fn start_python_process(script_path: &Path) -> Result<String, String> {
    // 直接使用系统Python
    println!("使用系统Python");
    println!("使用系统Python启动脚本: {:?}", script_path);

    // 使用系统Python启动脚本
    let result = Command::new("python")
        .arg(script_path)
        .spawn()
        .map_err(|e| format!("无法启动Python脚本: {}", e))?;

    Ok(format!("Python服务器已启动，进程ID: {}", result.id()))
}

#[tauri::command]
fn check_ollama_service() -> Result<serde_json::Value, String> {
    // 首先检查Ollama是否安装
    let ollama_check_output = Command::new("cmd")
        .args(["/c", "where", "ollama"])
        .output()
        .map_err(|e| format!("检查Ollama安装状态失败: {}", e))?;

    // 检查Ollama是否安装
    if !ollama_check_output.status.success() {
        // Ollama未安装
        return Ok(serde_json::json!({
            "installed": false,
            "running": false,
            "message": "Ollama未安装"
        }));
    }

    // 检查Ollama服务是否正在运行
    let service_check_output = Command::new("cmd")
        .args(["/c", "curl", "-s", "http://localhost:11434/api/version"])
        .output()
        .map_err(|e| format!("检查Ollama服务状态失败: {}", e))?;

    // 如果命令执行成功且有输出，说明服务正在运行
    if service_check_output.status.success() && !service_check_output.stdout.is_empty() {
        Ok(serde_json::json!({
            "installed": true,
            "running": true,
            "message": "Ollama服务正在运行"
        }))
    } else {
        Ok(serde_json::json!({
            "installed": true,
            "running": false,
            "message": "Ollama已安装但服务未运行"
        }))
    }
}

#[tauri::command]
fn start_ollama_service() -> Result<String, String> {
    // 先检查Ollama是否安装
    let ollama_check_output = Command::new("cmd")
        .args(["/c", "where", "ollama"])
        .output()
        .map_err(|e| format!("检查Ollama安装状态失败: {}", e))?;

    if !ollama_check_output.status.success() {
        return Err("Ollama未安装，无法启动服务".to_string());
    }

    // 启动Ollama服务
    // 使用更可靠的方式在后台启动，不显示窗口
    #[cfg(windows)]
    let result = {
        use std::os::windows::process::CommandExt;
        Command::new("ollama")
            .arg("serve")
            .creation_flags(0x08000000) // CREATE_NO_WINDOW
            .spawn()
            .map_err(|e| format!("启动Ollama服务失败: {}", e))?
    };

    #[cfg(not(windows))]
    let result = {
        // 在非Windows系统上，使用标准的spawn方式
        Command::new("ollama")
            .arg("serve")
            .spawn()
            .map_err(|e| format!("启动Ollama服务失败: {}", e))?
    };

    Ok(format!("Ollama服务已启动，进程ID: {}", result.id()))
}

#[tauri::command]
fn create_knowledge_base(name: &str) -> Result<serde_json::Value, String> {
    // 验证输入
    let name = name.trim();
    if name.is_empty() {
        return Err("知识库名称不能为空".to_string());
    }

    // 获取当前可执行文件所在目录
    let exe_path = env::current_exe().map_err(|e| format!("无法获取可执行文件路径: {}", e))?;
    let exe_dir = exe_path.parent().ok_or("无法获取可执行文件所在目录")?;

    // 确定知识库存储路径
    let rag_files_path = exe_dir.join("resources").join("python").join("userData").join("rag").join("ragFiles");
    
    // 确保父目录存在
    fs::create_dir_all(&rag_files_path).map_err(|e| format!("无法创建父目录: {}", e))?;

    // 生成8位UUID
    let uuid = Uuid::new_v4().to_string().replace("-", "").chars().take(8).collect::<String>();
    
    // 构建完整的文件夹路径
    let folder_path = rag_files_path.join(name);
    
    // 检查文件夹是否已存在
    if folder_path.exists() {
        return Err(format!("文件夹'{}'已存在", name).to_string());
    }

    // 创建文件夹
    fs::create_dir(&folder_path).map_err(|e| format!("无法创建文件夹: {}", e))?;
    
    // 创建标记文件
    let marker_path = folder_path.join(".kb_marker.json");
    
    // 构建标记文件内容
    let marker_content = serde_json::json!({
        "id": uuid,
        "name": name,
        "created_at": SystemTime::now()
            .duration_since(SystemTime::UNIX_EPOCH)
            .map_err(|e| format!("无法获取系统时间: {}", e))?
            .as_secs(),
        "updated_at": SystemTime::now()
            .duration_since(SystemTime::UNIX_EPOCH)
            .map_err(|e| format!("无法获取系统时间: {}", e))?
            .as_secs()
    });
    
    // 写入标记文件
    fs::write(
        &marker_path,
        serde_json::to_string_pretty(&marker_content)
            .map_err(|e| format!("无法序列化标记文件内容: {}", e))?
    ).map_err(|e| format!("无法写入标记文件: {}", e))?;
    
    // 返回结果
    Ok(serde_json::json!({
        "success": true,
        "id": uuid,
        "name": name,
        "path": folder_path.to_str().ok_or("无法转换路径为字符串")?
    }))
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_cli::init())
        .plugin(tauri_plugin_opener::init())
        .invoke_handler(tauri::generate_handler![

            start_python_server,
            execute_command,
            check_ollama_service,
            start_ollama_service,
            create_knowledge_base
        ])
        .setup(|_| {
            // 应用启动时自动启动Python服务器
            match start_python_server() {
                Ok(msg) => println!("{}", msg),
                Err(e) => println!("Python服务器启动失败: {}", e),
            }
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
