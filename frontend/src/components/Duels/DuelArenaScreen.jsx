import { useState, useEffect, useRef } from 'react';
import PropTypes from 'prop-types';
import { useGameState } from '../../context/GameContext';
import DuelPlayer from './DuelPlayer';
import VSBadge from './VSBadge';
import SpellDuelArena from './SpellDuelArena';
import SpellRevealComparison from './SpellRevealComparison';
import '../../styles/games/duels/duels.css';

export default function DuelArenaScreen({
  player,
  opponent,
  round,
  onSpellSelect,
  playerSpell,
  opponentSpell,
  roundResult,
  playerScore,
  opponentScore,
}) {
  const { duel } = useGameState();
  const isPVE = duel.mode === 'pve';
  const [vsBadgeState, setVsBadgeState] = useState('waiting');
  const [displayResult, setDisplayResult] = useState(null);
  const [revealData, setRevealData] = useState(null);
  const hasShownReveal = useRef(false);

  useEffect(() => {
    if (roundResult && playerSpell && opponentSpell && opponentSpell !== 'pending' && !hasShownReveal.current) {
      hasShownReveal.current = true;
      setRevealData({
        playerSpell,
        opponentSpell,
        result: roundResult,
      });
    }
  }, [roundResult, playerSpell, opponentSpell]);

  useEffect(() => {
    if (!roundResult) {
      hasShownReveal.current = false;
    }
  }, [roundResult]);

  useEffect(() => {
    if (roundResult) {
      setVsBadgeState('revealing');
      const revealTimer = setTimeout(() => {
        setVsBadgeState('result');
        setDisplayResult(roundResult);
      }, 1000);

      return () => clearTimeout(revealTimer);
    } else if (playerSpell && opponentSpell) {
      setVsBadgeState('ready');
    } else {
      setVsBadgeState('waiting');
      setDisplayResult(null);
    }
  }, [playerSpell, opponentSpell, roundResult]);

  const playerStatus = roundResult ? 'revealed' : (!playerSpell ? 'choosing' : 'ready');

  const getOpponentStatus = () => {
    if (roundResult) return 'revealed';
    if (opponentSpell === 'pending') return 'ready';
    if (!opponentSpell) return 'choosing';
    return 'revealed';
  };

  const opponentStatus = getOpponentStatus();

  const isPlayerActive = playerSpell && !opponentSpell;
  const isOpponentActive = opponentSpell && !playerSpell;

  return (
    <div className="duel-arena-screen">
      <div className="duel-arena-header">
        <div className="duel-round-info">
          Ronda {round.current}/{round.total}
        </div>
        {isPVE && (
          <div style={{
            fontSize: '0.85rem',
            color: 'var(--accent-muted)',
            fontFamily: 'var(--font-body)',
            display: 'flex',
            alignItems: 'center',
            gap: '4px'
          }}>
            <span>⚔️</span> Modo Entrenamiento
          </div>
        )}
      </div>

      <div className="duel-players-compact">
        <div className="compact-player-info">
          <DuelPlayer
            player={player}
            score={playerScore}
            status={playerStatus === 'revealed' ? 'ready' : playerStatus}
            isActive={isPlayerActive}
          />
        </div>

        <VSBadge
          state={vsBadgeState}
          playerSpell={playerSpell}
          opponentSpell={opponentSpell}
          result={displayResult}
        />

        <div className="compact-player-info">
          <DuelPlayer
            player={opponent}
            score={opponentScore}
            status={opponentStatus}
            isActive={isOpponentActive}
          />
        </div>
      </div>

      <div style={{ marginTop: 'var(--space-xl)' }}>
        <SpellDuelArena
          playerSpell={playerSpell}
          opponentSpell={opponentSpell}
          playerStatus={playerStatus}
          opponentStatus={opponentStatus}
          roundResult={roundResult}
          disabled={!!playerSpell}
          onSpellSelect={onSpellSelect}
        />
      </div>

      {revealData && (
        <SpellRevealComparison
          playerSpell={revealData.playerSpell}
          opponentSpell={revealData.opponentSpell}
          result={revealData.result}
          onComplete={() => setRevealData(null)}
        />
      )}
    </div>
  );
}

DuelArenaScreen.propTypes = {
  player: PropTypes.shape({
    id: PropTypes.string,
    name: PropTypes.string,
  }).isRequired,
  opponent: PropTypes.shape({
    id: PropTypes.string,
    name: PropTypes.string,
  }).isRequired,
  round: PropTypes.shape({
    current: PropTypes.number.isRequired,
    total: PropTypes.number.isRequired,
  }).isRequired,
  onSpellSelect: PropTypes.func.isRequired,
  playerSpell: PropTypes.string,
  opponentSpell: PropTypes.string,
  roundResult: PropTypes.oneOf(['win', 'lose', 'tie']),
  playerScore: PropTypes.arrayOf(PropTypes.string).isRequired,
  opponentScore: PropTypes.arrayOf(PropTypes.string).isRequired,
};
