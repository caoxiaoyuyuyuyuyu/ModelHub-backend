import json
from datasets import Dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    DataCollatorForLanguageModeling, BitsAndBytesConfig, Trainer, TrainerCallback
)
from peft import LoraConfig, prepare_model_for_kbit_training, get_peft_model
import torch

from app.utils.PEFT.DataLoader import DataLoader


class ModelTrainer:
    @staticmethod
    def load_model(model_path, bnb_config, peft_config):
        # 加载模型
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            quantization_config=bnb_config,
            device_map="auto",
            torch_dtype=torch.bfloat16
        )
        model = prepare_model_for_kbit_training(model)
        if peft_config:
            model = get_peft_model(model, peft_config)
        return model
    @staticmethod
    def load_tokenizer(model_path):
        tokenizer = AutoTokenizer.from_pretrained(model_path, use_fast=True)
        tokenizer.pad_token = tokenizer.eos_token
        # tokenizer.padding_side = "right"
        return tokenizer
    # 数据预处理函数（将文本tokenize）
    @staticmethod
    def preprocess(tokenizer, dataset, type):
        if type == "dialogue":
            def preprocess_dialog_function(examples):
                return tokenizer(
                    examples["text"],
                    padding="max_length",
                    truncation=True,
                    max_length=1024,
                    return_tensors="pt"
                )

            return dataset.map(preprocess_dialog_function, batched=True, remove_columns=["text"])
        elif type == "instruction":
            def preprocess_instruction_function(examples):
                # 构建文本
                texts = [
                    f"### Instruction:\n{inst}\n\n### Input:\n{inp}\n\n### Response:\n{out}"
                    for inst, inp, out in zip(examples["instruction"], examples["input"], examples["output"])
                ]

                # Tokenize并处理padding
                tokenized = tokenizer(
                    texts,
                    padding="max_length",  # 显式启用padding
                    truncation=True,  # 显式启用truncation
                    max_length=1024,  # 设置最大长度
                    return_tensors="pt"
                )

                # 添加labels字段
                tokenized["labels"] = tokenized["input_ids"].clone()
                return tokenized

            # 应用预处理
            return dataset.map(
                preprocess_instruction_function,
                batched=True,
                remove_columns=["instruction", "input", "output"]  # 移除原始列
            )

        def tokenize_function(examples):
            # 确保返回PyTorch张量并统一长度
            output = tokenizer(
                examples["text"],
                truncation=True,
                max_length=128,
                padding="max_length",
                return_tensors="pt"
            )
            return {k: v.squeeze(0) for k, v in output.items()}  # 移除batch维度

        return dataset.map(
            tokenize_function,
            batched=False,  # 改为逐样本处理
            remove_columns=["text"]
        )
    @staticmethod
    def train(model_path, dataset, type, bnb_config, peft_config, training_args, output_dir, log_path):
        tokenizer = ModelTrainer.load_tokenizer(model_path)
        model = ModelTrainer.load_model(model_path, bnb_config, peft_config)
        tokenizer_dataset = ModelTrainer.preprocess(tokenizer, dataset, type)

        # 开始训练
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=tokenizer_dataset,
            data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False),
        )

        trainer.train()
        trainer.save_model(output_dir)

        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(trainer.state.log_history, f, indent=2)  # 格式化保存

def finetune(base_model_path, file_path, data_type, output_dir, log_path, **kwargs):
    dataset = DataLoader.load_data(file_path, data_type)
    # 配置4-bit量化和LoRA
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=kwargs.get("load_in_4bit", True),
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        # bnb_4bit_use_double_quant=True,
    )
    if kwargs.get("use_lora", True):
        peft_config = LoraConfig(
            r=kwargs.get("lora_r", 8),
            lora_alpha=kwargs.get("lora_alpha", 32),
            target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
            lora_dropout=kwargs.get("lora_dropout", 0.05),
            bias="none",
            task_type="CAUSAL_LM"
        )
    else:
        peft_config = None
    training_args = TrainingArguments(
        output_dir=output_dir,
        per_device_train_batch_size=2,
        gradient_accumulation_steps=kwargs.get("gradient_accumulation_steps", 4),
        learning_rate=2e-5,
        num_train_epochs=kwargs.get("num_train_epochs", 3),
        logging_steps=kwargs.get("logging_steps", 10),
        save_strategy=kwargs.get("save_strategy", "epoch"),
        fp16=kwargs.get("fp16", True),
        optim=kwargs.get("optim", "paged_adamw_8bit")
    )
    ModelTrainer.train(base_model_path, dataset, data_type, bnb_config, peft_config, training_args, output_dir, log_path)


if __name__ == "__main__":
    # # 加载数据
    # dataset = DataLoader.load_data(r"D:\Projects\PEFT\dialogue_data.json", "dialogue")
    # # 训练
    # # 配置4-bit量化和LoRA
    # bnb_config = BitsAndBytesConfig(
    #     load_in_4bit=True,
    #     bnb_4bit_quant_type="nf4",
    #     bnb_4bit_compute_dtype=torch.bfloat16,
    #     # bnb_4bit_use_double_quant=True,
    # )
    #
    # peft_config = LoraConfig(
    #     r=8,
    #     lora_alpha=32,
    #     target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    #     lora_dropout=0.05,
    #     bias="none",
    #     task_type="CAUSAL_LM"
    # )
    # # 训练参数配置
    # training_args = TrainingArguments(
    #     output_dir="./dialogue_finetuned",
    #     per_device_train_batch_size=2,
    #     gradient_accumulation_steps=4,
    #     learning_rate=2e-5,
    #     num_train_epochs=3,
    #     logging_steps=10,
    #     save_strategy="epoch",
    #     fp16=True,
    #     optim="paged_adamw_8bit"
    # )
    # output_dir = "./dialogue_finetuned_lora"
    # log_path = "./training_logs.json"
    # ModelTrainer.train(r"D:\Projects\PEFT\Qwen\Qwen1.5-1.8B-Chat", dataset, "dialogue", bnb_config,  peft_config, training_args, output_dir, log_path)
    finetune(r"D:\Projects\PEFT\Qwen\Qwen1.5-1.8B-Chat", r"D:\Projects\PEFT\dialogue_data.json", "dialogue", "./dialogue_finetuned_lora", "./training_logs.json", load_in_4bit=True, use_lora=True)