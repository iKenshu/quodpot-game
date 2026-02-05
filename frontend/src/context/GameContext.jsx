import { createContext, useContext, useReducer, useEffect, useCallback } from 'react';
import useWebSocket from '../hooks/useWebSocket';

const GameContext = createContext(null);

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
  SET_PLAYERS: 'SET_PLAYERS',
  UPDATE_STATION: 'UPDATE_STATION',
  UPDATE_REVEALED: 'UPDATE_REVEALED',
  UPDATE_ATTEMPTS: 'UPDATE_ATTEMPTS',
  ADD_GUESSED_LETTER: 'ADD_GUESSED_LETTER',
  SET_LAST_GUESS: 'SET_LAST_GUESS',
  UPDATE_PLAYER_PROGRESS: 'UPDATE_PLAYER_PROGRESS',
  UPDATE_STATION_STATUS: 'UPDATE_STATION_STATUS',
  SET_GAME_OVER: 'SET_GAME_OVER',
  SET_WAITING_INFO: 'SET_WAITING_INFO',
  RESET_GAME: 'RESET_GAME',
  SET_TOTAL_STATIONS: 'SET_TOTAL_STATIONS',
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

    case ActionTypes.SET_PLAYERS:
      return {
        ...state,
        players: action.payload,
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

    case ActionTypes.UPDATE_REVEALED:
      return {
        ...state,
        revealed: action.payload,
      };

    case ActionTypes.UPDATE_ATTEMPTS:
      return {
        ...state,
        attemptsLeft: action.payload,
      };

    case ActionTypes.ADD_GUESSED_LETTER:
      return {
        ...state,
        guessedLetters: new Set([...state.guessedLetters, action.payload.toUpperCase()]),
      };

    case ActionTypes.SET_LAST_GUESS:
      return {
        ...state,
        lastGuess: action.payload,
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
        playersInQueue: action.payload.count,
        waitingMessage: action.payload.message,
      };

    case ActionTypes.SET_TOTAL_STATIONS:
      return {
        ...state,
        totalStations: action.payload,
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
      }
    });
  }, [subscribe]);

  // Handle waiting message
  useEffect(() => {
    return subscribe('waiting', (data) => {
      dispatch({ type: ActionTypes.SET_GAME_STATE, payload: GameState.WAITING });
      dispatch({
        type: ActionTypes.SET_WAITING_INFO,
        payload: { count: data.players_in_queue, message: data.message },
      });
    });
  }, [subscribe]);

  // Handle game start
  useEffect(() => {
    return subscribe('game_start', (data) => {
      dispatch({ type: ActionTypes.SET_GAME_STATE, payload: GameState.PLAYING });
      dispatch({
        type: ActionTypes.SET_PLAYERS,
        payload: data.players.map(p => ({ ...p, station: 1 })),
      });
      dispatch({ type: ActionTypes.SET_TOTAL_STATIONS, payload: data.total_stations });
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
      dispatch({ type: ActionTypes.ADD_GUESSED_LETTER, payload: data.letter });
      dispatch({ type: ActionTypes.UPDATE_REVEALED, payload: data.revealed });
      dispatch({ type: ActionTypes.SET_LAST_GUESS, payload: { letter: data.letter, correct: true } });
    });
  }, [subscribe]);

  // Handle wrong guess
  useEffect(() => {
    return subscribe('wrong_guess', (data) => {
      dispatch({ type: ActionTypes.ADD_GUESSED_LETTER, payload: data.letter });
      dispatch({ type: ActionTypes.UPDATE_ATTEMPTS, payload: data.attempts_left });
      dispatch({ type: ActionTypes.SET_LAST_GUESS, payload: { letter: data.letter, correct: false } });
    });
  }, [subscribe]);

  // Handle station complete
  useEffect(() => {
    return subscribe('station_complete', (data) => {
      // Station update will follow with new station info
      console.log(`Station ${data.station} complete! Word was: ${data.word}`);
    });
  }, [subscribe]);

  // Handle station failed
  useEffect(() => {
    return subscribe('station_failed', (data) => {
      console.log(`Station failed! Word was: ${data.word}. Resetting to station ${data.reset_to}`);
    });
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
    return subscribe('error', (data) => {
      console.error('Game error:', data.message);
    });
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

  const value = {
    // State
    ...state,
    isConnected,

    // Actions
    joinGame,
    guessLetter,
    leaveGame,
    resetGame,
  };

  return (
    <GameContext.Provider value={value}>
      {children}
    </GameContext.Provider>
  );
}

export function useGame() {
  const context = useContext(GameContext);
  if (!context) {
    throw new Error('useGame must be used within a GameProvider');
  }
  return context;
}

export default GameContext;
