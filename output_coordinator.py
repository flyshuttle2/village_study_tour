"""输出编排器 - 串联整个生成流程"""
import json
import httpx
from pathlib import Path
from datetime import datetime

from config import OUTPUT_DIR, MINIMAX_API_KEY
from models.input_schema import VillageInput
from models.output_schema import VillageFeatures
from agents.solution_agent import SolutionAgent
from agents.lesson_plan_agent import LessonPlanAgent
from agents.camp_manual_agent import CampManualAgent
from agents.exhibition_agent import ExhibitionAgent
from agents.curriculum_agent import CurriculumAgent
from multimodal.image_analyzer import ImageAnalyzer
from rag.village_knowledge import enrich_features, get_location_from_amap
from knowledge.local_chronicler import parse_local_document, merge_documents, LocalDocument
from generators.pdf_solution import generate_solution_pdf
from generators.pdf_lesson_plan import generate_lesson_plan_pdf
from generators.pdf_camp_manual import generate_camp_manual_pdf
from generators.pdf_exhibition import generate_exhibition_pdf
from generators.pdf_curriculum import generate_curriculum_pdf
from generators.treasure_hunt_generator import generate_treasure_hunt_card, generate_treasure_hunt_prompt
from generators.poster_generator import generate_all_poster_concepts, generate_poster_image
from generators.brand_generator import generate_slogans, generate_logo_concept, generate_cultural_products, generate_brand_image
from generators.pdf_keyword_course import generate_keyword_course_pdf, generate_keyword_course_markdown
from generators.pdf_execution_form import generate_execution_form_pdf
from generators.pdf_material_list import generate_material_list_pdf
from generators.pdf_inspection import generate_inspection_pdf
from generators.pdf_signin import generate_signin_pdf
from agents.keyword_course_agent import KeywordCourseAgent


