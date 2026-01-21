import os
import openai

def get_cocktail_suggestion(inventory_list, user_request):
    # 优先检查 DASHSCOPE_API_KEY
    api_key = os.environ.get("DASHSCOPE_API_KEY")
    if not api_key:
        # 兼容旧配置或 mock 模式
        api_key = os.environ.get("OPENAI_API_KEY")
    
    if not api_key:
        # Mock response for testing without API key
        return "提示：未检测到 DASHSCOPE_API_KEY，正在使用模拟模式。\n\n推荐：**经典金汤力 (Gin & Tonic)**\n\n配方：\n- 45ml 金酒 (Gin)\n- 适量 通宁水 (Tonic Water)\n- 柠檬角装饰\n\n步骤：\n1. 在杯中加满冰块。\n2. 倒入金酒。\n3. 缓缓倒入通宁水。\n4. 轻轻搅拌，挤入柠檬汁并放入杯中。"

    # 配置 Aliyun Bailian (DashScope) 兼容 OpenAI 的客户端
    # 如果是 OpenAI Key 则不使用自定义 base_url (这里假设用户想切换到阿里云，但也保留一点兼容性)
    base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1" if "sk-" not in api_key or len(api_key) > 30 else None 
    # 注意：阿里云的 key 通常也可能以 sk- 开头或者不一定，这里主要依据用户需求强制切换
    # 根据用户明确要求 "api供应商变成阿里云百炼"，我们直接使用阿里云配置
    
    client = openai.OpenAI(
        api_key=api_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )
    
    inventory_str = ", ".join(inventory_list)
    prompt = f"""
    我是一个家庭调酒师。我有以下酒水库存：{inventory_str}。
    用户的具体要求是：{user_request}。
    请根据我的库存推荐一款鸡尾酒，并提供配方和制作步骤。
    如果库存不足以制作经典款，请提供创意搭配建议。
    请用中文回答，仅提供推荐的鸡尾酒名称、配方和制作步骤。
    """

    try:
        response = client.chat.completions.create(
            model="qwen-plus", # 使用通义千问模型
            messages=[
                {"role": "system", "content": "你是一位专业的调酒师助手。"},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"获取建议时出错: {str(e)}"
