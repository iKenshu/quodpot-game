import { useEffect, useState } from 'react';
import { useGameState, useGameActions, GameState } from '../../context/GameContext';
import DuelJoinScreen from './DuelJoinScreen';
import DuelWaitingScreen from './DuelWaitingScreen';
import DuelArenaScreen from './DuelArenaScreen';
import DuelResultScreen from './DuelResultScreen';
import '../../styles/games/duels/duels.css';

export default function DuelsGame() {
  const { gameState, playerId, playerName, playersInQueue, duel, winner } = useGameState();
  const { joinGame, castSpell, requestRematch, leaveGame } = useGameActions();

  const handleJoin = (name, mode = 'pvp') => {
    joinGame(name, 'duels', mode);
  };

  const handleSpellSelect = (spell) => {
    castSpell(spell);
  };

  const handleRematch = () => {
    requestRematch();
  };

  const handleExit = () => {
    leaveGame();
  };

  // Render based on game state
  if (gameState === GameState.IDLE || gameState === GameState.JOINING) {
    return <DuelJoinScreen onJoin={handleJoin} />;
  }

  if (gameState === GameState.WAITING) {
    return (
      <DuelWaitingScreen
        playerName={playerName}
        playersInQueue={playersInQueue}
      />
    );
  }

  if (gameState === GameState.PLAYING) {
    return (
      <DuelArenaScreen
        player={{ id: playerId, name: playerName }}
        opponent={duel.opponent || { id: null, name: 'Oponente' }}
        round={{
          current: duel.currentRound,
          total: duel.totalRounds,
        }}
        onSpellSelect={handleSpellSelect}
        playerSpell={duel.playerSpell}
        opponentSpell={duel.opponentSpell}
        roundResult={duel.roundResult}
        playerScore={duel.playerScore}
        opponentScore={duel.opponentScore}
      />
    );
  }

  if (gameState === GameState.GAME_OVER) {
    const isVictory = duel.isWinner;
    const finalScore = {
      player: duel.playerScore.length,
      opponent: duel.opponentScore.length,
    };

    return (
      <DuelResultScreen
        isVictory={isVictory}
        winner={winner || duel.opponent}
        finalScore={finalScore}
        rounds={duel.roundHistory}
        onRematch={handleRematch}
        onExit={handleExit}
      />
    );
  }

  return null;
}
