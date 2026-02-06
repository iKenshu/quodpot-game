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
};

const initialState = {
  // Player info
  playerId: null,
  playerName: '',

  // Game state
  gameState: GameState.IDLE,
  gameId: null,

  // All players in game
  players: [],

  // Station data
  currentStation: 1,
  totalStations: 10,
  revealed: '',
  attemptsLeft: 6,
  guessedLetters: new Set(),
  lastGuess: null, // { letter, correct }

  // Station status (players per station)
  stationStatus: {}, // { stationNumber: [playerNames] }

  // Waiting room
  playersInQueue: 0,
  waitingMessage: '',

  // Game over
  winner: null,
  completedWords: [],
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

    default:
      return state;
  }
}

export function GameProvider({ children }) {
  const [state, dispatch] = useReducer(gameReducer, initialState);
  const { isConnected, sendMessage, subscribe } = useWebSocket();

  // Handle joined message
  useEffect(() => {
    return subscribe('joined', (data) => {
      dispatch({
        type: ActionTypes.SET_PLAYER,
        payload: { id: data.player_id, name: data.player_name },
      });
      if (data.game_id) {
        dispatch({ type: ActionTypes.SET_GAME_ID, payload: data.game_id });
        dispatch({ type: ActionTypes.SET_GAME_STATE, payload: GameState.WAITING });
      }
    });
  }, [subscribe]);

  // Handle waiting message
  useEffect(() => {
    return subscribe('waiting', (data) => {
      dispatch({
        type: ActionTypes.SET_WAITING_INFO,
        payload: { count: data.players_in_queue, message: data.message },
      });
    });
  }, [subscribe]);

  // Handle game start
  useEffect(() => {
    return subscribe('game_start', (data) => {
      dispatch({
        type: ActionTypes.GAME_STARTED,
        payload: { players: data.players, totalStations: data.total_stations },
      });
    });
  }, [subscribe]);

  // Handle station update
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

  // Handle correct guess
  useEffect(() => {
    return subscribe('correct_guess', (data) => {
      dispatch({
        type: ActionTypes.CORRECT_GUESS,
        payload: { letter: data.letter, revealed: data.revealed },
      });
    });
  }, [subscribe]);

  // Handle wrong guess
  useEffect(() => {
    return subscribe('wrong_guess', (data) => {
      dispatch({
        type: ActionTypes.WRONG_GUESS,
        payload: { letter: data.letter, attemptsLeft: data.attempts_left },
      });
    });
  }, [subscribe]);

  // Handle station complete
  useEffect(() => {
    return subscribe('station_complete', () => {});
  }, [subscribe]);

  // Handle station failed
  useEffect(() => {
    return subscribe('station_failed', () => {});
  }, [subscribe]);

  // Handle player progress
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

  // Handle player joined
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

  // Handle station status broadcast
  useEffect(() => {
    return subscribe('station_status', (data) => {
      dispatch({
        type: ActionTypes.UPDATE_STATION_STATUS,
        payload: data.stations,
      });
    });
  }, [subscribe]);

  // Handle game over
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

  // Handle error
  useEffect(() => {
    return subscribe('error', () => {});
  }, [subscribe]);

  // Actions
  const joinGame = useCallback((playerName) => {
    dispatch({ type: ActionTypes.SET_GAME_STATE, payload: GameState.JOINING });
    sendMessage({ type: 'join', player_name: playerName });
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

  const stateValue = useMemo(() => ({
    ...state,
    isConnected,
  }), [state, isConnected]);

  const actionsValue = useMemo(() => ({
    joinGame,
    guessLetter,
    leaveGame,
    resetGame,
  }), [joinGame, guessLetter, leaveGame, resetGame]);

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
