const wsUrl = "ws://localhost:8765";
let socket = null;
let myTurn = false;
let gameId = null;
let gameEnded = false;
const sunkShips = { p: new Set(), a: new Set() };

let placingShip = null;
let placingSize = 0;
let placeDirection = 'right';
let lastPlaceRequest = null;

const ROWS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J'];
const COLS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];

// DOM Elements
const statusDot = document.querySelector('.dot');
const statusText = document.querySelector('#status');
const modal = document.getElementById('modal');
const modalBtn = document.getElementById('modal-btn');
const modalTitle = document.getElementById('modal-title');
const modalDesc = document.getElementById('modal-desc');
const gameArea = document.getElementById('game-area');
const turnIndicator = document.getElementById('turn-indicator');
const playerGrid = document.getElementById('player-grid');
const agentGrid = document.getElementById('agent-grid');
const playerActionLog = document.getElementById('player-action-log');
const agentActionLog = document.getElementById('agent-action-log');
const playerSunk = document.getElementById('player-sunk');
const playerHits = document.getElementById('player-hits');
const agentSunk = document.getElementById('agent-sunk');
const agentHits = document.getElementById('agent-hits');

// Initialize grids
function initGrids() {
  playerGrid.innerHTML = '';
  agentGrid.innerHTML = '';

  // Header row
  playerGrid.appendChild(createCell('', 'header'));
  agentGrid.appendChild(createCell('', 'header'));
  COLS.forEach(c => {
    playerGrid.appendChild(createCell(c, 'header'));
    agentGrid.appendChild(createCell(c, 'header'));
  });

  // Rows
  ROWS.forEach((r, rIdx) => {
    playerGrid.appendChild(createCell(r, 'header'));
    agentGrid.appendChild(createCell(r, 'header'));

    COLS.forEach((c, cIdx) => {
      const pCell = createCell('', 'playable');
      pCell.id = `p-${rIdx}-${cIdx}`;
      pCell.dataset.coord = `${r}${c}`;
      pCell.dataset.r = rIdx;
      pCell.dataset.c = cIdx;
      pCell.addEventListener('click', () => handlePlayerCellClick(pCell.dataset.coord, rIdx, cIdx));
      pCell.addEventListener('contextmenu', (e) => {
        e.preventDefault();
        if (placingShip) {
          placeDirection = placeDirection === 'right' ? 'down' : 'right';
          updatePlacementUI();
          renderPlacementHover(rIdx, cIdx);
        }
      });
      pCell.addEventListener('mouseenter', () => renderPlacementHover(rIdx, cIdx));
      pCell.addEventListener('mouseleave', clearPlacementHover);
      playerGrid.appendChild(pCell);

      const aCell = createCell('', 'playable');
      aCell.id = `a-${rIdx}-${cIdx}`;
      aCell.dataset.coord = `${r}${c}`;
      aCell.addEventListener('click', () => handleCellClick(aCell.dataset.coord));
      agentGrid.appendChild(aCell);
    });
  });
}

function createCell(text, className) {
  const div = document.createElement('div');
  div.className = `cell ${className}`;
  div.textContent = text;
  return div;
}

initGrids();

// WebSocket logic
modalBtn.addEventListener('click', connect);

function resetGameUI() {
  gameEnded = false;
  myTurn = false;
  gameId = null;
  placingShip = null;
  placingSize = 0;
  lastPlaceRequest = null;
  sunkShips.p.clear();
  sunkShips.a.clear();

  // Clear Action logs
  playerActionLog.innerHTML = '';
  agentActionLog.innerHTML = '';

  // Clear stats
  playerSunk.textContent = '0';
  playerHits.textContent = '0';
  agentSunk.textContent = '0';
  agentHits.textContent = '0';

  // Ensure connect button is visible
  modalBtn.style.display = '';

  // Re-initialize grids
  initGrids();
}

function connect() {
  modalBtn.textContent = 'Connecting...';
  modalBtn.disabled = true;

  resetGameUI();

  socket = new WebSocket(wsUrl);

  socket.onopen = () => {
    statusDot.className = 'dot connected';
    statusText.innerHTML = '<span class="dot connected"></span> Connected';
    socket.send(JSON.stringify({ role: "player" }));
  };

  socket.onmessage = (event) => {
    const msg = JSON.parse(event.data);
    handleServerMessage(msg);
  };

  socket.onclose = () => {
    statusDot.className = 'dot disconnected';
    statusText.innerHTML = '<span class="dot disconnected"></span> Disconnected';
    if (!gameEnded) {
      showModal("Disconnected", "Connection to the game server was lost. Please restart the backend and try again.", "Reconnect");
    }
    modalBtn.disabled = false;
  };

  socket.onerror = (error) => {
    console.error("WebSocket Error:", error);
    showModal("Connection Error", "Could not connect to the backend server. Is it running?", "Try Again");
    modalBtn.disabled = false;
  };
}

