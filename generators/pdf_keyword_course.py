"""
关键词课程 PDF 生成器
将课程数据生成为可下载的 PDF 文档
"""

from pathlib import Path
from generators.pdf_utils import generate_pdf_from_html


def generate_keyword_course_pdf(courses: list, village_name: str, output_path: str) -> bool:
    """
    生成关键词课程 PDF
    
    参数:
        courses: 课程列表
        village_name: 村庄名称
        output_path: 输出文件路径
    
    返回:
        bool: 是否生成成功
    """
    if not courses:
        return False
    
    html = _build_course_html(courses, village_name)
    return generate_pdf_from_html(html, output_path)


def generate_keyword_course_markdown(courses: list, village_name: str, output_path: str) -> bool:
    """
    生成关键词课程 Markdown 文档
    
    参数:
        courses: 课程列表
        village_name: 村庄名称
        output_path: 输出文件路径
    
    返回:
        bool: 是否生成成功
    """
    if not courses:
        return False
    
    md = _build_course_markdown(courses, village_name)
    try:
        Path(output_path).write_text(md, encoding="utf-8")
        return True
    except Exception as e:
        print(f"Markdown generation failed: {e}")
        return False


def _build_course_html(courses: list, village_name: str) -> str:
    """构建课程 HTML"""
    
    course_blocks = ""
    for i, course in enumerate(courses, 1):
        activities_html = ""
        for activity in course.get("activities", []):
            activities_html += f"""
            <tr>
                <td>{activity.get('name', '')}</td>
                <td>{activity.get('duration', 0)}分钟</td>
                <td>{activity.get('content', '')}</td>
            </tr>
            """
        
        materials_list = "、".join(course.get('materials', [])) if course.get('materials') else "待定"
        safety_list = "".join(f"<li>{s}</li>" for s in course.get('safety', [])) if course.get('safety') else "<li>遵守活动规则</li>"
        
        course_blocks += f"""
        <div class="course-block">
            <h2>课程 {i}：{course.get('name', '')}</h2>
            
            <div class="course-meta">
                <span class="tag type">{course.get('type', '')}</span>
                <span class="tag grade">{course.get('grade_level', '')}</span>
                <span class="tag duration">{course.get('duration_minutes', 0)}分钟</span>
            </div>
            
            <h3>一、课程目标</h3>
            <ul>
                <li><strong>知识目标：</strong>{course.get('objectives', {}).get('知识', '了解相关知识')}</li>
                <li><strong>能力目标：</strong>{course.get('objectives', {}).get('能力', '掌握相关技能')}</li>
                <li><strong>情感目标：</strong>{course.get('objectives', {}).get('情感', '培养相关情感')}</li>
            </ul>
            
            <h3>二、活动流程</h3>
            <table class="activity-table">
                <thead>
                    <tr>
                        <th>活动名称</th>
                        <th>时长</th>
                        <th>活动内容</th>
                    </tr>
                </thead>
                <tbody>
                    {activities_html}
                </tbody>
            </table>
            
            <h3>三、所需材料</h3>
            <p>{materials_list}</p>
            
            <h3>四、安全注意事项</h3>
            <ul>
                {safety_list}
            </ul>
        </div>
        """
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{ font-family: SimSun, serif; margin: 2cm; color: #333; line-height: 1.6; }}
        h1 {{ color: #2D5016; text-align: center; border-bottom: 3px solid #2D5016; padding-bottom: 15px; margin-bottom: 30px; }}
        h2 {{ color: #27AE60; margin-top: 35px; border-left: 4px solid #27AE60; padding-left: 10px; }}
        h3 {{ color: #2D5016; margin-top: 25px; font-size: 16px; }}
        .course-block {{ margin-bottom: 50px; page-break-inside: avoid; background: #fafafa; padding: 20px; border-radius: 8px; }}
        .course-meta {{ margin: 15px 0; display: flex; gap: 10px; flex-wrap: wrap; }}
        .tag {{ display: inline-block; padding: 5px 15px; border-radius: 20px; margin-right: 10px; font-size: 12px; }}
        .tag.type {{ background: #E8F5EE; color: #2D5016; }}
        .tag.grade {{ background: #FDEEE9; color: #D94F30; }}
        .tag.duration {{ background: #E4F2F7; color: #2A7B9B; }}
        table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background: #2D5016; color: white; }}
        tr:nth-child(even) {{ background: #f9f9f9; }}
        ul {{ margin: 10px 0; padding-left: 25px; }}
        li {{ margin: 8px 0; }}
        p {{ margin: 10px 0; }}
        .footer {{ margin-top: 40px; text-align: center; color: #999; font-size: 12px; border-top: 1px solid #eee; padding-top: 20px; }}
    </style>
</head>
<body>
    <h1>{village_name}研学体验课程</h1>
    <p style="text-align:center;color:#666;font-size:14px">基于关键词生成的特色研学体验课程</p>
    
    {course_blocks}
    
    <div class="footer">
        <p>本课程文档由 AI 辅助生成，可根据实际情况调整</p>
    </div>
</body>
</html>"""
    
    return html


def _build_course_markdown(courses: list, village_name: str) -> str:
    """构建课程 Markdown"""
    
    lines = [f"# {village_name}研学体验课程\n"]
    lines.append("> 基于关键词生成的特色研学体验课程\n")
    
    for i, course in enumerate(courses, 1):
        lines.append(f"## 课程 {i}：{course.get('name', '')}\n")
        
        lines.append(f"- **类型**：{course.get('type', '')}")
        lines.append(f"- **适用年级**：{course.get('grade_level', '')}")
        lines.append(f"- **课时时长**：{course.get('duration_minutes', 0)}分钟\n")
        
        lines.append("### 一、课程目标\n")
        objectives = course.get('objectives', {})
        lines.append(f"- **知识目标**：{objectives.get('知识', '了解相关知识')}")
        lines.append(f"- **能力目标**：{objectives.get('能力', '掌握相关技能')}")
        lines.append(f"- **情感目标**：{objectives.get('情感', '培养相关情感')}\n")
        
        lines.append("### 二、活动流程\n")
        lines.append("| 活动名称 | 时长 | 活动内容 |")
        lines.append("|---------|------|----------|")
        for activity in course.get('activities', []):
            lines.append(f"| {activity.get('name', '')} | {activity.get('duration', 0)}分钟 | {activity.get('content', '')} |")
        lines.append("")
        
        lines.append("### 三、所需材料\n")
        materials = "、".join(course.get('materials', [])) if course.get('materials') else "待定"
        lines.append(f"{materials}\n")
        
        lines.append("### 四、安全注意事项\n")
        for s in course.get('safety', []):
            lines.append(f"- {s}")
        lines.append("")
        lines.append("---\n")
    
    lines.append("\n*本课程文档由 AI 辅助生成，可根据实际情况调整*\n")
    
    return "\n".join(lines)
