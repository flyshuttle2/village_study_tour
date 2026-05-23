"""教案 PDF 生成器"""
from pathlib import Path

def generate_lesson_plan_pdf(plan, features, output_path):
    obj = plan.get("objectives", {})
    prep = plan.get("preparations", {})
    impl = plan.get("implementation", {})
    
    acts_html = ""
    for i, a in enumerate(impl.get("activities", [])):
        steps = " → ".join(a.get("steps", []))
        obs = " / ".join(a.get("observation_points", []))
        acts_html += "<div class=act-card><h4>活动" + str(i+1) + "：" + a.get("name","") + "（" + str(a.get("duration","")) + "分钟）</h4>"
        acts_html += "<p><strong>步骤：</strong>" + steps + "</p>"
        acts_html += "<p><strong>观察点：</strong>" + obs + "</p>"
        acts_html += "<p><strong>记录表：</strong>" + a.get("recording_form","") + "</p></div>"
    
    safety_html = ""
    for s in prep.get("safety", []):
        safety_html += "<div class=safety-item>⚠ " + s.get("risk","") + " → " + s.get("measure","") + "</div>"
    
    warmup = impl.get("warmup", {})
    summary = impl.get("summary", {})
    eval_dict = plan.get("evaluation", {})
    appendix = plan.get("appendix", {})
    knowledge = " / ".join(obj.get("knowledge", []))
    abilities = " / ".join(obj.get("abilities", []))
    values = " / ".join(obj.get("values", []))
    teacher = " / ".join(prep.get("teacher", []))
    student = " / ".join(prep.get("student", []))
    reflection = " / ".join(eval_dict.get("reflection_questions", []))
    materials = " / ".join(appendix.get("materials", []))
    
    html = "<!DOCTYPE html><html><head><meta charset=utf-8><style>"
    html += "body{font-family:SimSun;margin:2cm;color:#333}"
    html += "h1{color:#1A5276;font-size:22px;text-align:center;border-bottom:2px solid #27AE60;padding-bottom:8px}"
    html += "h2{color:#27AE60;font-size:15px;margin-top:20px}"
    html += "h4{color:#E67E22}"
    html += ".info{background:#F8F9FA;padding:12px;margin-bottom:15px}"
    html += ".obj-box{background:#E8F6F3;padding:10px;border-left:4px solid #27AE60;margin:10px 0}"
    html += ".act-card{background:#FDFEFE;border:1px solid #ddd;padding:12px;margin:8px 0}"
    html += ".safety-item{background:#FDEDEC;padding:6px;margin:4px 0}"
    html += "table{width:100%;border-collapse:collapse;font-size:12px}"
    html += "th{background:#1A5276;color:white;padding:7px}"
    html += "td{padding:7px;border:1px solid #ddd}"
    html += "</style></head><body>"
    html += "<h1>" + plan.get("course_name","课程名称") + "</h1>"
    html += "<div class=info><p><strong>类型：</strong>" + plan.get("course_type","") + " | <strong>板块：</strong>" + plan.get("theme_block","") + "</p>"
    html += "<p><strong>年级：</strong>" + plan.get("grade_level","") + " | <strong>时长：</strong>" + str(plan.get("duration_minutes","")) + "分钟</p>"
    html += "<p><strong>地点：</strong>" + plan.get("location","") + " | <strong>容量：</strong>" + str(plan.get("capacity","")) + "人</p></div>"
    html += "<h2>一、课程目标</h2><div class=obj-box>"
    html += "<p><strong>知识：</strong>" + knowledge + "</p>"
    html += "<p><strong>能力：</strong>" + abilities + "</p>"
    html += "<p><strong>情感：</strong>" + values + "</p></div>"
    html += "<h2>二、课程准备</h2>"
    html += "<p><strong>教师：</strong>" + teacher + "</p>"
    html += "<p><strong>学生：</strong>" + student + "</p>"
    html += "<h2>安全预案</h2>" + safety_html
    html += "<h2>三、实施过程</h2>"
    html += "<h4>导入（" + str(warmup.get("duration","")) + "分钟）</h4><p>" + warmup.get("content","") + "</p>"
    html += "<h2>主体活动</h2>" + acts_html
    html += "<h4>总结（" + str(summary.get("duration","")) + "分钟）</h4><p>" + summary.get("content","") + "</p>"
    html += "<h2>四、评价</h2>"
    html += "<p><strong>方式：</strong>" + eval_dict.get("method","") + "</p>"
    html += "<p><strong>量规：</strong>" + eval_dict.get("rubric","") + "</p>"
    html += "<p><strong>反思：</strong>" + reflection + "</p>"
    html += "<h2>五、附录</h2>"
    html += "<p><strong>任务单：</strong>" + appendix.get("task_sheet","") + "</p>"
    html += "<p><strong>素材：</strong>" + materials + "</p>"
    html += "</body></html>"
    
    from generators.pdf_utils import generate_pdf_from_html
    generate_pdf_from_html(html, output_path)
    Path(output_path.replace(".pdf", ".html")).write_text(html, encoding="utf-8")
