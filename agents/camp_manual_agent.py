import json
import re
from openai import OpenAI
from config import MINIMAX_API_KEY, BASE_URL, LLM_MODEL


def extract_content(raw_response: str) -> str:
    raw_response = raw_response.strip()
    
    # Priority: If contains \n\n, use content after the last \n\n (MiniMax thinking pattern)
    if '\n\n' in raw_response:
        parts = raw_response.rsplit('\n\n', 1)
        candidate = parts[-1].strip()
        if candidate.startswith('{') and candidate.endswith('}'):
            return candidate
    
    # Strategy 2: If starts with { and ends with }, likely the whole response is JSON
    if raw_response.startswith('{') and raw_response.endswith('}'):
        try:
            json.loads(raw_response)
            return raw_response
        except:
            pass
    
    # Strategy 3: Find the largest valid JSON object
    depth = 0
    start = -1
    end = -1
    for i, c in enumerate(raw_response):
        if c == '{':
            if start == -1:
                start = i
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    
    if start != -1 and end != -1:
        candidate = raw_response[start:end]
        try:
            json.loads(candidate)
            return candidate
        except:
            pass
    
    return raw_response


CAMP_PROMPT = """你是一个专业的研学旅行运营专家。
请为以下村庄设计一份完整的{season}令营研学手册。

## 必须使用的JSON格式（严格按此格式输出）
{{
    "overview": {{
        "name": "营名，如：龙潭村夏令营",
        "theme": "主题",
        "duration": "时间，如：7天6夜",
        "target": "招生对象，如：小学生4-6年级",
        "scale": "规模，如：30-50人/期"
    }},
    "daily_schedule": [
        {{"day": 1, "theme": "开营日主题", "summary": "日程概述"}},
        {{"day": 2, "theme": "第二天主题", "summary": "日程概述"}}
    ],
    "living_guide": {{
        "schedule": "作息时间，如：07:00起床-21:30就寝",
        "meals": "餐饮安排",
        "accommodation": "住宿安排",
        "packing_list": "行李清单"
    }},
    "safety": {{
        "general": "总体安全保障",
        "medical": "医疗保障"
    }},
    "parent_notice": {{
        "pickup": "接送安排",
        "refund": "退营条款"
    }},
    "evaluation": {{
        "method": "评价方式"
    }}
}}

## 设计原则
- 每天主题不重复，能力培养呈螺旋上升
- 冬令营突出冬季节令文化：腌制/酿造/传统节俗/防寒安全
- 安全预案必须包含：滑倒/失温/食物中毒/蚊虫叮咬/走失
- 作息时间符合该年龄段作息规律

## 输出要求
只输出JSON，不要任何解释文字。
"""

class CampManualAgent:
    def __init__(self, api_key=None):
        api_key = api_key or MINIMAX_API_KEY
        self.client = OpenAI(api_key=api_key, base_url=BASE_URL)
        self.model = LLM_MODEL

    def generate(self, features, season, days, lesson_plans, retries=3):
        village_info = "村名：" + features.name + "，位置：" + features.location + "\n"
        village_info += "地理风貌：" + ", ".join(features.geography) + "\n"
        village_info += "非遗文化：" + ", ".join(features.intangible_heritage) + "\n"
        village_info += "农耕食物：" + ", ".join(features.food) + "\n"
        village_info += "特色物产：" + ", ".join(features.products) + "\n"
        village_info += "民俗活动：" + ", ".join(features.customs)
        course_names = ", ".join([p.get("course_name", "") for p in lesson_plans])
        prompt = village_info + "\n\n已设计的课程教案：" + course_names + "\n\n请生成完整的" + season + "令营研学手册JSON。只输出JSON，不要解释。"
        system_prompt = CAMP_PROMPT.format(season=season, days=days)
        
        for attempt in range(retries):
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}],
                temperature=1.0,
                max_tokens=8192
            )
            raw = resp.choices[0].message.content
            content = extract_content(raw)
            if content and len(content) > 100:
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    if attempt == retries - 1:
                        print(f"Warning: Failed to parse camp manual JSON after {retries} attempts")
                    continue
        
        return {"title": f"{features.name}{season}令营研学手册", "overview": {}, "daily_schedule": []}

    def generate_summer(self, features, lesson_plans):
        return self.generate(features, "夏", 7, lesson_plans)

    def generate_winter(self, features, lesson_plans):
        return self.generate(features, "冬", 5, lesson_plans)
