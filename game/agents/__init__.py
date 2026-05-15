from game.agents.base_agent import BaseAgent
from game.agents.bayesian_agent import BayesianAgent
from game.agents.hunt_agent import HuntAgent
from game.agents.q_agent import QAgent
from game.agents.random_agent import RandomAgent

AGENT_REGISTRY: dict[str, type[BaseAgent]] = {
    "random": RandomAgent,
    "hunt": HuntAgent,
    "bayes": BayesianAgent,
    "q_learning": QAgent,
}
