"""智能地图问答助手服务。"""

import json
import re
import urllib.error
import urllib.request

from django.conf import settings

from apps.countries.models import CountryIndicator
from apps.recommendation.recommendation import TravelRecommendationEngine
from apps.recommendation.tourism_suitability import TourismSuitabilityCalculator


CONFLICT_COUNTRY_HINTS = {
    "Ukraine",
    "Russia",
    "Israel",
    "Syria",
    "Sudan",
    "Yemen",
    "Iraq",
    "Afghanistan",
    "Somalia",
    "Myanmar",
}

DISEASE_COUNTRY_HINTS = {
    "Democratic Republic of the Congo",
    "Congo",
    "Nigeria",
    "Uganda",
    "Sudan",
    "Ethiopia",
    "Kenya",
    "India",
    "Bangladesh",
    "Pakistan",
}

MOUNTAIN_DESTINATION_HINTS = {
    "Switzerland",
    "Austria",
    "Norway",
    "Italy",
    "France",
    "Slovenia",
    "Iceland",
    "Spain",
    "New Zealand",
    "Canada",
    "Japan",
    "Nepal",
}

CITY_DESTINATION_HINTS = {
    "France",
    "Italy",
    "Spain",
    "United Kingdom",
    "Germany",
    "Netherlands",
    "Czechia",
    "Japan",
    "Singapore",
    "United Arab Emirates",
    "United States",
    "South Korea",
}

LANDSCAPE_DESTINATION_HINTS = {
    "Switzerland",
    "Norway",
    "New Zealand",
    "Canada",
    "Iceland",
    "Austria",
    "Japan",
    "Italy",
    "France",
    "Australia",
}

CONTINENT_KEYWORDS = {
    "亚洲": "亚洲",
    "asia": "亚洲",
    "欧洲": "欧洲",
    "europe": "欧洲",
    "非洲": "非洲",
    "africa": "非洲",
    "北美": "北美洲",
    "北美洲": "北美洲",
    "north america": "北美洲",
    "南美": "南美洲",
    "南美洲": "南美洲",
    "south america": "南美洲",
    "大洋洲": "大洋洲",
    "澳洲": "大洋洲",
    "oceania": "大洋洲",
}

CONTINENT_QUERY_ALIASES = {
    "亚洲": "asia",
    "asia": "asia",
    "欧洲": "europe",
    "europe": "europe",
    "欧州": "europe",
    "非洲": "africa",
    "africa": "africa",
    "北美": "north_america",
    "北美洲": "north_america",
    "north america": "north_america",
    "南美": "south_america",
    "南美洲": "south_america",
    "south america": "south_america",
    "大洋洲": "oceania",
    "澳洲": "oceania",
    "oceania": "oceania",
}

CONTINENT_DISPLAY_NAMES = {
    "asia": "亚洲",
    "europe": "欧洲",
    "africa": "非洲",
    "north_america": "北美洲",
    "south_america": "南美洲",
    "oceania": "大洋洲",
}

COUNTRY_CONTINENT_CODES = {
    "Austria": "europe",
    "France": "europe",
    "Germany": "europe",
    "Iceland": "europe",
    "Italy": "europe",
    "Netherlands": "europe",
    "Norway": "europe",
    "Slovenia": "europe",
    "Spain": "europe",
    "Switzerland": "europe",
    "United Kingdom": "europe",
    "Czechia": "europe",
    "Canada": "north_america",
    "United States": "north_america",
    "United States of America": "north_america",
    "Australia": "oceania",
    "New Zealand": "oceania",
    "Japan": "asia",
    "South Korea": "asia",
    "Singapore": "asia",
    "United Arab Emirates": "asia",
    "Nepal": "asia",
}


def normalize_score(value):
    """将指标值转换为 float。"""
    try:
        return round(float(value), 2)
    except (TypeError, ValueError):
        return 0


