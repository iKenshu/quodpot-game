import { GameProvider, useGame, GameState } from './context/GameContext';
import { JoinScreen, WaitingScreen } from './components/Screens';
import { GameLayout } from './components/Layout';

function GameRouter() {
  const { gameState } = useGame();

  switch (gameState) {
    case GameState.IDLE:
    case GameState.JOINING:
      return <JoinScreen />;

    case GameState.WAITING:
      return <WaitingScreen />;

    case GameState.PLAYING:
    case GameState.GAME_OVER:
      return <GameLayout />;

    default:
      return <JoinScreen />;
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
