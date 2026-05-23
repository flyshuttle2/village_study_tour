"""Gradio Web 入口 - 村庄文旅研学一揽子解决方案智能体"""
import gradio as gr
import os
import threading
from pathlib import Path

from config import MINIMAX_API_KEY, OUTPUT_DIR
from models.input_schema import VillageInput
from output_coordinator import OutputCoordinator


def generate_with_progress(village_name, province, city, county, township, keywords, images, local_chronicle, progress=gr.Progress()):
    if not village_name or not province or not city or not county:
        return "请填写完整的村庄信息（村名、省份、城市、县区）", None

    if not MINIMAX_API_KEY:
        return "错误：请先配置 MINIMAX_API_KEY 环境变量", None

    def run_pipeline():
        coordinator = OutputCoordinator()
        return coordinator.run_full_pipeline(village)

    try:
        chronicle_paths = []
        if local_chronicle:
            if isinstance(local_chronicle, list):
                chronicle_paths = local_chronicle
            else:
                chronicle_paths = [local_chronicle]

        village = VillageInput(
            name=village_name,
            province=province,
            city=city,
            county=county,
            township=township if township else None,
            keywords=keywords if keywords else None,
            images=images if images else [],
            local_chronicle_paths=chronicle_paths,
        )

        progress(0, desc="初始化...")
        
        result = {}
        error_msg = [None]
        
        def run():
            try:
                result.update(run_pipeline())
            except Exception as e:
                error_msg[0] = str(e)
        
        thread = threading.Thread(target=run)
        thread.start()
        
        steps = [
            (0.03, "提取村庄特色..."),
            (0.1, "生成研学解决方案..."),
            (0.15, "生成九宫格寻宝卡..."),
            (0.25, "生成教案 (1/5)..."),
            (0.32, "生成教案 (2/5)..."),
            (0.38, "生成教案 (3/5)..."),
            (0.45, "生成教案 (4/5)..."),
            (0.52, "生成教案 (5/5)..."),
            (0.58, "生成夏令营手册..."),
            (0.64, "生成策展方案..."),
            (0.7, "生成课程体系..."),
            (0.78, "生成执行表单..."),
            (0.85, "生成课程海报 (1-5)..."),
            (0.92, "生成品牌视觉..."),
            (1.0, "生成完成！"),
        ]
        
        for i, (pct, desc) in enumerate(steps):
            progress(pct, desc=desc)
            if thread.is_alive():
                thread.join(timeout=2)
            else:
                break
        
        if thread.is_alive():
            thread.join()
        
        if error_msg[0]:
            return f"生成失败：{error_msg[0]}", None
        
        files = result.get("files", {})
        
        file_list = []
        if files.get("solution_pdf"):
            path = files["solution_pdf"]
            if os.path.exists(path):
                file_list.append(path)
        
        if files.get("treasure_hunt_pdf"):
            path = files["treasure_hunt_pdf"]
            if os.path.exists(path):
                file_list.append(path)
        
        for path in files.get("lesson_plan_pdfs", []):
            if os.path.exists(path):
                file_list.append(path)
        
        if files.get("summer_camp_pdf"):
            path = files["summer_camp_pdf"]
            if os.path.exists(path):
                file_list.append(path)
        
        for path in files.get("poster_pngs", []):
            if os.path.exists(path):
                file_list.append(path)
        
        if files.get("logo_path"):
            path = files["logo_path"]
            if os.path.exists(path):
                file_list.append(path)
        
        for path in files.get("cultural_products", []):
            if os.path.exists(path):
                file_list.append(path)
        
        if files.get("keyword_course_pdf"):
            path = files["keyword_course_pdf"]
            if os.path.exists(path):
                file_list.append(path)
        
        if files.get("keyword_course_md"):
            path = files["keyword_course_md"]
            if os.path.exists(path):
                file_list.append(path)
        
        summary = f"生成完成！共 {len(file_list)} 个文件"
        if files.get("slogans"):
            summary += "\n\n品牌标语：\n" + "\n".join(files["slogans"][:3])
        
        return summary, file_list if file_list else None
        
    except Exception as e:
        return f"生成失败：{str(e)}", None


