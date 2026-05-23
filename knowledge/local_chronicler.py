"""地方文献解析模块 - 支持村史/乡志/县志等文档，优先级：村史 > 乡志 > 县志"""
import re
from pathlib import Path
from typing import Optional, Dict, List
from dataclasses import dataclass
from enum import Enum


class DocumentType(Enum):
    VILLAGE_HISTORY = "village_history"
    TOWNSHIP_CHRONICLE = "township_chronicle"
    COUNTY_CHRONICLE = "county_chronicle"
    UNKNOWN = "unknown"


@dataclass
class LocalDocument:
    doc_type: DocumentType
    file_path: str
    raw_text: str = ""
    county_info: Dict = None
    success: bool = False
    error: str = ""
    char_count: int = 0

    def __post_init__(self):
        if self.county_info is None:
            self.county_info = {}


def detect_document_type(file_path: str, text: str = "") -> DocumentType:
    """根据文件名和内容检测文档类型
    
    优先级：村史 > 乡志 > 县志
    """
    path_lower = file_path.lower()
    
    if any(kw in path_lower for kw in ["村史", "村志", "村级", "村庄志"]):
        return DocumentType.VILLAGE_HISTORY
    
    if any(kw in path_lower for kw in ["乡志", "乡志", "镇志", "乡镇志"]):
        return DocumentType.TOWNSHIP_CHRONICLE
    
    if any(kw in path_lower for kw in ["县志", "县志", "地方志", "县志书"]):
        return DocumentType.COUNTY_CHRONICLE
    
    if text:
        text_lower = text.lower()[:1000]
        if any(kw in text_lower for kw in ["本村", "我村", "村民", "村史馆", "建村"]):
            return DocumentType.VILLAGE_HISTORY
        if any(kw in text_lower for kw in ["本乡", "我乡", "乡志"]):
            return DocumentType.TOWNSHIP_CHRONICLE
    
    return DocumentType.UNKNOWN


def extract_text_from_pdf(pdf_path: str) -> str:
    """从PDF文件提取文本内容"""
    try:
        import pymupdf
        doc = pymupdf.open(pdf_path)
        text_parts = []
        for page in doc:
            text_parts.append(page.get_text())
        doc.close()
        return "\n".join(text_parts)
    except ImportError:
        try:
            import fitz
            doc = fitz.open(pdf_path)
            text_parts = []
            for page in doc:
                text_parts.append(page.get_text())
            doc.close()
            return "\n".join(text_parts)
        except ImportError:
            return _fallback_pdf_extract(pdf_path)
    except Exception as e:
        print(f"PDF解析失败: {e}")
        return _fallback_pdf_extract(pdf_path)


def _fallback_pdf_extract(pdf_path: str) -> str:
    """备用PDF解析方案"""
    try:
        import pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)
    except ImportError:
        return f"[无法解析PDF: {pdf_path}]"


def extract_village_info(text: str, village_name: str) -> Dict[str, any]:
    """从村史文档提取村庄信息
    
    村史的特点：
    - 更聚焦于具体村庄
    - 包含村名由来、姓氏源流、重大事件、人物故事
    - 往往有口述历史、传说故事
    """
    result = {
        "doc_type": "village_history",
        "village_name": village_name,
        "name_origin": [],
        "clan_history": [],
        "historical_events": [],
        "notable_villagers": [],
        "legends_stories": [],
        "ancient_buildings": [],
        "folk_customs": [],
        "agricultural_history": [],
        "modern_changes": [],
    }
    
    if not text or len(text) < 100:
        return result
    
    sections = _split_into_sections(text)
    
    for section_title, section_content in sections:
        section_lower = section_title.lower() if section_title else ""
        content = section_content.strip()
        
        if any(k in section_lower for k in ["村名", "来历", "起源", "得名"]):
            result["name_origin"].extend(_extract_meaningful_sentences(content, village_name, max_count=3))
        elif any(k in section_lower for k in ["姓氏", "族谱", "源流", "宗族"]):
            result["clan_history"].extend(_extract_paragraphs(content, max_count=3))
        elif any(k in section_lower for k in ["大事", "纪事", "事件", "变迁"]):
            result["historical_events"].extend(_extract_events(content, max_count=5))
        elif any(k in section_lower for k in ["人物", "名人", "乡贤", "英雄"]):
            result["notable_villagers"].extend(_extract_person_stories(content, max_count=5))
        elif any(k in section_lower for k in ["传说", "故事", "典故", "轶事"]):
            result["legends_stories"].extend(_extract_stories(content, max_count=3))
        elif any(k in section_lower for k in ["古建", "建筑", "祠堂", "庙宇", "古树"]):
            result["ancient_buildings"].extend(_extract_site_items(content, max_count=5))
        elif any(k in section_lower for k in ["民俗", "风俗", "节庆", "祭祀"]):
            result["folk_customs"].extend(_extract_custom_items(content, max_count=5))
        elif any(k in section_lower for k in ["农耕", "农业", "生产", "作物"]):
            result["agricultural_history"].extend(_extract_paragraphs(content, max_count=3))
        elif any(k in section_lower for k in ["当代", "现代", "改革", "新貌"]):
            result["modern_changes"].extend(_extract_paragraphs(content, max_count=3))
    
    for key in result:
        result[key] = list(dict.fromkeys(result[key]))[:10]
    
    return result


