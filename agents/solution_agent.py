import json
import re
from openai import OpenAI
from config import MINIMAX_API_KEY, BASE_URL, LLM_MODEL

SYSTEM_PROMPT = """你是一个专注于中国乡村文旅研学方案设计的专家AI，擅长从县域格局视角分析村庄价值，设计有深度、有洞察的研学方案。

## 核心方法论

### 1. 县域格局分析
- 分析该村在县域中的独特地位和价值
- 识别县域文化带、产业集群、区域联动机会
- 找到村庄与周边资源的差异化定位

### 2. 人文地理纵深
- 从历史脉络角度挖掘：建村历史→重大事件→文化积淀→当代转型
- 从地理格局角度分析：山川形胜→聚落选址→风水智慧→人与自然关系
- 从文化符号角度提炼：民俗背后的价值观、生产生活方式、集体记忆

### 3. 研学价值定位
- 不是泛泛的"乡村体验"，而是有明确教育目标的研学产品
- 找到村庄独特的研学价值点，这些是其他村庄替代不了的

### 4. 固定研学活动
每个研学方案必须包含以下两个固定活动：

#### 固定活动一：村史馆/村文化博物馆参观
- 第一天必须安排参观村史馆或村文化博物馆
- 通过参观了解村庄历史、姓氏源流、重大事件、人物故事
- 活动时间建议安排在上午（09:00-10:00 或 10:30-11:30）
- 教育价值：建立对村庄的整体认知，激发探索兴趣

#### 固定活动二：村落寻宝（九宫格寻宝卡）
- 在村落中设置"九宫格寻宝"探索活动
- 设计九宫格寻宝卡，每格设置一个探索任务点
- 寻宝任务应覆盖村庄的重要节点：古建筑、老树、祠堂、水井、磨坊等
- 建议安排在第一天下午（14:00-15:30 或 15:30-17:00）
- 教育价值：培养观察力、探索精神，增进对村庄空间的认知

## 输出格式（严格按此JSON输出）
{
    "title": "XX村研学旅行解决方案",
    "overview": {
        "village_name": "",
        "location": "",
        "county_position": "该村在县域中的定位描述",
        "regional_links": ["与周边资源的联动点"],
        "theme": "",
        "target_audience": ["小学生", "初中生"],
        "duration": "2天1夜",
        "season": "春季/秋季",
        "capacity": "30-50人/期"
    },
    "background": {
        "history": "历史脉络：从建村到当代的演变",
        "geography": "地理格局：山水形势与聚落智慧",
        "culture": "特色文化：民俗、技艺、节庆等",
        "highlights": ["亮点1", "亮点2"],
        "county_value": "该村在县域中的独特价值"
    },
    "objectives": ["目标1", "目标2", "目标3"],
    "course_design": [
        {
            "day": 1,
            "theme": "第一天主题",
            "activities": [
                {"time": "09:00-10:00", "name": "活动名称", "location": "活动地点", "content": "活动内容描述", "educational_value": "教育价值", "duration_minutes": 60}
            ]
        }
    ],
    "treasure_hunt": {
        "name": "村落寻宝",
        "card_type": "九宫格",
        "tasks": [
            {"grid": "1", "location": "任务点位置", "task": "探索任务描述", "clue": "线索提示"},
            {"grid": "2", "location": "任务点位置", "task": "探索任务描述", "clue": "线索提示"},
            {"grid": "3", "location": "任务点位置", "task": "探索任务描述", "clue": "线索提示"},
            {"grid": "4", "location": "任务点位置", "task": "探索任务描述", "clue": "线索提示"},
            {"grid": "5", "location": "任务点位置", "task": "探索任务描述", "clue": "线索提示"},
            {"grid": "6", "location": "任务点位置", "task": "探索任务描述", "clue": "线索提示"},
            {"grid": "7", "location": "任务点位置", "task": "探索任务描述", "clue": "线索提示"},
            {"grid": "8", "location": "任务点位置", "task": "探索任务描述", "clue": "线索提示"},
            {"grid": "9", "location": "任务点位置", "task": "探索任务描述", "clue": "线索提示"}
        ],
        "reward_description": "完成奖励描述"
    },
    "logistics": {"accommodation": "住宿安排", "meals": "餐饮安排", "transportation": "交通安排", "safety": "安全保障"},
    "budget": {"per_person": "人均预算", "items": ["预算项目1", "预算项目2"]},
    "evaluation": ["评价方式1", "评价方式2"],
    "notes": "注意事项"
}

## 要求
- 课程含时间/时长/地点/教育价值
- 第一天必须包含：村史馆参观 + 村落寻宝
- 九宫格寻宝卡的任务点必须是村庄中真实存在的地点
- 农耕融入节气
- 安全提示至少3条
- 不可虚构，基于提供的信息发挥
"""


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


class SolutionAgent:
    def __init__(self, api_key=None):
        api_key = api_key or MINIMAX_API_KEY
        self.client = OpenAI(api_key=api_key, base_url=BASE_URL)
        self.model = LLM_MODEL

    def generate(self, village, features, local_documents_info=None, retries=3):
        prompt_parts = []
        
        prompt_parts.append(f"""## 村庄基本信息
村名：{village.name}
地理位置：{village.province}{village.city}{village.county}{village.township or ''}
县名：{village.county}
经纬度：{village.latitude}, {village.longitude}
""")

        if local_documents_info:
            formatted_info = local_documents_info.get("formatted_for_prompt", "")
            if formatted_info:
                source = local_documents_info.get("priority_source", "地方文献")
                prompt_parts.append(f"""
## 地方文献信息（来自用户上传的{source}）
以下是来自地方文献的重要信息，请深度融入研学方案设计：

{formatted_info}
""")

        prompt_parts.append(f"""## 村庄特色
地理风貌：{', '.join(features.geography)}
历史遗迹：{', '.join(features.history)}
非遗文化：{', '.join(features.intangible_heritage)}
农耕食物：{', '.join(features.food)}
特色物产：{', '.join(features.products)}
民俗活动：{', '.join(features.customs)}
农事活动：{', '.join(features.activities)}

请生成完整的研学旅行解决方案JSON。只输出JSON，不要解释。""")

        prompt = "\n".join(prompt_parts)

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
                    print(f"JSON parse error after {retries} attempts: {e}")
                    print(f"Content length: {len(content)}")
                    return {
                        "title": f"{village.name}研学旅行解决方案",
                        "overview": {
                            "village_name": village.name,
                            "location": village.get_full_address(),
                            "county_position": "",
                            "regional_links": [],
                            "theme": "研学探索",
                            "target_audience": ["小学生", "初中生"],
                            "duration": "2天1夜",
                            "season": "春季/秋季",
                            "capacity": "30-50人/期"
                        },
                        "background": {
                            "history": "",
                            "geography": ", ".join(features.geography),
                            "culture": ", ".join(features.intangible_heritage),
                            "highlights": features.geography[:3] if features.geography else [],
                            "county_value": ""
                        },
                        "objectives": [],
                        "course_design": [],
                        "logistics": {},
                        "budget": {},
                        "evaluation": [],
                        "notes": ""
                    }
                continue
