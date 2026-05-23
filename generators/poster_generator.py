"""海报生成器 - 统一手绘涂鸦风格（Obsidian 手绘插件风格）"""
from typing import List, Optional
import httpx
from pathlib import Path
from config import MINIMAX_API_KEY, LOVART_AVAILABLE


STYLE_PREFIX = "竖版9:16，手绘涂鸦风，Obsidian手绘插件风格，有机线条，笔记本涂鸦质感"


def generate_poster_image(prompt: str, output_path: str) -> str:
    """生成海报图片，优先使用 Lovart，失败则回退到 MiniMax"""
    
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
                    print(f"[INFO] 海报已通过 Lovart 生成: {local_paths[0]}")
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


def _generate_with_minimax(prompt: str, output_path: str) -> str:
    """使用 MiniMax image-01 生成海报图片"""
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
                "aspect_ratio": "9:16",
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


def build_poster_prompt(
    subject: str,
    village_name: str,
    elements: List[str] = None,
    extra: str = ""
) -> str:
    """构建海报 prompt"""
    parts = [STYLE_PREFIX, subject]
    
    if village_name:
        parts.append(f"{village_name}")
    
    if elements:
        parts.append("。".join(elements[:3]))
    
    if extra:
        parts.append(f"。{extra}")
    
    return "。".join(parts)


def generate_course_poster(lesson_plan: dict, village_name: str, features) -> dict:
    """生成课程海报 prompt
    
    Args:
        lesson_plan: 教案数据
        village_name: 村庄名称
        features: 村庄特色
        
    Returns:
        {"course_name": str, "prompt": str}
    """
    course_name = lesson_plan.get("course_name", "研学课程")
    course_type = lesson_plan.get("course_type", "体验")
    theme_block = lesson_plan.get("theme_block", "人文")
    location = lesson_plan.get("location", "")
    
    elements = []
    if features.food:
        elements.append(f"美食：{features.food[0]}")
    if features.activities:
        elements.append(f"活动：{features.activities[0]}")
    if features.intangible_heritage:
        elements.append(f"文化：{features.intangible_heritage[0]}")
    
    subject = f"{course_name}研学活动"
    extra = f"{course_type}类·{theme_block}板块。地点：{location}。"
    
    return {
        "course_name": course_name,
        "prompt": build_poster_prompt(subject, village_name, elements, extra)
    }


def generate_day_tour_poster(solution: dict, village_name: str, features) -> dict:
    """生成一日游学海报 prompt
    
    Args:
        solution: 解决方案数据
        village_name: 村庄名称
        features: 村庄特色
        
    Returns:
        {"prompt": str}
    """
    theme = solution.get("overview", {}).get("theme", "乡村探索")
    duration = solution.get("overview", {}).get("duration", "一日")
    target = "/".join(solution.get("overview", {}).get("target_audience", ["亲子"]))
    
    elements = []
    if features.geography:
        elements.append(f"风景：{features.geography[0]}")
    if features.food:
        elements.append(f"美食：{features.food[0]}")
    if features.customs:
        elements.append(f"民俗：{features.customs[0]}")
    
    subject = f"{village_name}{duration}游学体验"
    extra = f"主题：{theme}。适合：{target}。"
    
    return {
        "prompt": build_poster_prompt(subject, village_name, elements, extra)
    }


def generate_camp_poster(season: str, village_name: str, features) -> dict:
    """生成夏/冬令营海报 prompt
    
    Args:
        season: "夏" 或 "冬"
        village_name: 村庄名称
        features: 村庄特色
        
    Returns:
        {"prompt": str}
    """
    camp_name = f"{village_name}{season}令营"
    camp_theme = "乡村探索 · 自然成长" if season == "夏" else "乡村暖冬 · 成长之旅"
    
    elements = []
    if season == "夏":
        elements.append("夏日田野风光")
        elements.append("户外探索体验")
    else:
        elements.append("冬日乡村美景")
        elements.append("温暖农事体验")
    
    if features.intangible_heritage:
        elements.append(f"非遗体验：{features.intangible_heritage[0]}")
    
    extra = f"7天6夜/5天4夜。适合：亲子/小学生。"
    
    return {
        "season": season,
        "prompt": build_poster_prompt(camp_name, village_name, elements, extra)
    }


def generate_treasure_hunt_poster(village_name: str, features, treasure_hunt: dict = None) -> dict:
    """生成寻宝卡海报 prompt
    
    Args:
        village_name: 村庄名称
        features: 村庄特色
        treasure_hunt: 寻宝数据
        
    Returns:
        {"prompt": str}
    """
    hunt_name = f"{village_name}村落寻宝"
    hunt_theme = "九宫格探索挑战"
    
    elements = []
    if features.geography:
        elements.append(f"场景：{features.geography[0]}")
    elements.append("古建筑探索")
    elements.append("村落文化发现")
    
    if treasure_hunt:
        reward = treasure_hunt.get("reward_description", "")
        if reward:
            elements.append(f"奖励：{reward[:20]}")
    
    extra = "研学探索 · 亲子互动"
    
    return {
        "prompt": build_poster_prompt(hunt_name, village_name, elements, extra)
    }


def generate_village_poster(solution: dict, village_name: str, features) -> dict:
    """生成整村文旅宣传海报 prompt
    
    Args:
        solution: 解决方案数据
        village_name: 村庄名称
        features: 村庄特色
        
    Returns:
        {"prompt": str}
    """
    theme = solution.get("overview", {}).get("theme", "乡村探索")
    county_pos = solution.get("overview", {}).get("county_position", "")
    highlights = solution.get("background", {}).get("highlights", [])
    
    elements = []
    if highlights:
        elements.append(f"亮点：{highlights[0]}")
    if features.geography:
        elements.append(f"风景：{features.geography[0]}")
    if features.intangible_heritage:
        elements.append(f"非遗：{features.intangible_heritage[0]}")
    if features.food:
        elements.append(f"美食：{features.food[0]}")
    
    extra = f"定位：{county_pos[:30] if county_pos else '乡村文旅目的地'}。" if county_pos else ""
    
    subject = f"{village_name}乡村文旅目的地"
    
    return {
        "prompt": build_poster_prompt(subject, village_name, elements, extra)
    }


def generate_all_poster_concepts(solution: dict, village_name: str, features, lesson_plans: list) -> dict:
    """生成所有海报的 prompt 配置
    
    Returns:
        {
            "course_posters": [5个课程海报配置],
            "day_tour_poster": 一日游学海报,
            "camp_poster": 夏令营海报,
            "treasure_hunt_poster": 寻宝卡,
            "village_poster": 村庄宣传海报
        }
    """
    treasure_hunt = solution.get("treasure_hunt", {})
    
    course_posters = []
    for plan in lesson_plans[:5]:
        poster = generate_course_poster(plan, village_name, features)
        course_posters.append(poster)
    
    return {
        "course_posters": course_posters,
        "day_tour_poster": generate_day_tour_poster(solution, village_name, features),
        "camp_poster": generate_camp_poster("夏", village_name, features),
        "treasure_hunt_poster": generate_treasure_hunt_poster(village_name, features, treasure_hunt),
        "village_poster": generate_village_poster(solution, village_name, features)
    }
