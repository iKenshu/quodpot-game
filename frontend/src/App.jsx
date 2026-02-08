import { useEffect } from 'react';
import { GameProvider, useGameState, useGameActions, GameState } from './context/GameContext';
import { WaitingScreen } from './components/Screens';
import { GameLayout } from './components/Layout';
import GameSelector from './components/Screens/GameSelector';
import DuelsGame from './components/Duels/DuelsGame';

// Import new CSS architecture
import './styles/foundation/reset.css';
import './styles/foundation/variables.css';
import './styles/foundation/animations.css';
import './styles/foundation/utilities.css';
import './styles/themes/theme-base.css';
import './styles/themes/theme-hangman.css';
import './styles/themes/theme-duels.css';
import './styles/components/layout.css';
import './styles/components/sidebar.css';
import './styles/components/screens.css';
import './styles/games/hangman/hangman.css';

const THEME_MAP = {
  hangman: 'hangman',
  duels: 'duels',
};

function GameRouter() {
  const { gameState, gameType } = useGameState();
  const { joinGame } = useGameActions();

  useEffect(() => {
    const theme = THEME_MAP[gameType] || 'base';
    document.documentElement.setAttribute('data-theme', theme);
  }, [gameType]);

  const handleSelectGame = (selectedGameType, playerName, gameMode = 'pvp') => {
    joinGame(playerName, selectedGameType, gameMode);
  };

  if (gameState === GameState.IDLE) {
    return <GameSelector onSelectGame={handleSelectGame} />;
  }

  if (gameType === 'duels') {
    return <DuelsGame />;
  }

  if (gameState === GameState.JOINING) {
    return <WaitingScreen />;
  }

  switch (gameState) {
    case GameState.WAITING:
      return <WaitingScreen />;

    case GameState.PLAYING:
    case GameState.GAME_OVER:
      return <GameLayout />;

    default:
      return <GameSelector onSelectGame={handleSelectGame} />;
  }
}

function App() {
  return (
    <GameProvider>
      <GameRouter />
    </GameProvider>
  );
}

export default App;
