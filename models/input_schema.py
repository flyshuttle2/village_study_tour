from pydantic import BaseModel, Field
from typing import Optional, List


class VillageInput(BaseModel):
    name: str = Field(..., description="村庄名称，含省市区县")
    province: str = Field(..., description="省份")
    city: str = Field(..., description="城市")
    county: str = Field(..., description="县/区")
    township: Optional[str] = Field(None, description="乡镇")
    keywords: Optional[str] = Field(None, description="关键词，空格分隔，如：土豆 石拱廊桥 黄酒")
    latitude: Optional[float] = Field(None, description="纬度")
    longitude: Optional[float] = Field(None, description="经度")
    images: Optional[List[str]] = Field(default_factory=list, description="图片base64或URL列表")
    videos: Optional[List[str]] = Field(default_factory=list, description="视频路径或URL列表")
    custom_tags: Optional[List[str]] = Field(default_factory=list, description="用户手动标注的特色标签")
    local_chronicle_path: Optional[str] = Field(None, description="地方文献PDF路径，支持村史/乡志/县志（可选）")
    local_chronicle_paths: Optional[List[str]] = Field(default_factory=list, description="多个地方文献PDF路径（可选）")
    fanpu_cases_path: Optional[str] = Field(None, description="凡朴案例文档路径（可选）")

    def get_full_address(self) -> str:
        parts = [self.province, self.city, self.county]
        if self.township:
            parts.append(self.township)
        parts.append(self.name)
        return "".join(parts)
