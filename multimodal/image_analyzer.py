from models.output_schema import VillageFeatures
from typing import List


class ImageAnalyzer:
    def __init__(self, api_key=None):
        self.enabled = False

    def analyze_images(self, image_list: List[str], village_name: str) -> VillageFeatures:
        return VillageFeatures(
            name=village_name,
            location="待补充",
            latitude=27.02,
            longitude=118.98,
            geography=["丘陵", "梯田", "溪流", "山区"],
            history=["古建筑", "传统村落"],
            intangible_heritage=["传统手工艺"],
            food=["农家菜", "土特产"],
            products=["农产品", "手工艺品"],
            customs=["乡村习俗", "节庆活动"],
            activities=["农耕", "采摘", "手工艺"],
            tags=["传统村落", "乡村"]
        )
