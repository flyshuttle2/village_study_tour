"""PDF 工具模块 - 提供 WeasyPrint 备选方案"""
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import re


def try_register_fonts():
    """尝试注册中文字体"""
    font_paths = [
        "C:/Windows/Fonts/msyh.ttc",    # 微软雅黑
        "C:/Windows/Fonts/simhei.ttf",  # 黑体
        "C:/Windows/Fonts/simsun.ttc",  # 宋体
    ]
    for fp in font_paths:
        if Path(fp).exists():
            try:
                if fp.endswith('.ttc'):
                    pdfmetrics.registerFont(TTFont('Chinese', fp, subfontIndex=0))
                else:
                    pdfmetrics.registerFont(TTFont('Chinese', fp))
                return True
            except Exception:
                pass
    return False


_use_cjk_font = try_register_fonts()


def get_styles():
    """获取样式定义"""
    base_font = 'Chinese' if _use_cjk_font else 'Helvetica'
    return {
        'title': ParagraphStyle('Title', fontName=base_font, fontSize=18, leading=24, alignment=1, textColor=colors.HexColor('#2D5016')),
        'h2': ParagraphStyle('H2', fontName=base_font, fontSize=14, leading=20, spaceAfter=10, textColor=colors.HexColor('#27AE60')),
        'body': ParagraphStyle('Body', fontName=base_font, fontSize=10, leading=14),
        'bold': ParagraphStyle('Bold', fontName='Helvetica-Bold', fontSize=10, leading=14),
        'small': ParagraphStyle('Small', fontName=base_font, fontSize=8, leading=11),
        'center': ParagraphStyle('Center', fontName=base_font, fontSize=10, alignment=1),
    }


def html_to_paragraph(text: str, style_name='body') -> Paragraph:
    """简单 HTML 标签转 Paragraph"""
    text = re.sub(r'<br\s*/?>', '\n', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = text.replace('&nbsp;', ' ').replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
    lines = text.split('\n')
    style = get_styles().get(style_name, get_styles()['body'])
    return Paragraph(text.strip(), style)


def html_table_to_reportlab(table_html: str) -> Table:
    """将 HTML table 转换为 reportlab Table"""
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', table_html, re.DOTALL)
    data = []
    for row in rows:
        cells = re.findall(r'<t[hd][^>]*>(.*?)</t[hd]>', row, re.DOTALL)
        row_data = []
        for cell in cells:
            cell = re.sub(r'<[^>]+>', '', cell)
            cell = cell.replace('&nbsp;', ' ').strip()
            row_data.append(cell)
        if row_data:
            data.append(row_data)
    
    if not data:
        return None
    
    col_count = max(len(row) for row in data) if data else 0
    
    table = Table(data, colWidths=[(A4[0] - 4*cm) / max(col_count, 1)] * col_count if col_count else [A4[0] - 4*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2D5016')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, -1), 'Chinese' if _use_cjk_font else 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F8F9FA')),
    ]))
    return table


