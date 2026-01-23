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