function showModal(title, desc, btnText) {
  modalTitle.textContent = title;
  modalDesc.textContent = desc;
  modalBtn.textContent = btnText;
  modal.classList.remove('hidden');
  gameArea.classList.add('hidden');
}

function hideModal() {
  modal.classList.add('hidden');
  gameArea.classList.remove('hidden');
}

function logAction(text, type = '', owner = 'player') {
  const li = document.createElement('li');
  li.textContent = text;
  if (type) li.className = type + '-log';
  const targetLog = owner === 'agent' ? agentActionLog : playerActionLog;
  targetLog.prepend(li);
  if (targetLog.children.length > 20) {
    targetLog.removeChild(targetLog.lastChild);
  }
}

function updatePlacementUI() {
  if (placingShip) {
    turnIndicator.textContent = `Place ${placingShip} (Size: ${placingSize}). Right-click to rotate. Direction: ${placeDirection.toUpperCase()}`;
    turnIndicator.className = 'turn-indicator active';
  }
}

function handleServerMessage(msg) {
  console.log("Received:", msg);

  switch (msg.type) {
    case "welcome":
      gameId = msg.game_id;
      if (msg.role !== "player") {
        showModal("Observer Mode", "Another player is already connected. You are an observer.", "Wait");
        modalBtn.style.display = 'none';
      } else {
        hideModal();
        logAction("Connected to game engine.", "info");
      }
      break;

    case "place_ship":
      placingShip = msg.ship;
      placingSize = msg.size;
      updatePlacementUI();
      break;

    case "placement_ack":
      if (msg.valid) {
        logAction(`Successfully placed ${placingShip}.`, "info");
        // Color the placed ship locally
        if (lastPlaceRequest) {
          const { r, c, dir, size } = lastPlaceRequest;
          for (let i = 0; i < size; i++) {
            const row = dir === 'down' ? r + i : r;
            const col = dir === 'right' ? c + i : c;
            const cell = document.getElementById(`p-${row}-${col}`);
            if (cell) {
              cell.classList.add('ship');
              cell.textContent = placingShip.charAt(0);
            }
          }
        }
        placingShip = null;
        lastPlaceRequest = null;
      } else {
        logAction(`Invalid placement: ${msg.error}`, "hit");
      }
      break;

    case "game_start":
      placingShip = null;
      sunkShips.p.clear();
      sunkShips.a.clear();
      logAction("Game started! Your fleet is deployed.", "info");
      updateBoard(playerGrid, msg.your_board, 'p');
      break;

    case "ship_sunk":
      const isPlayer = msg.attacker === "player";
      const prefix = isPlayer ? 'a' : 'p';
      sunkShips[prefix].add(msg.ship);
      
      const target = isPlayer ? "enemy's" : "your";
      const subject = isPlayer ? "You" : "Agent";
      showToast(`💥 ${subject} sunk ${target} ${msg.ship}!`);
      
      highlightSunkShip(prefix, msg.ship, true);
      break;

    case "player_view":
      myTurn = true;
      turnIndicator.textContent = `Turn ${msg.turn} — Your Move`;
      turnIndicator.className = 'turn-indicator active';
      updateBoard(agentGrid, msg.enemy_board, 'a');
      updateBoard(playerGrid, msg.your_board, 'p');
      updateStats(msg.ships_sunk.against_you, null, msg.ships_sunk.by_you, null);
      break;

    case "move_ack":
      let logType = msg.result === "HIT" ? "hit" : "miss";
      let logText = `You fired at ${msg.coordinate}: ${msg.result}`;
      if (msg.ship_sunk) {
        logText += ` — Sunk enemy ${msg.ship_sunk}!`;
        logType = "sunk";
      } else if (msg.ship_hit) {
        logText += ` — Hit ${msg.ship_hit}`;
      }
      logAction(logText, logType);
      myTurn = false;
      turnIndicator.textContent = `Waiting for Agent...`;
      turnIndicator.className = 'turn-indicator';
      break;

    case "game_state":
      if (!myTurn && !placingShip) {
        updateBoard(playerGrid, msg.player_board.cells, 'p');
        updateBoard(agentGrid, msg.agent_board.cells, 'a');
        updateStats(
          msg.player_board.ships_sunk, 
          msg.player_board.cells_hit, 
          msg.agent_board.ships_sunk, 
          msg.agent_board.cells_hit
        );
      }
      if (msg.last_move && msg.last_move.player === "agent") {
        let lm = msg.last_move;
        let lType = lm.result === "HIT" ? "hit" : "miss";
        let lText = `Agent fired at ${lm.coordinate}: ${lm.result}`;
        if (lm.ship_sunk) {
          lText += ` — Sunk your ${lm.ship_sunk}!`;
          lType = "sunk";
        } else if (lm.ship_hit) {
          lText += ` — Hit your ${lm.ship_hit}`;
        }
        logAction(lText, lType, 'agent');
      }
      break;

    case "game_over":
      myTurn = false;
      gameEnded = true;
      turnIndicator.className = 'turn-indicator';
      const winner = msg.winner === "player" ? "You won!" : "Agent won!";
      turnIndicator.textContent = `Game Over — ${winner}`;
      logAction(`GAME OVER. ${winner}`, "sunk", 'player');
      logAction(`GAME OVER. ${winner}`, "sunk", 'agent');
      
      const stats = `Total Turns: ${msg.total_turns}<br><br>
      <b>Your Performance:</b><br>
      Hits: ${msg.scores.player.cells_hit} | Ships Sunk: ${msg.scores.player.ships_sunk}<br><br>
      <b>Agent's Performance:</b><br>
      Hits: ${msg.scores.agent.cells_hit} | Ships Sunk: ${msg.scores.agent.ships_sunk}`;
      
      modalTitle.textContent = winner;
      modalDesc.innerHTML = stats;
      modalBtn.textContent = "Play Again";
      modal.classList.remove('hidden');
      gameArea.classList.remove('hidden'); // don't hide game area, just show overlay
      break;
  }
}