def build_country_payload(indicator):
    """将国家指标整理为地图助手可用的数据结构。"""
    raw_visa_score = (
        float(indicator.visa_index)
        if float(indicator.visa_index) != 50.0
        else float(indicator.tourism_index)
    )
    country_payload = {
        "country_id": indicator.country.id,
        "country_name": indicator.country.name_zh,
        "country_name_en": indicator.country.name_en,
        "continent": indicator.country.continent,
        "raw_visa_score": raw_visa_score,
        "visa_index": normalize_score(indicator.visa_index),
        "tourism_index": normalize_score(indicator.tourism_index),
        "safety_index": normalize_score(indicator.safety_index),
        "medical_index": normalize_score(indicator.medical_index),
        "cost_index": normalize_score(indicator.cost_index),
        "ppp_index": normalize_score(indicator.cost_index),
        "happiness_index": normalize_score(indicator.overall_score),
        "year": indicator.year,
    }
    tourism_detail = TourismSuitabilityCalculator.build_detail(country_payload)
    country_payload["tourism_index"] = normalize_score(tourism_detail["tourism_index"])
    country_payload["tourism_detail"] = tourism_detail
    country_payload["recommendation_index"] = normalize_score(
        TravelRecommendationEngine.calculate_default_recommendation_index(country_payload)
    )
    return country_payload


def get_latest_country_payloads():
    """读取最新年份的国家指标数据。"""
    latest_year = CountryIndicator.objects.order_by("-year").values_list("year", flat=True).first()
    if latest_year is None:
        return None, []

    indicators = (
        CountryIndicator.objects.select_related("country")
        .filter(year=latest_year, country__is_active=True)
        .order_by("country__name_en")
    )
    return latest_year, [build_country_payload(indicator) for indicator in indicators]


def detect_intent(message):
    """根据用户自然语言判断地图动作意图。"""
    text = (message or "").strip().lower()
    if any(keyword in text for keyword in ["战事", "战争", "冲突", "打仗", "军事", "war", "conflict"]):
        return "risk_conflict"
    if any(keyword in text for keyword in ["传染病", "疫情", "流行病", "疾病", "病毒", "disease", "epidemic"]):
        return "risk_disease"
    if any(keyword in text for keyword in ["山", "雪山", "山脉", "阿尔卑斯", "mountain", "alps"]):
        return "scenery_mountain"
    if any(keyword in text for keyword in ["城市", "都市", "古城", "建筑", "city", "urban"]):
        return "scenery_city"
    if any(keyword in text for keyword in ["风景", "山水", "自然", "湖", "海", "森林", "landscape", "nature"]):
        return "scenery_landscape"
    return "general_recommendation"


def detect_continent(message):
    """从用户问题中提取洲别偏好。"""
    text = (message or "").lower()
    for keyword, continent_code in CONTINENT_QUERY_ALIASES.items():
        if keyword in text:
            return continent_code

    for keyword, continent in CONTINENT_KEYWORDS.items():
        if keyword in text:
            return continent
    return ""


def country_matches_continent(country, continent):
    """判断国家是否属于用户指定洲别，优先使用英文国家名兜底。"""
    if not continent:
        return True

    country_continent_code = COUNTRY_CONTINENT_CODES.get(country["country_name_en"])
    if country_continent_code:
        return country_continent_code == continent

    return country["continent"] == continent


def country_sort_key_for_recommendation(country):
    """推荐目的地排序。"""
    return (
        country["tourism_index"] * 0.46
        + country["recommendation_index"] * 0.28
        + country["safety_index"] * 0.18
        + country["happiness_index"] * 0.08
    )


def enrich_target(country, category, title, detail, reason, priority):
    """统一构造地图标注对象。"""
    return {
        "country_id": country["country_id"],
        "country_name": country["country_name"],
        "country_name_en": country["country_name_en"],
        "continent": country["continent"],
        "category": category,
        "priority": priority,
        "title": title,
        "detail": detail,
        "reason": reason,
        "scores": {
            "recommendation_index": country["recommendation_index"],
            "tourism_index": country["tourism_index"],
            "safety_index": country["safety_index"],
            "medical_index": country["medical_index"],
            "happiness_index": country["happiness_index"],
            "cost_index": country["cost_index"],
        },
    }


