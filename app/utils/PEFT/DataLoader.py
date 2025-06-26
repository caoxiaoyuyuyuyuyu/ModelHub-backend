import json
from datasets import Dataset

class DataLoader:
    @staticmethod
    def load_dialog_data(path, encoding="utf-8"):
        with open(path, "r", encoding=encoding) as f:
            raw_data = json.load(f)
        # 将多轮对话拼接为训练文本（格式：`[角色]: 内容\n`）
        formatted_data = []
        for item in raw_data:
            dialogue_text = ""
            for turn in item["dialogue"]:
                dialogue_text += f"[{turn['role']}]: {turn['content']}\n"
            formatted_data.append({"text": dialogue_text.strip()})

        return Dataset.from_list(formatted_data)
    @staticmethod
    def load_instruction_data(path, encoding="utf-8"):
        with open(path, "r", encoding=encoding) as f:
            raw_data = json.load(f)
        # 数据清洗：确保所有字段为字符串，无嵌套结构
        formatted_data = []
        for item in raw_data:
            formatted_data.append({
                "instruction": str(item["instruction"]).strip(),
                "input": str(item.get("input", "")).strip(),  # 处理可能缺失的input
                "output": str(item["output"]).strip()
            })

        return Dataset.from_list(formatted_data)
    @staticmethod
    def load_plain_data(path, encoding="utf-8"):
        from datasets import load_dataset
        return load_dataset("text", data_files=path, split="train")

    @staticmethod
    def load_data(path, type,  encoding="utf-8"):
        try :
            if type == "dialogue":
                return DataLoader.load_dialog_data(path, encoding)
            elif type == "instruction":
                return DataLoader.load_instruction_data(path, encoding)
            elif type == "plain":
                return DataLoader.load_plain_data(path, encoding)
            else:
                return DataLoader.load_plain_data(path, encoding)
        except Exception as e:
            print(f"Error loading data: {e}")