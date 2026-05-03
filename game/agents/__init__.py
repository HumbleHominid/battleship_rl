from game.agents.base_agent import BaseAgent
from game.agents.probability_agent import ProbabilityAgent
from game.agents.random_agent import RandomAgent

AGENT_REGISTRY: dict[str, type[BaseAgent]] = {
    "random": RandomAgent,
    "probability": ProbabilityAgent,
}
