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
    def generate_dialogue(self, jobj: dict, include_reasoning: bool = False) -> dict:
        if jobj["name"] == "system":
            return {"from": "system", "value": jobj["mes"]}
        elif jobj["is_user"] == True:
            return {"from": "human", "value": jobj["mes"]}
        elif jobj["is_user"] == False:
            # Handle assistant messages with reasoning
            value = jobj["mes"]
            
            # Check if extra field exists and contains reasoning
            if include_reasoning:
                if "extra" in jobj and isinstance(jobj["extra"], dict) and "reasoning" in jobj["extra"]:
                    reasoning = jobj["extra"]["reasoning"]
                    value = f"<think>{reasoning}</think>\n{value}"
                
            return {"from": "gpt", "value": value}
        else:
            print("Not supported", jobj)

    def generate_conversation(self, cleaned_log_file: str, include_reasoning: bool = False) -> list[dict]:
        with open(cleaned_log_file, "r") as f:
            lines = f.readlines()

        conversations = []
        for line in lines:
            jobj = json.loads(line)
            dialogue = self.generate_dialogue(jobj, include_reasoning)
            conversations.append(dialogue)

        return conversations


class AxolotlConverter:
    def __init__(self, format_name: str, input_dir: str, output_file: str):
        """
        Initialize the converter with format type, input directory, and output file.
        
        Args:
            format_name: The format to convert to ('sharegpt' or 'alpaca')
            input_dir: Directory containing cleaned log files
            output_file: Path to the output file
        """
        self.input_dir = input_dir
        self.output_file = output_file
        
        # Initialize the appropriate format handler
        if format_name == "sharegpt":
            self.dialogue_format = ShareGPTFormat()
        else:
            raise ValueError(f"Unsupported format: {format_name}")
        
        # Remove output file if it already exists
        if os.path.isfile(output_file):
            os.remove(output_file)
    
    def process_file(self, file_path: str, include_reasoning: bool) -> int:
        """
        Process a single file and append the result to the output file.
        
        Args:
            file_path: Path to the input file
            
        Returns:
            Number of conversations processed
        """
        conversations = self.dialogue_format.generate_conversation(file_path, include_reasoning)
        
        with open(self.output_file, "a") as fout:
            data = json.dumps({"conversations": conversations}) + "\n"
            fout.write(data)
        
        return len(conversations)
    
    def process_all_files(self, include_reasoning: bool = False) -> int:
        """
        Process all JSONL files in the input directory and write to the output file.
        
        Returns:
            Total number of conversations processed
        """
        total_conversations = 0
        
        for root, _, files in os.walk(self.input_dir):
            for file in files:
                if file.endswith(".jsonl"):
                    file_path = os.path.join(root, file)
                    conversations_count = self.process_file(file_path, include_reasoning)
                    total_conversations += conversations_count
        
        return total_conversations