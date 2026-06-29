import json
import os
import re
from datetime import datetime, timedelta, timezone

import requests
from loguru import logger
from pydantic import BaseModel, Field

from zuno.settings import app_settings


class ImportedConfigInfo(BaseModel):
    name: str
    url: str | None = None
    type: str = "sse"
    headers: dict | None = None
    command: str | None = None
    args: list[str] | None = None
    env: dict | None = None
    env_passthrough: list[str] | None = None
    cwd: str | None = None


def parse_imported_config(imported_config):
    name, info = next(iter(imported_config.get("mcpServers", {}).items()))

    return ImportedConfigInfo(
        name=name,
        url=info.get("url"),
        type=info.get("type"),
        headers=info.get("headers"),
        command=info.get("command"),
        args=info.get("args"),
        env=info.get("env"),
        env_passthrough=info.get("env_passthrough"),
        cwd=info.get("cwd"),
    )


def build_completion_system_prompt(system_prompt, history):
    if "{history}" in system_prompt:
        system_prompt = system_prompt.format(
            history=f"<chat_history>\n{history}\n</chat_history>"
        )
    else:
        system_prompt += f"""
        馃摐 瀵硅瘽鍘嗗彶
        - {history}
        """
    return system_prompt


def build_completion_history_messages(history_messages):
    if len(history_messages) % 2 == 1:
        history_messages = history_messages[: len(history_messages) - 1]

    history_content = ""
    for idx in range(0, len(history_messages), 2):
        user_msg = history_messages[idx]
        ai_msg = history_messages[idx + 1]
        history_content += f"<chat_history_{idx // 2 + 1}>\n"
        history_content += f"role: {user_msg.type}, content: {user_msg.content}\n"
        history_content += f"role: {ai_msg.type}, content: {ai_msg.content}\n"
        history_content += f"</chat_history_{idx // 2 + 1}>\n"

    return history_content


def fix_json_text(text: str):
    return text.replace("'", '"')


def get_cache_key(client_id, chat_id):
    return f"{client_id}_{chat_id}"


def check_or_create(path):
    if not os.path.exists(path):
        os.makedirs(path)


def build_completion_user_input(user_input, file_url):
    if file_url:
        return f"{user_input}, 涓婁紶鐨勬枃浠堕摼鎺ワ細{file_url}"
    return user_input


def init_dir(path):
    try:
        if not os.path.exists(path):
            os.makedirs(path)
    except Exception as err:
        logger.error(f"create dir appear: {err}")


def get_now_beijing_time(delta: int = 0):
    beijing_tz = timezone(timedelta(hours=8 + delta))
    now = datetime.now(beijing_tz)
    return now.strftime("%Y-%m-%d %H:%M")


def get_provider_from_model(model_name):
    model_provider_map = {
        "qwen": "閫氫箟鍗冮棶",
        "gpt": "OpenAI",
        "o1": "OpenAI",
        "deepseek": "娣卞害姹傜储",
        "ernie": "鐧惧害鏂囧績涓€瑷€",
        "wenxin": "鐧惧害鏂囧績涓€瑷€",
        "doubao": "瀛楄妭璺冲姩",
        "xinghuo": "绉戝ぇ璁",
        "claude": "Anthropic",
        "gemini": "Google",
        "gemma": "Google",
        "glm": "鏅鸿氨AI",
        "kimi": "KiMi",
        "sensechat": "鍟嗘堡鍟嗛噺",
        "abab": "MiniMax",
    }

    if not isinstance(model_name, str) or model_name.strip() == "":
        return "鏈煡鏈嶅姟鍟?"

    model_name_lower = model_name.strip().lower()
    for keyword, provider in model_provider_map.items():
        if keyword in model_name_lower:
            return provider

    return "鏈煡鏈嶅姟鍟?"


def check_input(user_input):
    alphabet_pattern = re.compile(r"^[a-zA-Z0-9]+$")
    return bool(alphabet_pattern.match(user_input))


def delete_img(logo: str):
    try:
        if os.path.exists(logo) and logo != app_settings.default_config.get("agent_logo_url"):
            os.remove(logo)
        else:
            logger.info("The logo Path is no exist")
    except Exception as err:
        logger.error(f"delete img appear error: {err}")


def filename_to_classname(filename):
    parts = filename.split("_")
    return "".join(part.capitalize() for part in parts)


