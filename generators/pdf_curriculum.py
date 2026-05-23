"""课程体系 PDF 生成器"""
from pathlib import Path


def generate_curriculum_pdf(curriculum, features, output_path):
    philosophy = curriculum.get("philosophy", {})
    methods = curriculum.get("teaching_methods", [])
    courses = curriculum.get("course_sequence", [])
    workshops = curriculum.get("workshop_list", [])
    principles = curriculum.get("curriculum_principles", {})
    
    html = "<!DOCTYPE html><html><head><meta charset=utf-8><style>"
    html += """
    body{font-family:SimSun;margin:2cm;color:#333;line-height:1.8}
    h1{color:#27AE60;text-align:center;border-bottom:3px solid #2ECC71;padding-bottom:15px}
    h2{color:#27AE60;margin-top:35px;border-left:4px solid #2ECC71;padding-left:10px}
    h3{color:#229954;margin-top:15px}
    .cover{text-align:center;padding:40px 0;background:linear-gradient(135deg,#E8F8F5,#FFF)}
    .subtitle{color:#666;font-size:14px;margin-top:10px}
    .philosophy-box{background:#E8F8F5;padding:20px;border-radius:10px;margin:15px 0;border-left:4px solid #2ECC71}
    .value-list{display:flex;flex-wrap:wrap;gap:10px;margin:10px 0}
    .value-tag{background:#2ECC71;color:white;padding:5px 15px;border-radius:20px;font-size:13px}
    .method-card{background:#F8F9FA;padding:15px;border-radius:8px;margin:10px 0;page-break-inside:avoid}
    .method-name{color:#27AE60;font-size:16px;font-weight:bold;margin-bottom:5px}
    .method-desc{color:#555;font-size:13px}
    .method-app{background:#E8F8F5;padding:8px;border-radius:5px;font-size:12px;margin-top:5px}
    .course-table{width:100%;border-collapse:collapse;font-size:12px;margin:15px 0}
    .course-table th{background:#27AE60;color:white;padding:10px;text-align:left}
    .course-table td{padding:8px;border-bottom:1px solid #ddd;vertical-align:top}
    .course-table tr:nth-child(even){background:#F8F9FA}
    .workshop-card{background:#FFF;border:1px solid #2ECC71;border-radius:8px;padding:15px;margin:10px 0;page-break-inside:avoid}
    .workshop-header{display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #eee;padding-bottom:8px;margin-bottom:8px}
    .workshop-name{color:#27AE60;font-size:16px;font-weight:bold}
    .workshop-meta{font-size:12px;color:#666}
    .workshop-details{display:grid;grid-template-columns:1fr 1fr;gap:10px;font-size:12px}
    .workshop-item{background:#F8F9FA;padding:8px;border-radius:5px}
    .workshop-item strong{color:#229954}
    .principle-box{background:#FEF9E7;padding:15px;border-radius:8px;margin:10px 0}
    .safety-warning{background:#FDEDEC;padding:10px;border-radius:5px;border-left:3px solid #E74C3C;font-size:12px;color:#C0392B}
    """
    html += "</style></head><body>"
    
    html += f"""
    <div class="cover">
        <h1>📚 {features.name}课程体系</h1>
        <p class="subtitle">探学玩创 · 乡村研学课程体系手册</p>
    </div>
    
    <h2>一、教育理念</h2>
    <div class="philosophy-box">
        <p><strong>教育愿景</strong><br>{philosophy.get('education_vision', '')}</p>
        <p><strong>探学玩创理念</strong><br>{philosophy.get('tan_xue_wan_chuang_concept', '')}</p>
        <p><strong>核心价值</strong></p>
        <div class="value-list">
            {"".join(f'<span class="value-tag">{v}</span>' for v in philosophy.get('core_values', []))}
        </div>
        <p><strong>孩子成长</strong><br>{philosophy.get('child_growth', '')}</p>
    </div>
    
    <h2>二、执教方法</h2>
    {"".join(f'''
    <div class="method-card">
        <div class="method-name">{m.get('name', '')}</div>
        <div class="method-desc">{m.get('description', '')}</div>
        <div class="method-app"><strong>应用场景：</strong>{m.get('application', '')}</div>
        <div class="method-app"><strong>导师角色：</strong>{m.get('teacher_role', '')}</div>
    </div>
    ''' for m in methods)}
    
    <h2>三、课程序列</h2>
    <table class="course-table">
        <tr>
            <th style="width:25%">课程名称</th>
            <th>年级</th>
            <th>时长</th>
            <th>主题</th>
            <th>核心活动</th>
            <th>学习成果</th>
        </tr>
    """
    
    for c in courses:
        activities = "<br>".join(c.get('key_activities', [])[:2])
        html += f"""
        <tr>
            <td><strong>{c.get('course_name', '')}</strong></td>
            <td>{c.get('target_grade', '')}</td>
            <td>{c.get('duration', '')}</td>
            <td>{c.get('theme', '')}</td>
            <td>{activities}</td>
            <td>{c.get('learning_outcomes', '')}</td>
        </tr>
        """
    
    if not courses:
        html += "<tr><td colspan='6' style='text-align:center'>暂无课程序列</td></tr>"
    
    html += "</table>"
    
    html += f"""
    <h2>四、设计原则</h2>
    <div class="principle-box">
        <p><strong>难度梯度：</strong>{principles.get('difficulty_gradient', '从认知→体验→创造，难度递进')}</p>
        <p><strong>季节设计：</strong>{principles.get('seasonal_design', '根据四季变化设计应季课程')}</p>
        <p><strong>跨学科融合：</strong>{principles.get('interdisciplinary', '融合自然、科技、艺术、人文多学科')}</p>
    </div>
    
    <h2>五、工坊清单</h2>
    """
    
    for w in workshops:
        materials = "、".join(w.get('materials', [])[:4])
        tools = "、".join(w.get('tools', [])[:3])
        safety = w.get('safety_notes', '')
        
        html += f"""
        <div class="workshop-card">
            <div class="workshop-header">
                <span class="workshop-name">{w.get('workshop_name', '')}</span>
                <span class="workshop-meta">{w.get('age_range', '')} | {w.get('duration', '')} | 最多{w.get('max_participants', '')}人</span>
            </div>
            <p>{w.get('description', '')}</p>
            <div class="workshop-details">
                <div class="workshop-item"><strong>材料：</strong>{materials or '暂无'}</div>
                <div class="workshop-item"><strong>工具：</strong>{tools or '暂无'}</div>
                <div class="workshop-item" style="grid-column:1/-1"><strong>场地：</strong>{w.get('location', '')}</div>
            </div>
            {f'<div class="safety-warning">⚠️ 安全注意：{safety}</div>' if safety else ''}
        </div>
        """
    
    if not workshops:
        html += "<p>暂无工坊项目</p>"
    
    html += "</body></html>"
    
    from generators.pdf_utils import generate_pdf_from_html
    generate_pdf_from_html(html, output_path)
    Path(output_path.replace(".pdf", ".html")).write_text(html, encoding="utf-8")
