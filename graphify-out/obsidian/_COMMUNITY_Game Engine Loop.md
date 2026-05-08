---
type: community
cohesion: 0.22
members: 17
---

# Game Engine Loop

**Cohesion:** 0.22 - loosely connected
**Members:** 17 nodes

## Members
- [[.__init__()]] - code - game/game_engine.py
- [[._build_agent_obs()]] - code - game/game_engine.py
- [[._build_game_over_dict()]] - code - game/game_engine.py
- [[._build_player_view()]] - code - game/game_engine.py
- [[._build_state_dict()]] - code - game/game_engine.py
- [[._check_win_condition()]] - code - game/game_engine.py
- [[._display_boards()]] - code - game/game_engine.py
- [[._display_game_over()]] - code - game/game_engine.py
- [[._fire_on_agent_board()]] - code - game/game_engine.py
- [[._game_loop()]] - code - game/game_engine.py
- [[._setup()]] - code - game/game_engine.py
- [[._setup_ws_player()]] - code - game/game_engine.py
- [[._take_agent_turn()]] - code - game/game_engine.py
- [[._take_player_turn()]] - code - game/game_engine.py
- [[.reset()]] - code - game/game_engine.py
- [[.run()]] - code - game/game_engine.py
- [[GameEngine]] - code - game/game_engine.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Game_Engine_Loop
SORT file.name ASC
```

## Connections to other communities
- 4 edges to [[_COMMUNITY_Game Board & Actions]]
- 1 edge to [[_COMMUNITY_Coordinate & Game Core]]
- 1 edge to [[_COMMUNITY_Agent Interface]]

## Top bridge nodes
- [[GameEngine]] - degree 22, connects to 3 communities