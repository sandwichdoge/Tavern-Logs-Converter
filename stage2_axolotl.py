import json
import os


def _generate_sharegpt_dialogue(jobj: dict) -> dict:
    if jobj["name"] == "system":
        return {"from": "system", "value": jobj["mes"]}
    elif jobj["is_user"] == True:
        return {"from": "human", "value": jobj["mes"]}
    elif jobj["is_user"] == False:
        return {"from": "gpt", "value": jobj["mes"]}
    else:
        print("Not supported", jobj)


# Generate a "conversations" json item for sharegpt
def _generate_sharegpt_conversations(cleaned_log_file: str) -> list[dict]:
    with open(cleaned_log_file, "r") as f:
        lines = f.readlines()

    conversations = []
    for line in lines:
        jobj = json.loads(line)
        dialogue = _generate_sharegpt_dialogue(jobj)
        conversations.append(dialogue)

    return conversations


def to_sharegpt(cleaned_log_dir: str, output_file: str):
    if os.path.isfile(output_file):
        os.remove(output_file)

    fout = open(output_file, "a")

    for root, _, files in os.walk(cleaned_log_dir):
        for file in files:
            if file.endswith(".jsonl"):
                conversations = _generate_sharegpt_conversations(os.path.join(root, file))
                data = json.dumps({"conversations": conversations}) + "\n"
                fout.write(data)

    fout.close()
