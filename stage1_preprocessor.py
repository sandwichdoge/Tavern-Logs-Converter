# This script goes through your SillyTavern logs folder, cleans all metadata, only keeping relevant fields, and obfuscates the username in the logs.
# How to use:
# Put this script in your SillyTavern folder
# Run `python3 stage1_preprocessor.py`
# Cleaned output are saved to cleaned_logs folder, in SillyTavern folder (same place where you put it)

import json
import os
import random
import v2_card


def random_unisex_name(blacklisted: str) -> str:
    unisex_names = [
        "Avery",
        "Blake",
        "Cameron",
        "Dakota",
        "Elliott",
        "Finley",
        "Hayden",
        "Kennedy",
        "Logan",
        "Morgan",
        "Peyton",
        "Quinn",
        "Noel",
        "Wyatt",
        "Alex",
        "Ash",
        "Bailey",
        "Milan",
        "Drew",
        "Kris",
        "Frankie",
        "Gabriel",
        "Jamie",
        "Carey",
        "Lee",
        "Max",
        "Parker",
        "Quinn",
        "Riley",
        "Skyler",
        "Taylor",
        "River",
        "Rene",
        "Blair",
        "Drew",
        "Jordan",
        "Parker",
        "Angel",
        "Garrett",
        "Nova",
        "Jesse",
        "Kendall",
        "Landon",
        "Charlie",
        "Nolan",
        "Oliver",
        "Robin",
        "Ellis",
        "Sam",
        "Noah",
        "Wesley",
        "Shiki",
        "Sora",
        "Akira",
        "Maki",
    ]
    name = random.choice(unisex_names)
    while name == blacklisted:
        name = random.choice(unisex_names)
    return name


def validate_inputs(log_path: str, output_folder: str):
    if not isinstance(log_path, str):
        raise TypeError("log_path must be a string")
    if not isinstance(output_folder, str):
        raise TypeError("output_folder must be a string")


def should_process_file(log_path: str) -> bool:
    return os.path.getsize(log_path) >= 4 * 1024


def search_metadata(lines: list[str], field: str) -> str:
    for line in lines:
        jobj = json.loads(line)
        for k, v in jobj.items():
            if k == field:
                return jobj[k]


def obfuscate_user_name(line: dict, og_user_name: str, user_name: str) -> dict:
    if not line or not og_user_name or not user_name:
        return

    new_data = {}

    for k, v in line.items():
        if k == "name" and line.get("is_user"):
            new_data[k] = user_name
        elif k == "mes":
            new_data[k] = replace_name(v, og_user_name, user_name)
        else:
            new_data[k] = v

    return new_data


def replace_name(mes: str, og_user_name: str, user_name: str) -> str:
    s = fuzzy_replace_name(mes, og_user_name, user_name)
    # Handle case full name - replace both first and last name
    if " " in og_user_name:
        firstname = og_user_name.split(" ")[0]
        lastname = og_user_name.split(" ")[-1]
        s = fuzzy_replace_name(mes, firstname, user_name)
        s = fuzzy_replace_name(mes, lastname, user_name)
    return s


def fuzzy_replace_name(mes: str, og_user_name: str, user_name: str) -> str:
    mes = mes.replace(og_user_name[0] + "-" + og_user_name, user_name[0] + "-" + user_name)
    mes = mes.replace(" " + og_user_name, " " + user_name)
    mes = mes.replace('"' + og_user_name, '"' + user_name)
    mes = mes.replace("—" + og_user_name, "—" + user_name)
    mes = mes.replace("-" + og_user_name, "-" + user_name)
    mes = mes.replace("'" + og_user_name, "'" + user_name)
    mes = mes.replace("*" + og_user_name, "*" + user_name)
    mes = mes.replace(og_user_name + " ", user_name + " ")
    mes = mes.replace(og_user_name + ",", user_name + ",")
    mes = mes.replace(og_user_name + "*", user_name + "*")
    mes = mes.replace(og_user_name + "'", user_name + "'")
    mes = mes.replace(og_user_name + ",", user_name + ",")
    mes = mes.replace(og_user_name + ".", user_name + ".")
    mes = mes.replace(og_user_name + "-", user_name + "-")
    mes = mes.replace(og_user_name + "?", user_name + "?")

    return mes


def keep_fields(data: dict, fields_to_keep: list[str]) -> dict:
    return {k: v for k, v in data.items() if k in fields_to_keep}


def prepend_instructions(convo: list[dict], user_name, char_name, char_desc) -> list[dict]:
    sysprompt = "You are '{0}' in this roleplay chat with '{1}'. Respond to '{1}', be creative.".format(
        char_name, user_name
    )
    if char_desc:
        sysprompt += " {0}'s description: {1}".format(char_name, char_desc)

    system = {"name": "system", "mes": sysprompt, "is_user": False}
    starter = {"name": user_name, "mes": "The roleplay begins.", "is_user": True}

    return [system, starter] + convo


def get_char_description(log_path: str) -> str:
    a = log_path.replace("/chats/", "/characters/", 1).split("/")[:-1]
    card_path = "/".join(a) + ".png"

    if not os.path.exists(card_path):
        return

    card = v2_card.parse(card_path)
    return card.data.description


def fix_char_description(char_desc: str, user_name: str, char_name: str) -> str:
    if not char_desc:
        return char_desc
    return char_desc.replace("{{char}}", char_name).replace("{{user}}", user_name)


def process_file(log_path: str, output_folder: str) -> bool:
    validate_inputs(log_path, output_folder)

    if not should_process_file(log_path):
        return False

    with open(log_path, "r") as f:
        lines = f.readlines()

    convo = []
    og_user_name = search_metadata(lines, "user_name")
    og_char_name = search_metadata(lines, "character_name")
    char_name = og_char_name
    user_name = random_unisex_name(char_name)

    for line in lines:
        jobj = json.loads(line)

        jobj = obfuscate_user_name(jobj, og_user_name, user_name)
        jobj = keep_fields(jobj, ["name", "mes", "is_user"])

        if jobj:
            convo.append(jobj)

    char_desc = get_char_description(log_path)
    char_desc = fix_char_description(char_desc, user_name, char_name)
    convo = prepend_instructions(convo, user_name, char_name, char_desc)

    # Write processed output to new file
    with open(f"{output_folder}/{os.path.basename(log_path)}", "w") as f:
        for line in convo:
            f.write(json.dumps(line) + "\n")

    return True


def execute(st_folder: str, output_folder: str) -> int:
    input_folder = st_folder + "/public/chats"
    if not os.path.exists(input_folder):
        raise Exception("No public/chats folder detected in Tavern folder.")

    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Recursively process all .jsonl files in the input folder
    logs_processed = 0
    for root, _, files in os.walk(input_folder):
        for file in files:
            if file.endswith(".jsonl"):
                if process_file(os.path.join(root, file), output_folder) == True:
                    logs_processed += 1

    return logs_processed
