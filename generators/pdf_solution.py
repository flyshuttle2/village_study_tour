"""研学解决方案 PDF 生成器"""
from pathlib import Path

def generate_solution_pdf(solution, features, output_path):
    ov = solution.get("overview", {})
    bg = solution.get("background", {})
    logistics = solution.get("logistics", {})
    budget = solution.get("budget", {})
    courses = solution.get("course_design", [])
    
    courses_html = ""
    for day in courses:
        rows = ""
        for a in day.get("activities", []):
            rows += "<tr><td>" + a.get("time","") + "</td>"
            rows += "<td>" + a.get("name","") + "</td>"
            rows += "<td>" + a.get("location","") + "</td>"
            rows += "<td>" + str(a.get("duration_minutes","")) + "分钟</td>"
            rows += "<td>" + a.get("content","") + "</td>"
            rows += "<td>" + a.get("educational_value","") + "</td></tr>"
        day_html = "<div class=day-block><h2>第" + str(day.get("day","")) + "天 — " + day.get("theme","") + "</h2>"
        day_html += "<table class=act-table><thead><tr><th>时间</th><th>活动</th><th>地点</th><th>时长</th><th>内容</th><th>教育价值</th></tr></thead>"
        day_html += "<tbody>" + rows + "</tbody></table></div>"
        courses_html += day_html
    
    obj_html = "".join("<li>" + o + "</li>" for o in solution.get("objectives", []))
    budget_items = "".join("<li>" + i + "</li>" for i in budget.get("items", []))
    audience = "/".join(ov.get("target_audience", []))
    highlights = " / ".join(bg.get("highlights", []))
    
    html = "<!DOCTYPE html><html><head><meta charset=utf-8><style>"
    html += "body{font-family:SimSun;margin:2cm;color:#333}"
    html += "h1{color:#2D5016;text-align:center;border-bottom:3px solid #D4A017}"
    html += "h2{color:#27AE60;margin-top:25px}"
    html += ".grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:15px 0}"
    html += ".box{background:#F8F9FA;padding:12px;border-left:4px solid #27AE60}"
    html += "table{width:100%;border-collapse:collapse;font-size:12px;margin:10px 0}"
    html += "th{background:#2D5016;color:white;padding:8px}"
    html += "td{padding:8px;border-bottom:1px solid #ddd;vertical-align:top}"
    html += ".day-block{margin:25px 0;page-break-inside:avoid}"
    html += ".budget{background:#FFF9E6;padding:12px;border:1px solid #D4A017}"
    html += ".cover{text-align:center;padding:50px 0}.subtitle{color:#666;font-size:13px}"
    html += "</style></head><body>"
    html += "<div class=cover><h1>" + solution.get("title","研学旅行解决方案") + "</h1>"
    html += "<div class=subtitle><p>主题：" + ov.get("theme","") + " | 时长：" + ov.get("duration","") + "</p>"
    html += "<p>对象：" + audience + " | 规模：" + ov.get("capacity","") + "</p></div></div>"
    html += "<h2>一、村庄概述</h2><div class=grid>"
    html += "<div class=box><strong>地理位置：</strong>" + bg.get("geography","") + "</div>"
    html += "<div class=box><strong>历史背景：</strong>" + bg.get("history","") + "</div>"
    html += "<div class=box><strong>特色文化：</strong>" + bg.get("culture","") + "</div>"
    html += "<div class=box><strong>核心亮点：</strong>" + highlights + "</div></div>"
    obj_html = "".join("<li>" + str(o) + "</li>" for o in solution.get("objectives", []))
    budget_items = "".join("<li>" + str(i) + "</li>" for i in budget.get("items", []))
    audience = "/".join(str(x) for x in ov.get("target_audience", []))
    highlights = " / ".join(str(x) for x in bg.get("highlights", []))
    
    html = "<!DOCTYPE html><html><head><meta charset=utf-8><style>"
    html += "body{font-family:SimSun;margin:2cm;color:#333}"
    html += "h1{color:#2D5016;text-align:center;border-bottom:3px solid #D4A017}"
    html += "h2{color:#27AE60;margin-top:25px}"
    html += ".grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:15px 0}"
    html += ".box{background:#F8F9FA;padding:12px;border-left:4px solid #27AE60}"
    html += "table{width:100%;border-collapse:collapse;font-size:12px;margin:10px 0}"
    html += "th{background:#2D5016;color:white;padding:8px}"
    html += "td{padding:8px;border-bottom:1px solid #ddd;vertical-align:top}"
    html += ".day-block{margin:25px 0;page-break-inside:avoid}"
    html += ".budget{background:#FFF9E6;padding:12px;border:1px solid #D4A017}"
    html += ".cover{text-align:center;padding:50px 0}.subtitle{color:#666;font-size:13px}"
    html += "</style></head><body>"
    html += "<div class=cover><h1>" + str(solution.get("title","研学旅行解决方案")) + "</h1>"
    html += "<div class=subtitle><p>主题：" + str(ov.get("theme","")) + " | 时长：" + str(ov.get("duration","")) + "</p>"
    html += "<p>对象：" + audience + " | 规模：" + str(ov.get("capacity","")) + "</p></div></div>"
    html += "<h2>一、村庄概述</h2><div class=grid>"
    html += "<div class=box><strong>地理位置：</strong>" + str(bg.get("geography","")) + "</div>"
    html += "<div class=box><strong>历史背景：</strong>" + str(bg.get("history","")) + "</div>"
    html += "<div class=box><strong>特色文化：</strong>" + str(bg.get("culture","")) + "</div>"
    html += "<div class=box><strong>核心亮点：</strong>" + highlights + "</div></div>"
    html += "<h2>二、研学目标</h2><ul>" + obj_html + "</ul>"
    html += "<h2>三、课程安排</h2>" + courses_html
    html += "<h2>四、后勤保障</h2><div class=grid>"
    html += "<div class=box><strong>住宿：</strong>" + str(logistics.get("accommodation","")) + "</div>"
    html += "<div class=box><strong>餐饮：</strong>" + str(logistics.get("meals","")) + "</div>"
    html += "<div class=box><strong>交通：</strong>" + str(logistics.get("transportation","")) + "</div>"
    safety = logistics.get("safety","")
    if isinstance(safety, list):
        safety = "；".join(str(x) for x in safety)
    html += "<div class=box><strong>安全：</strong>" + str(safety) + "</div></div>"
    html += "<h2>五、预算参考</h2><div class=budget><p><strong>人均：</strong>" + str(budget.get("per_person","")) + "</p><ul>" + budget_items + "</ul></div>"
    html += "<h2>六、注意事项</h2><p>" + str(solution.get("notes","")) + "</p>"
    html += "</body></html>"
    
    from generators.pdf_utils import generate_pdf_from_html
    if not generate_pdf_from_html(html, output_path):
        Path(output_path.replace(".pdf", ".html")).write_text(html, encoding="utf-8")
