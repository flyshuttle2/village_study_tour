"""物料准备清单 PDF 生成器"""
from pathlib import Path

def generate_material_list_pdf(solution, features, lesson_plans, output_path):
    """生成物料准备清单 PDF
    
    Args:
        solution: 研学解决方案数据
        features: 村庄特色信息
        lesson_plans: 课程教案列表
        output_path: 输出文件路径
    """
    courses = solution.get("course_design", [])
    theme = solution.get("overview", {}).get("theme", "研学活动")
    village_name = features.name
    
    material_sections = []
    
    if courses and len(courses) > 0:
        for day in courses:
            day_num = day.get("day", 1)
            day_theme = day.get("theme", f"第{day_num}天")
            activities = day.get("activities", [])
            
            for act in activities:
                name = act.get("name", "")
                duration = act.get("duration_minutes", "")
                location = act.get("location", "")
                
                materials_html = "<tr><td>" + name + "</td><td>" + location + "</td><td>" + str(duration) + "分钟</td><td>"
                
                act_materials = act.get("materials", [])
                if act_materials:
                    materials_html += "、".join(act_materials)
                else:
                    materials_html += "（根据课程准备）"
                
                materials_html += "</td><td></td><td></td><td></td></tr>"
                material_sections.append(materials_html)
    
    if not material_sections:
        material_sections = [
            "<tr><td>主题活动1</td><td>待定</td><td>60分钟</td><td>根据活动内容准备</td><td></td><td></td><td></td></tr>",
            "<tr><td>主题活动2</td><td>待定</td><td>60分钟</td><td>根据活动内容准备</td><td></td><td></td><td></td></tr>",
            "<tr><td>主题活动3</td><td>待定</td><td>90分钟</td><td>根据活动内容准备</td><td></td><td></td><td></td></tr>",
        ]
    
    if lesson_plans:
        for i, plan in enumerate(lesson_plans[:3]):
            course_name = plan.get("course_name", f"课程{i+1}")
            prep = plan.get("preparation", {})
            items = prep.get("materials", []) if isinstance(prep, dict) else []
            if items:
                materials_html = f"<tr><td>{course_name}</td><td>工坊</td><td>90分钟</td><td>" + "、".join(str(x) for x in items[:5]) + "</td><td></td><td></td><td></td></tr>"
                material_sections.append(materials_html)
    
    html = "<!DOCTYPE html><html><head><meta charset=utf-8><style>"
    html += "body{font-family:SimSun;margin:1.5cm;color:#333;font-size:12px}"
    html += "h1{color:#2D5016;text-align:center;border-bottom:3px solid #D4A017;padding-bottom:10px}"
    html += "h2{color:#27AE60;margin-top:15px;font-size:13px}"
    html += ".header{text-align:center;margin-bottom:15px}"
    html += "table{width:100%;border-collapse:collapse;font-size:11px;margin:8px 0}"
    html += "th{background:#2D5016;color:white;padding:6px;text-align:center}"
    html += "td{padding:6px;border:1px solid #ddd}"
    html += ".checkbox{display:inline-block;width:12px;height:12px;border:1px solid #333;margin-right:3px}"
    html += ".section{background:#FAFAFA;padding:10px;border:1px solid #E0E0E0;margin:10px 0}"
    html += ".prepare-ratio{background:#FFF9E6;padding:8px;border-left:3px solid #D4A017;margin:10px 0}"
    html += ".footer{text-align:center;color:#666;font-size:10px;margin-top:15px}"
    html += "</style></head><body>"
    
    html += "<div class=header><h1>" + village_name + " 物料准备清单</h1></div>"
    
    html += "<h2>基本信息</h2>"
    html += "<table>"
    html += "<tr><td style='width:15%;background:#E8F5E9'><strong>活动主题</strong></td><td>" + theme + "</td>"
    html += "<td style='width:15%;background:#E8F5E9'><strong>活动日期</strong></td><td>_______年_____月_____日</td></tr>"
    html += "<tr><td style='background:#E8F5E9'><strong>活动地点</strong></td><td colspan=3>" + village_name + "</td></tr>"
    html += "<tr><td style='background:#E8F5E9'><strong>参与人数</strong></td>"
    html += "<td>_____人（大人_____人，小孩_____人）</td>"
    html += "<td style='background:#E8F5E9'><strong>物料准备比例</strong></td><td>n+10%（n=小孩人数）</td></tr>"
    html += "</table>"
    
    html += "<div class=prepare-ratio>"
    html += "<strong>物料准备说明：</strong>以小朋友人数为准，准备n+10%份物料。例如：20个小朋友准备22份物料。"
    html += "</div>"
    
    html += "<h2>通用物料（活动必备）</h2>"
    html += "<table>"
    html += "<tr><th style='width:5%'>序号</th><th style='width:15%'>物料类别</th><th style='width:35%'>物料明细</th><th style='width:10%'>数量</th><th style='width:10%'>负责人</th><th style='width:10%'>确认</th><th>备注</th></tr>"
    html += "<tr><td>1</td><td>签到用品</td><td>签到表、签到笔、记号笔、贴牌（颜色分组用）</td><td>1套</td><td></td><td></td><td></td></tr>"
    html += "<tr><td>2</td><td>音响设备</td><td>音响、话筒、电池</td><td>1套</td><td></td><td></td><td></td></tr>"
    html += "<tr><td>3</td><td>安全用品</td><td>急救药箱、藿香正气水、创可贴</td><td>1套</td><td></td><td></td><td></td></tr>"
    html += "<tr><td>4</td><td>扩音设备</td><td>小蜜蜂扩音器</td><td>_____个</td><td></td><td></td><td></td></tr>"
    html += "<tr><td>5</td><td>通讯设备</td><td>对讲机</td><td>_____个</td><td></td><td></td><td></td></tr>"
    html += "<tr><td>6</td><td>活动道具</td><td>分队背心/马甲、彩旗</td><td></td><td></td><td></td><td></td></tr>"
    html += "<tr><td>7</td><td>打印资料</td><td>活动流程图（带负责人）、学员名单</td><td></td><td></td><td></td><td></td></tr>"
    html += "<tr><td>8</td><td>清洁用品</td><td>纸巾、垃圾袋、抹布</td><td></td><td></td><td></td><td></td></tr>"
    html += "<tr><td>9</td><td>天气应对</td><td>雨具（雨衣/雨伞）、防晒用品</td><td></td><td></td><td></td><td></td></tr>"
    html += "<tr><td>10</td><td>桌椅布置</td><td>折叠桌、折叠椅、桌布</td><td></td><td></td><td></td><td></td></tr>"
    html += "</table>"
    
    html += "<h2>课程专用物料</h2>"
    html += "<table>"
    html += "<tr><th style='width:5%'>序号</th><th style='width:18%'>活动名称</th><th style='width:12%'>地点</th><th style='width:8%'>时长</th><th style='width:27%'>物料明细</th><th style='width:8%'>负责人</th><th style='width:7%'>确认</th><th>备注</th></tr>"
    html += "".join(material_sections)
    html += "</table>"
    
    html += "<h2>需采购物料</h2>"
    html += "<table>"
    html += "<tr><th style='width:5%'>序号</th><th style='width:35%'>物料名称</th><th style='width:15%'>数量</th><th style='width:15%'>采购负责人</th><th>采购渠道/备注</th></tr>"
    html += "<tr><td>1</td><td></td><td></td><td></td><td></td></tr>"
    html += "<tr><td>2</td><td></td><td></td><td></td><td></td></tr>"
    html += "<tr><td>3</td><td></td><td></td><td></td><td></td></tr>"
    html += "<tr><td>4</td><td></td><td></td><td></td><td></td></tr>"
    html += "<tr><td>5</td><td></td><td></td><td></td><td></td></tr>"
    html += "</table>"
    
    html += "<h2>物料确认</h2>"
    html += "<table>"
    html += "<tr><td style='width:25%;background:#E8F5E9'><strong>主教确认签名</strong></td><td>________________</td>"
    html += "<td style='width:25%;background:#E8F5E9'><strong>确认时间</strong></td><td>_____年_____月_____日</td></tr>"
    html += "<tr><td style='background:#E8F5E9'><strong>场地管家确认</strong></td><td>________________</td>"
    html += "<td style='background:#E8F5E9'><strong>确认时间</strong></td><td>_____年_____月_____日</td></tr>"
    html += "<tr><td style='background:#E8F5E9'><strong>采购负责人</strong></td><td>________________</td>"
    html += "<td style='background:#E8F5E9'><strong>采购完成日期</strong></td><td>_____年_____月_____日</td></tr>"
    html += "</table>"
    
    html += "<div class=footer>本清单由" + village_name + "研学基地提供 | 活动前3天确认物料</div>"
    html += "</body></html>"
    
    from generators.pdf_utils import generate_pdf_from_html
    if not generate_pdf_from_html(html, output_path):
        Path(output_path.replace(".pdf", ".html")).write_text(html, encoding="utf-8")
