import json
import os

REGISTRY_FILE = "agents.json"


def load_agents():
    if not os.path.exists(REGISTRY_FILE):
        return []
    with open(REGISTRY_FILE, "r") as f:
        return json.load(f)


def save_agents(agents):
    with open(REGISTRY_FILE, "w") as f:
        json.dump(agents, f, indent=2)


def register_agent(agent):
    agents = load_agents()

    # не дублируем по name
    for a in agents:
        if a["name"] == agent["name"]:
            a.update(agent)
            save_agents(agents)
            return

    agents.append(agent)
    save_agents(agents)
