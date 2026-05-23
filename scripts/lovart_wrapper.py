"""
Lovart Wrapper - 封装 Lovart API 调用，适配 village_study_tour 项目
"""
import json
import subprocess
import sys
import os
from pathlib import Path


def get_script_dir():
    """获取脚本所在目录"""
    return Path(__file__).parent.absolute()


def load_env():
    """加载 .env 文件中的环境变量"""
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        with open(env_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ.setdefault(key.strip(), value.strip())


def chat(prompt: str, output_dir: str = None, thread_id: str = None, 
          prefer_models: str = None, mode: str = None, timeout: int = 300) -> dict:
    """
    调用 Lovart 生成图片/视频
    
    Args:
        prompt: 提示词
        output_dir: 输出目录（默认 village_study_tour/output）
        thread_id: 会话 ID（用于继续对话）
        prefer_models: 模型偏好 JSON 字符串
        mode: 'thinking' 或 'fast'
        timeout: 超时时间（秒）
    
    Returns:
        dict: 包含 success, url, local_path, error 等字段
    """
    load_env()
    
    access_key = os.environ.get("LOVART_ACCESS_KEY", "")
    secret_key = os.environ.get("LOVART_SECRET_KEY", "")
    
    if not access_key or not secret_key:
        return {
            "success": False,
            "error": "LOVART_ACCESS_KEY or LOVART_SECRET_KEY not set"
        }
    
    # 默认输出目录
    if not output_dir:
        project_root = Path(__file__).parent.parent
        output_dir = str(project_root / "output")
    
    script_dir = get_script_dir()
    agent_script = script_dir / "agent_skill.py"
    
    # 构建命令
    cmd = [
        sys.executable,
        str(agent_script),
        "chat",
        "--prompt", prompt,
        "--json",
        "--download",
        "--output-dir", output_dir,
    ]
    
    if thread_id:
        cmd.extend(["--thread-id", thread_id])
    
    if prefer_models:
        cmd.extend(["--prefer-models", prefer_models])
    
    if mode:
        cmd.extend(["--mode", mode])
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout + 30
        )
        
        if result.returncode != 0:
            return {
                "success": False,
                "error": result.stderr or "Unknown error",
                "stdout": result.stdout
            }
        
        output = json.loads(result.stdout)
        
        # 检查生成是否成功
        final_status = output.get("final_status", "")
        
        if final_status == "done":
            downloaded = output.get("downloaded", [])
            if downloaded:
                return {
                    "success": True,
                    "thread_id": output.get("thread_id"),
                    "project_id": output.get("project_id"),
                    "artifacts": output.get("items", []),
                    "downloaded": downloaded,
                    "local_paths": [d.get("local_path") for d in downloaded if d.get("local_path")],
                    "urls": [d.get("url") for d in downloaded if d.get("url")]
                }
            elif output.get("generation_succeeded") == False:
                return {
                    "success": False,
                    "error": output.get("warning", "Generation completed but no artifact produced"),
                    "agent_message": output.get("agent_message", "")
                }
        
        return {
            "success": False,
            "error": f"Generation status: {final_status}",
            "output": output
        }
        
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": f"Command timeout after {timeout} seconds"
        }
    except json.JSONDecodeError as e:
        return {
            "success": False,
            "error": f"Failed to parse output: {e}",
            "stdout": result.stdout if 'result' in locals() else "",
            "stderr": result.stderr if 'result' in locals() else ""
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def config() -> dict:
    """查看本地配置"""
    load_env()
    
    script_dir = get_script_dir()
    agent_script = script_dir / "agent_skill.py"
    
    cmd = [sys.executable, str(agent_script), "config", "--json"]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return json.loads(result.stdout)
        return {"error": result.stderr}
    except Exception as e:
        return {"error": str(e)}


def projects() -> dict:
    """列出所有项目"""
    load_env()
    
    script_dir = get_script_dir()
    agent_script = script_dir / "agent_skill.py"
    
    cmd = [sys.executable, str(agent_script), "projects", "--json"]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return json.loads(result.stdout)
        return {"error": result.stderr}
    except Exception as e:
        return {"error": str(e)}


def threads(project_id: str = None) -> dict:
    """列出会话历史"""
    load_env()
    
    script_dir = get_script_dir()
    agent_script = script_dir / "agent_skill.py"
    
    cmd = [sys.executable, str(agent_script), "threads", "--json"]
    if project_id:
        cmd.extend(["--project-id", project_id])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return json.loads(result.stdout)
        return {"error": result.stderr}
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Lovart Wrapper for village_study_tour")
    parser.add_argument("--prompt", required=True, help="提示词")
    parser.add_argument("--output-dir", default=None, help="输出目录")
    parser.add_argument("--thread-id", default=None, help="会话 ID")
    parser.add_argument("--prefer-models", default=None, help="模型偏好 JSON")
    parser.add_argument("--mode", default=None, choices=["thinking", "fast"], help="推理模式")
    parser.add_argument("--timeout", type=int, default=300, help="超时时间（秒）")
    
    args = parser.parse_args()
    
    result = chat(
        prompt=args.prompt,
        output_dir=args.output_dir,
        thread_id=args.thread_id,
        prefer_models=args.prefer_models,
        mode=args.mode,
        timeout=args.timeout
    )
    
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    sys.exit(0 if result.get("success") else 1)
