from game.agents.base_agent import BaseAgent
from game.agents.bayesian_agent import BayesianAgent
from game.agents.biased_bayesian_agent import BiasedBayesianAgent
from game.agents.hunt_agent import HuntAgent
from game.agents.q_agent import QAgent
from game.agents.random_agent import RandomAgent
from game.agents.cognitive_q_agent import CognitiveQAgent

AGENT_REGISTRY: dict[str, type[BaseAgent]] = {
    "random": RandomAgent,
    "hunt": HuntAgent,
    "bayes": BayesianAgent,
    "biased-bayes": BiasedBayesianAgent,
    "q-agent": QAgent,
    "cognitive-q": CognitiveQAgent,
}

