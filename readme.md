# Battleship RL

A battleship RL agent.

## Installation

```bash
conda env create -n battleship-rl -f environment.yaml
conda activate battleship-rl
```

## Usage

```
python main --help
python main --mode {"automated" | "interactive"}
python main --ws-host <host>
python main --ws-port <port>
python main --no-ws
python main --log-level {"DEBUG" | "INFO" | "WARNING" | "ERROR"}
```