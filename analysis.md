# Using RL to Play Battleship

Battleship is a classic two-player game where each player tries to sink the other's fleet of ships by guessing their locations on a grid. With a board size of 10x10 and each cell having 2 possible states (hit or miss), the state space of the game is $2^{100}$, which is very large but still possible to model in a 128-bit integer. The action space is also large, with 100 possible actions (guessing each cell). This makes it an interesting problem for reinforcement learning, as it requires strategic decision-making and can be used to test various RL algorithms.

## Baseline Approach

There are multiple ways to approach this problem algorithmically. We will look at three different agents to serve as a baseline for our RL model: a random agent, a "hunt" agent, and a bayesian agent.

### Random Agent

The random agent simply guesses a random valid cell on the board for each turn. That is, the agent cannot repeat guesses and will only select from the remaining cells. This is straightforward to implement and serves as a lower bound for performance.

### Hunt Agent

The hunt agent uses a simple hunt strategy. It starts by randomly guessing cells in a checkerboard pattern (e.g., guessing all the cells where the sum of the row and column indices is even). Once it gets a hit, it switches to a "hunt" mode where it guesses the adjacent cells to try to sink the ship.

### Bayesian Agent

The bayesian agent maintains a probability distribution over the board, representing the likelihood of each cell containing a ship based on the hits and misses observed so far. It updates this distribution after each guess and selects the cell with the highest probability for the next guess.

### Baseline Performance

To evaluate the performance of these baseline agents, we run 10,000 games against a random-guessing opponent and record the win-rate and average number of turns it takes for each agent to win. Whether the player or the agent goes first can affect the outcome so we employ a fair coin flip to determine the starting player. We also test for different ship placement strategies as the ship placement may influence the agents' performance. The results are as follows:

#### Random Placement

Ships are placed randomly on the board.

| Agent         | Win Rate | Average Turns to Win |
|---------------|----------|----------------------|
| Random        | 49.04%   | 92.67 ± 5.23         |
| Hunt          | 99.98%   | 55.16 ± 9.12         |
| Bayesian      | 100%     | 47.64 ± 9.31         |

#### Spread Placement

Ships are placed spread out, maximizing the distance between them.

| Agent         | Win Rate | Average Turns to Win |
|---------------|----------|----------------------|
| Random        | 49.07%   | 92.74 ± 5.21         |
| Hunt          | 99.99%   | 58.76 ± 7.49         |
| Bayesian      | 99.97%   | 52.09 ± 8.02         |

#### Gaussian Placement

Ships are placed near randomly generated "hotspots" on the board. These hotspots act as seeds for clusters of ships.

| Agent         | Win Rate | Average Turns to Win |
|---------------|----------|----------------------|
| Random        | 49.74%   | 92.61 ± 5.32         |
| Hunt          | 99.99%   | 54.09 ± 9.43         |
| Bayesian      | 99.99%   | 47.71 ± 9.30         |

### Baseline Analysis

The random agent performs as expected, with a win rate around 50% and an average of around 92 turns to win. The hunt agent performs significantly better, with a win rate of basically 100% and an average of around 55-59 turns to win, depending on the ship placement strategy. The bayesian agent performs the best, with a perfect or near-perfect win rate and an average of around 47-52 turns to win. It is notable that the bayesian agent struggled the most with the spread placement strategy. This intuitively makes sense, however, as the spread placement strategy minimizes the clustering of ships, which is what the bayesian agent relies on to make informed guesses.

Overall, these metrics provide a strong baseline for evaluating the performance of our RL agent. Sophisticated algorithms and heuristics can easily reach fewer than 50 turns to win, so we will aim to beat that threshold with our RL agent.