def extract_county_info(text: str, county_name: str) -> Dict[str, any]:
    """从县志提取县域信息"""
    result = {
        "doc_type": "county_chronicle",
        "county_name": county_name,
        "history": [],
        "geography": [],
        "notable_figures": [],
        "intangible_heritage": [],
        "specialty_products": [],
        "folk_customs": [],
        "historical_sites": [],
        "famous_foods": [],
    }
    
    if not text or len(text) < 100:
        return result
    
    sections = _split_into_sections(text)
    
    for section_title, section_content in sections:
        section_lower = section_title.lower() if section_title else ""
        
        if any(k in section_lower for k in ["历史", "沿革", "建制"]):
            result["history"].extend(_extract_meaningful_sentences(section_content, county_name, max_count=5))
        elif any(k in section_lower for k in ["地理", "山川", "地貌", "气候"]):
            result["geography"].extend(_extract_meaningful_sentences(section_content, county_name, max_count=5))
        elif any(k in section_lower for k in ["人物", "名流", "乡贤"]):
            result["notable_figures"].extend(_extract_notable_figures(section_content))
        elif any(k in section_lower for k in ["非遗", "民俗", "民间", "技艺"]):
            result["intangible_heritage"].extend(_extract_heritage_items(section_content))
        elif any(k in section_lower for k in ["物产", "特产", "资源"]):
            result["specialty_products"].extend(_extract_product_items(section_content))
        elif any(k in section_lower for k in ["风俗", "民风", "节庆"]):
            result["folk_customs"].extend(_extract_custom_items(section_content))
        elif any(k in section_lower for k in ["古迹", "遗址", "建筑"]):
            result["historical_sites"].extend(_extract_site_items(section_content))
        elif any(k in section_lower for k in ["美食", "饮食", "风味"]):
            result["famous_foods"].extend(_extract_food_items(section_content))
    
    for key in result:
        result[key] = list(dict.fromkeys(result[key]))[:20]
    
    return result


def _split_into_sections(text: str) -> List[tuple]:
    """将文本按章节分割"""
    section_patterns = [
        r"第[一二三四五六七八九十百]+[章节篇部编]",
        r"\n[一二三四五六七八九十百]+[、.、](?!\d)",
        r"\n【[^】]+】",
        r"\n[^\n]{2,30}\n={3,}",
    ]
    
    sections = []
    current_title = "概述"
    current_content = ""
    
    lines = text.split("\n")
    for line in lines:
        is_section_start = False
        for pattern in section_patterns:
            if re.search(pattern, line):
                if current_content.strip():
                    sections.append((current_title, current_content))
                current_title = line.strip()
                current_content = ""
                is_section_start = True
                break
        
        if not is_section_start:
            current_content += line + "\n"
    
    if current_content.strip():
        sections.append((current_title, current_content))
    
    return sections


def _extract_meaningful_sentences(text: str, keyword: str, max_count: int = 5) -> List[str]:
    """提取包含关键词的有意义的句子"""
    sentences = re.split(r'[。！？；\n]', text)
    meaningful = []
    
    for s in sentences:
        s = s.strip()
        if len(s) > 10 and len(s) < 200 and keyword in s:
            clean = re.sub(r'\s+', ' ', s)
            if clean not in meaningful:
                meaningful.append(clean)
        
        if len(meaningful) >= max_count:
            break
    
    return meaningful


def _extract_paragraphs(text: str, max_count: int = 3) -> List[str]:
    """提取有意义的段落"""
    paragraphs = [p.strip() for p in re.split(r'\n\n+', text) if len(p.strip()) > 30]
    return paragraphs[:max_count]


