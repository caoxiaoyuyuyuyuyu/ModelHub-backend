import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
from transformers import BitsAndBytesConfig


print(torch.cuda.is_available())  # 应该返回True
print(torch.version.cuda)  # 显示CUDA版本
print(torch.__version__)  # 显示PyTorch版本
device = "cuda" if torch.cuda.is_available() else "cpu"
def chat_with_finetuned(model_path, peft_model_path, load_in_4bit, history):
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"

    bnb_config = BitsAndBytesConfig(
        load_in_4bit=load_in_4bit,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16
    )
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        quantization_config=bnb_config,
        device_map="auto"
    )

    # 然后加载LoRA
    model = PeftModel.from_pretrained(model, peft_model_path)

    # 使用组合模型进行推理
    inputs = tokenizer(history, return_tensors="pt").to("cuda")
    outputs = model.generate(**inputs, max_new_tokens=1024)
    print(tokenizer.decode(outputs[0], skip_special_tokens=True))
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

if __name__ == "__main__":
    model_path = r"D:\Projects\PEFT\Qwen\Qwen1.5-1.8B-Chat"
    peft_model_path = r"D:\Projects\PEFT\qwen_finetuned_lora"
    load_in_4bit = True
    print(chat_with_finetuned(model_path, peft_model_path, load_in_4bit, "若是能重来，你想改变什么？"))

