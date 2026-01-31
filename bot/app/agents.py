import aiohttp
from app.config import AGENTS, AGENT_TOKEN


async def fetch_agent(session: aiohttp.ClientSession, url: str):
    try:
        async with session.get(
            f"{url}/status",
            headers={
                "Authorization": f"Bearer {AGENT_TOKEN}"
            },
            timeout=aiohttp.ClientTimeout(total=3)
        ) as resp:
            return await resp.json()
    except Exception as e:
        return {
            "node": url,
            "status": "error",
            "error": str(e)
        }


async def fetch_all_agents():
    results = []

    async with aiohttp.ClientSession() as session:
        for agent in AGENTS:
            data = await fetch_agent(session, agent)
            results.append(data)

    return results
