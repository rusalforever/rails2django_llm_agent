import json, logging

def log_state(node, state):
    snapshot = json.dumps(state.__dict__, indent=2, ensure_ascii=False)
    logging.debug(f"\n📦 STATE SNAPSHOT AFTER [{node}]\n{snapshot}\n")