def build_conflict_targets(countries):
    """生成战事/冲突风险地图标注。"""
    hinted = [
        country
        for country in countries
        if country["country_name_en"] in CONFLICT_COUNTRY_HINTS or country["safety_index"] <= 45
    ]
    if not hinted:
        hinted = sorted(countries, key=lambda item: item["safety_index"])[:6]

    targets = []
    for country in sorted(hinted, key=lambda item: item["safety_index"])[:8]:
        targets.append(
            enrich_target(
                country=country,
                category="risk",
                priority="high",
                title="安全风险提醒",
                detail=(
                    f"{country['country_name']}当前被识别为需重点关注区域，"
                    f"安全指数为 {country['safety_index']}。"
                ),
                reason=(
                    "不推荐作为近期旅游目的地：该地安全风险信号较强，"
                    "可能影响交通、住宿、医疗救助和行程连续性。"
                ),
            )
        )
    return targets


def build_disease_targets(countries):
    """生成传染病/公共卫生风险地图标注。"""
    hinted = [
        country
        for country in countries
        if country["country_name_en"] in DISEASE_COUNTRY_HINTS
        or country["medical_index"] <= 45
    ]
    source = hinted or countries
    scored = sorted(
        source,
        key=lambda item: (item["medical_index"] * 0.7 + item["safety_index"] * 0.3),
    )
    targets = []
    for country in scored[:8]:
        targets.append(
            enrich_target(
                country=country,
                category="risk",
                priority="high" if country["medical_index"] < 50 else "medium",
                title="公共卫生关注",
                detail=(
                    f"{country['country_name']}医疗保障指数为 {country['medical_index']}，"
                    f"安全指数为 {country['safety_index']}。"
                ),
                reason=(
                    "不推荐直接作为近期出行首选：系统未接入官方疫情实时源，"
                    "但该地医疗与安全代理指标偏弱，出行前必须核验官方旅行健康提醒。"
                ),
            )
        )
    return targets


def build_scenery_targets(countries, intent, continent):
    """生成山水/城市风景推荐地图标注。"""
    if continent:
        countries = [
            country
            for country in countries
            if country_matches_continent(country, continent)
        ]

    hint_map = {
        "scenery_mountain": MOUNTAIN_DESTINATION_HINTS,
        "scenery_city": CITY_DESTINATION_HINTS,
        "scenery_landscape": LANDSCAPE_DESTINATION_HINTS,
        "general_recommendation": LANDSCAPE_DESTINATION_HINTS | CITY_DESTINATION_HINTS,
    }
    hints = hint_map[intent]
    hinted = [country for country in countries if country["country_name_en"] in hints]
    source = hinted or countries

    title_map = {
        "scenery_mountain": "山景目的地",
        "scenery_city": "城市风景目的地",
        "scenery_landscape": "自然风景目的地",
        "general_recommendation": "综合旅行目的地",
    }
    scene_label = title_map[intent]
    targets = []
    for country in sorted(source, key=country_sort_key_for_recommendation, reverse=True)[:6]:
        detail = (
            f"{country['country_name']}旅游适宜指数 {country['tourism_index']}，"
            f"推荐指数 {country['recommendation_index']}，安全指数 {country['safety_index']}。"
        )
        reason = (
            "推荐理由：旅游适宜性、综合推荐指数和安全指标表现较好，"
            "适合作为本次偏好下的候选目的地。"
        )
        targets.append(
            enrich_target(
                country=country,
                category="recommendation",
                priority="normal",
                title=scene_label,
                detail=detail,
                reason=reason,
            )
        )
    return targets


