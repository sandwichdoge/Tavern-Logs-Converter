#!/usr/bin/env python3
"""
SillyTavern Log Preprocessor

This script processes SillyTavern logs by:
1. Cleaning metadata to keep only relevant fields
2. Optionally obfuscating usernames in the logs
3. Adding system instructions for roleplay

Usage as a library:
    from stage1_preprocessor import LogPreprocessor
    
    # Initialize preprocessor
    processor = LogPreprocessor("path/to/sillytavern", "./cleaned_logs", obfuscate=True)
    
    # Process all logs
    logs_processed = processor.process_all_files()
"""

import json
import os
import random
from typing import Dict, List, Optional, Any
import v2_card 


class LogPreprocessor:
    """Handles the preprocessing of SillyTavern log files."""
    
    # Fields to keep in the processed output
    FIELDS_TO_KEEP = ["name", "mes", "is_user", "extra"]
    
    # Collection of system prompts to randomly choose from
    SYSTEM_PROMPTS = [
        "You are '{0}' in this roleplay chat with '{1}'. Respond to '{1}', be creative.",
        "In this roleplay chat, you are '{0}', interacting with '{1}'. Ensure your responses are imaginative and engaging.",
        "Assume the role of '{0}' in a roleplay scenario with '{1}'. Make your responses captivating and character-appropriate.",
        "You have taken on the persona of '{0}' in this roleplay conversation with '{1}'. Respond to '{1}' with creativity and depth.",
        "As '{0}', engage in this roleplay chat with '{1}'. Your responses should be inventive and true to the character.",
        "In this roleplay scenario, you are '{0}' interacting with '{1}'. Make your responses engaging and authentic."
    ]
    
    # Simple fixed system prompt for when obfuscation is disabled
    FIXED_SYSTEM_PROMPT = "Assume the role of '{0}' in a roleplay conversation with '{1}'. Respond as your character would."
    
    # List of unisex names for obfuscation
    UNISEX_NAMES = [
        "Avery", "Blake", "Cameron", "Dakota", "Elliott", "Finley", "Hayden", "Kennedy",
        "Logan", "Morgan", "Peyton", "Quinn", "Noel", "Wyatt", "Alex", "Ash", "Bailey",
        "Milan", "Drew", "Kris", "Frankie", "Gabriel", "Jamie", "Carey", "Lee", "Max",
        "Parker", "Quinn", "Riley", "Skyler", "Taylor", "River", "Rene", "Blair", "Drew",
        "Jordan", "Parker", "Angel", "Garrett", "Nova", "Jesse", "Kendall", "Landon",
        "Charlie", "Nolan", "Oliver", "Robin", "Ellis", "Sam", "Noah", "Wesley", "Shiki",
        "Sora", "Akira", "Maki", "Adrian", "Ariel", "Ashton", "Aubrey", "Briar", "Casey",
        "Dakota", "Dallas", "Devon", "Eden", "Emerson", "Harper", "Jaden", "Jayden",
        "Jessie", "Jodie", "Jules", "Kai", "Kelly", "Kim", "Lennon", "Lexi", "London",
        "Mackenzie", "Maddison", "Marley", "Merritt", "Micah", "Nico", "Pat", "Phoenix",
        "Ray", "Reese", "Rory", "Rowan", "Sage", "Santiago", "Shawn", "Sidney", "Spencer",
        "Stevie", "Tatum", "Toni", "Tracy", "Valentino", "Valerie", "Wren", "Yael", "Zion",
        "Amari", "Amina", "Chi", "Fatima", "Guadalupe", "Isla", "Ji-hu", "Kiran", "Lior",
        "Ming", "Nia", "Omari", "Priya", "Qadir", "Ravi", "Siobhan", "Tariq", "Uma", "Van",
        "Xiu", "Yara", "Zahra"
    ]
    
    def __init__(self, st_folder: str, output_folder: str, obfuscate: bool = True):
        """
        Initialize the LogPreprocessor with the required parameters.
        
        Args:
            st_folder: Path to the SillyTavern folder
            output_folder: Path where processed logs will be saved
            obfuscate: Whether to obfuscate usernames in the logs
        """
        self.st_folder = st_folder
        self.input_folder = os.path.join(st_folder, "data", "default-user", "chats")
        self.output_folder = output_folder
        self.obfuscate = obfuscate
        
        # Validate input folder existence
        if not os.path.exists(self.input_folder):
            raise FileNotFoundError(
                "No data/default-user/chats folder detected in Tavern folder."
            )
        
        # Create output folder if it doesn't exist
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)
    
    def get_random_unisex_name(self, blacklisted: str) -> str:
        """
        Get a random unisex name that isn't the blacklisted name.
        
        Args:
            blacklisted: Name to avoid selecting
            
        Returns:
            A randomly selected unisex name
        """
        name = random.choice(self.UNISEX_NAMES)
        while name == blacklisted:
            name = random.choice(self.UNISEX_NAMES)
        return name
    
    def should_process_file(self, log_path: str) -> bool:
        return os.path.getsize(log_path) >= 4 * 1024  # 4KB minimum
    
    def search_metadata(self, lines: List[str], field: str) -> Optional[str]:
        """
        Search for a specific metadata field in the log lines.
        
        Args:
            lines: List of log lines (JSON strings)
            field: Field name to search for
            
        Returns:
            Value of the field if found, None otherwise
        """
        for line in lines:
            try:
                jobj = json.loads(line)
                if field in jobj:
                    return jobj[field]
            except json.JSONDecodeError:
                continue
        return None
    
    def replace_name(self, message: str, original_name: str, new_name: str) -> str:
        # Handle full names (first and last name)
        if " " in original_name:
            firstname = original_name.split(" ")[0]
            lastname = original_name.split(" ")[-1]
            message = self._fuzzy_replace_name(message, firstname, new_name)
            message = self._fuzzy_replace_name(message, lastname, new_name)
        
        # Handle the whole name
        return self._fuzzy_replace_name(message, original_name, new_name)
    
    def _fuzzy_replace_name(self, message: str, original_name: str, new_name: str) -> str:
        """
        Replace names with surrounding context to avoid partial word replacements.
        Handles regular case, uppercase, and lowercase versions of the name.
        """
        # Define surrounding context patterns
        prefixes = ["", f"{original_name[0]}-", " ", "\"", "—", "-", "'", "*"]
        suffixes = ["", " ", ",", "*", "'", ".", "-", "?"]
        
        # Process regular case, uppercase, and lowercase versions
        case_variants = [
            (original_name, new_name),            # Original case
            (original_name.upper(), new_name.upper()),  # ALL CAPS
            (original_name.lower(), new_name.lower())   # all lowercase
        ]
        
        for orig, replacement in case_variants:
            for prefix in prefixes:
                for suffix in suffixes:
                    old = f"{prefix}{orig}{suffix}"
                    new = f"{prefix}{replacement}{suffix}"
                    message = message.replace(old, new)
                    
        return message
    
    def obfuscate_user_name(self, entry: Dict[str, Any], original_name: str, new_name: str) -> Dict[str, Any]:
        """
        Obfuscate the username in a log entry.
        
        Args:
            entry: Log entry as dictionary
            original_name: Original username
            new_name: New username for obfuscation
            
        Returns:
            Processed log entry with obfuscated names
        """
        if not entry or not original_name or not new_name:
            return entry
        
        new_data = {}
        
        for key, value in entry.items():
            if key == "name" and entry.get("is_user"):
                new_data[key] = new_name
            elif key == "mes":
                new_data[key] = self.replace_name(value, original_name, new_name)
            elif key == "extra":
                if isinstance(value, dict):
                    new_extra = value.copy()
                    if "reasoning" in new_extra and isinstance(new_extra["reasoning"], str):
                        new_extra["reasoning"] = self.replace_name(new_extra["reasoning"], original_name, new_name)
                    new_data[key] = new_extra
                else:
                    # Fallback for non-dict extra value
                    new_data[key] = value
            else:
                new_data[key] = value

        return new_data
    
    def keep_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Filter out unwanted fields, keeping only those specified in FIELDS_TO_KEEP.
        
        Args:
            data: Original log entry
            
        Returns:
            Filtered log entry
        """
        return {k: v for k, v in data.items() if k in self.FIELDS_TO_KEEP}
    
    def get_char_description(self, log_path: str) -> Optional[str]:
        """
        Extract character description from character card.
        """
        try:
            # Convert chat path to character card path
            card_path_parts = log_path.replace("/chats/", "/characters/", 1).split("/")[:-1]
            card_path = "/".join(card_path_parts) + ".png"
            
            if not os.path.exists(card_path):
                return None
                
            card = v2_card.parse(card_path)
            return card.data.description
        except Exception:
            return None
    
    def fix_char_description(self, char_desc: Optional[str], user_name: str, char_name: str) -> Optional[str]:
        """
        Replace placeholders in character description with actual names.
        
        Args:
            char_desc: Character description
            user_name: Username to substitute
            char_name: Character name to substitute
            
        Returns:
            Processed character description
        """
        if not char_desc:
            return None
            
        return char_desc.replace("{{char}}", char_name).replace("{{user}}", user_name)
    
    def prepend_instructions(self, conversation: List[Dict[str, Any]], 
                           user_name: str, char_name: str, 
                           char_desc: Optional[str]) -> List[Dict[str, Any]]:
        """
        Add system instructions to the beginning of the conversation.
        
        Args:
            conversation: Original conversation entries
            user_name: Username for the conversation
            char_name: Character name for the conversation
            char_desc: Character description
            
        Returns:
            Conversation with prepended system instructions
        """
        # Choose system prompt based on obfuscation setting
        if self.obfuscate:
            # Select a random system prompt template when obfuscating
            sysprompt_template = random.choice(self.SYSTEM_PROMPTS)
        else:
            # Use fixed system prompt when not obfuscating
            sysprompt_template = self.FIXED_SYSTEM_PROMPT
        
        # Format the selected system prompt
        sysprompt = sysprompt_template.format(char_name, user_name)
        
        # Add character description if provided
        if char_desc:
            sysprompt += f" {char_name}'s description: {char_desc}"
        
        # Create the system message and starter message
        system = {"name": "system", "mes": sysprompt, "is_user": False}
        starter = {"name": user_name, "mes": "The roleplay begins.", "is_user": True}
        
        # Return the new conversation with the prepended instructions
        return [system, starter] + conversation
    
    def process_file(self, log_path: str) -> bool:
        if not self.should_process_file(log_path):
            return False
        
        try:
            with open(log_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            conversation = []
            original_user_name = self.search_metadata(lines, "user_name")
            original_char_name = self.search_metadata(lines, "character_name")
            
            if not original_user_name or not original_char_name:
                return False
                
            char_name = original_char_name
            user_name = original_user_name
            
            if self.obfuscate:
                user_name = self.get_random_unisex_name(char_name)
            else:
                user_name = "User"
            
            print(f"Processing {log_path} with user name {original_user_name} and char name {char_name}")
            for line in lines:
                try:
                    entry = json.loads(line)
                    
                    entry = self.keep_fields(entry)

                    entry = self.obfuscate_user_name(entry, original_user_name, user_name)
                    
                    if entry:  # Only add valid entries
                        conversation.append(entry)
                except json.JSONDecodeError:
                    continue
            
            char_desc = self.get_char_description(log_path)
            char_desc = self.fix_char_description(char_desc, user_name, char_name)
            conversation = self.prepend_instructions(conversation, user_name, char_name, char_desc)
            
            # Write processed output to new file
            output_path = os.path.join(self.output_folder, os.path.basename(log_path))
            with open(output_path, "w", encoding="utf-8") as f:
                for entry in conversation:
                    f.write(json.dumps(entry) + "\n")
            
            return True
            
        except Exception as e:
            print(f"Error processing {log_path}: {e}")
            return False
    
    def process_all_files(self) -> int:
        logs_processed = 0
        
        for root, _, files in os.walk(self.input_folder):
            for file in files:
                if file.endswith(".jsonl"):
                    log_path = os.path.join(root, file)
                    if self.process_file(log_path):
                        logs_processed += 1
        
        return logs_processed
