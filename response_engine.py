import json
from datetime import datetime

from identity_database import identity_map
from scent import trigger_scent


def trigger_response(name):
    if name not in identity_map:
        print("Unknown person.")
        return None

    profile = identity_map[name]
    scent_name = profile.get("scent", "")
    audio_name = profile.get("audio", "")

    trigger_scent(scent_name)

    if audio_name:
        print(f"Audio available: {audio_name}")
    else:
        print("Audio: Not assigned")

    log_entry = {
        "person": name,
        "scent": scent_name,
        "audio": audio_name,
        "timestamp": str(datetime.now()),
    }

    try:
        with open("interaction_log.json", "r", encoding="utf-8") as file:
            logs = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        logs = []

    logs.append(log_entry)

    with open("interaction_log.json", "w", encoding="utf-8") as file:
        json.dump(logs, file, indent=4)

    print("Interaction logged.")
    return {"person": name, "scent": scent_name, "audio": audio_name}
