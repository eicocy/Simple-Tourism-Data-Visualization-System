"""从 Excel 导入安全指数数据到 Django 数据库。"""

import os
import re
import sys
import zipfile
from decimal import Decimal
import xml.etree.ElementTree as ET

import django
from django.db import ProgrammingError


# 将 server 目录加入 Python 路径，便于脚本独立执行
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SERVER_DIR = os.path.dirname(CURRENT_DIR)
if SERVER_DIR not in sys.path:
    sys.path.insert(0, SERVER_DIR)

# 指定 Django 配置模块
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.countries.models import Country, CountryIndicator  # noqa: E402


# 默认 Excel 文件路径
DEFAULT_XLSX_PATH = os.path.join(CURRENT_DIR, "global_safety_full_144.xlsx")

# 工作表中年份的默认值
DEFAULT_YEAR = 2024

# 部分常见国家中文名映射，便于展示更友好
COUNTRY_NAME_ZH_MAP = {
    "Hong Kong": "????",
    "Singapore": "新加坡",
    "Tajikistan": "塔吉克斯坦",
    "China": "中国",
    "Oman": "阿曼",
    "Saudi Arabia": "沙特阿拉伯",
    "Hong Kong": "中国香港",
    "Kuwait": "科威特",
    "Norway": "挪威",
    "Bahrain": "巴林",
    "Japan": "日本",
    "South Korea": "韩国",
    "Thailand": "泰国",
    "Malaysia": "马来西亚",
    "United Arab Emirates": "阿联酋",
    "Switzerland": "瑞士",
    "Germany": "德国",
    "France": "法国",
    "Italy": "意大利",
    "Spain": "西班牙",
    "Canada": "加拿大",
    "United States": "美国",
    "Australia": "澳大利亚",
    "New Zealand": "新西兰",
    "Turkey": "土耳其",
    "Vietnam": "越南",
    "Indonesia": "印度尼西亚",
    "Portugal": "葡萄牙",
}



# ????????????????????
COUNTRY_NAME_ALIAS_MAP = {
    "USA": "United States",
    "U.S.A.": "United States",
    "UK": "United Kingdom",
    "UAE": "United Arab Emirates",
    "South Korea": "South Korea",
    "Viet Nam": "Vietnam",
}


def normalize_country_name(country_name_en):
    """???????????????"""
    return COUNTRY_NAME_ALIAS_MAP.get(country_name_en.strip(), country_name_en.strip())


