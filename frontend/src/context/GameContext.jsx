import { createContext, useContext, useReducer, useEffect, useCallback, useMemo } from 'react';
import useWebSocket from '../hooks/useWebSocket';

const GameStateContext = createContext(null);
const GameActionsContext = createContext(null);

// Game states
export const GameState = {
  IDLE: 'idle',
  JOINING: 'joining',
  WAITING: 'waiting',
  PLAYING: 'playing',
  GAME_OVER: 'game_over',
};

// Action types
const ActionTypes = {
  SET_PLAYER: 'SET_PLAYER',
  SET_GAME_STATE: 'SET_GAME_STATE',
  SET_GAME_ID: 'SET_GAME_ID',
  SET_GAME_TYPE: 'SET_GAME_TYPE',
  UPDATE_STATION: 'UPDATE_STATION',
  ADD_GUESSED_LETTER: 'ADD_GUESSED_LETTER',
  UPDATE_PLAYER_PROGRESS: 'UPDATE_PLAYER_PROGRESS',
  UPDATE_STATION_STATUS: 'UPDATE_STATION_STATUS',
  ADD_PLAYER: 'ADD_PLAYER',
  SET_GAME_OVER: 'SET_GAME_OVER',
  SET_WAITING_INFO: 'SET_WAITING_INFO',
  RESET_GAME: 'RESET_GAME',
  GAME_STARTED: 'GAME_STARTED',
  CORRECT_GUESS: 'CORRECT_GUESS',
  WRONG_GUESS: 'WRONG_GUESS',

  // Duel-specific actions
  DUEL_START: 'DUEL_START',
  DUEL_ROUND_START: 'DUEL_ROUND_START',
  DUEL_PLAYER_CAST: 'DUEL_PLAYER_CAST',
  DUEL_OPPONENT_CAST: 'DUEL_OPPONENT_CAST',
  DUEL_ROUND_RESULT: 'DUEL_ROUND_RESULT',
  DUEL_OVER: 'DUEL_OVER',
};

const initialState = {
  playerId: null,
  playerName: '',

  gameState: GameState.IDLE,
  gameId: null,
  gameType: null, // 'quodpot' or 'duels'

  players: [],

  currentStation: 1,
  totalStations: 10,
  revealed: '',
  attemptsLeft: 6,
  guessedLetters: new Set(),
  lastGuess: null, // { letter, correct }

  stationStatus: {}, // { stationNumber: [playerNames] }

  playersInQueue: 0,
  waitingMessage: '',

  winner: null,
  completedWords: [],

  // Duel-specific state
  duel: {
    opponent: null, // { id, name }
    currentRound: 1,
    totalRounds: 5,
    playerSpell: null,
    opponentSpell: null,
    playerScore: [],
    opponentScore: [],
    roundResult: null,
    roundHistory: [],
    isWinner: null,
    mode: 'pvp',
  },
};

