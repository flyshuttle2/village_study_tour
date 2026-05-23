from pydantic import BaseModel
from typing import List, Dict, Optional

class VillageFeatures(BaseModel):
    name: str
    location: str
    latitude: float
    longitude: float
    geography: List[str] = []
    history: List[str] = []
    intangible_heritage: List[str] = []
    food: List[str] = []
    products: List[str] = []
    customs: List[str] = []
    activities: List[str] = []
    tags: List[str] = []

class SolutionOverview(BaseModel):
    village_name: str
    location: str
    theme: str
    target_audience: List[str]
    duration: str
    season: str
    capacity: str

class SolutionOutput(BaseModel):
    title: str
    overview: SolutionOverview
    background: Dict
    objectives: List[str]
    course_design: List[Dict]
    logistics: Dict
    budget: Dict
    evaluation: List[str]
    notes: str

class LessonPlanOutput(BaseModel):
    course_name: str
    course_type: str
    theme_block: str
    grade_level: str
    duration_minutes: int
    location: str
    capacity: int
    objectives: Dict
    preparations: Dict
    implementation: Dict
    evaluation: Dict
    appendix: Dict

class CampManualOutput(BaseModel):
    season: str
    days: int
    title: str
    overview: Dict
    daily_schedule: List[Dict]
    course_system: Dict
    living_guide: Dict
    safety: Dict
    parent_notice: Dict
    evaluation: Dict

class ExhibitionZone(BaseModel):
    zone_name: str
    tan_xue_wan_chuang_tag: str
    narrative: str
    key_exhibits: List[str] = []
    interactive_nodes: List[str] = []
    workshop_items: List[str] = []


class ExhibitionOutput(BaseModel):
    curatorial_theme: str
    target_audience: List[str]
    exhibition_zones: List[ExhibitionZone]
    sensory_design: Dict
    visitor_flow: str
    installation_list: List[Dict]
    cultural_products: List[str]


class CurriculumOutput(BaseModel):
    philosophy: str
    teaching_methods: List[str]
    course_sequence: List[Dict]
    workshop_list: List[Dict]


class GenerationResult(BaseModel):
    village_name: str
    solution_pdf: str
    lesson_plan_pdfs: List[str]
    summer_camp_pdf: str
    winter_camp_pdf: str
    exhibition_pdf: Optional[str] = None
    curriculum_pdf: Optional[str] = None
    poster_pngs: List[str]
    slogans: List[str]
    logo_path: str
    cultural_product_pngs: List[str]
