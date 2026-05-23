import json
from openai import OpenAI
from config import MINIMAX_API_KEY, BASE_URL, LLM_MODEL


SYSTEM_PROMPT = """你是一个乡村研学课程体系设计专家。

## 课程体系框架

一份完整的课程体系手册应包含：

### 1. 理念（Philosophy）
- 教育理念：为什么要做这个课程体系
- 探学玩创理念：如何用探学玩创引导学习
- 核心价值：希望孩子收获什么

### 2. 执教方法（Teaching Methods）
- PBL（项目制学习）：如何通过项目驱动学习
- 探究式学习：如何引导提问和探索
- 体验式学习：如何通过亲身经历获得知识
- 跨学科融合：如何连接不同学科知识

### 3. 课程序列（Course Sequence）
- 系列课程的逻辑顺序
- 从浅入深的难度梯度
- 四季/不同时节的课程安排

### 4. 工坊清单（Workshop List）
- 可开展的工坊项目
- 所需材料和场地
- 适合年龄段

## 输出格式（严格JSON）
{
    "philosophy": {
        "education_vision": "教育愿景（一段话）",
        "tan_xue_wan_chuang_concept": "探学玩创理念说明",
        "core_values": ["核心价值1", "核心价值2", "核心价值3"],
        "child_growth": "希望孩子获得的成长"
    },
    "teaching_methods": [
        {
            "name": "方法名称（如：PBL项目制学习）",
            "description": "方法说明",
            "application": "在本课程中的应用场景",
            "teacher_role": "导师角色"
        }
    ],
    "course_sequence": [
        {
            "course_name": "课程名称",
            "sequence": 1,
            "target_grade": "年级段",
            "duration": "时长",
            "theme": "主题",
            "key_activities": ["核心活动1", "核心活动2"],
            "learning_outcomes": "学习成果",
            "season": "适合季节（春夏秋冬）"
        }
    ],
    "workshop_list": [
        {
            "workshop_name": "工坊名称",
            "description": "工坊简介",
            "materials": ["材料1", "材料2"],
            "tools": ["工具1"],
            "location": "场地要求",
            "duration": "时长",
            "age_range": "适合年龄",
            "max_participants": "最大人数",
            "safety_notes": "安全注意事项"
        }
    ],
    "curriculum_principles": {
        "difficulty_gradient": "难度梯度设计说明",
        "seasonal_design": "季节性课程设计说明",
        "interdisciplinary": "跨学科融合说明"
    }
}

## 要求
- 课程序列至少5门课程
- 工坊项目至少6个
- 执教方法至少3种
- 语言简洁专业但易懂"""


def extract_content(raw_response: str) -> str:
    raw_response = raw_response.strip()
    
    if '\n\n' in raw_response:
        parts = raw_response.rsplit('\n\n', 1)
        candidate = parts[-1].strip()
        if (candidate.startswith('{') and candidate.endswith('}')) or \
           (candidate.startswith('[') and candidate.endswith(']')):
            return candidate
    
    if (raw_response.startswith('{') and raw_response.endswith('}')) or \
       (raw_response.startswith('[') and raw_response.endswith(']')):
        try:
            json.loads(raw_response)
            return raw_response
        except:
            pass
    
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
        if candidate.count('{') == candidate.count('}'):
            return candidate
    
    return raw_response


class CurriculumAgent:
    def __init__(self, api_key=None):
        api_key = api_key or MINIMAX_API_KEY
        self.client = OpenAI(api_key=api_key, base_url=BASE_URL)
        self.model = LLM_MODEL

    def generate(self, features, lesson_plans=None, retries=3):
        village_info = f"""村名：{features.name}
地理位置：{features.location}

村庄特色：
- 地理风貌：{', '.join(features.geography[:3])}
- 非遗文化：{', '.join(features.intangible_heritage[:3])}
- 特色食物：{', '.join(features.food[:3])}
- 特色物产：{', '.join(features.products[:3])}
- 民俗活动：{', '.join(features.customs[:3])}
"""
        
        courses_info = ""
        if lesson_plans and len(lesson_plans) > 0:
            courses_info = "\n已设计的课程：\n"
            for i, plan in enumerate(lesson_plans[:5]):
                name = plan.get("course_name", f"课程{i+1}")
                courses_info += f"- {name}\n"
        
        prompt = village_info + courses_info + "\n\n请根据以上村庄特色和已有课程，设计完整的课程体系JSON。只输出JSON，不要解释。"

        for attempt in range(retries):
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=1.0,
                max_tokens=8192
            )
            raw = resp.choices[0].message.content
            content = extract_content(raw)
            
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            elif content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            
            try:
                return json.loads(content.strip())
            except json.JSONDecodeError as e:
                if attempt == retries - 1:
                    print(f"Curriculum JSON parse error: {e}")
                    return self._default_curriculum(features)
                continue
        
        return self._default_curriculum(features)
    
    def _default_curriculum(self, features):
        return {
            "philosophy": {
                "education_vision": f"在{features.name}，我们相信最好的教育在大自然里。",
                "tan_xue_wan_chuang_concept": "用探·学·玩·创的方式，让孩子在大自然中探索、学习、玩耍、创造。",
                "core_values": ["热爱自然", "尊重传统", "勇于创造", "善于合作"],
                "child_growth": "通过乡村研学，孩子将收获自然知识、动手能力、创造力和对乡土文化的热爱。"
            },
            "teaching_methods": [
                {
                    "name": "PBL项目制学习",
                    "description": "围绕一个真实问题或项目，让孩子自主探究、协作完成",
                    "application": "如：设计一个村庄导览方案、制作一份乡村美食",
                    "teacher_role": "引导者、资源提供者"
                },
                {
                    "name": "体验式学习",
                    "description": "通过亲身经历获得知识和技能",
                    "application": "如：亲手制作手工艺品、参与农事活动",
                    "teacher_role": "示范者、安全守护者"
                },
                {
                    "name": "探究式学习",
                    "description": "引导孩子提问、假设、验证、总结",
                    "application": "如：探索村庄的水源、设计环保方案",
                    "teacher_role": "提问者、思考引导者"
                }
            ],
            "course_sequence": [],
            "workshop_list": [],
            "curriculum_principles": {
                "difficulty_gradient": "从认知→体验→创造，难度递进",
                "seasonal_design": "根据四季变化设计应季课程",
                "interdisciplinary": "融合自然、科技、艺术、人文多学科"
            }
        }
