"""活动前巡场检查表 PDF 生成器"""
from pathlib import Path

def generate_inspection_pdf(solution, features, output_path):
    """生成巡场检查表 PDF
    
    Args:
        solution: 研学解决方案数据
        features: 村庄特色信息
        output_path: 输出文件路径
    """
    village_name = features.name
    theme = solution.get("overview", {}).get("theme", "研学活动")
    
    inspection_items = [
        ("入口区域", [
            ("农场大门", "地面卫生整洁", ""),
            ("农场大门", "花坛植物修剪整齐", ""),
            ("签到处", "桌面卫生整洁", ""),
            ("签到处", "签到用品齐全（签到表、笔）", ""),
        ]),
        ("餐饮区域", [
            ("餐厅", "空间清洁卫生", ""),
            ("餐厅", "物品摆放整齐", ""),
            ("自助厨房", "桌面/灶台清洁", ""),
            ("自助厨房", "工具摆放整齐", ""),
            ("自助厨房", "饮水机清洁、饮用水充足", ""),
            ("垃圾分类处", "垃圾桶清洁、垃圾及时倾倒", ""),
            ("垃圾分类处", "分类垃圾桶摆放整理", ""),
        ]),
        ("户外区域", [
            ("前院草坪/菜园", "清洁卫生", ""),
            ("前院草坪/菜园", "路面无杂物", ""),
            ("菜园", "菜牌标识清晰", ""),
            ("温室大棚", "土壤不乱洒", ""),
            ("温室大棚", "农耕用具摆放整齐", ""),
            ("动物区", "道路清洁", ""),
            ("动物区", "动物食物准备", ""),
            ("儿童活动区", "设备安全检查", ""),
            ("儿童活动区", "场地清洁卫生", ""),
        ]),
        ("工坊教室", [
            ("工坊", "桌面地面清洁", ""),
            ("工坊", "工具材料摆放整齐", ""),
            ("工坊", "窗户/书柜卫生", ""),
            ("工坊", "卫生间清洁", ""),
            ("工坊", "饮水点清洁", ""),
            ("烘焙室", "桌面地面清洁", ""),
            ("烘焙室", "餐食工具摆放整齐", ""),
            ("烘焙室", "纸巾/垃圾桶充足", ""),
        ]),
        ("安全检查", [
            ("设施", "急救药箱物品齐全", ""),
            ("设施", "消防设施完好", ""),
            ("夏季", "风扇/空调清洁可用", ""),
            ("夏季", "灭蚊/防虫措施到位", ""),
            ("天气", "雨具准备（如需要）", ""),
            ("整体", "场地基础设施保障", ""),
        ]),
    ]
    
    rows_html = ""
    seq = 1
    for section, items in inspection_items:
        for location, item, _ in items:
            rows_html += f"<tr><td>{seq}</td><td>{location}</td><td>{item}</td><td></td><td></td><td></td></tr>"
            seq += 1
    
    html = "<!DOCTYPE html><html><head><meta charset=utf-8><style>"
    html += "body{font-family:SimSun;margin:1.2cm;color:#333;font-size:11px}"
    html += "h1{color:#2D5016;text-align:center;border-bottom:3px solid #D4A017;padding-bottom:8px}"
    html += "h2{color:#27AE60;margin-top:12px;font-size:12px;background:#E8F5E9;padding:5px}"
    html += ".header{text-align:center;margin-bottom:12px}"
    html += "table{width:100%;border-collapse:collapse;font-size:10px;margin:6px 0}"
    html += "th{background:#2D5016;color:white;padding:5px;text-align:center}"
    html += "td{padding:5px;border:1px solid #ddd}"
    html += ".checkbox{display:inline-block;width:10px;height:10px;border:1px solid #333}"
    html += ".summary{background:#FFF9E6;padding:10px;border:1px solid #D4A017;margin:15px 0}"
    html += ".footer{text-align:center;color:#666;font-size:9px;margin-top:15px}"
    html += ".signatures{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-top:15px}"
    html += "</style></head><body>"
    
    html += "<div class=header><h1>" + village_name + " 活动前巡场检查表</h1></div>"
    
    html += "<table>"
    html += "<tr><td style='width:15%;background:#E8F5E9'><strong>活动主题</strong></td><td>" + theme + "</td>"
    html += "<td style='width:15%;background:#E8F5E9'><strong>检查日期</strong></td><td>_____年_____月_____日</td></tr>"
    html += "<tr><td style='background:#E8F5E9'><strong>团队名称</strong></td><td>________________</td>"
    html += "<td style='background:#E8F5E9'><strong>团队人数</strong></td><td>_____人</td></tr>"
    html += "<tr><td style='background:#E8F5E9'><strong>检查人</strong></td><td>________________</td>"
    html += "<td style='background:#E8F5E9'><strong>完成时间</strong></td><td>_____时_____分</td></tr>"
    html += "</table>"
    
    html += "<table>"
    html += "<tr><th style='width:5%'>序号</th><th style='width:18%'>检查区域</th><th style='width:42%'>检查项目</th><th style='width:10%'>完成</th><th style='width:10%'>负责人</th><th style='width:15%'>备注</th></tr>"
    html += rows_html
    html += "</table>"
    
    html += "<div class=summary>"
    html += "<strong>检查汇总：</strong>总检查项：<u>_____</u>项 | 已完成：<u>_____</u>项 | 未完成：<u>_____</u>项 | 需紧急处理：<u>_____</u>项"
    html += "<br><br><strong>未完成/需处理事项：</strong><br>"
    html += "1. ________________________________________________<br>"
    html += "2. ________________________________________________<br>"
    html += "3. ________________________________________________"
    html += "</div>"
    
    html += "<div class=signatures>"
    html += "<div style='text-align:center'><strong>检查人签字：</strong>________________</div>"
    html += "<div style='text-align:center'><strong>复核人签字：</strong>________________</div>"
    html += "</div>"
    
    html += "<div class=footer>本检查表由" + village_name + "研学基地提供 | 活动当天执行前1小时内完成</div>"
    html += "</body></html>"
    
    from generators.pdf_utils import generate_pdf_from_html
    if not generate_pdf_from_html(html, output_path):
        Path(output_path.replace(".pdf", ".html")).write_text(html, encoding="utf-8")
