import json
from openai import OpenAI
from config import MINIMAX_API_KEY, BASE_URL, LLM_MODEL


SYSTEM_PROMPT = """你是一个乡村研学策展专家，擅长用"探学玩创"的理念设计乡村主题展览。

## 策展理念（参考凡朴"米的N次方"展览）

### 探学玩创四大展馆
- **探（探索发现馆）**：一步一景的沉浸式探索，用探索卡引导发现
- **学（知识学习馆）**：互动展板、实物展示、知识讲解
- **玩（游戏体验馆）**：AR/VR互动、闯关游戏、手作工坊
- **创（创意成果馆）**：作品展示、文创商店、拍照打卡

### 感官体验设计
- **视觉**：大面积插画、数字媒体、卡通风格
- **听觉**：自然音效、环境音乐、互动声音反馈
- **触觉**：实物感知、手作体验、互动装置
- **味觉**：特色美食体验、食育工坊

### 策展语言风格
用亲和、有趣的语言面向孩子和家长，避免过于专业的策展术语。

## 输出格式（严格JSON）
{
    "curatorial_theme": "策展主题定位（一句吸引人的话）",
    "theme_story": "策展故事线（用孩子的语言讲述）",
    "target_audience": ["亲子家庭", "学校研学", "成人团建"],
    "exhibition_zones": [
        {
            "zone_name": "XX馆（如：探 · 秘密花园）",
            "zone_icon": "emoji图标",
            "tan_xue_wan_chuang_tag": "探/学/玩/创",
            "narrative": "展馆故事线（孩子的语言）",
            "key_exhibits": ["主要展品1", "主要展品2"],
            "interactive_nodes": ["互动体验点1", "互动体验点2"],
            "workshop_items": ["工坊体验项目"]
        }
    ],
    "sensory_design": {
        "visual": "视觉风格描述（如：卡通插画风格、自然田野色调）",
        "audio": "声音场景描述（如：溪水声、鸟鸣声、风声）",
        "tactile": "触觉体验点（如：触摸稻穗感受粗糙、触摸陶泥感受细腻）",
        "taste": "味觉体验（如：品尝特色米食、农家点心）"
    },
    "visitor_flow": "动线设计说明（建议游览顺序）",
    "installation_list": [
        {"name": "装置名称", "location": "位置", "interaction": "交互方式", "type": "装饰型/互动型/拍照型"}
    ],
    "cultural_products": ["文创开发方向1", "文创开发方向2"],
    "photo_spots": ["拍照打卡点1", "拍照打卡点2"],
    "engagement_elements": ["留客元素（探索卡/印章/抽奖等）"]
}

## 要求
- 展馆数量建议3-4个
- 每个展馆对应探学玩创的一个或多个环节
- 动线设计要符合游览逻辑
- 语言风格亲和有趣，面向孩子
- 不可虚构，基于村庄特色设计"""


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


class ExhibitionAgent:
    def __init__(self, api_key=None):
        api_key = api_key or MINIMAX_API_KEY
        self.client = OpenAI(api_key=api_key, base_url=BASE_URL)
        self.model = LLM_MODEL

    def generate(self, features, solution=None, retries=3):
        village_info = f"""村名：{features.name}
地理位置：{features.location}

村庄特色：
- 地理风貌：{', '.join(features.geography[:3])}
- 非遗文化：{', '.join(features.intangible_heritage[:3])}
- 特色食物：{', '.join(features.food[:3])}
- 特色物产：{', '.join(features.products[:3])}
- 民俗活动：{', '.join(features.customs[:3])}
"""
        
        if solution:
            theme = solution.get("overview", {}).get("theme", "")
            if theme:
                village_info += f"\n研学主题：{theme}"
        
        prompt = village_info + "\n\n请根据以上村庄特色，设计一份完整的策展方案JSON。只输出JSON，不要解释。"

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
                    print(f"Exhibition JSON parse error: {e}")
                    return self._default_exhibition(features)
                continue
        
        return self._default_exhibition(features)
    
    def _default_exhibition(self, features):
        return {
            "curatorial_theme": f"走进{features.name}",
            "theme_story": f"欢迎来到{features.name}，这里有很多有趣的故事等着我们去发现！",
            "target_audience": ["亲子家庭", "学校研学"],
            "exhibition_zones": [
                {
                    "zone_name": "探 · 发现之旅",
                    "zone_icon": "🔍",
                    "tan_xue_wan_chuang_tag": "探",
                    "narrative": "带上探索卡，开启发现之旅",
                    "key_exhibits": ["村庄地图", "特色展品"],
                    "interactive_nodes": ["探索卡打卡"],
                    "workshop_items": []
                },
                {
                    "zone_name": "学 · 知识乐园",
                    "zone_icon": "📚",
                    "tan_xue_wan_chuang_tag": "学",
                    "narrative": "边玩边学，收获知识",
                    "key_exhibits": ["互动展板", "实物展示"],
                    "interactive_nodes": ["知识问答机"],
                    "workshop_items": []
                },
                {
                    "zone_name": "玩 · 快乐时光",
                    "zone_icon": "🎮",
                    "tan_xue_wan_chuang_tag": "玩",
                    "narrative": "动手又动脑，好玩又有趣",
                    "key_exhibits": ["游戏装置"],
                    "interactive_nodes": ["互动游戏"],
                    "workshop_items": ["手作体验"]
                },
                {
                    "zone_name": "创 · 我最棒",
                    "zone_icon": "🎨",
                    "tan_xue_wan_chuang_tag": "创",
                    "narrative": "发挥想象力，创造独一无二的作品",
                    "key_exhibits": ["作品展示"],
                    "interactive_nodes": [],
                    "workshop_items": ["创作工坊"]
                }
            ],
            "sensory_design": {
                "visual": "温馨可爱的卡通风格",
                "audio": "自然环境音效",
                "tactile": "触摸自然材料",
                "taste": "品尝特色美食"
            },
            "visitor_flow": "入口→探索馆→学习馆→体验馆→创作馆→出口",
            "installation_list": [],
            "cultural_products": [],
            "photo_spots": [],
            "engagement_elements": ["探索卡", "印章收集"]
        }
