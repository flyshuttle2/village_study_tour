"""营地手册 PDF 生成器"""
from pathlib import Path

def generate_camp_manual_pdf(manual, features, season, output_path):
    ov = manual.get("overview", {})
    daily = manual.get("daily_schedule", [])
    lg = manual.get("living_guide", {})
    safety = manual.get("safety", {})
    pn = manual.get("parent_notice", {})
    ev = manual.get("evaluation", {})
    
    days_html = ""
    for d in daily:
        days_html += "<div class=day-card><h3>第" + str(d.get("day","")) + "天 — " + d.get("theme","") + "</h3>"
        days_html += "<p>" + d.get("summary","") + "</p></div>"
    
    title = manual.get("title", features.name + season + "令营研学手册")
    html = "<!DOCTYPE html><html><head><meta charset=utf-8><style>"
    html += "body{font-family:SimSun;margin:2cm;color:#333}"
    html += "h1{color:#2D5016;text-align:center;border-bottom:3px solid #D4A017}"
    html += "h2{color:#27AE60;margin-top:22px}"
    html += ".cover{text-align:center;padding:40px 0}"
    html += ".info-box{background:#F8F9FA;padding:12px;margin:10px 0}"
    html += ".day-card{background:#FDFEFE;border:1px solid #ddd;padding:12px;margin:8px 0}"
    html += "table{width:100%;border-collapse:collapse;font-size:12px}"
    html += "th{background:#2D5016;color:white;padding:7px}"
    html += "td{padding:7px;border:1px solid #ddd}"
    html += "</style></head><body>"
    html += "<div class=cover><h1>" + title + "</h1>"
    html += "<p>" + ov.get("theme","") + " | " + ov.get("duration","") + "</p>"
    html += "<p>招生：" + ov.get("target","") + " | 规模：" + ov.get("scale","") + "</p></div>"
    html += "<h2>一、营期概述</h2><div class=info-box>"
    html += "<p><strong>营名：</strong>" + ov.get("name","") + "</p>"
    html += "<p><strong>主题：</strong>" + ov.get("theme","") + "</p>"
    html += "<p><strong>时间：</strong>" + ov.get("duration","") + "</p>"
    html += "<p><strong>地点：</strong>" + features.location + " " + features.name + "</p>"
    html += "<p><strong>对象：</strong>" + ov.get("target","") + "</p></div>"
    html += "<h2>二、日程安排</h2>" + days_html
    html += "<h2>三、生活指南</h2>"
    html += "<p><strong>作息：</strong>" + lg.get("schedule","") + "</p>"
    html += "<p><strong>餐饮：</strong>" + lg.get("meals","") + "</p>"
    html += "<p><strong>住宿：</strong>" + lg.get("accommodation","") + "</p>"
    html += "<p><strong>行李：</strong>" + lg.get("packing_list","") + "</p>"
    html += "<h2>四、安全保障</h2>"
    html += "<p>" + safety.get("general","") + "</p>"
    html += "<p><strong>医疗：</strong>" + safety.get("medical","") + "</p>"
    html += "<h2>五、家长须知</h2>"
    html += "<p><strong>接送：</strong>" + pn.get("pickup","") + "</p>"
    html += "<p><strong>退营：</strong>" + pn.get("refund","") + "</p>"
    html += "<h2>六、成果评价</h2>"
    html += "<p>" + ev.get("method","") + "</p>"
    html += "</body></html>"
    
    from generators.pdf_utils import generate_pdf_from_html
    generate_pdf_from_html(html, output_path)
    Path(output_path.replace(".pdf", ".html")).write_text(html, encoding="utf-8")