def load_scene_templates(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def load_all_scene_configs(chatId):
    all_scene_configs = {}

    original_path = "./Agent_data/first_important.json"
    file_path = f"./Agent_data/{chatId}.json"
    if not os.path.exists(file_path):
        with open(original_path, "r", encoding="utf-8") as original_file:
            data = json.load(original_file)

        with open(file_path, "w", encoding="utf-8") as new_file:
            json.dump(data, new_file, ensure_ascii=False, indent=4)

    current_config = load_scene_templates(file_path)

    for key, value in current_config.items():
        if key not in all_scene_configs:
            all_scene_configs[key] = value

    return all_scene_configs


def send_message(prompt, user_input):
    headers = {
        "Content-Type": "application/json",
        "Authorization": "-------------",
    }
    data = {
        "models": "Qwen1.5-72b-chat",
        "messages": [{"role": "user", "content": prompt}],
    }

    response = requests.post("models.url", data=json.dumps(data), headers=headers).content
    print(response)

    response_1 = json.loads(response)
    message = response_1["choices"][0]["message"]["content"]
    return str(message)


def is_slot_fully_filled(json_data):
    for item in json_data:
        if item.get("value") == "" or "鏈彁渚?" in item.get("value"):
            return False
    return True


def get_raw_slot(parameters):
    output_data = []
    for item in parameters:
        new_item = {"name": item["name"], "desc": item["desc"], "schema": item["schema"], "value": ""}
        output_data.append(new_item)
    return output_data


def get_dynamic_example(scene_config):
    if "example" in scene_config:
        return scene_config["example"]
    return '绛旓細{"name":"xx","value":"xx"}'


def get_slot_update_json(slot):
    output_data = []
    for item in slot:
        new_item = {"name": item["name"], "desc": item["desc"], "value": item["value"]}
        output_data.append(new_item)
    return output_data


def get_slot_query_user_json(slot):
    output_data = []
    for item in slot:
        if not item["value"] or "鏈彁渚?" in item["value"]:
            new_item = {"name": item["name"], "desc": item["desc"], "value": item["value"]}
            output_data.append(new_item)
    return output_data


def update_slot(json_data, dict_target):
    for item in json_data:
        if item is not None and "value" in item and item["value"] != "":
            for target in dict_target:
                if target["name"] == item["name"]:
                    target["value"] = item.get("value")
                    break


def update_agent_json(scene_name, slot, chatId):
    file_path = f"./Agent_data/{chatId}.json"
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    for index in range(len(slot)):
        data[scene_name]["parameters"][index]["value"] = slot[index]["value"]

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def clear_agent_json(scene_name, chatId):
    file_path = f"./Agent_data/{chatId}.json"
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    for index in range(len(data[scene_name]["parameters"])):
        data[scene_name]["parameters"][index]["value"] = ""

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def clean_slot_json(slot):
    return get_raw_slot(slot)


def update_agent_current_scene(current_scene, chatId):
    file_path = "./Agent_data/current_scene.json"
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    data[chatId] = current_scene

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def get_agent_current_scene(chatId):
    file_path = "./Agent_data/current_scene.json"
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    return data.get(chatId, "")


def format_name_value_for_logging(json_data):
    log_strings = []
    for item in json_data:
        name = item.get("name", "Unknown name")
        value = item.get("value", "N/A")
        log_strings.append(f"name: {name}, Value: {value}")
    return "\n".join(log_strings)


def extract_json_from_string(input_string):
    try:
        matches = re.findall(r"\{.*?\}", input_string, re.DOTALL)

        valid_jsons = []
        for match in matches:
            try:
                json_obj = json.loads(match)
                valid_jsons.append(json_obj)
            except json.JSONDecodeError:
                try:
                    valid_jsons.append(fix_json(match))
                except json.JSONDecodeError:
                    continue
                continue

        return valid_jsons
    except Exception as exc:
        print(f"Error occurred: {exc}")
        return []


def fix_json(bad_json):
    fixed_json = bad_json.replace("'", '"')
    try:
        return json.loads(fixed_json)
    except json.JSONDecodeError:
        print("缁欏畾鐨勫瓧绗︿覆涓嶆槸鏈夋晥鐨?JSON 鏍煎紡銆?")


def get_function(type: str = "openai"):
    if type == "openai":
        return get_function_openai()
    return get_function_qwen()


def get_function_openai():
    parameter = AgentService.select_agent_by_type(type="openai")
    result = []
    for data in parameter:
        para = json.loads(data.parameter)
        result.append(para)
    return result


def get_function_qwen():
    parameter = AgentService.select_agent_by_type(type="qwen")
    result = []
    for data in parameter:
        para = json.loads(data.parameter)
        result.append(para)
    return result


def get_function_by_name_type(function_name: str, type: str = "openai"):
    parameter = AgentService.get_agent_by_name_type(name=function_name, type=type)

    for data in parameter:
        para = json.loads(data.parameter)
        return para
    logger.info("get function by name schema appear no data")