function gameReducer(state, action) {
  switch (action.type) {
    case ActionTypes.SET_PLAYER:
      return {
        ...state,
        playerId: action.payload.id,
        playerName: action.payload.name,
      };

    case ActionTypes.SET_GAME_STATE:
      return {
        ...state,
        gameState: action.payload,
      };

    case ActionTypes.SET_GAME_ID:
      return {
        ...state,
        gameId: action.payload,
      };

    case ActionTypes.SET_GAME_TYPE:
      return {
        ...state,
        gameType: action.payload,
      };

    case ActionTypes.GAME_STARTED:
      return {
        ...state,
        gameState: GameState.PLAYING,
        players: action.payload.players.map(p => ({ ...p, station: 1 })),
        totalStations: action.payload.totalStations,
      };

    case ActionTypes.UPDATE_STATION:
      return {
        ...state,
        currentStation: action.payload.station,
        revealed: action.payload.revealed,
        attemptsLeft: action.payload.attemptsLeft,
        guessedLetters: new Set(),
        lastGuess: null,
      };

    case ActionTypes.CORRECT_GUESS:
      return {
        ...state,
        guessedLetters: new Set([...state.guessedLetters, action.payload.letter.toUpperCase()]),
        revealed: action.payload.revealed,
        lastGuess: { letter: action.payload.letter, correct: true },
      };

    case ActionTypes.WRONG_GUESS:
      return {
        ...state,
        guessedLetters: new Set([...state.guessedLetters, action.payload.letter.toUpperCase()]),
        attemptsLeft: action.payload.attemptsLeft,
        lastGuess: { letter: action.payload.letter, correct: false },
      };

    case ActionTypes.UPDATE_PLAYER_PROGRESS:
      return {
        ...state,
        players: state.players.map(player =>
          player.id === action.payload.playerId
            ? { ...player, station: action.payload.station }
            : player
        ),
      };

    case ActionTypes.UPDATE_STATION_STATUS:
      return {
        ...state,
        stationStatus: action.payload,
      };

    case ActionTypes.ADD_PLAYER:
      return {
        ...state,
        players: [
          ...state.players,
          {
            id: action.payload.playerId,
            name: action.payload.playerName,
            station: action.payload.station,
          },
        ],
      };

    case ActionTypes.SET_GAME_OVER:
      return {
        ...state,
        gameState: GameState.GAME_OVER,
        winner: action.payload.winner,
        completedWords: action.payload.words,
      };

    case ActionTypes.SET_WAITING_INFO:
      return {
        ...state,
        gameState: GameState.WAITING,
        playersInQueue: action.payload.count,
        waitingMessage: action.payload.message,
      };

    case ActionTypes.RESET_GAME:
      return {
        ...initialState,
        playerName: state.playerName,
      };

    case ActionTypes.DUEL_START: {
      const isAI = action.payload.opponent?.name === 'Guardián Arcano' ||
                   action.payload.opponent?.id.startsWith('ai_');

      return {
        ...state,
        gameState: GameState.PLAYING,
        gameType: 'duels',
        duel: {
          ...state.duel,
          opponent: action.payload.opponent,
          currentRound: action.payload.currentRound || 1,
          totalRounds: action.payload.totalRounds || 5,
          playerSpell: null,
          opponentSpell: null,
          roundResult: null,
          mode: isAI ? 'pve' : action.payload.mode || 'pvp',
        },
      };
    }

    case ActionTypes.DUEL_ROUND_START:
      return {
        ...state,
        duel: {
          ...state.duel,
          currentRound: action.payload.round,
          playerSpell: null,
          opponentSpell: null,
          roundResult: null,
        },
      };

    case ActionTypes.DUEL_PLAYER_CAST:
      return {
        ...state,
        duel: {
          ...state.duel,
          playerSpell: action.payload.spell,
        },
      };

    case ActionTypes.DUEL_OPPONENT_CAST:
      return {
        ...state,
        duel: {
          ...state.duel,
          opponentSpell: action.payload.spell || 'pending',
        },
      };

    case ActionTypes.DUEL_ROUND_RESULT:
      return {
        ...state,
        duel: {
          ...state.duel,
          opponentSpell: action.payload.opponentSpell,
          roundResult: action.payload.result,
          playerScore:
            action.payload.result === 'win'
              ? [...state.duel.playerScore, action.payload.playerSpell]
              : state.duel.playerScore,
          opponentScore:
            action.payload.result === 'lose'
              ? [...state.duel.opponentScore, action.payload.opponentSpell]
              : state.duel.opponentScore,
          roundHistory: [
            ...state.duel.roundHistory,
            {
              player: action.payload.playerSpell,
              opponent: action.payload.opponentSpell,
              winner:
                action.payload.result === 'win'
                  ? 'player'
                  : action.payload.result === 'lose'
                  ? 'opponent'
                  : 'tie',
            },
          ],
        },
      };

    case ActionTypes.DUEL_OVER:
      return {
        ...state,
        gameState: GameState.GAME_OVER,
        duel: {
          ...state.duel,
          isWinner: action.payload.isWinner,
        },
        winner: action.payload.winner,
      };

    default:
      return state;
  }
}

