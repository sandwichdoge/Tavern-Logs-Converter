import json
import os
from abc import ABC, abstractmethod


class DialogueFormat(ABC):
    @abstractmethod
    def generate_dialogue(self, jobj: dict) -> dict:
        pass

    @abstractmethod
    def generate_conversation(self, cleaned_log_file: str) -> list[dict]:
        pass


class ShareGPTFormat(DialogueFormat):
    def generate_dialogue(self, jobj: dict) -> dict:
        if jobj["name"] == "system":
            return {"from": "system", "value": jobj["mes"]}
        elif jobj["is_user"] == True:
            return {"from": "human", "value": jobj["mes"]}
        elif jobj["is_user"] == False:
            return {"from": "gpt", "value": jobj["mes"]}
        else:
            print("Not supported", jobj)

    def generate_conversation(self, cleaned_log_file: str) -> list[dict]:
        with open(cleaned_log_file, "r") as f:
            lines = f.readlines()

        conversations = []
        for line in lines:
            jobj = json.loads(line)
            dialogue = self.generate_dialogue(jobj)
            conversations.append(dialogue)

        return conversations


class AlpacaFormat(DialogueFormat):
    # Implement Alpaca-specific methods here
    pass


def to_format(format_name: str, cleaned_log_dir: str, output_file: str):
    if format_name == "sharegpt":
        dialogue_format = ShareGPTFormat()
    elif format_name == "alpaca":
        dialogue_format = AlpacaFormat()
    else:
        raise ValueError("Unsupported format")

    if os.path.isfile(output_file):
        os.remove(output_file)

    fout = open(output_file, "a")

    for root, _, files in os.walk(cleaned_log_dir):
        for file in files:
            if file.endswith(".jsonl"):
                conversations = dialogue_format.generate_conversation(os.path.join(root, file))
                data = json.dumps({"conversations": conversations}) + "\n"
                fout.write(data)

    fout.close()
