import os
import requests
import json
import re

DASHSCOPE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"

def _clean_json_string(s):
    """Attempt to extract and clean JSON string from LLM response"""
    s = s.strip()
    # Try to find JSON block
    match = re.search(r"```json\s*(.*?)\s*```", s, re.DOTALL)
    if match:
        s = match.group(1)
    elif s.startswith("```"):
        s = s.strip("`")
    return s

def get_cocktail_suggestion(inventory_list, user_request):
    api_key = os.environ.get("DASHSCOPE_API_KEY")

    if not api_key:
        return {
            "name": "经典金汤力 (Gin & Tonic) [模拟]",
            "ingredients": [
                {"name": "金酒", "amount": 45, "unit": "ml"},
                {"name": "通宁水", "amount": 100, "unit": "ml"},
                {"name": "柠檬角", "amount": 1, "unit": "个"}
            ],
            "instructions": "1. 在杯中加满冰块。\n2. 倒入金酒。\n3. 缓缓倒入通宁水。\n4. 搅拌并挤入柠檬汁。",
            "comment": "模拟模式：未配置 API Key。"
        }

    inventory_str = ", ".join(inventory_list)

    prompt = f"""
    我是一个家庭调酒师。我有以下酒水库存：{inventory_str}。
    用户的具体要求是：{user_request}。
    
    请根据我的库存推荐一款鸡尾酒。
    
    【重要】请务必返回标准的 JSON 格式，不要包含任何其他文字。
    JSON 结构如下：
    {{
        "name": "鸡尾酒名称 (中英文)",
        "ingredients": [
            {{"name": "配料名", "amount": 数字(ml或g), "unit": "单位(ml/g/part/dash)"}}
        ],
        "instructions": "制作步骤 (清晰明了)",
        "comment": "简短的推荐理由或口感描述"
    }}
    注意：amount 必须是数字，如果是适量请估算或写0，unit 必须统一。
    """

    payload = {
        "model": "qwen3-max",
        "messages": [
            {"role": "system", "content": "你是一位专业的调酒师助手。请只返回 JSON 格式的数据。"},
            {"role": "user", "content": prompt}
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
        content = data["choices"][0]["message"]["content"]
        
        # Parse JSON
        try:
            cleaned_content = _clean_json_string(content)
            return json.loads(cleaned_content)
        except json.JSONDecodeError:
            # Fallback for parsing error
            return {
                "name": "解析失败",
                "ingredients": "见描述",
                "instructions": content,
                "comment": "AI 返回格式有误"
            }

    except Exception as e:
        return {"error": str(e)}

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
        "model": "qwen3-max",
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
        return {
            "name": "热托迪 (Hot Toddy) [模拟]",
            "ingredients": [
                {"name": "威士忌", "amount": 45, "unit": "ml"},
                {"name": "热水", "amount": 100, "unit": "ml"},
                {"name": "蜂蜜", "amount": 10, "unit": "ml"},
                {"name": "柠檬", "amount": 1, "unit": "片"}
            ],
            "instructions": "1. 混合所有材料。\n2. 搅拌均匀。\n3. 趁热饮用。",
            "comment": "Kenji (模拟): 今天的风有点喧嚣呢... 喝杯热酒暖暖身子吧。"
        }

    inventory_str = ", ".join(inventory_list)
    prompt = f"""
    我是一个家庭调酒师，我有这些库存：{inventory_str}。
    现在客人的心情是：{mood}。
    现在的天气是：{weather}。

    请你扮演一位名叫 Kenji 的日式酒吧老板（类似于《深夜食堂》的老板）。
    请根据客人的心情和天气，以及我的库存，为他特调一杯酒。

    【重要】请务必返回标准的 JSON 格式，不要包含任何其他文字。
    JSON 结构如下：
    {{
        "comment": "Kenji 的开场白：一句富有哲理或温暖的话，与心情/天气有关（50字以内）",
        "name": "推荐酒名 (中英文)",
        "ingredients": [
            {{"name": "配料名", "amount": 数字(ml或g), "unit": "单位"}}
        ],
        "instructions": "制作步骤",
        "ending": "一句简单的祝福"
    }}
    
    请用温暖、治愈的语气撰写 comment 和 ending。
    """

    payload = {
        "model": "qwen3-max",
        "messages": [
            {"role": "system", "content": "你是一位拥有20年经验的日式酒吧老板 Kenji。请只返回 JSON 格式的数据。"},
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
        content = data["choices"][0]["message"]["content"]
        
        # Parse JSON
        try:
            cleaned_content = _clean_json_string(content)
            res_json = json.loads(cleaned_content)
            # Combine ending into comment or separate? Let's keep them structured but maybe combine for display
            # But the user wants structured fields for saving.
            # We can put 'ending' into instructions or just keep it in JSON.
            return res_json
        except json.JSONDecodeError:
            return {
                "name": "解析失败",
                "ingredients": "见描述",
                "instructions": content,
                "comment": "Kenji 似乎喝醉了..."
            }
            
    except Exception as e:
        return {"error": str(e)}


def get_sommelier_recommendation(recipes_data, user_request):
    """专业侍酒师风格的单一推荐"""
    api_key = os.environ.get("DASHSCOPE_API_KEY")
    
    if not api_key:
        return {
            "recommendation": {
                "name": "经典马天尼 (Classic Martini)",
                "presentation": "今晚，我想为您推荐一款经典马天尼...",
                "tasting_notes": "入口冰冷纯净，中段金酒的植物香气缓缓释放...",
                "pairing_reason": "它的简约与优雅，正如您所追求的品质。",
                "service_tip": "建议冰镇至-5°C，使用马天尼杯，一饮而尽。"
            }
        }
    
    # 构造配方列表文本
    recipes_text = "\n".join([
        f"- {r['name']}：{r['ingredients']}" 
        for r in recipes_data
    ])
    
    prompt = f"""
你是一位在米其林三星餐厅工作了15年的首席侍酒师 Alexandre。你深谙品鉴之道，擅长通过倾听客人的细微需求，为他们推荐最完美的一款酒。

【当前酒单】
{recipes_text}

【客人需求】
{user_request}

【你的任务】
请运用专业的侍酒师推销技巧，从酒单中选择**唯一一款**最适合客人的鸡尾酒。

【推销技巧要求】
1. 倾听理解：深入解读客人的真实需求（不仅是字面意思）
2. 建立信任：展现你的专业知识，但语气温和而非炫耀
3. 感官描述：用视觉、嗅觉、味觉的语言描绘这款酒
4. 情感连接：将酒与客人的情绪、场景关联
5. 明确推荐：自信地给出唯一推荐，避免"您也可以试试..."的犹豫
6. 适度留白：给客人想象空间，不要说太满

【输出格式（JSON）】
{{
    "name": "推荐的配方名称",
    "presentation": "开场白（40-80字）：以'今晚，我想为您...'或'如果您允许，让我为您...'开始，用故事化的方式引出推荐，融入客人需求的关键词",
    "tasting_notes": "品鉴描述（60-100字）：描述入口、中段、尾韵的味觉层次，使用专业术语但保持易懂",
    "pairing_reason": "推荐理由（50-80字）：解释为什么这款酒与客人的需求完美契合，体现你对客人的理解",
    "service_tip": "侍酒建议（30-50字）：给出专业的饮用建议（温度、杯具、饮用时机等），提升仪式感"
}}

【语气风格】
- 优雅而不矫情
- 专业而不生硬  
- 热情而不夸张
- 自信而不傲慢

请只返回JSON，不要有其他内容。
"""
    
    payload = {
        "model": "qwen3-max",
        "messages": [
            {"role": "system", "content": "你是米其林三星餐厅的首席侍酒师 Alexandre，拥有15年侍酒经验。你的推荐总是精准且令人信服。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.85
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
        content = data["choices"][0]["message"]["content"]
        
        # Parse JSON
        try:
            cleaned_content = _clean_json_string(content)
            result = json.loads(cleaned_content)
            return {"recommendation": result}
        except json.JSONDecodeError:
            return {
                "recommendation": {
                    "name": "解析失败",
                    "presentation": content[:200],
                    "tasting_notes": "抱歉，侍酒师的笔记有些潦草...",
                    "pairing_reason": "但我相信这会是个不错的选择。",
                    "service_tip": ""
                }
            }
    except Exception as e:
        return {"error": str(e)}

