import torch
import os
from pathlib import Path
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

# Check if bitsandbytes is available
try:
    import bitsandbytes as bnb
    from transformers import BitsAndBytesConfig
    BITSANDBYTES_AVAILABLE = True
except (ImportError, ModuleNotFoundError, Exception) as e:
    BITSANDBYTES_AVAILABLE = False
    BitsAndBytesConfig = None
    error_msg = str(e)
    if "metadata" in error_msg.lower() or "package" in error_msg.lower():
        print(f"Warning: bitsandbytes package metadata is missing or corrupted: {e}")
        print("To fix this, try reinstalling bitsandbytes: pip uninstall bitsandbytes && pip install bitsandbytes")
    else:
        print(f"Warning: bitsandbytes is not available: {e}")

print(torch.cuda.is_available())  # 应该返回True
print(torch.version.cuda)  # 显示CUDA版本
print(torch.__version__)  # 显示PyTorch版本
device = "cuda" if torch.cuda.is_available() else "cpu"

def chat_with_finetuned(model_path, peft_model_path, load_in_4bit, history):
    # Normalize paths to handle mixed path separators
    model_path = str(Path(model_path).resolve())
    peft_model_path = str(Path(peft_model_path).resolve())
    
    tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"

    # Check if bitsandbytes is available when load_in_4bit is requested
    if load_in_4bit and not BITSANDBYTES_AVAILABLE:
        raise ImportError(
            "bitsandbytes is required for 4-bit quantization but is not available. "
            "This may be due to missing package metadata. "
            "To fix: pip uninstall bitsandbytes && pip install bitsandbytes "
            "Alternatively, set load_in_4bit=False to disable quantization."
        )
    
    model_kwargs = {
        "device_map": "auto",
        "local_files_only": True
    }
    
    if load_in_4bit and BITSANDBYTES_AVAILABLE:
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16
        )
        model_kwargs["quantization_config"] = bnb_config
    
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        **model_kwargs
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

