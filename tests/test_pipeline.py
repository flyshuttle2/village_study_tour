#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试脚本 - 用 Mock 数据跑通全流程（不调用真实 API）"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from models.input_schema import VillageInput
from models.output_schema import VillageFeatures
from output_coordinator import OutputCoordinator

village = VillageInput(
    name="龙潭村",
    province="福建省",
    city="宁德市",
    county="屏南县",
    township="熙岭乡",
    latitude=27.02,
    longitude=118.98,
    images=[],
)

class MockSolutionAgent:
    def generate(self, village, features):
        return {
            "title": f"{features.name}研学旅行解决方案",
            "overview": {
                "village_name": features.name, "location": features.location,
                "theme": "古村文创探索营", "target_audience": ["小学生", "初中生", "亲子家庭"],
                "duration": "3天2夜", "season": "全年适宜", "capacity": "30-50人/期"
            },
            "background": {
                "history": f"{features.name}位于福建省屏南县熙岭乡，是中国传统村落、国家级乡村振兴示范村，保留完整的明清古厝建筑群和非遗文化。",
                "geography": "海拔约800米，属鹫峰山脉高山丘陵地带，气候宜人，溪流穿村而过。",
                "culture": "四平戏、屏南黄酒酿造技艺、木拱廊桥营造技艺等非遗在此传承。",
                "highlights": ["传统夯土古厝", "四平戏", "文创产业", "黄酒酿造", "乡村集市"]
            },
            "objectives": [
                "了解中国传统村落的建筑特色与保护价值",
                "体验非遗文化（黄酒酿造、四平戏）",
                "感受乡村振兴背景下文创产业的发展",
                "培养乡土文化认同与文化遗产保护意识",
                "提升动手能力和团队协作精神"
            ],
            "course_design": [
                {"day": 1, "theme": "开营·走进古村",
                 "activities": [
                     {"time": "09:00-10:00", "name": "开营仪式", "location": "村口广场", "duration_minutes": 60, "content": "破冰游戏+分组+安全须知", "educational_value": "团队建设"},
                     {"time": "10:30-12:00", "name": "古村导览", "location": "村内", "duration_minutes": 90, "content": "参观明清古厝+讲解建筑特色", "educational_value": "建筑认知"},
                     {"time": "14:00-16:00", "name": "四平戏体验", "location": "古戏台", "duration_minutes": 120, "content": "学唱四平戏选段+戏服穿戴", "educational_value": "非遗传承"},
                     {"time": "16:30-18:00", "name": "古村写生", "location": "溪边/古厝前", "duration_minutes": 90, "content": "用画笔记录古村风景", "educational_value": "艺术审美"},
                 ]},
                {"day": 2, "theme": "非遗·黄酒酿造",
                 "activities": [
                     {"time": "09:00-11:30", "name": "黄酒文化讲座", "location": "酿酒坊", "duration_minutes": 150, "content": "了解屏南黄酒历史+酿造工艺", "educational_value": "传统文化"},
                     {"time": "14:00-16:00", "name": "酿酒体验", "location": "酿酒坊", "duration_minutes": 120, "content": "亲手参与酿酒环节（拌曲/入缸）", "educational_value": "动手实践"},
                     {"time": "16:30-18:00", "name": "文创市集探访", "location": "文创街区", "duration_minutes": 90, "content": "参观文创店铺+与创业者交流", "educational_value": "乡村振兴认知"},
                 ]},
                {"day": 3, "theme": "探索·成果展示",
                 "activities": [
                     {"time": "09:00-11:00", "name": "古村探秘定向", "location": "村内", "duration_minutes": 120, "content": "定向任务+民俗调查", "educational_value": "探究能力"},
                     {"time": "14:00-16:00", "name": "成果展示", "location": "活动中心", "duration_minutes": 120, "content": "小组汇报+作品展示+互评", "educational_value": "表达与反思"},
                     {"time": "16:00-17:00", "name": "闭营仪式", "location": "村口广场", "duration_minutes": 60, "content": "总结+颁发研学证书", "educational_value": "情感升华"},
                 ]},
            ],
            "logistics": {
                "accommodation": "古村民宿（体验式住宿）",
                "meals": "农家菜，食材来自本村有机农田",
                "transportation": "大巴全程接送（含应急车辆）",
                "safety": "师生比1:5，随队急救员，附近卫生院10分钟车程"
            },
            "budget": {
                "per_person": "¥980/人（含交通、食宿、材料、保险）",
                "items": ["交通：¥180", "餐饮：¥250", "住宿：¥200", "材料费：¥120", "保险：¥50", "讲师费：¥180"]
            },
            "evaluation": ["过程观察记录", "研学日志批改", "成果展示评分", "同伴互评"],
            "notes": "建议穿运动鞋/登山鞋，带防晒用品和驱蚊液；爱护古村环境，不大声喧哗；尊重当地民俗。"
        }