export function GameProvider({ children }) {
  const [state, dispatch] = useReducer(gameReducer, initialState);
  const { isConnected, sendMessage, subscribe } = useWebSocket();

  useEffect(() => {
    return subscribe('joined', (data) => {
      dispatch({
        type: ActionTypes.SET_PLAYER,
        payload: { id: data.player_id, name: data.player_name },
      });
      if (data.game_id) {
        dispatch({ type: ActionTypes.SET_GAME_ID, payload: data.game_id });
      } else {
        dispatch({ type: ActionTypes.SET_GAME_STATE, payload: GameState.WAITING });
      }
    });
  }, [subscribe]);

  useEffect(() => {
    return subscribe('waiting', (data) => {
      dispatch({
        type: ActionTypes.SET_WAITING_INFO,
        payload: { count: data.players_in_queue, message: data.message },
      });
    });
  }, [subscribe]);

  useEffect(() => {
    return subscribe('game_start', (data) => {
      dispatch({
        type: ActionTypes.GAME_STARTED,
        payload: { players: data.players, totalStations: data.total_stations },
      });
    });
  }, [subscribe]);

  useEffect(() => {
    return subscribe('station_update', (data) => {
      dispatch({
        type: ActionTypes.UPDATE_STATION,
        payload: {
          station: data.station,
          revealed: data.revealed,
          attemptsLeft: data.attempts_left,
        },
      });
    });
  }, [subscribe]);

  useEffect(() => {
    return subscribe('correct_guess', (data) => {
      dispatch({
        type: ActionTypes.CORRECT_GUESS,
        payload: { letter: data.letter, revealed: data.revealed },
      });
    });
  }, [subscribe]);

  useEffect(() => {
    return subscribe('wrong_guess', (data) => {
      dispatch({
        type: ActionTypes.WRONG_GUESS,
        payload: { letter: data.letter, attemptsLeft: data.attempts_left },
      });
    });
  }, [subscribe]);

  useEffect(() => {
    return subscribe('station_complete', () => {});
  }, [subscribe]);

  useEffect(() => {
    return subscribe('station_failed', () => {});
  }, [subscribe]);

  useEffect(() => {
    return subscribe('player_progress', (data) => {
      dispatch({
        type: ActionTypes.UPDATE_PLAYER_PROGRESS,
        payload: {
          playerId: data.player_id,
          station: data.station,
        },
      });
    });
  }, [subscribe]);

  useEffect(() => {
    return subscribe('player_joined', (data) => {
      dispatch({
        type: ActionTypes.ADD_PLAYER,
        payload: {
          playerId: data.player_id,
          playerName: data.player_name,
          station: data.station,
        },
      });
    });
  }, [subscribe]);

  useEffect(() => {
    return subscribe('station_status', (data) => {
      dispatch({
        type: ActionTypes.UPDATE_STATION_STATUS,
        payload: data.stations,
      });
    });
  }, [subscribe]);

  useEffect(() => {
    return subscribe('game_over', (data) => {
      dispatch({
        type: ActionTypes.SET_GAME_OVER,
        payload: {
          winner: { id: data.winner_id, name: data.winner_name },
          words: data.words,
        },
      });
    });
  }, [subscribe]);

  useEffect(() => {
    return subscribe('error', () => {});
  }, [subscribe]);

  useEffect(() => {
    return subscribe('duel_start', (data) => {
      dispatch({
        type: ActionTypes.DUEL_START,
        payload: {
          opponent: { id: data.opponent_id, name: data.opponent_name },
          currentRound: 1,
          totalRounds: data.rounds_to_win || 2,
        },
      });
    });
  }, [subscribe]);

  useEffect(() => {
    return subscribe('round_start', (data) => {
      dispatch({
        type: ActionTypes.DUEL_ROUND_START,
        payload: {
          round: data.round_number,
        },
      });
    });
  }, [subscribe]);

  useEffect(() => {
    return subscribe('opponent_cast', () => {
      dispatch({
        type: ActionTypes.DUEL_OPPONENT_CAST,
        payload: { spell: 'pending' },
      });
    });
  }, [subscribe]);

  useEffect(() => {
    return subscribe('round_result', (data) => {
      dispatch({
        type: ActionTypes.DUEL_ROUND_RESULT,
        payload: {
          playerSpell: data.your_spell,
          opponentSpell: data.opponent_spell,
          result: data.result, // 'win', 'lose', 'tie'
        },
      });
    });
  }, [subscribe]);

  useEffect(() => {
    return subscribe('duel_over', (data) => {
      dispatch({
        type: ActionTypes.DUEL_OVER,
        payload: {
          isWinner: data.winner_id === state.playerId,
          winner: { id: data.winner_id, name: data.winner_name },
        },
      });
    });
  }, [subscribe, state.playerId]);

  // Actions
  const joinGame = useCallback((playerName, gameType = 'hangman', gameMode = 'pvp') => {
    dispatch({ type: ActionTypes.SET_GAME_STATE, payload: GameState.JOINING });
    dispatch({ type: ActionTypes.SET_GAME_TYPE, payload: gameType });
    sendMessage({
      type: 'join',
      player_name: playerName,
      game_type: gameType,
      game_mode: gameMode
    });
  }, [sendMessage]);

  const guessLetter = useCallback((letter) => {
    sendMessage({ type: 'guess', letter: letter.toUpperCase() });
  }, [sendMessage]);

  const leaveGame = useCallback(() => {
    sendMessage({ type: 'leave' });
    dispatch({ type: ActionTypes.RESET_GAME });
  }, [sendMessage]);

  const resetGame = useCallback(() => {
    dispatch({ type: ActionTypes.RESET_GAME });
  }, []);

  const castSpell = useCallback((spell) => {
    dispatch({ type: ActionTypes.DUEL_PLAYER_CAST, payload: { spell } });
    sendMessage({ type: 'spell_cast', spell });
  }, [sendMessage]);

  const requestRematch = useCallback(() => {
    sendMessage({ type: 'rematch' });
    dispatch({ type: ActionTypes.RESET_GAME });
  }, [sendMessage]);

  const stateValue = useMemo(() => ({
    ...state,
    isConnected,
  }), [state, isConnected]);

  const actionsValue = useMemo(() => ({
    joinGame,
    guessLetter,
    leaveGame,
    resetGame,
    castSpell,
    requestRematch,
  }), [joinGame, guessLetter, leaveGame, resetGame, castSpell, requestRematch]);

  return (
    <GameActionsContext.Provider value={actionsValue}>
      <GameStateContext.Provider value={stateValue}>
        {children}
      </GameStateContext.Provider>
    </GameActionsContext.Provider>
  );
}

export function useGameState() {
  const context = useContext(GameStateContext);
  if (!context) {
    throw new Error('useGameState must be used within a GameProvider');
  }
  return context;
}

export function useGameActions() {
  const context = useContext(GameActionsContext);
  if (!context) {
    throw new Error('useGameActions must be used within a GameProvider');
  }
  return context;
}

export function useGame() {
  return { ...useGameState(), ...useGameActions() };
}

export default GameStateContext;
