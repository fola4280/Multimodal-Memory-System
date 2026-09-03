import json
from datetime import datetime
from identity_database import identity_map


def trigger_response(name):

    if name not in identity_map:
        print("Unknown person.")
        return

    profile = identity_map[name]

    print(f"Releasing scent: {profile['scent']}")
    print(f"Playing audio: {profile['audio']}")

    log_entry = {
        "person": name,
        "relationship": profile["relationship"],
        "scent": profile["scent"],
        "audio": profile["audio"],
        "timestamp": str(datetime.now())
    }

    try:
        with open("interaction_log.json", "r") as file:
            logs = json.load(file)
    except:
        logs = []

    logs.append(log_entry)

    with open("interaction_log.json", "w") as file:
        json.dump(logs, file, indent=4)

    print("Interaction logged.")