class MockLessonPlanAgent:
    def extract_themes(self, features):
        return [
            {"name": "古建筑探秘", "type": "探究", "block": "人文", "reason": "龙潭明清古厝保存完好，适合开展建筑美学教育"},
            {"name": "四平戏学唱", "type": "体验", "block": "人文", "reason": "四平戏是国家级非遗，村里保留有古戏台"},
            {"name": "黄酒酿造体验", "type": "体验", "block": "劳动", "reason": "屏南黄酒是省级非遗，酿酒坊可实地体验"},
            {"name": "文创产业调研", "type": "探究", "block": "人文", "reason": "龙潭是乡村振兴示范村，文创产业案例典型"},
            {"name": "乡村美食工坊", "type": "体验", "block": "劳动", "reason": "芋头面、米烧兔等乡土美食体验价值高"},
        ]

    def generate_one(self, features, course_theme):
        theme = course_theme["name"]
        return {
            "course_name": f"{features.name}{theme}研学课程",
            "course_type": course_theme["type"],
            "theme_block": course_theme["block"],
            "grade_level": "小学4-6年级",
            "duration_minutes": 90,
            "location": f"{features.name}相关体验点",
            "capacity": 30,
            "objectives": {
                "knowledge": [f"了解{theme}的基本知识", "理解相关文化/科学原理"],
                "abilities": ["培养动手操作能力", "提升观察记录技能"],
                "values": ["建立乡土文化认同", "培养文化遗产保护意识"]
            },
            "preparations": {
                "teacher": ["相关知识背景资料", "教具和材料准备", "安全预案"],
                "student": ["穿着运动装", "自带水杯", "预习相关背景知识"],
                "safety": [
                    {"risk": "工具使用不当", "measure": "老师示范在先，分组指导"},
                    {"risk": "户外蚊虫", "measure": "穿长袖，喷驱蚊液"}
                ]
            },
            "implementation": {
                "warmup": {"duration": 10, "content": f"通过提问引出{theme}主题，激发学生兴趣"},
                "activities": [
                    {"name": "基础知识讲解", "duration": 20, "steps": ["讲解原理", "展示样品", "互动问答"], "observation_points": ["学生参与度"], "recording_form": "学习记录表"},
                    {"name": "动手体验", "duration": 50, "steps": ["老师示范", "学生模仿", "独立制作"], "observation_points": ["操作规范性", "创意表现"], "recording_form": "作品评价表"},
                ],
                "summary": {"duration": 10, "content": "总结要点，布置延伸任务"}
            },
            "evaluation": {"method": "过程性评价", "rubric": "优秀/良好/合格", "reflection_questions": ["你学到了什么?", "有什么困难?"]},
            "appendix": {"task_sheet": "研学任务单", "materials": ["参考图册", "操作步骤卡"]}
        }

    def generate_all(self, features):
        themes = self.extract_themes(features)
        return [self.generate_one(features, t) for t in themes]

class MockCampManualAgent:
    def generate_summer(self, features, lesson_plans):
        return self._build_manual(features, "夏", 7, lesson_plans)
    def generate_winter(self, features, lesson_plans):
        return self._build_manual(features, "冬", 5, lesson_plans)

    def _build_manual(self, features, season, days, lesson_plans):
        daily = []
        if season == "夏":
            themes = ["开营·破冰", "古村探秘", "非遗体验", "文创调研", "美食工坊", "成果准备", "闭营"]
            for i, t in enumerate(themes):
                daily.append({"day": i+1, "theme": t, "summary": f"第{i+1}天主题活动，通过{t}培养相应能力"})
        else:
            themes = ["开营·认识", "冬日美食", "非遗手工艺", "古村年俗", "闭营"]
            for i, t in enumerate(themes):
                daily.append({"day": i+1, "theme": t, "summary": f"第{i+1}天主题活动，{t}相关内容"})

        return {
            "title": f"{features.name}{season}令营研学手册",
            "overview": {
                "name": f"{features.name}{season}令营", "theme": "古村文创探索",
                "duration": f"{days}天{self._nights(days)}夜",
                "target": "小学生/初中生/亲子家庭", "scale": "30-50人/期"
            },
            "daily_schedule": daily,
            "course_system": {"framework": "主题式课程，能力螺旋上升", "courses": [p.get("course_name","") for p in lesson_plans]},
            "living_guide": {
                "schedule": "07:00起床 - 21:30就寝",
                "meals": "三餐+下午茶，以农家菜为主",
                "accommodation": "古村民宿（2人/间，有独立卫浴）",
                "packing_list": "换洗衣物、运动鞋、洗漱用品、防蚊防晒"
            },
            "safety": {
                "general": "封闭式管理，老师24小时值班",
                "medical": "随队医护人员1名急救箱，常用药品齐全"
            },
            "parent_notice": {
                "pickup": "闭营当天17:00前接回",
                "refund": "开营前7天全额退款，3天退50%，开营后不退"
            },
            "evaluation": {"method": "成长档案+结营证书"}
        }

    def _nights(self, days):
        return days - 1


