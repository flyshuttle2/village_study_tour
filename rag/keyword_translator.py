"""
关键词转译引擎
负责关键词解析、关联度计算、课程匹配
"""

from typing import List, Dict, Optional
from rag.keyword_registry import (
    KEYWORD_COURSES, 
    KEYWORD_CATEGORIES,
    RURAL_FEATURES,
    UNRELATED_PATTERNS,
    MIN_RELEVANCE_THRESHOLD,
    MAX_COURSES
)


def calculate_relevance(keyword: str) -> float:
    """
    计算关键词与乡村研学的关联度
    返回 0.0 ~ 1.0
    """
    if not keyword or not keyword.strip():
        return 0.0
    
    keyword = keyword.strip()
    
    # 1. 精确匹配预设关键词
    if keyword in KEYWORD_COURSES:
        return KEYWORD_COURSES[keyword]["relevance"]
    
    # 2. 计算特征匹配分数
    score = 0.0
    
    # 包含乡村特征字符
    for char in keyword:
        if char in RURAL_FEATURES:
            score += 0.12
    
    # 匹配类别关键词
    for category, category_keywords in KEYWORD_CATEGORIES.items():
        for kw in category_keywords:
            if kw in keyword or keyword in kw:
                score += 0.3
                break
    
    # 包含活动特征词
    activity_keywords = ["体验", "制作", "学习", "探究", "挑战", "工作坊", "探秘", "观察", "传承"]
    for act_kw in activity_keywords:
        if act_kw in keyword:
            score += 0.15
            break
    
    # 特定主题词增强
    theme_boosters = ["传统", "非遗", "文化", "手工", "户外", "自然"]
    for booster in theme_boosters:
        if booster in keyword:
            score += 0.1
            break
    
    # 3. 惩罚项（明显不相关）
    for pattern in UNRELATED_PATTERNS:
        if pattern in keyword:
            score -= 0.6
            break
    
    return max(0.0, min(1.0, score))


def detect_category(keyword: str) -> Optional[str]:
    """识别关键词所属类别"""
    for category, category_keywords in KEYWORD_CATEGORIES.items():
        for kw in category_keywords:
            if kw in keyword or keyword in kw:
                return category
    return None


def parse_keywords(keyword_string: str) -> List[str]:
    """解析关键词字符串，按空格分隔"""
    if not keyword_string:
        return []
    return [kw.strip() for kw in keyword_string.split() if kw.strip()]


def filter_keywords(keywords: List[str]) -> List[str]:
    """过滤出高关联度关键词"""
    return [kw for kw in keywords if calculate_relevance(kw) >= MIN_RELEVANCE_THRESHOLD]


def match_courses(keyword: str) -> List[Dict]:
    """
    匹配关键词对应的课程
    返回课程配置列表
    """
    courses = []
    
    # 精确匹配
    if keyword in KEYWORD_COURSES:
        courses.extend(KEYWORD_COURSES[keyword]["courses"])
    
    return courses


def translate_keywords(keyword_string: str) -> Dict:
    """
    关键词转译主函数
    输入: "土豆 石拱廊桥 黄酒"
    输出: {
        "valid_keywords": ["土豆", "石拱廊桥", "黄酒"],
        "rejected_keywords": [],
        "courses": [课程配置列表],
        "total_count": 3
    }
    """
    keywords = parse_keywords(keyword_string)
    
    valid_keywords = []
    rejected_keywords = []
    all_courses = []
    
    for kw in keywords:
        relevance = calculate_relevance(kw)
        if relevance >= MIN_RELEVANCE_THRESHOLD:
            valid_keywords.append(kw)
            courses = match_courses(kw)
            all_courses.extend(courses)
        else:
            rejected_keywords.append(kw)
    
    # 限制课程数量
    all_courses = all_courses[:MAX_COURSES]
    
    rejection_message = ""
    if rejected_keywords:
        rejection_message = f"以下关键词与乡村研学关联度较低，已忽略：{', '.join(rejected_keywords)}"
    
    return {
        "valid_keywords": valid_keywords,
        "rejected_keywords": rejected_keywords,
        "courses": all_courses,
        "total_count": len(all_courses),
        "rejection_message": rejection_message
    }


def get_keyword_info(keyword: str) -> Optional[Dict]:
    """获取关键词的详细信息"""
    if keyword in KEYWORD_COURSES:
        return {
            "keyword": keyword,
            "category": KEYWORD_COURSES[keyword]["category"],
            "relevance": KEYWORD_COURSES[keyword]["relevance"],
            "course_count": len(KEYWORD_COURSES[keyword]["courses"]),
            "courses": [c["name"] for c in KEYWORD_COURSES[keyword]["courses"]]
        }
    else:
        category = detect_category(keyword)
        if category:
            return {
                "keyword": keyword,
                "category": category,
                "relevance": calculate_relevance(keyword),
                "course_count": 1,
                "courses": [f"{keyword}体验课"]
            }
    return None


def preview_keyword_courses(keyword_string: str) -> str:
    """预览关键词将生成的课程（用于UI显示）"""
    result = translate_keywords(keyword_string)
    
    if not result["valid_keywords"]:
        return "未检测到有效的乡村研学关键词"
    
    lines = []
    lines.append(f"检测到 {len(result['valid_keywords'])} 个有效关键词，将生成 {result['total_count']} 个课程：\n")
    
    for kw in result["valid_keywords"]:
        info = get_keyword_info(kw)
        if info:
            lines.append(f"• {kw}（{info['category']}）→ {', '.join(info['courses'])}")
    
    if result["rejected_keywords"]:
        lines.append(f"\n{result['rejection_message']}")
    
    return "\n".join(lines)


if __name__ == "__main__":
    # 测试
    test_input = "土豆 石拱廊桥 无人机 编程"
    result = translate_keywords(test_input)
    print(f"输入: {test_input}")
    print(f"有效关键词: {result['valid_keywords']}")
    print(f"忽略关键词: {result['rejected_keywords']}")
    print(f"生成课程数: {result['total_count']}")
    for course in result["courses"]:
        print(f"  - {course['name']} ({course['type']})")
    print(f"\n{result['rejection_message']}")
