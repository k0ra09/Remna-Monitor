import aiohttp
from app.registry import load_agents
from app.config import AGENT_TOKEN


async def fetch_agent(session, agent):
    try:
        async with session.get(
            f"{agent['url']}/status",
            headers={"Authorization": f"Bearer {AGENT_TOKEN}"},
            timeout=aiohttp.ClientTimeout(total=3)
        ) as resp:
            data = await resp.json()
            data["node"] = agent["name"]
            return data
    except Exception as e:
        return {
            "node": agent["name"],
            "status": "error",
            "error": str(e)
        }


async def fetch_all_agents():
    agents = load_agents()
    results = []

    async with aiohttp.ClientSession() as session:
        for agent in agents:
            results.append(await fetch_agent(session, agent))

    return results
