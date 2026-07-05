"""从 Excel 导入人均 GDP 数据到 Django 数据库。"""

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
DEFAULT_XLSX_PATH = os.path.join(CURRENT_DIR, "latest_gdp_per_capita.xlsx")

# 常见国家中文名映射，便于前端展示
COUNTRY_NAME_ZH_MAP = {
    "Hong Kong": "????",
    "Singapore": "新加坡",
    "Luxembourg": "卢森堡",
    "Ireland": "爱尔兰",
    "Macao": "中国澳门",
    "Qatar": "卡塔尔",
    "Bermuda": "百慕大",
    "Norway": "挪威",
    "Switzerland": "瑞士",
    "United States": "美国",
    "Iceland": "冰岛",
    "Denmark": "丹麦",
    "Australia": "澳大利亚",
    "Netherlands": "荷兰",
    "Austria": "奥地利",
    "Sweden": "瑞典",
    "Germany": "德国",
    "Belgium": "比利时",
    "Canada": "加拿大",
    "Finland": "芬兰",
    "France": "法国",
    "United Kingdom": "英国",
    "Japan": "日本",
    "New Zealand": "新西兰",
    "South Korea": "韩国",
    "China": "中国",
    "Malaysia": "马来西亚",
    "Thailand": "泰国",
    "Vietnam": "越南",
    "Indonesia": "印度尼西亚",
    "Portugal": "葡萄牙",
    "Spain": "西班牙",
    "Italy": "意大利",
    "Turkey": "土耳其",
    "Saudi Arabia": "沙特阿拉伯",
    "United Arab Emirates": "阿联酋",
    "Hong Kong SAR, China": "中国香港",
}

# 常见英文别名统一映射，避免重复导入
COUNTRY_NAME_ALIAS_MAP = {
    "USA": "United States",
    "U.S.A.": "United States",
    "UK": "United Kingdom",
    "UAE": "United Arab Emirates",
    "Korea, Rep.": "South Korea",
    "South Korea": "South Korea",
    "Viet Nam": "Vietnam",
    "Hong Kong SAR, China": "Hong Kong",
    "Macao SAR, China": "Macao",
    "Türkiye": "Turkey",
}



# ?????????????????????????
EXCLUDED_ENTITY_NAMES = {
    "World",
    "North America (WB)",
    "European Union (27)",
    "High-income countries",
    "Upper-middle-income countries",
    "Lower-middle-income countries",
    "Low-income countries",
    "East Asia and Pacific (WB)",
    "Latin America and Caribbean (WB)",
    "South Asia (WB)",
    "Sub-Saharan Africa (WB)",
    "Middle East, North Africa, Afghanistan and Pakistan (WB)",
    "Europe and Central Asia (WB)",
}

def safe_print(message):
    """兼容 Windows 终端编码的安全输出函数。"""
    try:
        print(message)
    except UnicodeEncodeError:
        fallback_message = message.encode("gbk", errors="replace").decode("gbk")
        print(fallback_message)


def normalize_country_name(country_name_en):
    """统一国家英文名，减少重复导入。"""
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


def generate_country_code(country_name, index):
    """为缺失国家生成唯一占位代码。"""
    letters = re.sub(r"[^A-Za-z]", "", country_name).upper()
    prefix = (letters[:3] or "CTY").ljust(3, "X")
    return f"{prefix}{index:04d}"


def get_country_name_zh(country_name_en):
    """获取国家中文名，若无映射则退回英文名。"""
    return COUNTRY_NAME_ZH_MAP.get(country_name_en, country_name_en)


def calculate_normalized_score(value, min_value, max_value):
    """对原始人均 GDP 进行极差标准化，映射到 0-100。"""
    if max_value == min_value:
        return Decimal("50.00")
    normalized = ((value - min_value) / (max_value - min_value)) * Decimal("100")
    return normalized.quantize(Decimal("0.01"))


def import_gdp_per_capita_data(file_path=DEFAULT_XLSX_PATH):
    """将人均 GDP 数据导入 CountryIndicator.cost_index。"""
    if not os.path.exists(file_path):
        safe_print(f"未找到导入文件：{file_path}")
        return

    try:
        Country.objects.exists()
    except ProgrammingError:
        safe_print("数据库表尚未创建，请先执行迁移命令：")
        safe_print("python manage.py makemigrations")
        safe_print("python manage.py migrate")
        return

    rows = read_xlsx_rows(file_path)
    if len(rows) <= 1:
        safe_print("Excel 文件中没有可导入的数据。")
        return

    header = rows[0]
    expected_header = ["Country", "Year", "GDP per capita"]
    if header[:3] != expected_header:
        safe_print(f"Excel 表头不符合预期，当前表头为：{header}")
        return

    parsed_records = []
    gdp_values = []
    for row in rows[1:]:
        if len(row) < 3:
            continue

        country_name_en = normalize_country_name(str(row[0]).strip())
        year_text = str(row[1]).strip()
        gdp_text = str(row[2]).strip()
        if not country_name_en or not year_text or not gdp_text:
            continue
        if country_name_en in EXCLUDED_ENTITY_NAMES:
            continue

        year = int(float(year_text))
        gdp_value = Decimal(gdp_text)
        parsed_records.append(
            {
                "country_name_en": country_name_en,
                "year": year,
                "gdp_value": gdp_value,
            }
        )
        gdp_values.append(gdp_value)

    if not parsed_records:
        safe_print("未解析到有效的人均 GDP 数据。")
        return

    min_gdp = min(gdp_values)
    max_gdp = max(gdp_values)

    created_country_count = 0
    updated_indicator_count = 0

    for index, record in enumerate(parsed_records, start=1):
        country_name_en = record["country_name_en"]
        year = record["year"]
        gdp_value = record["gdp_value"]
        normalized_score = calculate_normalized_score(gdp_value, min_gdp, max_gdp)

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

        indicator, created = CountryIndicator.objects.get_or_create(
            country=country,
            year=year,
            defaults={
                "safety_index": Decimal("50.00"),
                # 将标准化后的人均 GDP 正式写入消费水平指标字段
                "cost_index": normalized_score,
                "climate_index": Decimal("50.00"),
                "medical_index": Decimal("50.00"),
                "visa_index": Decimal("50.00"),
                "overall_score": Decimal("50.00"),
                "data_source": "latest_gdp_per_capita.xlsx 导入的人均 GDP 标准化数据",
            },
        )

        if not created:
            indicator.cost_index = normalized_score
            if indicator.data_source:
                if "人均 GDP 标准化数据" not in indicator.data_source:
                    indicator.data_source = (
                        f"{indicator.data_source}；latest_gdp_per_capita.xlsx 导入的人均 GDP 标准化数据"
                    )
            else:
                indicator.data_source = "latest_gdp_per_capita.xlsx 导入的人均 GDP 标准化数据"
            indicator.save(update_fields=["cost_index", "data_source", "updated_at"])

        updated_indicator_count += 1
        safe_print(
            f"已导入：{country_name_en} -> 原始人均 GDP {gdp_value}，标准化得分 {normalized_score}"
        )

    safe_print("导入完成。")
    safe_print(f"新增国家数量：{created_country_count}")
    safe_print(f"处理指标记录数量：{updated_indicator_count}")
    safe_print(f"最小人均 GDP：{min_gdp}")
    safe_print(f"最大人均 GDP：{max_gdp}")


if __name__ == "__main__":
    import_gdp_per_capita_data()
