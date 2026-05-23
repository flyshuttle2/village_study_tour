"""策展方案 PDF 生成器"""
from pathlib import Path


def generate_exhibition_pdf(exhibition, features, output_path):
    theme = exhibition.get("curatorial_theme", f"{features.name}探学玩创研学展")
    story = exhibition.get("theme_story", "")
    target = "、".join(exhibition.get("target_audience", []))
    flow = exhibition.get("visitor_flow", "")
    
    zones_html = ""
    for zone in exhibition.get("exhibition_zones", []):
        exhibits = "<br>".join(f"• {e}" for e in zone.get("key_exhibits", []))
        interactive = "<br>".join(f"• {i}" for i in zone.get("interactive_nodes", []))
        workshops = "<br>".join(f"• {w}" for w in zone.get("workshop_items", []))
        
        zone_html = f"""
        <div class="zone-card">
            <div class="zone-header">
                <span class="zone-icon">{zone.get('zone_icon', '')}</span>
                <span class="zone-name">{zone.get('zone_name', '')}</span>
                <span class="zone-tag">{zone.get('tan_xue_wan_chuang_tag', '')}</span>
            </div>
            <p class="zone-narrative">{zone.get('narrative', '')}</p>
            <div class="zone-details">
                <div class="detail-item"><strong>展品：</strong>{exhibits or '暂无'}</div>
                <div class="detail-item"><strong>互动：</strong>{interactive or '暂无'}</div>
                <div class="detail-item"><strong>工坊：</strong>{workshops or '暂无'}</div>
            </div>
        </div>
        """
        zones_html += zone_html
    
    sensory = exhibition.get("sensory_design", {})
    sensory_html = f"""
    <div class="sensory-grid">
        <div class="sensory-item"><strong>视觉</strong><p>{sensory.get('visual', '温馨可爱的卡通风格')}</p></div>
        <div class="sensory-item"><strong>听觉</strong><p>{sensory.get('audio', '自然环境音效')}</p></div>
        <div class="sensory-item"><strong>触觉</strong><p>{sensory.get('tactile', '触摸自然材料')}</p></div>
        <div class="sensory-item"><strong>味觉</strong><p>{sensory.get('taste', '品尝特色美食')}</p></div>
    </div>
    """
    
    installations = ""
    for inst in exhibition.get("installation_list", []):
        installations += f"<tr><td>{inst.get('name', '')}</td><td>{inst.get('location', '')}</td><td>{inst.get('interaction', '')}</td><td>{inst.get('type', '')}</td></tr>"
    
    if not installations:
        installations = "<tr><td colspan='4'>暂无装置清单</td></tr>"
    
    products = "<br>".join(f"• {p}" for p in exhibition.get("cultural_products", []))
    photo_spots = "<br>".join(f"• {p}" for p in exhibition.get("photo_spots", []))
    engagement = "<br>".join(f"• {e}" for e in exhibition.get("engagement_elements", []))

    html = "<!DOCTYPE html><html><head><meta charset=utf-8><style>"
    html += """
    body{font-family:SimSun;margin:2cm;color:#333;line-height:1.8}
    h1{color:#E67E22;text-align:center;border-bottom:3px solid #F39C12;padding-bottom:15px}
    h2{color:#E67E22;margin-top:30px;border-left:4px solid #F39C12;padding-left:10px}
    h3{color:#D35400;margin-top:20px}
    .cover{text-align:center;padding:40px 0;background:linear-gradient(135deg,#FFF9E6,#FFF)}
    .subtitle{color:#666;font-size:14px;margin-top:10px}
    .story{background:#FFF9E6;padding:20px;border-radius:10px;margin:20px 0;font-size:15px}
    .zone-card{background:#FFF;border:2px solid #F39C12;border-radius:10px;padding:20px;margin:15px 0;page-break-inside:avoid}
    .zone-header{display:flex;align-items:center;gap:10px;margin-bottom:10px}
    .zone-icon{font-size:28px}
    .zone-name{font-size:20px;font-weight:bold;color:#E67E22}
    .zone-tag{background:#F39C12;color:white;padding:3px 12px;border-radius:15px;font-size:12px}
    .zone-narrative{color:#555;font-size:14px;margin:10px 0}
    .zone-details{background:#F8F9FA;padding:12px;border-radius:8px;font-size:13px}
    .detail-item{margin:5px 0}
    .sensory-grid{display:grid;grid-template-columns:1fr 1fr;gap:15px;margin:15px 0}
    .sensory-item{background:#FEF9E7;padding:15px;border-radius:8px;text-align:center}
    .sensory-item strong{color:#D35400;font-size:16px}
    .sensory-item p{margin:8px 0 0;font-size:13px;color:#666}
    table{width:100%;border-collapse:collapse;font-size:13px;margin:15px 0}
    th{background:#E67E22;color:white;padding:10px;text-align:left}
    td{padding:8px;border-bottom:1px solid #ddd}
    .engagement-box{background:#E8F8F5;padding:15px;border-radius:8px;margin:15px 0}
    .info-grid{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin:15px 0}
    .info-box{background:#F8F9FA;padding:15px;border-radius:8px}
    """
    html += "</style></head><body>"
    html += f"""
    <div class="cover">
        <h1>🌾 {theme}</h1>
        <p class="subtitle">探学玩创 · 乡村研学策展方案</p>
        <p class="subtitle">目标人群：{target}</p>
    </div>
    
    <div class="story">
        <strong>📖 策展故事线</strong><br>
        {story}
    </div>
    
    <h2>一、动线设计</h2>
    <p>{flow}</p>
    
    <h2>二、展馆设计</h2>
    {zones_html}
    
    <h2>三、感官体验设计</h2>
    {sensory_html}
    
    <div class="info-grid">
        <div class="info-box">
            <h3>📸 拍照打卡点</h3>
            <p>{photo_spots or '暂无'}</p>
        </div>
        <div class="info-box">
            <h3>🎁 文创开发方向</h3>
            <p>{products or '暂无'}</p>
        </div>
    </div>
    
    <h2>四、装置清单</h2>
    <table>
        <tr><th>装置名称</th><th>位置</th><th>交互方式</th><th>类型</th></tr>
        {installations}
    </table>
    
    <h2>五、留客互动元素</h2>
    <div class="engagement-box">
        {engagement or '探索卡、印章收集、抽奖等'}
    </div>
    """
    html += "</body></html>"
    
    from generators.pdf_utils import generate_pdf_from_html
    generate_pdf_from_html(html, output_path)
    Path(output_path.replace(".pdf", ".html")).write_text(html, encoding="utf-8")
