"""品牌视觉生成器 - 统一手绘涂鸦风格"""
from typing import List
import httpx
from pathlib import Path
from config import MINIMAX_API_KEY, LOVART_AVAILABLE


STYLE_PREFIX = "手绘涂鸦风，Obsidian手绘插件风格，有机线条，笔记本涂鸦质感"


def generate_slogans(solution: dict, features) -> List[str]:
    theme = solution.get("overview", {}).get("theme", "乡土探索")
    return [
        "走进" + features.name + "，探索乡土之美",
        features.name + "——" + theme + "新体验",
        "在" + features.name + "，读懂乡土中国",
    ]


def generate_logo_concept(features, theme: str) -> dict:
    """生成 Logo prompt
    
    Logo 保持 1:1 比例
    """
    prompt = f"{STYLE_PREFIX}。{features.name}乡村研学品牌Logo，圆形徽章设计。有机线条手绘风格。中心主题：{theme}。配色：深青+暖黄。适合研学品牌使用。"
    
    return {
        "style": "手绘涂鸦风圆形徽章",
        "description": f"{features.name}研学品牌Logo",
        "prompt": prompt
    }


def generate_cultural_products(features) -> List[dict]:
    """生成文创产品 prompt
    
    统一手绘涂鸦风格
    """
    base = f"{STYLE_PREFIX}。{features.name}主题设计。"
    
    return [
        {
            "type": "帆布袋",
            "prompt": f"{base}研学主题帆布袋设计。乡村元素：{features.geography[0] if features.geography else '田野'}。有机线条手绘风格。适合研学活动纪念品。"
        },
        {
            "type": "明信片",
            "prompt": f"{base}风景明信片套装。包含：{features.geography[0] if features.geography else '乡村风景'}。有机线条手绘风格。共4张不同图案。"
        },
        {
            "type": "文化衫",
            "prompt": f"{base}研学文化衫图案设计。胸前图案：{features.intangible_heritage[0] if features.intangible_heritage else '乡村元素'}。有机线条手绘风格。"
        }
    ]


def generate_brand_image(prompt: str, output_path: str) -> str:
    """生成品牌图片，优先使用 Lovart，失败则回退到 MiniMax"""
    
    output_dir = str(Path(output_path).parent)
    
    if LOVART_AVAILABLE:
        try:
            from scripts.lovart_wrapper import chat
            result = chat(
                prompt=prompt,
                output_dir=output_dir,
                timeout=180
            )
            
            if result.get("success"):
                local_paths = result.get("local_paths", [])
                if local_paths and local_paths[0]:
                    print(f"[INFO] 品牌图片已通过 Lovart 生成: {local_paths[0]}")
                    return local_paths[0]
            else:
                print(f"[INFO] Lovart 生成失败: {result.get('error', 'Unknown error')}")
                print("[INFO] 回退到 MiniMax 生成...")
        except ImportError as e:
            print(f"[INFO] Lovart 模块导入失败: {e}")
        except Exception as e:
            print(f"[INFO] Lovart 调用异常: {e}")
            print("[INFO] 回退到 MiniMax 生成...")
    else:
        print("[INFO] Lovart 未配置，尝试 MiniMax...")
    
    return _generate_with_minimax(prompt, output_path)


def _generate_with_minimax(prompt: str, output_path: str, aspect_ratio: str = "1:1") -> str:
    """使用 MiniMax image-01 生成品牌图片"""
    if not MINIMAX_API_KEY:
        print("Warning: No MINIMAX_API_KEY, skipping image generation")
        return ""
    
    try:
        response = httpx.post(
            "https://api.minimaxi.com/v1/image_generation",
            headers={
                "Authorization": f"Bearer {MINIMAX_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "image-01",
                "prompt": prompt,
                "aspect_ratio": aspect_ratio,
                "response_format": "url",
                "n": 1
            },
            timeout=120
        )
        data = response.json()
        
        if data.get("base_resp", {}).get("status_code") == 0:
            image_url = data["data"]["image_urls"][0]
            print(f"Generated image: {image_url}")
            return image_url
        else:
            error_msg = data.get("base_resp", {}).get("status_msg", "Unknown error")
            print(f"Image generation failed: {error_msg}")
            return ""
    except Exception as e:
        print(f"Image generation failed: {e}")
        return ""