def _extract_events(text: str, max_count: int = 5) -> List[str]:
    """提取历史事件"""
    events = []
    patterns = [
        r'[一二三四五六七八九十百0-9]{2,4}年[^。！？\n]{5,50}',
        r'(?:于|在)[^。！？\n]{5,30}年[^。！？\n]{3,30}',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text)
        for m in matches:
            if len(m) > 10:
                events.append(m.strip())
    
    return list(dict.fromkeys(events))[:max_count]


def _extract_person_stories(text: str, max_count: int = 5) -> List[str]:
    """提取人物故事"""
    stories = []
    paragraphs = [p.strip() for p in re.split(r'\n\n+', text) if len(p.strip()) > 20]
    
    for p in paragraphs[:10]:
        if len(p) < 200:
            stories.append(p)
        else:
            sentences = re.split(r'[。！？]', p)
            for s in sentences:
                if len(s) > 15 and len(s) < 150:
                    stories.append(s.strip())
    
    return list(dict.fromkeys(stories))[:max_count]


def _extract_stories(text: str, max_count: int = 3) -> List[str]:
    """提取传说故事"""
    stories = []
    paragraphs = [p.strip() for p in re.split(r'\n\n+', text) if len(p.strip()) > 50]
    
    for p in paragraphs[:5]:
        clean = re.sub(r'\s+', ' ', p)
        if len(clean) > 50:
            stories.append(clean[:200])
    
    return list(dict.fromkeys(stories))[:max_count]


def _extract_notable_figures(text: str) -> List[str]:
    """提取人物信息"""
    figures = []
    patterns = [
        r'([^，。！？]{2,6})(?:字|号|世称|被称为)[^，。！？]{2,15}',
        r'([^，。！？]{2,6})(?:为|是|称)(?:著名|代|代|历史)[^，。！？]{5,20}',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text)
        for m in matches:
            if len(m) > 2 and len(m) < 15:
                figures.append(m)
    
    return list(dict.fromkeys(figures))[:10]


def _extract_heritage_items(text: str) -> List[str]:
    """提取非遗项目"""
    items = []
    patterns = [
        r'(?:传统|手工|民间|省级|国家级)(?:[^\s，、。！？]{2,10}技艺|[^\s，、。！？]{2,10}工艺)',
        r'([^\s，。！？]{2,6})(?:技艺|工艺|制作技艺|营造技艺)',
        r'(?:列入|被评为)(?:省级|国家级|市级)[^\s，。！？]{5,15}',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text)
        for m in matches:
            if len(m) > 3:
                items.append(m.strip())
    
    return list(dict.fromkeys(items))[:10]


def _extract_product_items(text: str) -> List[str]:
    """提取特产物产"""
    items = []
    patterns = [
        r'(?:著名|特产|优质|传统)[的之]([^\s，、。！？]{2,8})',
        r'([^\s，。！？]{2,6})(?:茶|酒|米|果|药|油|丝|竹|瓷)',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text)
        for m in matches:
            if len(m) > 1:
                items.append(m.strip())
    
    return list(dict.fromkeys(items))[:10]


def _extract_custom_items(text: str) -> List[str]:
    """提取民俗活动"""
    items = []
    patterns = [
        r'([^\s，。！？]{2,8})(?:节|会|俗|祭|舞|戏|歌)',
        r'(?:传统|民俗|民间)[的之]([^\s，。！？]{2,8})',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text)
        for m in matches:
            if len(m) > 1 and len(m) < 10:
                items.append(m.strip())
    
    return list(dict.fromkeys(items))[:10]


def _extract_site_items(text: str) -> List[str]:
    """提取历史遗迹"""
    items = []
    patterns = [
        r'([^\s，。！？]{2,8})(?:古村|古建|古宅|古桥|古塔|祠堂|庙宇|遗址)',
        r'(?:省级|国家级|市级)[^\s，。！？]{3,8}(?:保护单位|文物|古迹)',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text)
        for m in matches:
            if len(m) > 2:
                items.append(m.strip())
    
    return list(dict.fromkeys(items))[:10]


def _extract_food_items(text: str) -> List[str]:
    """提取美食"""
    items = []
    patterns = [
        r'([^\s，。！？]{2,8})(?:面|饭|糕|饼|酒|茶|汤|菜)',
        r'(?:特色|传统|著名|风味)[的之]([^\s，。！？]{2,8})',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text)
        for m in matches:
            if len(m) > 1:
                items.append(m.strip())
    
    return list(dict.fromkeys(items))[:10]


