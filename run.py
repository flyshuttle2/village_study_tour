#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CLI 入口 - 乡村文旅研学解决方案生成器"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config import MINIMAX_API_KEY
from models.input_schema import VillageInput
from output_coordinator import OutputCoordinator


def main():
    parser = argparse.ArgumentParser(description="乡村文旅研学解决方案生成器")
    parser.add_argument("name", help="村庄名称")
    parser.add_argument("--province", "-p", default="福建省", help="省份")
    parser.add_argument("--city", "-c", default="宁德市", help="城市")
    parser.add_argument("--county", "-y", default="屏南县", help="县区")
    parser.add_argument("--township", "-t", default=None, help="乡镇")
    parser.add_argument("--lat", type=float, default=None, help="纬度")
    parser.add_argument("--lon", type=float, default=None, help="经度")
    parser.add_argument("--mock", "-m", action="store_true", help="使用 Mock 模式（不调用 API）")

    args = parser.parse_args()

    if not args.mock and not MINIMAX_API_KEY:
        print("错误：请设置 MINIMAX_API_KEY 环境变量，或使用 --mock 模式")
        print("  export MINIMAX_API_KEY=your-key  # Linux/Mac")
        print("  set MINIMAX_API_KEY=your-key     # Windows")
        sys.exit(1)

    village = VillageInput(
        name=args.name,
        province=args.province,
        city=args.city,
        county=args.county,
        township=args.township,
        latitude=args.lat,
        longitude=args.lon,
    )

    print("=" * 50)
    print(f"村庄：{village.name}")
    print(f"位置：{village.get_full_address()}")
    print(f"模式：{'Mock' if args.mock else '真实API'}")
    print("=" * 50)

    if args.mock:
        from tests.test_pipeline import run_mock_pipeline
        run_mock_pipeline(village)
    else:
        coordinator = OutputCoordinator()
        results = coordinator.run_full_pipeline(village)
        print(f"\n生成完成！输出目录：{results.get('village_name', args.name)}")


if __name__ == "__main__":
    main()
