import json
import re
from openai import OpenAI
from config import MINIMAX_API_KEY, BASE_URL, LLM_MODEL


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
    
    if raw_response.endswith(']'):
        depth = 0
        start = -1
        end = -1
        for i, c in enumerate(raw_response):
            if c == '[':
                if start == -1:
                    start = i
                depth += 1
            elif c == ']':
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
        if start != -1 and end != -1:
            candidate = raw_response[start:end]
            if candidate.count('[') == candidate.count(']'):
                return candidate
    
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


THEME_PROMPT = """根据以下村庄特色，推荐5个最值得开发的研学课程方向。

村庄特色：
{features}

## 探学玩创框架说明
- 探（探索）：通过观察、发现、提问，激发好奇心
- 学（学习）：知识习得、技能掌握、理解深化
- 玩（玩耍）：游戏化体验、互动参与、寓教于乐
- 创（创造）：动手创作、表达分享、成果输出

根据课程主题特性，灵活选择适合的环节组合：
- 文化探索类 → 探 → 学 → 创
- 农事体验类 → 探 → 学 → 玩 → 创
- 技艺传承类 → 探 → 学 → 创
- 自然认知类 → 探 → 玩 → 学

## 必须输出JSON数组格式（包含5个课程方向）
[
    {{"name": "课程名称", "type": "体验", "block": "劳动", "reason": "推荐理由", "tan_xue_wan_chuang": "探→学→创"}},
    {{"name": "课程名称", "type": "探究", "block": "人文", "reason": "推荐理由", "tan_xue_wan_chuang": "探→学→玩→创"}}
]

注意：必须输出JSON数组，以 [ 开头，以 ] 结尾。只输出JSON，不要任何其他文字。"""


LESSON_PROMPT = """你是一个专业的研学旅行课程设计师，擅长"探学玩创"课程设计。

## 探学玩创框架（灵活组合）

根据课程主题特性，选择适合的环节组合：

| 模式 | 适用场景 | 环节顺序 |
|------|---------|---------|
| 模式A | 文化探索类 | 探 → 学 → 创 |
| 模式B | 农事体验类 | 探 → 学 → 玩 → 创 |
| 模式C | 技艺传承类 | 探 → 学 → 创 |
| 模式D | 自然认知类 | 探 → 玩 → 学 |

各环节说明：
- 探（探索发现）：设置探索情境，引导观察、提问、发现
- 学（知识学习）：讲解知识、示范技能、互动问答
- 玩（游戏化体验）：互动游戏、角色扮演、竞赛挑战等
- 创（创造性产出）：动手制作、成果展示、分享表达

## 输出格式（严格JSON）
{{
    "course_name": "课程全称",
    "course_type": "考察/实验/体验/观赏/探究",
    "theme_block": "自然/人文/科技/劳动/安全",
    "grade_level": "小学3-4年级",
    "duration_minutes": 90,
    "location": "村内具体地点",
    "capacity": 30,
    "tan_xue_wan_chuang": {{
        "mode": "模式A/模式B/模式C/模式D",
        "sequence": "探→学→创",
        "explore": {{"duration": 15, "description": "探索环节描述，如无则null"}},
        "learn": {{"duration": 30, "description": "学习环节描述"}},
        "play": {{"duration": 20, "description": "玩耍环节描述，如无则null"}},
        "create": {{"duration": 25, "description": "创造环节描述"}}
    }},
    "objectives": {{
        "knowledge": ["知识点1", "知识点2"],
        "abilities": ["能力描述1"],
        "values": ["情感目标1"]
    }},
    "preparations": {{
        "teacher": ["教具准备1", "知识背景准备"],
        "student": ["预习要求", "着装要求"],
        "safety": [{{"risk": "风险描述", "measure": "应对措施"}}]
    }},
    "implementation": {{
        "warmup": {{"duration": 10, "content": "导入内容"}},
        "activities": [
            {{"name": "活动名称", "phase": "探/学/玩/创", "duration": 30, "steps": ["步骤1", "步骤2"], "observation_points": ["观察点1"], "recording_form": "记录表名称"}}
        ],
        "summary": {{"duration": 10, "content": "总结延伸内容"}}
    }},
    "evaluation": {{"method": "过程性评价", "rubric": "评价量规描述", "reflection_questions": ["反思问题1"]}},
    "appendix": {{"task_sheet": "任务单内容描述", "materials": ["素材图例列表"]}}
}}

## 要求
- 根据课程主题选择合适的探学玩创模式，不必每个环节都包含
- 环节时长总和应等于课程总时长
- 只输出JSON，不要解释。"""