def run_mock_pipeline(village):
    print("=" * 50)
    print(f"开始 Mock 全流程测试：{village.name}")
    print("=" * 50)

    import output_coordinator
    oc = OutputCoordinator.__new__(OutputCoordinator)
    oc.api_key = "mock"
    oc.solution_agent = MockSolutionAgent()
    oc.lesson_plan_agent = MockLessonPlanAgent()
    oc.camp_manual_agent = MockCampManualAgent()

    from models.output_schema import VillageFeatures
    from rag.village_knowledge import enrich_features
    from multimodal.image_analyzer import ImageAnalyzer

    analyzer = ImageAnalyzer()
    features = analyzer.analyze_images([], village.name)
    features.location = village.get_full_address()
    features.latitude = village.latitude
    features.longitude = village.longitude
    features = enrich_features(features, village.province, village.city, village.county)

    print(f"\n村庄特色提取完成：{features.name}")
    print(f"  地理：{features.geography}")
    print(f"  非遗：{features.intangible_heritage}")
    print(f"  食物：{features.food}")

    solution = oc.solution_agent.generate(village, features)
    print(f"\n[1] 解决方案生成完成")
    print(f"    标题：{solution['title']}")
    print(f"    主题：{solution['overview']['theme']}")
    print(f"    课程天数：{len(solution['course_design'])}天")

    lesson_plans = oc.lesson_plan_agent.generate_all(features)
    print(f"\n[2] 教案生成完成，共{len(lesson_plans)}份")
    for i, p in enumerate(lesson_plans):
        print(f"    教案{i+1}：{p['course_name']}")

    summer = oc.camp_manual_agent.generate_summer(features, lesson_plans)
    winter = oc.camp_manual_agent.generate_winter(features, lesson_plans)
    print(f"\n[3] 营地手册生成完成")
    print(f"    夏令营：{summer['title']}，{len(summer['daily_schedule'])}天")
    print(f"    冬令营：{winter['title']}，{len(winter['daily_schedule'])}天")

    from generators.pdf_solution import generate_solution_pdf
    from generators.pdf_lesson_plan import generate_lesson_plan_pdf
    from generators.pdf_camp_manual import generate_camp_manual_pdf
    from generators.poster_generator import generate_poster_concepts
    from generators.brand_generator import generate_slogans
    import tempfile

    tmpdir = tempfile.mkdtemp()
    solution_pdf = f"{tmpdir}/{features.name}_研学解决方案.html"
    generate_solution_pdf(solution, features, solution_pdf)

    for i, plan in enumerate(lesson_plans):
        plan_pdf = f"{tmpdir}/{features.name}_教案{i+1}.html"
        generate_lesson_plan_pdf(plan, features, plan_pdf)

    summer_pdf = f"{tmpdir}/{features.name}_夏令营研学手册.html"
    generate_camp_manual_pdf(summer, features, "夏", summer_pdf)

    winter_pdf = f"{tmpdir}/{features.name}_冬令营研学手册.html"
    generate_camp_manual_pdf(winter, features, "冬", winter_pdf)

    posters = generate_poster_concepts(solution, features)
    slogans = generate_slogans(solution, features)

    print(f"\n[4] PDF/HTML 生成完成（WeasyPrint未安装，输出HTML）")
    print(f"    输出目录：{tmpdir}")

    print(f"\n[5] 海报概念：{len(posters)}个")
    for p in posters:
        print(f"    - {p['style']}：{p['prompt'][:50]}...")

    print(f"\n[6] 品牌标语：{len(slogans)}条")
    for s in slogans:
        print(f"    - {s}")

    print("\n" + "=" * 50)
    print("Mock 测试全部通过！")
    print("=" * 50)


if __name__ == "__main__":
    run_mock_pipeline(village)
