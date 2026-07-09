"""AI 推荐说明生成服务。"""

import json
import re
import urllib.error
import urllib.request

from django.conf import settings


def format_score(value):
    """将指标值格式化为两位小数。"""
    try:
        return f"{float(value):.2f}"
    except (TypeError, ValueError):
        return "--"


def get_safety_level(score):
    """根据安全指数返回安全等级描述。"""
    score = float(score or 0)
    if score >= 85:
        return "安全水平很高"
    if score >= 75:
        return "安全水平较高"
    if score >= 60:
        return "安全水平中等"
    return "安全水平偏低"


def get_cost_level(score):
    """根据消费指数返回消费水平描述。"""
    score = float(score or 0)
    if score <= 45:
        return "消费压力较低"
    if score <= 65:
        return "消费水平中等"
    if score <= 80:
        return "消费水平中高"
    return "消费压力较高"


def get_tourism_level(score):
    """根据旅游适宜指数返回旅游适宜描述。"""
    score = float(score or 0)
    if score >= 80:
        return "旅游适宜性突出"
    if score >= 70:
        return "旅游适宜性较好"
    if score >= 60:
        return "旅游适宜性中等"
    return "旅游适宜性一般"


def build_local_explanation(country_payload):
    """在无 API Key 或远端调用失败时使用本地模板生成说明。"""
    country_name = country_payload["country_name"]
    safety_index = country_payload["safety_index"]
    happiness_index = country_payload["happiness_index"]
    cost_index = country_payload["cost_index"]
    tourism_index = country_payload["tourism_index"]
    recommendation_index = country_payload["recommendation_index"]
    continent = country_payload.get("continent") or "未分类地区"

    safety_level = get_safety_level(safety_index)
    cost_level = get_cost_level(cost_index)
    tourism_level = get_tourism_level(tourism_index)

    target_people = ["希望获得稳定旅行体验的游客"]
    if float(safety_index or 0) >= 75:
        target_people.append("亲子游、自由行和首次出境旅行人群")
    if float(cost_index or 0) <= 65:
        target_people.append("预算敏感型游客")
    if float(tourism_index or 0) >= 75:
        target_people.append("重视景点丰富度和目的地体验的人群")
    if float(happiness_index or 0) >= 75:
        target_people.append("偏好生活氛围舒适、公共服务成熟地区的人群")

    return {
        "recommendation_reason": (
            f"{country_name}位于{continent}，综合推荐指数为{format_score(recommendation_index)}。"
            f"该目的地的{tourism_level}，安全指数为{format_score(safety_index)}，"
            f"幸福指数为{format_score(happiness_index)}，整体表现较均衡。"
        ),
        "safety_notice": (
            f"当前安全判断为“{safety_level}”。出行前仍建议关注目的地最新旅行提醒，"
            "避开治安复杂区域，妥善保管证件和随身财物。"
        ),
        "cost_description": (
            f"该国消费指数为{format_score(cost_index)}，属于“{cost_level}”。"
            "建议根据住宿、交通、餐饮和景点门票提前规划预算。"
        ),
        "target_people": "、".join(dict.fromkeys(target_people)),
        "summary": (
            f"综合来看，{country_name}适合作为安全旅游国家推荐候选，"
            "尤其适合希望在安全性、旅游体验和预算之间取得平衡的用户。"
        ),
    }


def build_prompt(country_payload):
    """构造发送给大模型的提示词。"""
    return (
        "请为安全旅游国家推荐系统生成一段中文推荐说明。"
        "请只返回 JSON，不要输出 Markdown，不要添加额外解释。"
        "JSON 字段必须包含 recommendation_reason、safety_notice、"
        "cost_description、target_people、summary。"
        "要求：客观、简洁，每个字段 1 到 2 句话，不要编造实时新闻或具体事故。"
        "\n\n国家数据如下："
        f"\n国家名称：{country_payload['country_name']}"
        f"\n英文名称：{country_payload.get('country_name_en') or '--'}"
        f"\n洲别：{country_payload.get('continent') or '--'}"
        f"\n综合推荐指数：{format_score(country_payload['recommendation_index'])}"
        f"\n旅游适宜指数：{format_score(country_payload['tourism_index'])}"
        f"\n安全指数：{format_score(country_payload['safety_index'])}"
        f"\n幸福指数：{format_score(country_payload['happiness_index'])}"
        f"\n消费指数：{format_score(country_payload['cost_index'])}"
    )


