"""九宫格寻宝卡物料生成器"""
from pathlib import Path
import json


STYLE_PREFIX = "竖版9:16，手绘涂鸦风，Obsidian手绘插件风格，有机线条，笔记本涂鸦质感"


def generate_treasure_hunt_card(treasure_hunt: dict, village_name: str, output_path: str):
    """生成九宫格寻宝卡 HTML/PDF
    
    Args:
        treasure_hunt: treasure_hunt 数据字典
        village_name: 村庄名称
        output_path: 输出路径
    """
    name = treasure_hunt.get("name", "村落寻宝")
    card_type = treasure_hunt.get("card_type", "九宫格")
    tasks = treasure_hunt.get("tasks", [])
    reward = treasure_hunt.get("reward_description", "完成全部任务可获得神秘小礼品")

    task_map = {t.get("grid", str(i+1)): t for i, t in enumerate(tasks)}

    grid_cells = ""
    for i in range(1, 10):
        task = task_map.get(str(i), {})
        location = task.get("location", f"任务点{i}")
        task_desc = task.get("task", f"寻找并记录任务点{i}")
        clue = task.get("clue", "")
        
        grid_cells += f"""
        <div class="grid-cell">
            <div class="cell-number">{i}</div>
            <div class="cell-location">📍 {location}</div>
            <div class="cell-task">{task_desc}</div>
            <div class="cell-clue">💡 {clue}</div>
            <div class="cell-stamp">✅</div>
        </div>
        """

    html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        @page {
            size: A4 portrait;
            margin: 0;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: "SimHei", "Microsoft YaHei", sans-serif;
            background: linear-gradient(135deg, #FFF8E7 0%, #FFF 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .card-container {
            max-width: 600px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .card-header {
            background: linear-gradient(135deg, #E74C3C 0%, #C0392B 100%);
            color: white;
            padding: 25px;
            text-align: center;
        }
        .card-title {
            font-size: 28px;
            font-weight: bold;
            margin-bottom: 5px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }
        .card-subtitle {
            font-size: 14px;
            opacity: 0.9;
        }
        .village-name {
            background: #F39C12;
            color: white;
            padding: 8px 20px;
            border-radius: 20px;
            display: inline-block;
            margin-top: 10px;
            font-size: 14px;
        }
        .grid-container {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
            padding: 20px;
            background: #FEF9E7;
        }
        .grid-cell {
            background: white;
            border: 2px solid #F39C12;
            border-radius: 12px;
            padding: 12px;
            text-align: center;
            min-height: 120px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            position: relative;
            transition: transform 0.2s;
        }
        .grid-cell:hover {
            transform: scale(1.02);
        }
        .cell-number {
            background: #E74C3C;
            color: white;
            width: 28px;
            height: 28px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 14px;
            margin: 0 auto 8px;
        }
        .cell-location {
            font-size: 11px;
            color: #27AE60;
            font-weight: bold;
            margin-bottom: 5px;
        }
        .cell-task {
            font-size: 10px;
            color: #333;
            line-height: 1.4;
            flex: 1;
        }
        .cell-clue {
            font-size: 9px;
            color: #7F8C8D;
            margin-top: 5px;
            font-style: italic;
        }
        .cell-stamp {
            position: absolute;
            top: 5px;
            right: 5px;
            font-size: 16px;
            opacity: 0;
        }
        .card-footer {
            background: #2C3E50;
            color: white;
            padding: 15px 20px;
            text-align: center;
        }
        .reward-text {
            font-size: 13px;
            margin-bottom: 10px;
        }
        .reward-icon {
            font-size: 24px;
        }
        .instructions {
            background: #EBF5FB;
            padding: 15px 20px;
            font-size: 11px;
            color: #2C3E50;
        }
        .instructions h4 {
            color: #2980B9;
            margin-bottom: 8px;
        }
        .instructions ol {
            margin-left: 20px;
        }
        .instructions li {
            margin-bottom: 3px;
        }
        .decorations {
            position: fixed;
            font-size: 60px;
            opacity: 0.1;
            pointer-events: none;
        }
        .deco-1 { top: 10px; left: 10px; }
        .deco-2 { top: 10px; right: 10px; }
        .deco-3 { bottom: 10px; left: 10px; }
        .deco-4 { bottom: 10px; right: 10px; }
    </style>
</head>
<body>
    <div class="decorations deco-1">🗺️</div>
    <div class="decorations deco-2">🎯</div>
    <div class="decorations deco-3">🔍</div>
    <div class="decorations deco-4">⭐</div>
    
    <div class="card-container">
        <div class="card-header">
            <div class="card-title">🏆 {name}</div>
            <div class="card-subtitle">{card_type}寻宝挑战</div>
            <div class="village-name">📍 {village_name}</div>
        </div>
        
        <div class="instructions">
            <h4>📋 寻宝规则</h4>
            <ol>
                <li>每人领取一张九宫格寻宝卡</li>
                <li>按照线索提示，在村落中找到对应的任务点</li>
                <li>完成任务后在对应的格子里盖章或打勾</li>
                <li>完成全部9个任务即可获得奖励</li>
            </ol>
        </div>
        
        <div class="grid-container">
            {grid_cells}
        </div>
        
        <div class="card-footer">
            <div class="reward-icon">🎁</div>
            <div class="reward-text">{reward}</div>
        </div>
    </div>
</body>
</html>"""

    html = html.replace("{name}", name)
    html = html.replace("{card_type}", card_type)
    html = html.replace("{village_name}", village_name)
    html = html.replace("{grid_cells}", grid_cells)
    html = html.replace("{reward}", reward)

    from generators.pdf_utils import generate_pdf_from_html
    generate_pdf_from_html(html, output_path)


def generate_treasure_hunt_prompt(village_name: str, features, treasure_hunt: dict = None) -> str:
    """生成寻宝卡图片的 prompt（竖版9:16）
    
    Args:
        village_name: 村庄名称
        features: 村庄特色信息
        treasure_hunt: 寻宝数据
        
    Returns:
        用于生成图片的 prompt
    """
    tasks = treasure_hunt.get("tasks", []) if treasure_hunt else []
    
    task_preview = ""
    if tasks:
        task_preview = "寻宝任务："
        for t in tasks[:3]:
            task_preview += f"{t.get('grid', '?')}. {t.get('location', '某处')}；"
    
    prompt = f"""{STYLE_PREFIX}。{village_name}村落寻宝活动海报。

主标题：{village_name}村落寻宝
副标题：九宫格探索挑战

元素设计：
- 寻宝主题元素：地图、罗盘、放大镜、宝箱、问号
- 村庄特色：{features.geography[0] if features.geography else '乡村风景'}
- 手绘涂鸦风格，有机线条，笔记本涂鸦质感

{task_preview}

风格要求：
- 竖版9:16比例
- 手绘涂鸦风格
- 适合儿童研学活动使用
- 色彩活泼但不过于花哨
- 整体风格温馨有趣"""
    
    return prompt