class OutputCoordinator:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or MINIMAX_API_KEY
        self.solution_agent = SolutionAgent(self.api_key)
        self.lesson_plan_agent = LessonPlanAgent(self.api_key)
        self.camp_manual_agent = CampManualAgent(self.api_key)
        self.exhibition_agent = ExhibitionAgent(self.api_key)
        self.curriculum_agent = CurriculumAgent(self.api_key)
        self.image_analyzer = ImageAnalyzer(self.api_key)
        self.keyword_course_agent = KeywordCourseAgent(self.api_key)

    def run_full_pipeline(self, village: VillageInput) -> dict:
        village_name = village.name
        village_dir = OUTPUT_DIR / village_name
        village_dir.mkdir(parents=True, exist_ok=True)

        results = {
            "village_name": village_name,
            "generated_at": datetime.now().isoformat(),
            "files": {}
        }

        local_documents_info = None
        
        doc_paths = village.local_chronicle_paths or []
        if village.local_chronicle_path and isinstance(village.local_chronicle_path, str):
            doc_paths.append(village.local_chronicle_path)
        
        if doc_paths:
            parsed_docs = []
            for path in doc_paths:
                if Path(path).exists():
                    print(f"[文献] 正在解析: {Path(path).name}")
                    doc = parse_local_document(path, village.name)
                    if doc.success:
                        doc_type_names = {
                            "village_history": "村史",
                            "township_chronicle": "乡志", 
                            "county_chronicle": "县志",
                            "unknown": "未知"
                        }
                        doc_type = doc.county_info.get("doc_type", "unknown")
                        print(f"[文献] 识别类型: {doc_type_names.get(doc_type, '未知')}, 字符数: {doc.char_count}")
                        parsed_docs.append(doc)
                    else:
                        print(f"[文献] 解析失败: {doc.error}")
            
            if parsed_docs:
                local_documents_info = merge_documents(parsed_docs, village.name, village.county)
                print(f"[文献] 合并完成，主要来源: {local_documents_info.get('priority_source', '综合')}")

        if not village.latitude or not village.longitude:
            geo = get_location_from_amap(village.name, "")
            village.latitude = geo["lat"]
            village.longitude = geo["lon"]

        features = self.image_analyzer.analyze_images(
            village.images or [], village.name
        )
        features.location = village.get_full_address()
        features.latitude = village.latitude
        features.longitude = village.longitude

        features = enrich_features(features, village.province, village.city, village.county)

        print(f"[1/9] 村庄特色提取完成：{features.name}")
        print(f"  地理：{features.geography}")
        print(f"  非遗：{features.intangible_heritage}")
        print(f"  食物：{features.food}")

        keyword_courses = []
        if village.keywords:
            print(f"[关键词] 检测到关键词：{village.keywords}")
            keyword_result = self.keyword_course_agent.generate(
                village.keywords,
                features.model_dump()
            )
            if keyword_result.get("courses"):
                keyword_courses = keyword_result["courses"]
                print(f"[关键词] 生成 {len(keyword_courses)} 个课程")
                
                keyword_course_pdf_path = village_dir / f"{village_name}_特色体验课程.pdf"
                keyword_course_md_path = village_dir / f"{village_name}_特色体验课程.md"
                
                generate_keyword_course_pdf(keyword_courses, village_name, str(keyword_course_pdf_path))
                generate_keyword_course_markdown(keyword_courses, village_name, str(keyword_course_md_path))
                
                results["files"]["keyword_course_pdf"] = str(keyword_course_pdf_path)
                results["files"]["keyword_course_md"] = str(keyword_course_md_path)
                print(f"[关键词] 课程文档生成完成")
                
                if keyword_result.get("keyword_result", {}).get("rejected_keywords"):
                    rejected = keyword_result["keyword_result"]["rejected_keywords"]
                    print(f"[关键词] 以下关键词已忽略（关联度较低）：{', '.join(rejected)}")
            else:
                print(f"[关键词] 未找到匹配的课程")

        solution = self.solution_agent.generate(
            village, features, 
            local_documents_info=local_documents_info
        )
        solution_path = village_dir / f"{village_name}_研学解决方案.pdf"
        generate_solution_pdf(solution, features, str(solution_path))
        results["files"]["solution_pdf"] = str(solution_path)
        print(f"[2/9] 研学解决方案生成完成：{solution_path.name}")

        treasure_hunt = solution.get("treasure_hunt", {})
        treasure_path = village_dir / f"{village_name}_九宫格寻宝卡.pdf"
        generate_treasure_hunt_card(treasure_hunt, village_name, str(treasure_path))
        results["files"]["treasure_hunt_pdf"] = str(treasure_path)
        print(f"[3/9] 九宫格寻宝卡生成完成")

        lesson_plans = self.lesson_plan_agent.generate_all(
            features, 
            local_documents_info=local_documents_info
        )
        lesson_paths = []
        for i, plan in enumerate(lesson_plans):
            course_name = plan.get("course_name", f"课程{i+1}").replace(" ", "_")[:10]
            plan_path = village_dir / f"{village_name}_教案{i+1}_{course_name}.pdf"
            generate_lesson_plan_pdf(plan, features, str(plan_path))
            lesson_paths.append(str(plan_path))
        results["files"]["lesson_plan_pdfs"] = lesson_paths
        print(f"[4/9] 5份教案生成完成")

        summer_manual = self.camp_manual_agent.generate_summer(features, lesson_plans)
        summer_path = village_dir / f"{village_name}_夏令营研学手册.pdf"
        generate_camp_manual_pdf(summer_manual, features, "夏", str(summer_path))
        results["files"]["summer_camp_pdf"] = str(summer_path)
        print(f"[5/9] 夏令营手册生成完成")

        exhibition = self.exhibition_agent.generate(features, solution)
        exhibition_path = village_dir / f"{village_name}_策展方案.pdf"
        generate_exhibition_pdf(exhibition, features, str(exhibition_path))
        results["files"]["exhibition_pdf"] = str(exhibition_path)
        print(f"[6/9] 策展方案生成完成")

        curriculum = self.curriculum_agent.generate(features, lesson_plans)
        curriculum_path = village_dir / f"{village_name}_课程体系.pdf"
        generate_curriculum_pdf(curriculum, features, str(curriculum_path))
        results["files"]["curriculum_pdf"] = str(curriculum_path)
        print(f"[7/10] 课程体系生成完成")

        execution_form_path = village_dir / f"{village_name}_执行单.pdf"
        generate_execution_form_pdf(solution, features, lesson_plans, str(execution_form_path))
        results["files"]["execution_form_pdf"] = str(execution_form_path)
        print(f"[8/10] 活动执行单生成完成")

        material_list_path = village_dir / f"{village_name}_物料清单.pdf"
        generate_material_list_pdf(solution, features, lesson_plans, str(material_list_path))
        results["files"]["material_list_pdf"] = str(material_list_path)
        print(f"[9/10] 物料准备清单生成完成")

        inspection_path = village_dir / f"{village_name}_巡场检查表.pdf"
        generate_inspection_pdf(solution, features, str(inspection_path))
        results["files"]["inspection_pdf"] = str(inspection_path)
        print(f"[10/10] 活动前巡场检查表生成完成")

        poster_configs = generate_all_poster_concepts(solution, village_name, features, lesson_plans)
        poster_paths = []
        
        print(f"开始生成研学海报（9张）...")
        
        course_posters = poster_configs.get("course_posters", [])
        for i, poster in enumerate(course_posters):
            poster_path = village_dir / f"{village_name}_海报_课程{i+1}_{poster['course_name'][:8]}.png"
            print(f"  生成课程{i+1}海报: {poster['course_name']}")
            image_url = generate_poster_image(poster["prompt"], str(poster_path))
            poster_paths.append(self._save_image(image_url, poster_path, poster["prompt"]))
        
        day_tour_poster = poster_configs.get("day_tour_poster", {})
        if day_tour_poster.get("prompt"):
            poster_path = village_dir / f"{village_name}_海报_一日游学.png"
            print(f"  生成一日游学海报")
            image_url = generate_poster_image(day_tour_poster["prompt"], str(poster_path))
            poster_paths.append(self._save_image(image_url, poster_path, day_tour_poster["prompt"]))
        
        camp_poster = poster_configs.get("camp_poster", {})
        if camp_poster.get("prompt"):
            poster_path = village_dir / f"{village_name}_海报_{camp_poster.get('season', '夏')}令营.png"
            print(f"  生成夏令营海报")
            image_url = generate_poster_image(camp_poster["prompt"], str(poster_path))
            poster_paths.append(self._save_image(image_url, poster_path, camp_poster["prompt"]))
        
        treasure_poster = poster_configs.get("treasure_hunt_poster", {})
        if treasure_poster.get("prompt"):
            poster_path = village_dir / f"{village_name}_海报_寻宝卡.png"
            print(f"  生成寻宝卡海报")
            image_url = generate_poster_image(treasure_poster["prompt"], str(poster_path))
            poster_paths.append(self._save_image(image_url, poster_path, treasure_poster["prompt"]))
        
        village_poster = poster_configs.get("village_poster", {})
        if village_poster.get("prompt"):
            poster_path = village_dir / f"{village_name}_海报_村庄宣传.png"
            print(f"  生成村庄宣传海报")
            image_url = generate_poster_image(village_poster["prompt"], str(poster_path))
            poster_paths.append(self._save_image(image_url, poster_path, village_poster["prompt"]))
        
        results["files"]["poster_pngs"] = poster_paths
        print(f"研学海报生成完成（共{len(poster_paths)}张）")

        slogans = generate_slogans(solution, features)
        logo = generate_logo_concept(features, solution.get("overview", {}).get("theme", ""))
        
        logo_path = village_dir / f"{village_name}_研学品牌Logo.png"
        print(f"  生成品牌Logo...")
        image_url = generate_brand_image(logo["prompt"], str(logo_path))
        if image_url:
            self._save_image(image_url, logo_path, logo["prompt"])
        results["files"]["slogans"] = slogans
        results["files"]["logo_path"] = str(logo_path)
        
        cultural_paths = []
        cultural = generate_cultural_products(features)
        for p in cultural:
            cultural_path = village_dir / f"{village_name}_文创_{p['type']}.png"
            print(f"  生成文创: {p['type']}")
            image_url = generate_brand_image(p["prompt"], str(cultural_path))
            cultural_paths.append(self._save_image(image_url, cultural_path, p["prompt"]))
        results["files"]["cultural_products"] = cultural_paths
        print(f"品牌视觉生成完成")

        manifest_path = village_dir / "manifest.json"
        manifest_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

        print(f"\n{'='*50}")
        print(f"生成完成！输出目录：{village_dir}")
        print(f"{'='*50}")

        return results

    def _save_image(self, image_url: str, poster_path: Path, prompt: str) -> str:
        """下载并保存图片"""
        if image_url:
            try:
                resp = httpx.get(image_url, timeout=60)
                poster_path.write_bytes(resp.content)
                return str(poster_path)
            except Exception as e:
                print(f"  下载失败: {e}")
                poster_path.write_text(f"[下载失败] {prompt[:80]}", encoding="utf-8")
                return str(poster_path)
        else:
            poster_path.write_text(f"[生成失败] {prompt[:80]}", encoding="utf-8")
            return str(poster_path)