def post_json(url, api_key, payload, timeout):
    """使用标准库发送 JSON 请求，避免额外 SDK 依赖。"""
    request = urllib.request.Request(
        url=url,
        data=json.dumps(payload).encode("utf-8"),
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


def normalize_remote_result(data):
    """保证远端结果字段完整。"""
    required_keys = [
        "recommendation_reason",
        "safety_notice",
        "cost_description",
        "target_people",
        "summary",
    ]
    return {key: str(data.get(key) or "").strip() for key in required_keys}


def call_deepseek(country_payload):
    """调用 DeepSeek Chat Completions API。"""
    prompt = build_prompt(country_payload)
    response = post_json(
        url=settings.DEEPSEEK_API_BASE_URL.rstrip("/") + "/chat/completions",
        api_key=settings.DEEPSEEK_API_KEY,
        timeout=settings.AI_RECOMMENDATION_TIMEOUT,
        payload={
            "model": settings.DEEPSEEK_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": "你是安全旅游国家推荐系统的说明生成助手。",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.4,
            "max_tokens": 700,
            "stream": False,
        },
    )
    content = response["choices"][0]["message"]["content"]
    return normalize_remote_result(extract_json_object(content))


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


def call_openai(country_payload):
    """调用 OpenAI Responses API。"""
    prompt = build_prompt(country_payload)
    response = post_json(
        url=settings.OPENAI_API_BASE_URL.rstrip("/") + "/responses",
        api_key=settings.OPENAI_API_KEY,
        timeout=settings.AI_RECOMMENDATION_TIMEOUT,
        payload={
            "model": settings.OPENAI_MODEL,
            "input": [
                {
                    "role": "system",
                    "content": "你是安全旅游国家推荐系统的说明生成助手。",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.4,
            "max_output_tokens": 700,
        },
    )
    return normalize_remote_result(extract_json_object(extract_openai_output_text(response)))


def call_openai_compatible(country_payload):
    """调用本地 OpenAI-compatible 模型服务。"""
    prompt = build_prompt(country_payload)
    response = post_json(
        url=settings.LOCAL_LLM_BASE_URL.rstrip("/") + "/chat/completions",
        api_key=settings.LOCAL_LLM_API_KEY,
        timeout=settings.AI_RECOMMENDATION_TIMEOUT,
        payload={
            "model": settings.LOCAL_LLM_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": "你是安全旅游国家推荐系统的说明生成助手。",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.4,
            "max_tokens": 700,
            "stream": False,
        },
    )
    content = response["choices"][0]["message"]["content"]
    return normalize_remote_result(extract_json_object(content))


def call_ollama(country_payload):
    """调用 Ollama 原生 Chat API。"""
    prompt = build_prompt(country_payload)
    response = post_json(
        url=settings.LOCAL_LLM_BASE_URL.rstrip("/") + "/api/chat",
        api_key=settings.LOCAL_LLM_API_KEY,
        timeout=settings.AI_RECOMMENDATION_TIMEOUT,
        payload={
            "model": settings.LOCAL_LLM_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": "你是安全旅游国家推荐系统的说明生成助手。",
                },
                {"role": "user", "content": prompt},
            ],
            "stream": False,
            "options": {
                "temperature": 0.4,
            },
        },
    )
    content = response["message"]["content"]
    return normalize_remote_result(extract_json_object(content))


def generate_ai_recommendation_explanation(country_payload):
    """按配置生成推荐说明，缺少 Key 或调用失败时自动回退到本地模板。"""
    provider = settings.AI_RECOMMENDATION_PROVIDER
    local_result = build_local_explanation(country_payload)

    try:
        if provider == "deepseek" and settings.DEEPSEEK_API_KEY:
            return {
                "provider": "deepseek",
                "source": "remote",
                "is_ai_generated": True,
                "explanation": call_deepseek(country_payload),
            }
        if provider == "openai" and settings.OPENAI_API_KEY:
            return {
                "provider": "openai",
                "source": "remote",
                "is_ai_generated": True,
                "explanation": call_openai(country_payload),
            }
        if provider == "openai_compatible":
            return {
                "provider": "openai_compatible",
                "source": "local_llm",
                "is_ai_generated": True,
                "explanation": call_openai_compatible(country_payload),
            }
        if provider == "ollama":
            return {
                "provider": "ollama",
                "source": "local_llm",
                "is_ai_generated": True,
                "explanation": call_ollama(country_payload),
            }
    except (urllib.error.URLError, TimeoutError, KeyError, ValueError, json.JSONDecodeError):
        pass

    return {
        "provider": "local",
        "source": "template",
        "is_ai_generated": False,
        "explanation": local_result,
    }
