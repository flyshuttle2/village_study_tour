"""签到表 PDF 生成器"""
from pathlib import Path

def generate_signin_pdf(village_name, team_name, output_path):
    """生成签到表 PDF
    
    Args:
        village_name: 村庄名称
        team_name: 团队名称
        output_path: 输出文件路径
    """
    html = "<!DOCTYPE html><html><head><meta charset=utf-8><style>"
    html += "body{font-family:SimSun;margin:1.5cm;color:#333;font-size:12px}"
    html += "h1{color:#2D5016;text-align:center;border-bottom:3px solid #D4A017;padding-bottom:10px}"
    html += ".header{text-align:center;margin-bottom:20px}"
    html += "table{width:100%;border-collapse:collapse;font-size:11px;margin:10px 0}"
    html += "th{background:#2D5016;color:white;padding:8px;text-align:center}"
    html += "td{padding:8px;border:1px solid #ddd;text-align:center}"
    html += ".info-table{width:100%;margin:15px 0}"
    html += ".info-table td{padding:8px;border:1px solid #ddd}"
    html += ".breakdown{background:#FFF9E6;padding:15px;border:1px solid #D4A017;margin:15px 0}"
    html += ".footer{text-align:center;color:#666;font-size:10px;margin-top:20px}"
    html += ".signatures{display:grid;grid-template-columns:1fr 1fr;gap:30px;margin-top:30px}"
    html += ".sig-item{text-align:center}"
    html += ".sig-line{border-bottom:1px solid #333;margin-top:40px;width:180px;display:inline-block}"
    html += "</style></head><body>"
    
    html += "<div class=header><h1>" + village_name + " 活动签到表</h1></div>"
    
    if team_name:
        html += "<p style='text-align:center;font-size:14px;'>团队：" + team_name + "</p>"
    
    html += "<table class=info-table>"
    html += "<tr><td style='width:20%;background:#E8F5E9'><strong>活动日期</strong></td><td>_____年_____月_____日</td>"
    html += "<td style='width:20%;background:#E8F5E9'><strong>应到人数</strong></td><td>_____人</td></tr>"
    html += "</table>"
    
    html += "<p style='font-weight:bold;margin-top:15px;'>第一组（1-15人）</p>"
    html += "<table>"
    html += "<tr><th style='width:8%'>序号</th><th style='width:20%'>姓名</th><th style='width:15%'>出行人数</th><th style='width:22%'>联系方式</th><th style='width:15%'>签到</th><th style='width:20%'>备注</th></tr>"
    for i in range(1, 16):
        html += f"<tr><td>{i}</td><td></td><td></td><td></td><td></td><td></td></tr>"
    html += "</table>"
    
    html += "<p style='font-weight:bold;margin-top:20px;'>第二组（16-30人）</p>"
    html += "<table>"
    html += "<tr><th style='width:8%'>序号</th><th style='width:20%'>姓名</th><th style='width:15%'>出行人数</th><th style='width:22%'>联系方式</th><th style='width:15%'>签到</th><th style='width:20%'>备注</th></tr>"
    for i in range(16, 31):
        html += f"<tr><td>{i}</td><td></td><td></td><td></td><td></td><td></td></tr>"
    html += "</table>"
    
    html += "<div class=breakdown>"
    html += "<strong>人员构成统计：</strong><br>"
    html += "应到人数：<u>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</u>人 | 实到人数：<u>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</u>人<br><br>"
    html += "含老师：<u>&nbsp;&nbsp;&nbsp;</u>人 | 小朋友：<u>&nbsp;&nbsp;&nbsp;</u>人 | 家长：<u>&nbsp;&nbsp;&nbsp;</u>人<br><br>"
    html += "年龄段：1-2岁 <u>&nbsp;&nbsp;&nbsp;</u>人 | 2-3岁 <u>&nbsp;&nbsp;&nbsp;</u>人 | 3岁以上 <u>&nbsp;&nbsp;&nbsp;</u>人"
    html += "</div>"
    
    html += "<div class=signatures>"
    html += "<div class=sig-item><div class=sig-line></div><p>主教确认签名</p></div>"
    html += "<div class=sig-item><div class=sig-line></div><p>对接教师签名</p></div>"
    html += "</div>"
    
    html += "<div class=footer>本签到表由" + village_name + "研学基地提供</div>"
    html += "</body></html>"
    
    from generators.pdf_utils import generate_pdf_from_html
    if not generate_pdf_from_html(html, output_path):
        Path(output_path.replace(".pdf", ".html")).write_text(html, encoding="utf-8")
