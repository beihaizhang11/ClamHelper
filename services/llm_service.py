import os
import requests

DASHSCOPE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"

def get_cocktail_suggestion(inventory_list, user_request):
    api_key = os.environ.get("DASHSCOPE_API_KEY")

    if not api_key:
        return (
            "提示：未检测到 DASHSCOPE_API_KEY，正在使用模拟模式。\n\n"
            "推荐：经典金汤力 (Gin & Tonic)\n"
            "- 金酒 45ml\n- 通宁水\n- 柠檬角\n"
        )

    inventory_str = ", ".join(inventory_list)

    payload = {
        "model": "qwen-plus",
        "messages": [
            {"role": "system", "content": "你是一位专业的调酒师。"},
            {
                "role": "user",
                "content": f"""
我有以下酒水库存：
{inventory_str}

用户需求：
{user_request}

请推荐一款鸡尾酒（只能一种），包含：
1. 名称
2. 配方
3. 制作步骤
4. 只用给我以上三个步骤的内容，去除其他不必要的文字

中文回答。
"""
            }
        ],
        "temperature": 0.7
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        resp = requests.post(
            DASHSCOPE_URL,
            json=payload,
            headers=headers,
            timeout=30
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]

    except Exception as e:
        return f"获取建议时出错: {e}"

def generate_event_summary(event_name, date_str, stats_summary):
    api_key = os.environ.get("DASHSCOPE_API_KEY")
    
    if not api_key:
        return "今夜微醺，好友相聚。虽然没有 AI 的加持，但快乐是真实的。（模拟总结）"

    prompt = f"""
    活动名称：{event_name}
    日期：{date_str}
    消费统计：
    {stats_summary}

    请以一位优雅的日式酒吧老板的口吻，为这场聚会写一段简短的“今夜总结语”（100字以内）。
    风格要求：温暖、治愈、稍微带一点点感性，类似于《深夜食堂》的旁白。
    内容包含：对大家酒量的调侃（如果有数据支持）、对聚会氛围的总结。
    """
    
    payload = {
        "model": "qwen-plus",
        "messages": [
            {"role": "system", "content": "你是一位经营日式酒吧多年的老板，见惯了悲欢离合，说话温和而有深意。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.8
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        resp = requests.post(
            DASHSCOPE_URL,
            json=payload,
            headers=headers,
            timeout=30
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"总结生成失败: {e}"

def get_omakase_suggestion(inventory_list, mood, weather):
    api_key = os.environ.get("DASHSCOPE_API_KEY")
    if not api_key:
        return "Kenji (模拟): 今天的风有点喧嚣呢... 不如来杯热托迪 (Hot Toddy) 暖暖身子吧。"

    inventory_str = ", ".join(inventory_list)
    prompt = f"""
    我是一个家庭调酒师，我有这些库存：{inventory_str}。
    现在客人的心情是：{mood}。
    现在的天气是：{weather}。

    请你扮演一位名叫 Kenji 的日式酒吧老板（类似于《深夜食堂》的老板）。
    请根据客人的心情和天气，以及我的库存，为他特调一杯酒。

    回复格式要求：
    1. 开场白：一句富有哲理或温暖的话，与心情/天气有关。（50字以内）
    2. 推荐酒名：(中英文)
    3. 简易配方：(基于我的库存)
    4. 结束语：一句简单的祝福。

    请用温暖、治愈的语气。
    """

    payload = {
        "model": "qwen-plus",
        "messages": [
            {"role": "system", "content": "你是一位拥有20年经验的日式酒吧老板 Kenji，擅长观察人心，制作抚慰心灵的鸡尾酒。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.9 # Higher creativity
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        resp = requests.post(
            DASHSCOPE_URL,
            json=payload,
            headers=headers,
            timeout=30
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Kenji 似乎正在忙碌中... (错误: {e})"