class LessonPlanAgent:
    def __init__(self, api_key=None):
        api_key = api_key or MINIMAX_API_KEY
        self.client = OpenAI(api_key=api_key, base_url=BASE_URL)
        self.model = LLM_MODEL

    def extract_themes(self, features, local_documents_info=None, retries=3):
        feat_str = "地理风貌：" + ", ".join(features.geography) + "\n"
        feat_str += "非遗文化：" + ", ".join(features.intangible_heritage) + "\n"
        feat_str += "农耕食物：" + ", ".join(features.food) + "\n"
        feat_str += "特色物产：" + ", ".join(features.products) + "\n"
        feat_str += "民俗活动：" + ", ".join(features.customs) + "\n"
        feat_str += "农事活动：" + ", ".join(features.activities)
        
        if local_documents_info:
            merged_info = local_documents_info.get("merged_info", {})
            if merged_info.get("intangible_heritage"):
                feat_str += "\n\n【文献补充-非遗】：" + "、".join(merged_info["intangible_heritage"][:5])
            if merged_info.get("folk_customs"):
                feat_str += "\n【文献补充-民俗】：" + "、".join(merged_info["folk_customs"][:5])
            if merged_info.get("historical_sites"):
                feat_str += "\n【文献补充-遗迹】：" + "、".join(merged_info["historical_sites"][:5])
            if merged_info.get("legends_stories"):
                feat_str += "\n【文献补充-传说】：" + "、".join(merged_info["legends_stories"][:3])
        
        prompt = THEME_PROMPT.format(features=feat_str)
        
        for attempt in range(retries):
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=1.0,
                max_tokens=4096
            )
            raw = resp.choices[0].message.content
            content = extract_content(raw)
            if content and len(content) > 10:
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    if attempt == retries - 1:
                        print(f"Warning: Failed to parse themes JSON after {retries} attempts")
                        print(f"Content: {content[:200]}")
                    continue
        return []

    def generate_one(self, features, course_theme, local_documents_info=None, retries=3):
        village_info = "村名：" + features.name + "，地理位置：" + features.location + "\n"
        village_info += "地理风貌：" + ", ".join(features.geography) + "\n"
        village_info += "非遗文化：" + ", ".join(features.intangible_heritage) + "\n"
        village_info += "农耕食物：" + ", ".join(features.food) + "\n"
        village_info += "特色物产：" + ", ".join(features.products) + "\n"
        village_info += "民俗活动：" + ", ".join(features.customs)
        
        if local_documents_info:
            merged_info = local_documents_info.get("merged_info", {})
            village_history = local_documents_info.get("village_history", {})
            if village_history.get("notable_villagers"):
                village_info += "\n村庄人物：" + "、".join(village_history["notable_villagers"][:3])
            if village_history.get("historical_events"):
                village_info += "\n历史大事：" + "、".join(village_history["historical_events"][:3])
            if merged_info.get("historical_sites"):
                village_info += "\n历史遗迹：" + "、".join(merged_info["historical_sites"][:3])
        
        prompt = village_info + "\n\n"
        prompt += "## 本次课程主题\n"
        prompt += "课程名称：" + course_theme.get("name", "") + "\n"
        prompt += "课程类型：" + course_theme.get("type", "体验") + "\n"
        prompt += "所属板块：" + course_theme.get("block", "劳动") + "\n"
        prompt += "推荐理由：" + course_theme.get("reason", "") + "\n"
        prompt += "探学玩创模式：" + course_theme.get("tan_xue_wan_chuang", "探→学→玩→创") + "\n\n"
        prompt += "请生成完整教案JSON。只输出JSON，不要解释。"
        
        for attempt in range(retries):
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": LESSON_PROMPT}, {"role": "user", "content": prompt}],
                temperature=1.0,
                max_tokens=8192
            )
            raw = resp.choices[0].message.content
            content = extract_content(raw)
            if content and len(content) > 50:
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    if attempt == retries - 1:
                        print(f"Warning: Failed to parse lesson plan JSON after {retries} attempts")
                    continue
        return {"course_name": "解析失败"}

    def generate_all(self, features, local_documents_info=None):
        themes = self.extract_themes(features, local_documents_info)
        plans = []
        for t in themes:
            if isinstance(t, dict) and 'name' in t:
                plans.append(self.generate_one(features, t, local_documents_info))
            else:
                print(f"Warning: Skipping invalid theme: {t}")
        return plans