def read_xlsx_rows(file_path):
    """使用标准库解析 xlsx 文件并返回二维数组。"""
    with zipfile.ZipFile(file_path) as workbook:
        shared_strings = []
        if "xl/sharedStrings.xml" in workbook.namelist():
            root = ET.fromstring(workbook.read("xl/sharedStrings.xml"))
            ns = {"a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
            for item in root.findall("a:si", ns):
                text = "".join(node.text or "" for node in item.findall(".//a:t", ns))
                shared_strings.append(text)

        workbook_xml = ET.fromstring(workbook.read("xl/workbook.xml"))
        ns = {
            "a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
            "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
        }
        first_sheet = workbook_xml.findall("a:sheets/a:sheet", ns)[0]
        relation_id = first_sheet.attrib.get(
            "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
        )

        workbook_rels = ET.fromstring(workbook.read("xl/_rels/workbook.xml.rels"))
        rel_ns = {"a": "http://schemas.openxmlformats.org/package/2006/relationships"}
        relation_map = {
            relation.attrib["Id"]: relation.attrib["Target"]
            for relation in workbook_rels.findall("a:Relationship", rel_ns)
        }

        sheet_target = relation_map[relation_id].lstrip("/")
        if not sheet_target.startswith("xl/"):
            sheet_target = f"xl/{sheet_target}"

        sheet_xml = ET.fromstring(workbook.read(sheet_target))
        rows = sheet_xml.findall(
            ".//a:sheetData/a:row",
            {"a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"},
        )
        sheet_ns = {"a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}

        parsed_rows = []
        for row in rows:
            values = []
            for cell in row.findall("a:c", sheet_ns):
                cell_type = cell.attrib.get("t")
                inline_text = cell.find("a:is", sheet_ns)
                value_node = cell.find("a:v", sheet_ns)

                if inline_text is not None:
                    value = "".join(
                        node.text or "" for node in inline_text.findall(".//a:t", sheet_ns)
                    )
                else:
                    value = value_node.text if value_node is not None else ""
                    if cell_type == "s" and value != "":
                        value = shared_strings[int(value)]

                values.append(value)
            parsed_rows.append(values)

        return parsed_rows


def extract_year_from_filename_or_sheet():
    """提取导入年份，当前固定返回 2024。"""
    return DEFAULT_YEAR


def generate_country_code(country_name, index):
    """为缺失国家生成唯一占位代码。"""
    # 先提取国家名称中的英文字母作为前缀
    letters = re.sub(r"[^A-Za-z]", "", country_name).upper()
    prefix = (letters[:3] or "CTY").ljust(3, "X")
    return f"{prefix}{index:04d}"


def get_country_name_zh(country_name_en):
    """获取国家中文名，若无映射则回退为英文名。"""
    return COUNTRY_NAME_ZH_MAP.get(country_name_en, country_name_en)


def import_safety_data(file_path=DEFAULT_XLSX_PATH):
    """将安全指数数据导入 Country 和 CountryIndicator 表。"""
    if not os.path.exists(file_path):
        print(f"未找到导入文件：{file_path}")
        return

    try:
        # 先触发表查询，提前检查数据库表是否已迁移
        Country.objects.exists()
    except ProgrammingError:
        print("数据库表尚未创建，请先执行迁移命令：")
        print("python manage.py makemigrations")
        print("python manage.py migrate")
        return

    rows = read_xlsx_rows(file_path)
    if len(rows) <= 1:
        print("Excel 文件中没有可导入的数据。")
        return

    header = rows[0]
    if header[:2] != ["Country", "Safe_to_Walk_%"]:
        print(f"Excel 表头不符合预期，当前表头为：{header}")
        return

    import_year = extract_year_from_filename_or_sheet()
    created_country_count = 0
    updated_indicator_count = 0

    for index, row in enumerate(rows[1:], start=1):
        if len(row) < 2:
            continue

        country_name_en = normalize_country_name(str(row[0]).strip())
        safety_raw_value = str(row[1]).strip()
        if not country_name_en or not safety_raw_value:
            continue

        safety_index = Decimal(safety_raw_value).quantize(Decimal("0.01"))

        # 优先按英文名查找国家，若不存在则创建基础国家信息
        country = Country.objects.filter(name_en=country_name_en).first()
        if not country:
            generated_code = generate_country_code(country_name_en, index)
            while Country.objects.filter(code=generated_code).exists():
                index += 1
                generated_code = generate_country_code(country_name_en, index)

            country = Country.objects.create(
                name_zh=get_country_name_zh(country_name_en),
                name_en=country_name_en,
                code=generated_code,
                continent="待补充",
                capital="",
                language="",
                currency="",
                is_active=True,
            )
            created_country_count += 1

        # 更新或创建年度指标数据
        indicator, created = CountryIndicator.objects.get_or_create(
            country=country,
            year=import_year,
            defaults={
                "safety_index": safety_index,
                "cost_index": Decimal("50.00"),
                "climate_index": Decimal("50.00"),
                "medical_index": Decimal("50.00"),
                "visa_index": Decimal("50.00"),
                "overall_score": safety_index,
                "data_source": "global_safety_full_144.xlsx 导入的 2024 安全指数数据",
            },
        )

        if not created:
            indicator.safety_index = safety_index
            if not indicator.data_source:
                indicator.data_source = "global_safety_full_144.xlsx 导入的 2024 安全指数数据"
            indicator.save(
                update_fields=["safety_index", "data_source", "updated_at"]
            )

        updated_indicator_count += 1
        print(f"已导入：{country_name_en} -> 安全指数 {safety_index}")

    print("导入完成。")
    print(f"新增国家数量：{created_country_count}")
    print(f"处理指标记录数量：{updated_indicator_count}")


if __name__ == "__main__":
    import_safety_data()
