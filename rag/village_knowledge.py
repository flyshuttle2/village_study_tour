from models.output_schema import VillageFeatures

KNOWLEDGE_BASE = {
    "屏南县": {
        "geography": ["鹫峰山脉", "高山丘陵", "天星山国家森林公园", "溪流峡谷"],
        "history": ["清代古廊桥", "明清古厝", "闽东北山区传统村落"],
        "intangible_heritage": ["木拱廊桥营造技艺", "屏南黄酒酿造技艺", "红曲制作技艺", "杖头木偶戏"],
        "food": ["芋头面", "米烧兔", "笋干", "黄酒", "光饼"],
        "products": ["高山白茶", "芙蓉李", "锥栗", "红曲", "屏南老酒"],
        "customs": ["迎神赛会", "农历庙会", "乡村集市（墟日）"],
        "activities": ["酿酒", "采茶", "采摘芙蓉李", "农耕"]
    },
    "龙潭村": {
        "geography": ["传统村落", "山涧溪流", "古树群"],
        "history": ["国家级传统村落", "四平戏传承地", "文创产业聚集区", "乡村振兴示范村"],
        "intangible_heritage": ["四平戏", "屏南黄酒酿造技艺", "传统夯土建筑营造技艺"],
        "food": ["古村黄酒", "本地农家菜", "时令蔬果"],
        "products": ["文创产品", "手工酿造黄酒", "传统手工艺品"],
        "customs": ["传统节庆活动", "文创市集", "村民自组织文化活动"],
        "activities": ["文创体验", "黄酒酿造体验", "古村写生", "农事体验"]
    },
    "默认": {
        "geography": ["山区", "梯田", "溪流"],
        "history": ["古建筑", "传统村落"],
        "intangible_heritage": ["传统手工艺"],
        "food": ["农家菜", "土特产"],
        "products": ["农产品", "手工艺品"],
        "customs": ["乡村习俗", "节庆活动"],
        "activities": ["农耕", "采摘", "手工艺"]
    }
}

def enrich_features(features, province, city, county):
    county_key = county.replace("县", "").replace("区", "").replace("市", "")
    city_key = city.replace("市", "")
    county_data = KNOWLEDGE_BASE.get(county_key, KNOWLEDGE_BASE.get(city_key, {}))
    village_data = KNOWLEDGE_BASE.get(features.name, {})
    default_data = KNOWLEDGE_BASE["默认"]

    def merge_lists(*lists):
        seen = set()
        result = []
        for lst in lists:
            for item in lst:
                if item not in seen:
                    seen.add(item)
                    result.append(item)
        return result

    return VillageFeatures(
        name=features.name,
        location=f"{province}{city}{county}",
        latitude=features.latitude,
        longitude=features.longitude,
        geography=merge_lists(features.geography, county_data.get("geography", []), village_data.get("geography", []), default_data["geography"]),
        history=merge_lists(features.history, county_data.get("history", []), village_data.get("history", []), default_data["history"]),
        intangible_heritage=merge_lists(features.intangible_heritage, county_data.get("intangible_heritage", []), village_data.get("intangible_heritage", []), default_data["intangible_heritage"]),
        food=merge_lists(features.food, county_data.get("food", []), village_data.get("food", []), default_data["food"]),
        products=merge_lists(features.products, county_data.get("products", []), village_data.get("products", []), default_data["products"]),
        customs=merge_lists(features.customs, county_data.get("customs", []), village_data.get("customs", []), default_data["customs"]),
        activities=merge_lists(features.activities, county_data.get("activities", []), village_data.get("activities", []), default_data["activities"]),
        tags=list(set(features.tags + county_data.get("geography", []) + county_data.get("intangible_heritage", [])))
    )

def get_location_from_amap(village_name, amap_key):
    try:
        import httpx
        resp = httpx.get("https://restapi.amap.com/v3/geocode/geo",
                          params={"key": amap_key, "address": village_name}, timeout=10)
        data = resp.json()
        if data.get("geocodes"):
            loc = data["geocodes"][0]["location"].split(",")
            return {"lat": float(loc[1]), "lon": float(loc[0])}
    except:
        pass
    return {"lat": 27.02, "lon": 118.98}