def html_to_reportlab(html: str) -> list:
    """将 HTML 转换为 reportlab 元素列表"""
    from reportlab.platypus.flowables import HRFlowable
    
    styles = get_styles()
    elements = []
    
    body_match = re.search(r'<body[^>]*>(.*?)</body>', html, re.DOTALL)
    content = body_match.group(1) if body_match else html
    
    blocks = re.split(r'(?=<div|<h[123]|</div>|<p|<table|<ul|<ol)', content)
    
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        
        if block.startswith('<div class="cover"') or block.startswith('<div class=cover'):
            title_match = re.search(r'<h1[^>]*>(.*?)</h1>', block, re.DOTALL)
            if title_match:
                elements.append(Spacer(1, 2*cm))
                elements.append(Paragraph(html_to_paragraph(title_match.group(1)).text, styles['title']))
                elements.append(Spacer(1, 0.5*cm))
            subtitle_match = re.search(r'<div class="subtitle"[^>]*>(.*?)</div>', block, re.DOTALL)
            if subtitle_match:
                sub_text = re.sub(r'<[^>]+>', ' ', subtitle_match.group(1))
                sub_text = sub_text.replace('|', '\n').strip()
                for line in sub_text.split('\n'):
                    if line.strip():
                        elements.append(Paragraph(line.strip(), styles['center']))
                elements.append(Spacer(1, 1*cm))
            continue
        
        if block.startswith('<h2'):
            text_match = re.search(r'<h2[^>]*>(.*?)</h2>', block, re.DOTALL)
            if text_match:
                elements.append(Spacer(1, 0.5*cm))
                elements.append(Paragraph(html_to_paragraph(text_match.group(1)).text, styles['h2']))
            continue
        
        if block.startswith('<p'):
            text_match = re.search(r'<p[^>]*>(.*?)</p>', block, re.DOTALL)
            if text_match:
                text = text_match.group(1)
                if '<strong>' in text:
                    parts = re.split(r'(<strong[^>]*>.*?</strong>)', text, re.DOTALL)
                    for part in parts:
                        strong_m = re.search(r'<strong[^>]*>(.*?)</strong>', part, re.DOTALL)
                        if strong_m:
                            elements.append(Paragraph(html_to_paragraph(strong_m.group(1)).text, styles['bold']))
                        elif part.strip() and not part.startswith('<'):
                            elements.append(Paragraph(part.strip(), styles['body']))
                else:
                    elements.append(Paragraph(html_to_paragraph(text).text, styles['body']))
            continue
        
        if block.startswith('<table'):
            table = html_table_to_reportlab(block)
            if table:
                elements.append(Spacer(1, 0.3*cm))
                elements.append(table)
                elements.append(Spacer(1, 0.3*cm))
            continue
        
        if block.startswith('<ul') or block.startswith('<ol'):
            items = re.findall(r'<li[^>]*>(.*?)</li>', block, re.DOTALL)
            for item in items:
                item_text = re.sub(r'<[^>]+>', '', item).strip()
                if item_text:
                    elements.append(Paragraph(f"• {item_text}", styles['body']))
            continue
        
        if block.startswith('<div class="grid"') or block.startswith('<div class=grid'):
            boxes = re.findall(r'<div class="box"[^>]*>(.*?)</div>', block, re.DOTALL)
            for box in boxes:
                box_text = re.sub(r'<[^>]+>', ' ', box).replace('&nbsp;', ' ').strip()
                box_text = re.sub(r'\s+', ' ', box_text)
                if box_text:
                    elements.append(Paragraph(box_text, styles['body']))
                    elements.append(Spacer(1, 0.2*cm))
            continue
        
        if block.startswith('<div class="budget"') or block.startswith('<div class=budget'):
            text = re.sub(r'<div[^>]*>', '', block)
            text = re.sub(r'</div>', '\n', text)
            text = re.sub(r'<[^>]+>', '', text).strip()
            for line in text.split('\n'):
                if line.strip():
                    elements.append(Paragraph(line.strip(), styles['body']))
            elements.append(Spacer(1, 0.3*cm))
            continue
        
        if block.startswith('<div class="day-block"') or block.startswith('<div class=day-block'):
            h2_match = re.search(r'<h2[^>]*>(.*?)</h2>', block, re.DOTALL)
            if h2_match:
                elements.append(PageBreak())
                elements.append(Paragraph(html_to_paragraph(h2_match.group(1)).text, styles['h2']))
            table_match = re.search(r'<table[^>]*>.*?</table>', block, re.DOTALL)
            if table_match:
                table = html_table_to_reportlab(table_match.group(0))
                if table:
                    elements.append(table)
            continue
        
        text = re.sub(r'<[^>]+>', '', block).strip()
        if text:
            elements.append(Paragraph(text, styles['body']))
    
    return elements


def html_to_pdf(html: str, output_path: str) -> bool:
    """将 HTML 转换为 PDF（使用 reportlab）"""
    try:
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            leftMargin=2*cm,
            rightMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        elements = html_to_reportlab(html)
        doc.build(elements)
        return True
    except Exception as e:
        print(f"reportlab PDF generation failed: {e}")
        return False


def can_use_weasyprint() -> bool:
    """检查 WeasyPrint 是否可用"""
    try:
        from weasyprint import HTML
        return True
    except Exception:
        return False


def generate_pdf_from_html(html: str, output_path: str) -> bool:
    """生成 PDF，优先使用 WeasyPrint，失败则使用 reportlab"""
    try:
        from weasyprint import HTML
        HTML(string=html).write_pdf(output_path)
        return True
    except Exception as e:
        print(f"WeasyPrint failed: {e}")
        print("Trying reportlab fallback...")
        return html_to_pdf(html, output_path)