def format_for_prompt(doc_info: Dict, target_name: str, doc_type: DocumentType) -> str:
    """将解析结果格式化为prompt可用的文本
    
    Args:
        doc_info: 解析出的文档信息字典
        target_name: 目标名称（村名或县名）
        doc_type: 文档类型
    """
    lines = []
    doc_type_name = {
        DocumentType.VILLAGE_HISTORY: "村史",
        DocumentType.TOWNSHIP_CHRONICLE: "乡志",
        DocumentType.COUNTY_CHRONICLE: "县志",
        DocumentType.UNKNOWN: "地方文献"
    }.get(doc_type, "地方文献")
    
    lines.append("=" * 40)
    lines.append(f"【{target_name}{doc_type_name}关键信息】")
    lines.append("=" * 40)
    
    if doc_type == DocumentType.VILLAGE_HISTORY:
        if doc_info.get("name_origin"):
            lines.append("\n【村名由来】")
            for item in doc_info["name_origin"][:3]:
                lines.append(f"  • {item}")
        
        if doc_info.get("clan_history"):
            lines.append("\n【姓氏源流】")
            for item in doc_info["clan_history"][:3]:
                lines.append(f"  • {item[:100]}")
        
        if doc_info.get("historical_events"):
            lines.append("\n【历史大事】")
            for item in doc_info["historical_events"][:5]:
                lines.append(f"  • {item}")
        
        if doc_info.get("notable_villagers"):
            lines.append("\n【村庄人物】")
            for item in doc_info["notable_villagers"][:5]:
                lines.append(f"  • {item[:100]}")
        
        if doc_info.get("legends_stories"):
            lines.append("\n【传说故事】")
            for item in doc_info["legends_stories"][:3]:
                lines.append(f"  • {item[:150]}")
        
        if doc_info.get("ancient_buildings"):
            lines.append("\n【古建筑】")
            for item in doc_info["ancient_buildings"][:5]:
                lines.append(f"  • {item}")
        
        if doc_info.get("folk_customs"):
            lines.append("\n【民俗风情】")
            for item in doc_info["folk_customs"][:5]:
                lines.append(f"  • {item}")
        
        if doc_info.get("agricultural_history"):
            lines.append("\n【农耕历史】")
            for item in doc_info["agricultural_history"][:3]:
                lines.append(f"  • {item[:100]}")
    
    else:
        if doc_info.get("history"):
            lines.append("\n【历史沿革】")
            for h in doc_info["history"][:5]:
                lines.append(f"  • {h}")
        
        if doc_info.get("geography"):
            lines.append("\n【地理风貌】")
            for g in doc_info["geography"][:5]:
                lines.append(f"  • {g}")
        
        if doc_info.get("notable_figures"):
            lines.append("\n【历史人物】")
            for f in doc_info["notable_figures"][:5]:
                lines.append(f"  • {f}")
        
        if doc_info.get("intangible_heritage"):
            lines.append("\n【非物质文化遗产】")
            for h in doc_info["intangible_heritage"][:5]:
                lines.append(f"  • {h}")
        
        if doc_info.get("specialty_products"):
            lines.append("\n【特色物产】")
            for p in doc_info["specialty_products"][:5]:
                lines.append(f"  • {p}")
        
        if doc_info.get("folk_customs"):
            lines.append("\n【民俗风情】")
            for c in doc_info["folk_customs"][:5]:
                lines.append(f"  • {c}")
        
        if doc_info.get("historical_sites"):
            lines.append("\n【历史遗迹】")
            for s in doc_info["historical_sites"][:5]:
                lines.append(f"  • {s}")
        
        if doc_info.get("famous_foods"):
            lines.append("\n【特色美食】")
            for f in doc_info["famous_foods"][:5]:
                lines.append(f"  • {f}")
    
    return "\n".join(lines)


