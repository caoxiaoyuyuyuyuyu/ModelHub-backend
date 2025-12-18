from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from pathlib import Path

def chat_with_base(model_path, history):
    # Normalize path to handle mixed path separators
    model_path = str(Path(model_path).resolve())
    
    tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        device_map="auto",  # 自动选择 GPU 或 CPU
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        local_files_only=True,
    )
    if isinstance(history, str):
        history = [
            {"role": "user", "content": history}
        ]

    # 生成回复
    inputs = tokenizer.apply_chat_template(
        history,
        return_tensors="pt",
        add_generation_prompt=True
    ).to(model.device)


    outputs = model.generate(
        inputs,
        max_new_tokens=512,
        do_sample=True,
        temperature=0.7,
        top_p=0.9,
    )
    # 解码AI 回复
    response = tokenizer.decode(outputs[0][len(inputs[0]):], skip_special_tokens=True)

    return response
if __name__ == '__main__':
    history = [
        {"role": "user", "content": "你好"},
        {"role": "assistant", "content": "你好，有什么我可以帮助你的吗？"},
        {"role": "user", "content": "我叫张三"},
        {"role": "assistant", "content": "我叫ChatGPT，一个基于OpenAI GPT-3的聊天机器人，有什么我可以帮助你的吗？"},
        {"role": "user", "content": "你喜欢什么？"},
        {"role": "assistant", "content": "我喜欢聊天，帮助人们解决问题。"},
        {"role": "user", "content": "我叫什么名字？"},
    ]
    print(chat_with_base(r"D:\Projects\PEFT\Qwen\Qwen1.5-1.8B-Chat", history))
