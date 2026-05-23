"""活动执行单 PDF 生成器"""
from pathlib import Path

def generate_execution_form_pdf(solution, features, lesson_plans, output_path):
    """生成活动执行单 PDF
    
    Args:
        solution: 研学解决方案数据
        features: 村庄特色信息
        lesson_plans: 课程教案列表
        output_path: 输出文件路径
    """
    ov = solution.get("overview", {})
    courses = solution.get("course_design", [])
    theme = ov.get("theme", "研学活动")
    village_name = features.name
    
    schedule_rows = ""
    if courses and len(courses) > 0:
        day_activities = courses[0].get("activities", [])
        for act in day_activities:
            time_str = act.get("time", "")
            duration = act.get("duration_minutes", "")
            name = act.get("name", "")
            location = act.get("location", "")
            content = act.get("content", "")[:50] if act.get("content") else ""
            schedule_rows += f"<tr><td>{time_str}</td><td>{name}</td><td>{location}</td><td>{duration}分钟</td><td>{content}</td></tr>"
    
    team_types = "、".join(ov.get("target_audience", ["亲子活动", "研学"]))
    
    html = "<!DOCTYPE html><html><head><meta charset=utf-8><style>"
    html += "body{font-family:SimSun;margin:1.5cm;color:#333;font-size:13px}"
    html += "h1{color:#2D5016;text-align:center;border-bottom:3px solid #D4A017;padding-bottom:10px}"
    html += "h2{color:#27AE60;margin-top:20px;font-size:14px;border-bottom:1px solid #27AE60;padding-bottom:5px}"
    html += ".header{text-align:center;margin-bottom:20px}"
    html += ".info-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:15px 0}"
    html += ".info-item{display:flex;align-items:center}"
    html += ".info-label{background:#E8F5E9;padding:5px 10px;min-width:80px;font-weight:bold}"
    html += ".info-value{padding:5px 10px;border-bottom:1px solid #ddd;flex:1}"
    html += "table{width:100%;border-collapse:collapse;font-size:12px;margin:10px 0}"
    html += "th{background:#2D5016;color:white;padding:8px;text-align:center}"
    html += "td{padding:8px;border:1px solid #ddd;text-align:center}"
    html += ".checkbox{display:inline-block;width:15px;height:15px;border:1px solid #333;margin-right:5px}"
    html += ".section{margin:15px 0;padding:10px;background:#FAFAFA;border:1px solid #E0E0E0}"
    html += ".signature{display:grid;grid-template-columns:1fr 1fr;gap:30px;margin-top:30px}"
    html += ".sig-item{text-align:center}"
    html += ".sig-line{border-bottom:1px solid #333;margin-top:40px;width:200px;display:inline-block}"
    html += ".footer{text-align:center;color:#666;font-size:10px;margin-top:20px}"
    html += "</style></head><body>"
    
    html += "<div class=header><h1>" + village_name + " 研学活动执行单</h1></div>"
    
    html += "<h2>基本信息</h2>"
    html += "<table>"
    html += "<tr><td style='width:15%;background:#E8F5E9'><strong>活动主题</strong></td><td>" + theme + "</td>"
    html += "<td style='width:15%;background:#E8F5E9'><strong>活动日期</strong></td><td>_______年_____月_____日</td></tr>"
    html += "<tr><td style='background:#E8F5E9'><strong>团队类型</strong></td><td colspan=3>" + team_types + "</td></tr>"
    html += "<tr><td style='background:#E8F5E9'><strong>团队名称</strong></td><td>________________</td>"
    html += "<td style='background:#E8F5E9'><strong>联系教师</strong></td><td>________________</td></tr>"
    html += "<tr><td style='background:#E8F5E9'><strong>应到人数</strong></td><td>_____人（大人_____人，小孩_____人）</td>"
    html += "<td style='background:#E8F5E9'><strong>实到人数</strong></td><td>_____人（大人_____人，小孩_____人）</td></tr>"
    html += "</table>"
    
    html += "<h2>人员安排</h2>"
    html += "<table>"
    html += "<tr><th style='width:20%'>岗位</th><th>姓名</th><th>联系电话</th><th>职责</th></tr>"
    html += "<tr><td>主教</td><td>________________</td><td>____________</td><td>整体协调、授课</td></tr>"
    html += "<tr><td>助教</td><td>________________</td><td>____________</td><td>协助授课、安全</td></tr>"
    html += "<tr><td>助教</td><td>________________</td><td>____________</td><td>协助授课、安全</td></tr>"
    html += "<tr><td>工坊老师</td><td>________________</td><td>____________</td><td>手工/烹饪指导</td></tr>"
    html += "<tr><td>后勤</td><td>________________</td><td>____________</td><td>餐饮、物资</td></tr>"
    html += "</table>"
    
    html += "<h2>活动流程</h2>"
    html += "<table>"
    html += "<tr><th style='width:12%'>时间</th><th style='width:18%'>活动内容</th><th style='width:15%'>地点</th><th style='width:10%'>时长</th><th>备注</th></tr>"
    html += schedule_rows if schedule_rows else """
    <tr><td>09:00</td><td>集合签到</td><td>村口/停车场</td><td>30分钟</td><td>分发活动资料</td></tr>
    <tr><td>09:30</td><td>开场介绍</td><td>村史馆</td><td>20分钟</td><td>安全提示</td></tr>
    <tr><td>09:50</td><td>主题活动1</td><td>指定地点</td><td>60分钟</td><td></td></tr>
    <tr><td>10:50</td><td>主题活动2</td><td>指定地点</td><td>60分钟</td><td></td></tr>
    <tr><td>11:50</td><td>休整</td><td>休息区</td><td>10分钟</td><td></td></tr>
    <tr><td>12:00</td><td>午餐</td><td>餐厅</td><td>90分钟</td><td></td></tr>
    <tr><td>13:30</td><td>主题活动3</td><td>指定地点</td><td>90分钟</td><td></td></tr>
    <tr><td>15:00</td><td>总结分享</td><td>集合点</td><td>30分钟</td><td></td></tr>
    <tr><td>15:30</td><td>返程</td><td>集合点</td><td></td><td></td></tr>
    """
    html += "</table>"
    
    html += "<h2>午餐安排</h2>"
    html += "<table>"
    html += "<tr><td style='width:20%;background:#E8F5E9'><strong>餐食类型</strong></td>"
    html += "<td colspan=3>□蒸笼宴  □桌餐  □自助  □其他：________</td></tr>"
    html += "<tr><td style='background:#E8F5E9'><strong>用餐地点</strong></td><td>________________</td>"
    html += "<td style='background:#E8F5E9'><strong>桌数</strong></td><td>_____桌</td></tr>"
    html += "<tr><td style='background:#E8F5E9'><strong>用餐人数</strong></td><td colspan=3>_____人（需准备____份）</td></tr>"
    html += "<tr><td style='background:#E8F5E9'><strong>特殊要求</strong></td><td colspan=3>________________</td></tr>"
    html += "</table>"
    
    html += "<h2>物料准备</h2>"
    html += "<table>"
    html += "<tr><th style='width:5%'>序号</th><th style='width:20%'>物料名称</th><th style='width:10%'>数量</th><th style='width:10%'>负责人</th><th>备注</th></tr>"
    html += "<tr><td>1</td><td>签到表/笔</td><td>1套</td><td></td><td></td></tr>"
    html += "<tr><td>2</td><td>音响/话筒</td><td>1套</td><td></td><td></td></tr>"
    html += "<tr><td>3</td><td>急救药箱</td><td>1个</td><td></td><td></td></tr>"
    html += "<tr><td>4</td><td>扩音器(小蜜蜂)</td><td>_____个</td><td></td><td></td></tr>"
    html += "<tr><td>5</td><td>对讲机</td><td>_____个</td><td></td><td></td></tr>"
    html += "<tr><td>6</td><td>活动横幅/KT板</td><td></td><td></td><td></td></tr>"
    html += "<tr><td>7</td><td>接送车辆</td><td>_____辆</td><td></td><td></td></tr>"
    html += "<tr><td colspan=5><strong>活动专用物料（根据课程准备）：</strong></td></tr>"
    html += "<tr><td></td><td colspan=4>________________________________________________</td></tr>"
    html += "<tr><td></td><td colspan=4>________________________________________________</td></tr>"
    html += "</table>"
    
    html += "<h2>金额结算</h2>"
    html += "<table>"
    html += "<tr><td style='width:20%;background:#E8F5E9'><strong>结算总金额</strong></td><td>￥_________元</td>"
    html += "<td style='width:20%;background:#E8F5E9'><strong>实际支付</strong></td><td>￥_________元</td></tr>"
    html += "<tr><td style='background:#E8F5E9'><strong>支付方式</strong></td>"
    html += "<td colspan=3>□微信  □支付宝  □银联  □现金  □其他：________</td></tr>"
    html += "<tr><td style='background:#E8F5E9'><strong>收据/发票</strong></td>"
    html += "<td colspan=3>□需要  □不需要</td></tr>"
    html += "</table>"
    
    html += "<h2>备注说明</h2>"
    html += "<div style='border:1px solid #ddd;min-height:80px;padding:10px;background:#FAFAFA'>"
    html += "_______________________________________________________________<br>"
    html += "_______________________________________________________________</div>"
    
    html += "<div class=signature>"
    html += "<div class=sig-item><div class=sig-line></div><p>主教签字</p></div>"
    html += "<div class=sig-item><div class=sig-line></div><p>对接教师签字</p></div>"
    html += "</div>"
    
    html += "<div class=footer>本执行单由" + village_name + "研学基地提供 | 联系电话：____________</div>"
    html += "</body></html>"
    
    from generators.pdf_utils import generate_pdf_from_html
    if not generate_pdf_from_html(html, output_path):
        Path(output_path.replace(".pdf", ".html")).write_text(html, encoding="utf-8")
