from game.agents.base_agent import BaseAgent
from game.agents.random_agent import RandomAgent

AGENT_REGISTRY: dict[str, type[BaseAgent]] = {
    "random": RandomAgent,
}
