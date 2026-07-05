"""从 Excel 导入签证便利评分到旅游适宜指数字段。"""

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
DEFAULT_XLSX_PATH = os.path.join(CURRENT_DIR, "china_passport_visa_score_144.xlsx")
DEFAULT_YEAR = 2024

# 常见国家中文名映射，便于前端展示
COUNTRY_NAME_ZH_MAP = {
    "Afghanistan": "阿富汗",
    "Albania": "阿尔巴尼亚",
    "Algeria": "阿尔及利亚",
    "Andorra": "安道尔",
    "Angola": "安哥拉",
    "Antigua and Barbuda": "安提瓜和巴布达",
    "Argentina": "阿根廷",
    "Armenia": "亚美尼亚",
    "Australia": "澳大利亚",
    "Austria": "奥地利",
    "Bahrain": "巴林",
    "Belgium": "比利时",
    "Brazil": "巴西",
    "Canada": "加拿大",
    "China": "中国",
    "Denmark": "丹麦",
    "France": "法国",
    "Germany": "德国",
    "Hong Kong": "中国香港",
    "Iceland": "冰岛",
    "Indonesia": "印度尼西亚",
    "Italy": "意大利",
    "Japan": "日本",
    "Malaysia": "马来西亚",
    "New Zealand": "新西兰",
    "Norway": "挪威",
    "Portugal": "葡萄牙",
    "Saudi Arabia": "沙特阿拉伯",
    "Singapore": "新加坡",
    "South Korea": "韩国",
    "Spain": "西班牙",
    "Switzerland": "瑞士",
    "Thailand": "泰国",
    "Turkey": "土耳其",
    "United Arab Emirates": "阿联酋",
    "United Kingdom": "英国",
    "United States": "美国",
    "Vietnam": "越南",
}

# 常见英文别名统一映射，避免与已有国家重复
COUNTRY_NAME_ALIAS_MAP = {
    "USA": "United States",
    "U.S.A.": "United States",
    "UK": "United Kingdom",
    "UAE": "United Arab Emirates",
    "Republic of Korea": "South Korea",
    "Korea, Rep.": "South Korea",
    "Hong Kong SAR of China": "Hong Kong",
    "Hong Kong SAR, China": "Hong Kong",
    "Viet Nam": "Vietnam",
    "Russian Federation": "Russia",
    "Czech Republic": "Czechia",
    "Congo (Dem. Rep.)": "Democratic Republic of Congo",
    "Cote d'Ivoire (Ivory Coast)": "Cote d'Ivoire",
    "Türkiye": "Turkey",
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


def read_target_sheet_rows(file_path, target_sheet_name):
    """使用标准库解析指定工作表并返回二维数组。"""
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
        sheets = workbook_xml.findall("a:sheets/a:sheet", ns)
        target_sheet = None
        for sheet in sheets:
            if sheet.attrib.get("name") == target_sheet_name:
                target_sheet = sheet
                break

        if target_sheet is None:
            raise ValueError(f"未找到目标工作表：{target_sheet_name}")

        relation_id = target_sheet.attrib.get(
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


def convert_visa_score_to_index(visa_score):
    """将 visa_score 转换为 0-100 的旅游适宜指数。"""
    return (visa_score * Decimal("100")).quantize(Decimal("0.01"))


def import_visa_score_data(file_path=DEFAULT_XLSX_PATH):
    """将签证便利评分导入 CountryIndicator.tourism_index。"""
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

    rows = read_target_sheet_rows(file_path, "144国评分表")
    if len(rows) <= 1:
        safe_print("Excel 文件中没有可导入的数据。")
        return

    header = rows[0]
    expected_header = [
        "seq",
        "country",
        "visa_requirement_raw",
        "visa_type_group",
        "visa_score",
        "source_url",
        "scoring_rule",
    ]
    if header[:7] != expected_header:
        safe_print(f"Excel 表头不符合预期，当前表头为：{header}")
        return

    created_country_count = 0
    updated_indicator_count = 0

    for index, row in enumerate(rows[1:], start=1):
        if len(row) < 5:
            continue

        country_name_en = normalize_country_name(str(row[1]).strip())
        visa_score_text = str(row[4]).strip()
        if not country_name_en or not visa_score_text:
            continue

        visa_score = Decimal(visa_score_text)
        tourism_index = convert_visa_score_to_index(visa_score)

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
            year=DEFAULT_YEAR,
            defaults={
                "safety_index": Decimal("50.00"),
                "cost_index": Decimal("50.00"),
                "tourism_index": tourism_index,
                "climate_index": Decimal("50.00"),
                "medical_index": Decimal("50.00"),
                "visa_index": Decimal("50.00"),
                "overall_score": Decimal("50.00"),
                "data_source": "china_passport_visa_score_144.xlsx 导入的签证便利评分数据",
            },
        )

        if not created:
            indicator.tourism_index = tourism_index
            if indicator.data_source:
                if "签证便利评分数据" not in indicator.data_source:
                    indicator.data_source = (
                        f"{indicator.data_source}；china_passport_visa_score_144.xlsx 导入的签证便利评分数据"
                    )
            else:
                indicator.data_source = "china_passport_visa_score_144.xlsx 导入的签证便利评分数据"
            indicator.save(update_fields=["tourism_index", "data_source", "updated_at"])

        updated_indicator_count += 1
        safe_print(
            f"已导入：{country_name_en} -> visa_score {visa_score}，旅游适宜指数 {tourism_index}"
        )

    safe_print("导入完成。")
    safe_print(f"新增国家数量：{created_country_count}")
    safe_print(f"处理指标记录数量：{updated_indicator_count}")


if __name__ == "__main__":
    import_visa_score_data()