def build_local_agent_response(message):
    """本地规则版地图助手，作为大模型不可用时的稳定降级。"""
    latest_year, countries = get_latest_country_payloads()
    if not countries:
        return {
            "provider": "local",
            "source": "template",
            "is_ai_generated": False,
            "intent": "empty",
            "title": "暂无地图数据",
            "answer": "当前数据库还没有国家指标数据，无法生成地图标注。请先导入国家数据后再使用智能问答助手。",
            "year": latest_year,
            "map_targets": [],
        }

    intent = detect_intent(message)
    continent = detect_continent(message)

    if intent == "risk_conflict":
        targets = build_conflict_targets(countries)
        title = "战事与冲突风险提示"
        answer = (
            "我已把需重点关注的安全风险区域标红。"
            "这些标注基于系统安全指标与示范风险知识库生成，不等同于实时官方旅行警报；"
            "交付建议为暂不推荐前往，并在出行前核验外交、疾控和当地官方信息。"
        )
    elif intent == "risk_disease":
        targets = build_disease_targets(countries)
        title = "传染病与公共卫生风险提示"
        answer = (
            "我已把公共卫生风险代理指标偏弱的区域标红。"
            "系统当前未接入 WHO/CDC 等实时疫情源，因此这些标注用于风险筛查和演示；"
            "交付建议为暂不推荐直接选择这些目的地，需先核验官方健康提醒和疫苗要求。"
        )
    else:
        targets = build_scenery_targets(countries, intent, continent)
        title = "目的地风景推荐"
        scope = CONTINENT_DISPLAY_NAMES.get(continent, continent) or "全球"
        answer = (
            f"我已按“{message}”的偏好在{scope}范围内筛选目的地，并在地图上高亮推荐。"
            "优先考虑旅游适宜指数、综合推荐指数、安全指数和幸福指数表现较好的国家。"
        )

    return {
        "provider": "local",
        "source": "template",
        "is_ai_generated": False,
        "intent": intent,
        "title": title,
        "answer": answer,
        "year": latest_year,
        "map_targets": targets,
    }


