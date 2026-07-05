"""批量更新国家洲别信息。"""

import json
import os
import sys
from pathlib import Path


# 将项目根目录加入 Python 路径，便于独立脚本加载 Django 配置
BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django  # noqa: E402

django.setup()

from apps.countries.models import Country  # noqa: E402


# 各大洲国家映射，使用国家英文名作为匹配主键
CONTINENT_MAP = {
    "亚洲": {
        "Afghanistan",
        "Armenia",
        "Azerbaijan",
        "Bahrain",
        "Bangladesh",
        "Bhutan",
        "Brunei",
        "Cambodia",
        "China",
        "East Timor",
        "Georgia",
        "Hong Kong",
        "India",
        "Indonesia",
        "Iran",
        "Iraq",
        "Israel",
        "Japan",
        "Jordan",
        "Kazakhstan",
        "Kuwait",
        "Kyrgyzstan",
        "Lao PDR",
        "Laos",
        "Lebanon",
        "Macao",
        "Malaysia",
        "Maldives",
        "Mongolia",
        "Myanmar",
        "Nepal",
        "North Korea",
        "Oman",
        "Pakistan",
        "Palestine",
        "Philippines",
        "Qatar",
        "Saudi Arabia",
        "Singapore",
        "South Korea",
        "Sri Lanka",
        "State of Palestine",
        "Syria",
        "Taiwan",
        "Taiwan Province of China",
        "Tajikistan",
        "Thailand",
        "Turkey",
        "Türkiye",
        "Turkmenistan",
        "United Arab Emirates",
        "Uzbekistan",
        "Vietnam",
        "Yemen",
    },
    "欧洲": {
        "Albania",
        "Andorra",
        "Austria",
        "Belarus",
        "Belgium",
        "Bosnia and Herzegovina",
        "Bulgaria",
        "Croatia",
        "Cyprus",
        "Czechia",
        "Denmark",
        "Estonia",
        "Faroe Islands",
        "Finland",
        "France",
        "Germany",
        "Greece",
        "Hungary",
        "Iceland",
        "Ireland",
        "Italy",
        "Kosovo",
        "Latvia",
        "Liechtenstein",
        "Lithuania",
        "Luxembourg",
        "Malta",
        "Moldova",
        "Monaco",
        "Montenegro",
        "Netherlands",
        "North Macedonia",
        "Norway",
        "Poland",
        "Portugal",
        "Republic of Moldova",
        "Romania",
        "Russia",
        "San Marino",
        "Serbia",
        "Slovakia",
        "Slovenia",
        "Spain",
        "Sweden",
        "Switzerland",
        "Ukraine",
        "United Kingdom",
    },
    "非洲": {
        "Algeria",
        "Angola",
        "Benin",
        "Botswana",
        "Burkina Faso",
        "Burundi",
        "Cameroon",
        "Cape Verde",
        "Central African Republic",
        "Chad",
        "Comoros",
        "Congo",
        "Cote d'Ivoire",
        "Côte d’Ivoire",
        "C么te d鈥橧voire",
        "Democratic Republic of Congo",
        "Djibouti",
        "DR Congo",
        "Egypt",
        "Equatorial Guinea",
        "Eritrea",
        "Eswatini",
        "Ethiopia",
        "Gabon",
        "Gambia",
        "Ghana",
        "Guinea",
        "Guinea-Bissau",
        "Kenya",
        "Lesotho",
        "Liberia",
        "Libya",
        "Madagascar",
        "Malawi",
        "Mali",
        "Mauritania",
        "Mauritius",
        "Morocco",
        "Mozambique",
        "Namibia",
        "Niger",
        "Nigeria",
        "Republic of Congo",
        "Rwanda",
        "Sao Tome and Principe",
        "Senegal",
        "Seychelles",
        "Sierra Leone",
        "Somalia",
        "South Africa",
        "Sudan",
        "Tanzania",
        "Togo",
        "Tunisia",
        "Uganda",
        "Zambia",
        "Zimbabwe",
    },
    "北美洲": {
        "Antigua and Barbuda",
        "Aruba",
        "Bahamas",
        "Barbados",
        "Belize",
        "Bermuda",
        "Canada",
        "Cayman Islands",
        "Costa Rica",
        "Cuba",
        "Curacao",
        "Dominica",
        "Dominican Republic",
        "El Salvador",
        "Greenland",
        "Grenada",
        "Guatemala",
        "Haiti",
        "Honduras",
        "Jamaica",
        "Mexico",
        "Nicaragua",
        "Panama",
        "Puerto Rico",
        "Saint Kitts and Nevis",
        "Saint Lucia",
        "Saint Vincent and the Grenadines",
        "Sint Maarten (Dutch part)",
        "Trinidad and Tobago",
        "Turks and Caicos Islands",
        "United States",
        "United States Virgin Islands",
    },
    "南美洲": {
        "Argentina",
        "Bolivia",
        "Brazil",
        "Chile",
        "Colombia",
        "Ecuador",
        "Guyana",
        "Paraguay",
        "Peru",
        "Suriname",
        "Uruguay",
        "Venezuela",
    },
    "大洋洲": {
        "Australia",
        "Fiji",
        "Kiribati",
        "Marshall Islands",
        "Micronesia",
        "Micronesia (country)",
        "Nauru",
        "New Zealand",
        "Palau",
        "Papua New Guinea",
        "Samoa",
        "Solomon Islands",
        "Tonga",
        "Tuvalu",
        "Vanuatu",
    },
}


def build_reverse_map():
    """构建国家到洲别的反向映射。"""
    reverse_map = {}
    for continent, country_names in CONTINENT_MAP.items():
        for name in country_names:
            reverse_map[name] = continent
    return reverse_map


def main():
    """批量更新数据库中的国家洲别。"""
    reverse_map = build_reverse_map()
    updated_count = 0
    unresolved_names = []

    for country in Country.objects.all():
        target_continent = reverse_map.get(country.name_en)
        if target_continent:
            if country.continent != target_continent:
                country.continent = target_continent
                country.save(update_fields=["continent", "updated_at"])
                updated_count += 1
        else:
            unresolved_names.append(country.name_en)

    unresolved_path = BASE_DIR / "scripts" / "unresolved_continents.json"
    unresolved_path.write_text(
        json.dumps(sorted(unresolved_names), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"已更新国家洲别：{updated_count} 条")
    print(f"未匹配国家数量：{len(unresolved_names)}")
    print(f"未匹配名单已写入：{unresolved_path}")
    if unresolved_names:
        print("未匹配国家名单预览：")
        for name in sorted(unresolved_names)[:10]:
            print(f"- {name.encode('unicode_escape').decode('ascii')}")


if __name__ == "__main__":
    main()