PROVINCES = [
    "福建省", "湖南省", "浙江省", "江西省", "广东省", "广西壮族自治区",
    "四川省", "贵州省", "云南省", "安徽省", "江苏省", "山东省", "河南省",
    "湖北省", "重庆市", "北京市", "上海市", "天津市", "其他"
]

css = """
/* 文件上传区域 - 缩小字号 + 替换文字 */
.file-input-compact div[class*="wrap"] * {
    font-size: 11px !important;
    white-space: nowrap !important;
}
.file-input-compact div[class*="wrap"] p {
    display: none !important;
}
.file-input-compact div[class*="wrap"]::after {
    content: "拖放文件或点击上传" !important;
    font-size: 11px !important;
    white-space: nowrap !important;
}
"""

with gr.Blocks(title="村庄研学魔法师") as demo:
    gr.HTML("""
    <h1 style="text-align:center;margin:5px 0">🏡 村庄研学魔法师</h1>
    <p style="text-align:center;color:#666;font-size:12px;margin:0 0 10px 0">将十二年乡村研学经验蒸馏进AI智能体，为村庄文旅研学产业生成一揽子解决方案</p>
    """)
    
    with gr.Row():
        with gr.Column(scale=1):
            gr.HTML('<div style="margin-bottom:8px"><b>📝 输入信息</b></div>')
            
            with gr.Row():
                village_name = gr.Textbox(placeholder="村庄名称", value="龙潭村", label="", container=False)
                province = gr.Dropdown(choices=PROVINCES, value="福建省", label="", container=False)
                city = gr.Textbox(placeholder="城市", value="宁德市", label="", container=False)
                county = gr.Textbox(placeholder="县区", value="屏南县", label="", container=False)
                township = gr.Textbox(placeholder="乡镇", label="", container=False)
            
            with gr.Row():
                keywords = gr.Textbox(placeholder="关键词 如：柿子 红粬黄酒 石拱廊桥 夯土建筑 水稻田", value="", label="", container=False)
            
            with gr.Row():
                gr.HTML('<span style="font-size:12px">🖼️ 村庄图片:</span>')
                images = gr.File(
                    file_count="multiple",
                    file_types=["image"],
                    label="",
                    height=50,
                    elem_classes="file-input-compact"
                )
            
            with gr.Row():
                gr.HTML('<span style="font-size:12px">📚 补充资料(村史/乡史/县志等):</span>')
                local_chronicle = gr.File(
                    file_count="multiple",
                    file_types=[".pdf"],
                    label="",
                    height=50,
                    elem_classes="file-input-compact"
                )
            
            with gr.Row():
                generate_btn = gr.Button("🚀 开始生成", variant="primary", size="lg")
            
            gr.Examples(
                examples=[
                    ["龙潭村", "", "福建省", "宁德市", "屏南县", "熙岭乡"],
                    ["龙潭村", "土豆 石拱廊桥", "福建省", "宁德市", "屏南县", "熙岭乡"],
                    ["龙潭村", "黄酒 竹编 四平戏", "福建省", "宁德市", "屏南县", "熙岭乡"],
                ],
                inputs=[village_name, keywords, province, city, county, township],
            )
        
        with gr.Column(scale=1):
            gr.HTML('<div style="margin-bottom:8px"><b>📦 生成结果</b></div>')
            status = gr.Textbox(label="", placeholder="生成状态...", lines=1, interactive=False)
            output_files = gr.File(label="", file_count="multiple", interactive=False, height=180)
        
        generate_btn.click(
            fn=generate_with_progress,
            inputs=[village_name, province, city, county, township, keywords, images, local_chronicle],
            outputs=[status, output_files]
        )


if __name__ == "__main__":
    print("=" * 50)
    print("村庄研学魔法师")
    print("=" * 50)
    print(f"API Key 状态: {'已配置' if MINIMAX_API_KEY else '未配置'}")
    print(f"输出目录: {OUTPUT_DIR}")
    print("启动 Gradio 服务...")
    demo.launch(server_name="0.0.0.0", server_port=7860, css=css)