def post_json(url, api_key, payload, timeout):
    """发送 JSON 请求到大模型服务。"""
    request = urllib.request.Request(
        url=url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def extract_json_object(text):
    """从模型输出中提取 JSON 对象。"""
    text = (text or "").strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?", "", text, flags=re.IGNORECASE).strip()
        text = re.sub(r"```$", "", text).strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if not match:
            raise
        return json.loads(match.group(0))


def extract_openai_output_text(response):
    """从 OpenAI Responses API 结果中提取文本。"""
    if response.get("output_text"):
        return response["output_text"]

    chunks = []
    for item in response.get("output", []):
        for content in item.get("content", []):
            text = content.get("text")
            if text:
                chunks.append(text)
    return "\n".join(chunks)


def build_llm_prompt(message, local_result):
    """构造大模型润色提示词。"""
    target_names = [item["country_name"] for item in local_result.get("map_targets", [])]
    return (
        "你是安全旅游可视化系统的地图问答助手。"
        "请根据系统已经筛选出的地图标注，生成简洁中文回答。"
        "只返回 JSON，不要 Markdown。字段包含 title 和 answer。"
        "不要新增国家、不要编造实时新闻、不要声称已接入官方实时预警源。"
        "风险类问题必须保留“需核验官方实时信息/旅行健康提醒”的意思。"
        "\n\n用户问题："
        f"{message}"
        "\n\n系统识别意图："
        f"{local_result.get('intent')}"
        "\n\n地图标注国家："
        f"{'、'.join(target_names) or '无'}"
        "\n\n本地回答草稿："
        f"{local_result.get('answer')}"
    )


def call_deepseek(message, local_result):
    """调用 DeepSeek Chat Completions API。"""
    prompt = build_llm_prompt(message, local_result)
    response = post_json(
        url=settings.DEEPSEEK_API_BASE_URL.rstrip("/") + "/chat/completions",
        api_key=settings.DEEPSEEK_API_KEY,
        timeout=settings.AI_RECOMMENDATION_TIMEOUT,
        payload={
            "model": settings.DEEPSEEK_MODEL,
            "messages": [
                {"role": "system", "content": "你是旅游安全地图问答助手。"},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.3,
            "max_tokens": 500,
            "stream": False,
        },
    )
    content = response["choices"][0]["message"]["content"]
    return extract_json_object(content)


def call_openai(message, local_result):
    """调用 OpenAI Responses API。"""
    prompt = build_llm_prompt(message, local_result)
    response = post_json(
        url=settings.OPENAI_API_BASE_URL.rstrip("/") + "/responses",
        api_key=settings.OPENAI_API_KEY,
        timeout=settings.AI_RECOMMENDATION_TIMEOUT,
        payload={
            "model": settings.OPENAI_MODEL,
            "input": [
                {"role": "system", "content": "你是旅游安全地图问答助手。"},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.3,
            "max_output_tokens": 500,
        },
    )
    return extract_json_object(extract_openai_output_text(response))


def call_openai_compatible(message, local_result):
    """调用 OpenAI-compatible Chat Completions API。"""
    prompt = build_llm_prompt(message, local_result)
    response = post_json(
        url=settings.LOCAL_LLM_BASE_URL.rstrip("/") + "/chat/completions",
        api_key=settings.LOCAL_LLM_API_KEY,
        timeout=settings.AI_RECOMMENDATION_TIMEOUT,
        payload={
            "model": settings.LOCAL_LLM_MODEL,
            "messages": [
                {"role": "system", "content": "你是旅游安全地图问答助手。"},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.3,
            "max_tokens": 500,
            "stream": False,
        },
    )
    content = response["choices"][0]["message"]["content"]
    return extract_json_object(content)


def call_ollama(message, local_result):
    """调用 Ollama 原生 Chat API。"""
    prompt = build_llm_prompt(message, local_result)
    response = post_json(
        url=settings.LOCAL_LLM_BASE_URL.rstrip("/") + "/api/chat",
        api_key=settings.LOCAL_LLM_API_KEY,
        timeout=settings.AI_RECOMMENDATION_TIMEOUT,
        payload={
            "model": settings.LOCAL_LLM_MODEL,
            "messages": [
                {"role": "system", "content": "你是旅游安全地图问答助手。"},
                {"role": "user", "content": prompt},
            ],
            "stream": False,
            "options": {"temperature": 0.3},
        },
    )
    return extract_json_object(response["message"]["content"])


def normalize_llm_text(remote_result):
    """只接受大模型返回的展示文案字段。"""
    return {
        "title": str(remote_result.get("title") or "").strip(),
        "answer": str(remote_result.get("answer") or "").strip(),
    }


def ensure_risk_answer_safety_text(result):
    """确保风险类回答始终保留严格安全口径。"""
    if result.get("intent") not in {"risk_conflict", "risk_disease"}:
        return result

    required_notice = (
        "交付建议：暂不推荐作为近期旅游目的地；出行前必须核验外交、疾控、"
        "旅行健康提醒和当地官方实时信息。"
    )
    answer = result.get("answer") or ""
    if "不推荐" not in answer or "官方" not in answer:
        result["answer"] = f"{answer} {required_notice}".strip()
    return result


def generate_agent_response(message):
    """生成智能地图问答结果。"""
    local_result = build_local_agent_response(message)
    provider = settings.AI_RECOMMENDATION_PROVIDER

    try:
        remote_text = None
        if provider == "deepseek" and settings.DEEPSEEK_API_KEY:
            remote_text = normalize_llm_text(call_deepseek(message, local_result))
        elif provider == "openai" and settings.OPENAI_API_KEY:
            remote_text = normalize_llm_text(call_openai(message, local_result))
        elif provider == "openai_compatible":
            remote_text = normalize_llm_text(call_openai_compatible(message, local_result))
        elif provider == "ollama":
            remote_text = normalize_llm_text(call_ollama(message, local_result))

        if remote_text and remote_text["answer"]:
            return ensure_risk_answer_safety_text({
                **local_result,
                "provider": provider,
                "source": "remote" if provider in {"deepseek", "openai"} else "local_llm",
                "is_ai_generated": True,
                "title": remote_text["title"] or local_result["title"],
                "answer": remote_text["answer"],
            })
    except (urllib.error.URLError, TimeoutError, KeyError, ValueError, json.JSONDecodeError):
        pass

    return ensure_risk_answer_safety_text(local_result)
