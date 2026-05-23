"""
关键词课程生成 Agent
基于关键词转译结果，生成完整的课程文档
"""

import json
from typing import Dict, Optional
from openai import OpenAI
from config import MINIMAX_API_KEY, BASE_URL, LLM_MODEL
from rag.keyword_translator import translate_keywords


SYSTEM_PROMPT = """你是一个专业的研学课程设计师，负责将关键词转化为完整的课程文档。

## 工作流程
1. 接收关键词列表和村庄特色信息
2. 为每个关键词匹配对应的课程模板
3. 生成完整的课程文档

## 课程文档格式
每个课程必须包含：
- name: 课程名称
- type: 课程类型（农耕体验/建造体验/美食制作/手工艺/戏曲表演/非遗传承/民俗文化/自然探索）
- grade_level: 适用年级
- duration_minutes: 课时时长
- objectives: 课程目标 {知识, 能力, 情感}
- activities: 活动列表 [{name, duration, content}]
- materials: 所需材料列表
- safety: 安全注意事项列表

## 输出格式
直接输出JSON数组，不要其他内容。"""


class KeywordCourseAgent:
    def __init__(self, api_key=None):
        api_key = api_key or MINIMAX_API_KEY
        self.client = OpenAI(api_key=api_key, base_url=BASE_URL)
        self.model = LLM_MODEL
    
    def generate(self, keyword_string: str, village_features: dict = None) -> Dict:
        """
        基于关键词生成课程
        输入: "土豆 石拱廊桥"
        输出: {"courses": [...], "keyword_result": {...}}
        """
        # 1. 转译关键词
        keyword_result = translate_keywords(keyword_string)
        
        if not keyword_result["courses"]:
            return {
                "courses": [],
                "keyword_result": keyword_result,
                "message": "没有找到匹配的课程，请尝试其他关键词"
            }
        
        # 2. 如果有关键词特色信息，用 AI 丰富课程内容
        if village_features and keyword_result["valid_keywords"]:
            enriched_courses = self._enrich_courses(
                keyword_result["courses"], 
                village_features
            )
            keyword_result["courses"] = enriched_courses
        
        return {
            "courses": keyword_result["courses"],
            "keyword_result": keyword_result,
            "message": None
        }
    
    def _enrich_courses(self, courses: list, features: dict) -> list:
        """使用村庄特色信息丰富课程内容"""
        village_name = features.get("name", "乡村")
        
        village_info = f"""村庄名称：{village_name}
地理特色：{', '.join(features.get('geography', []))}
历史遗迹：{', '.join(features.get('history', []))}
非遗文化：{', '.join(features.get('intangible_heritage', []))}
美食特产：{', '.join(features.get('food', []))}
特色物产：{', '.join(features.get('products', []))}
民俗活动：{', '.join(features.get('customs', []))}"""
        
        prompt = f"""请根据以下村庄信息丰富课程内容：

{village_info}

现有课程列表：
{json.dumps(courses, ensure_ascii=False, indent=2)}

要求：
1. 将课程活动与村庄特色结合，使活动描述更具体生动
2. 可以替换或添加具体的村庄相关元素
3. 保持课程结构不变
4. 直接输出JSON数组，不要其他内容"""

        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=8192
            )
            content = resp.choices[0].message.content.strip()
            
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            
            return json.loads(content.strip())
        except json.JSONDecodeError as e:
            print(f"JSON parse error: {e}")
            return courses
        except Exception as e:
            print(f"AI enrich courses failed: {e}")
            return courses
    
    def generate_custom_keyword_course(self, keyword: str, village_features: dict = None) -> Dict:
        """
        为自定义关键词生成课程（当关键词不在预设库中时）
        """
        from rag.keyword_translator import detect_category, calculate_relevance
        
        relevance = calculate_relevance(keyword)
        if relevance < 0.6:
            return {
                "success": False,
                "message": f"关键词 '{keyword}' 与乡村研学关联度较低"
            }
        
        category = detect_category(keyword) or "体验活动"
        village_name = village_features.get("name", "乡村") if village_features else "乡村"
        
        prompt = f"""请为乡村研学活动设计一个关于"{keyword}"的课程。

村庄名称：{village_name}
{"地理特色：," + "、".join(village_features.get('geography', [])) if village_features else ""}

课程要求：
- 课程名称：{keyword}体验课
- 课程类型：{category}
- 适用年级：3-6年级
- 课时时长：60-90分钟
- 必须包含4-5个活动环节

直接输出JSON格式：
{{"name": "课程名称", "type": "类型", "grade_level": "年级", "duration_minutes": 时长, "objectives": {{"知识": "", "能力": "", "情感": ""}}, "activities": [{{"name": "", "duration": 0, "content": ""}}], "materials": [], "safety": []}}"""
        
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2048
            )
            content = resp.choices[0].message.content.strip()
            
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            
            course = json.loads(content.strip())
            return {
                "success": True,
                "course": course
            }
        except Exception as e:
            print(f"Generate custom course failed: {e}")
            return {
                "success": False,
                "message": f"生成课程失败: {str(e)}"
            }