function updateBoard(gridElement, matrix, prefix) {
  if (!matrix) return;
  for (let r = 0; r < 10; r++) {
    for (let c = 0; c < 10; c++) {
      const cellData = matrix[r][c];
      const cell = document.getElementById(`${prefix}-${r}-${c}`);
      if (!cell) continue;
      
      const parts = cellData.split(':');
      const shipType = parts[0];
      const state = parts[1];
      cell.dataset.ship = shipType;

      // Reset classes
      cell.className = 'cell playable';
      cell.textContent = '';

      if (state === 'HIT') {
        cell.classList.add('hit');
        cell.textContent = 'X';
        if (sunkShips[prefix].has(shipType)) {
          cell.classList.add('sunk');
        }
      } else if (state === 'MISS') {
        cell.classList.add('miss');
        cell.textContent = '•';
      } else if (state === 'EMPTY') {
        if (shipType !== 'NONE') {
          cell.classList.add('ship');
          cell.textContent = shipType.charAt(0);
        }
      }
    }
  }
}

function showToast(message) {
  const toast = document.getElementById('toast');
  toast.textContent = message;
  toast.classList.remove('hidden');
  setTimeout(() => toast.classList.add('hidden'), 3500);
}

function highlightSunkShip(prefix, shipName, animate) {
  for (let r = 0; r < 10; r++) {
    for (let c = 0; c < 10; c++) {
      const cell = document.getElementById(`${prefix}-${r}-${c}`);
      if (cell && cell.dataset.ship === shipName && cell.classList.contains('hit')) {
        cell.classList.add('sunk');
        if (animate) {
          cell.classList.add('sunk-animation');
          setTimeout(() => cell.classList.remove('sunk-animation'), 1000);
        }
      }
    }
  }
}

function updateStats(pSunk, pHits, aSunk, aHits) {
  if (pSunk !== null) playerSunk.textContent = pSunk;
  if (pHits !== null) playerHits.textContent = pHits;
  if (aSunk !== null) agentSunk.textContent = aSunk;
  if (aHits !== null) agentHits.textContent = aHits;
}

function handleCellClick(coord) {
  if (!myTurn) {
    console.log("Not your turn!");
    return;
  }
  socket.send(JSON.stringify({ type: "move", coordinate: coord }));
}

function handlePlayerCellClick(coord, r, c) {
  if (placingShip) {
    lastPlaceRequest = { r, c, dir: placeDirection, size: placingSize };
    socket.send(JSON.stringify({
      type: "placement",
      coordinate: coord,
      direction: placeDirection
    }));
  }
}

function renderPlacementHover(r, c) {
  clearPlacementHover();
  if (!placingShip) return;

  for (let i = 0; i < placingSize; i++) {
    const row = placeDirection === 'down' ? r + i : r;
    const col = placeDirection === 'right' ? c + i : c;
    const cell = document.getElementById(`p-${row}-${col}`);
    if (cell) {
      cell.classList.add('placement-hover');
    }
  }
}

function clearPlacementHover() {
  document.querySelectorAll('.placement-hover').forEach(el => {
    el.classList.remove('placement-hover');
  });
}