def parse_local_document(pdf_path: str, target_name: str) -> LocalDocument:
    """解析地方文献的完整流程
    
    支持村史/乡志/县志，根据内容自动识别类型
    
    Args:
        pdf_path: PDF文件路径
        target_name: 目标名称（村名或县名）
        
    Returns:
        LocalDocument 对象
    """
    if not Path(pdf_path).exists():
        return LocalDocument(
            doc_type=DocumentType.UNKNOWN,
            file_path=pdf_path,
            success=False,
            error=f"文件不存在: {pdf_path}"
        )
    
    try:
        raw_text = extract_text_from_pdf(pdf_path)
        doc_type = detect_document_type(pdf_path, raw_text)
        
        if len(raw_text) < 500:
            return LocalDocument(
                doc_type=doc_type,
                file_path=pdf_path,
                raw_text=raw_text,
                success=False,
                error="PDF文本提取内容过少，可能无法解析"
            )
        
        if doc_type == DocumentType.VILLAGE_HISTORY:
            doc_info = extract_village_info(raw_text, target_name)
        else:
            doc_info = extract_county_info(raw_text, target_name)
        
        formatted_text = format_for_prompt(doc_info, target_name, doc_type)
        
        return LocalDocument(
            doc_type=doc_type,
            file_path=pdf_path,
            raw_text=raw_text[:50000],
            county_info=doc_info,
            success=True,
            char_count=len(raw_text)
        )
        
    except Exception as e:
        return LocalDocument(
            doc_type=DocumentType.UNKNOWN,
            file_path=pdf_path,
            success=False,
            error=str(e)
        )


def merge_documents(documents: List[LocalDocument], village_name: str, county_name: str) -> Dict:
    """合并多个地方文献的信息
    
    优先级：村史 > 乡志 > 县志
    相同字段，村史优先
    """
    merged = {
        "village_name": village_name,
        "county_name": county_name,
        "village_history": {},
        "township_chronicle": {},
        "county_chronicle": {},
        "merged_info": {},
        "priority_source": None
    }
    
    sorted_docs = sorted(documents, key=lambda d: {
        DocumentType.VILLAGE_HISTORY: 0,
        DocumentType.TOWNSHIP_CHRONICLE: 1,
        DocumentType.COUNTY_CHRONICLE: 2,
        DocumentType.UNKNOWN: 3
    }.get(d.doc_type, 3))
    
    for doc in sorted_docs:
        if doc.doc_type == DocumentType.VILLAGE_HISTORY:
            merged["village_history"] = doc.county_info
            if not merged["priority_source"]:
                merged["priority_source"] = "村史"
        elif doc.doc_type == DocumentType.TOWNSHIP_CHRONICLE:
            merged["township_chronicle"] = doc.county_info
            if not merged["priority_source"]:
                merged["priority_source"] = "乡志"
        elif doc.doc_type == DocumentType.COUNTY_CHRONICLE:
            merged["county_chronicle"] = doc.county_info
            if not merged["priority_source"]:
                merged["priority_source"] = "县志"
    
    merged["merged_info"] = {
        **merged["county_chronicle"],
        **merged["township_chronicle"],
        **merged["village_history"]
    }
    
    merged["formatted_for_prompt"] = format_merged_for_prompt(merged)
    
    return merged


def format_merged_for_prompt(merged: Dict) -> str:
    """将合并结果格式化为prompt"""
    lines = []
    lines.append("=" * 50)
    lines.append(f"【{merged['village_name']}地方文献综合信息】")
    lines.append(f"（主要参考来源：{merged.get('priority_source', '综合') or '综合'})")
    lines.append("=" * 50)
    
    if merged.get("village_history"):
        lines.append("\n--- 来自村史 ---")
        vh = merged["village_history"]
        for key, value in vh.items():
            if value and key != "doc_type" and key != "village_name":
                key_name = {
                    "name_origin": "村名由来",
                    "clan_history": "姓氏源流", 
                    "historical_events": "历史大事",
                    "notable_villagers": "村庄人物",
                    "legends_stories": "传说故事",
                    "ancient_buildings": "古建筑",
                    "folk_customs": "民俗风情",
                    "agricultural_history": "农耕历史",
                    "modern_changes": "当代变迁"
                }.get(key, key)
                lines.append(f"\n【{key_name}】")
                for item in (value if isinstance(value, list) else [value])[:5]:
                    lines.append(f"  • {str(item)[:150]}")
    
    if merged.get("township_chronicle"):
        lines.append("\n--- 来自乡志 ---")
        th = merged["township_chronicle"]
        for key, value in th.items():
            if value and key not in ["doc_type", "county_name"]:
                lines.append(f"  • {str(value)[:100]}")
    
    if merged.get("county_chronicle"):
        lines.append("\n--- 来自县志 ---")
        ch = merged["county_chronicle"]
        for key, value in ch.items():
            if value and key not in ["doc_type", "county_name"]:
                lines.append(f"  • {str(value)[:100]}")
    
    return "\n".join(lines)
