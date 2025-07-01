

# 通过model_config_id获取聊天模型
def get_chatllm(model_config_id: int):
    model_config = ModelConfig.query.get(model_config_id)
    if not model_config:
        raise Exception("模型配置不存在")

    base_model_id = model_config.base_model_id
    temperature = model_config.temperature
    top_p = model_config.top_p
    prompt = model_config.prompt

    base_model_info = ModelInfo.query.get(base_model_id)
    if not base_model_info:
        raise Exception("基础模型信息不存在")

    model_name = base_model_info.model_name
    base_url = base_model_info.base_url
    api_key = base_model_info.api_key

    try:
        ChatModel = ChatGLM(
            model=model_name,
            api_key=api_key,
            base_url=base_url,
            system_prompt=prompt,
            temperature=temperature,
            top_p=top_p
        )
        return ChatModel
    except Exception as e:
        raise Exception("聊天模型创建失败："+str(e))