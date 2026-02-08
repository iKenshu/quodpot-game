import PropTypes from 'prop-types';
import SpellCard from './SpellCard';
import OpponentSpellDisplay from './OpponentSpellDisplay';
import SpellStatus from './SpellStatus';
import '../../styles/games/duels/duels.css';

const AVAILABLE_SPELLS = ['ignis', 'aqua', 'virel'];

export default function SpellDuelArena({
  playerSpell,
  opponentSpell,
  playerStatus,
  opponentStatus,
  roundResult,
  disabled,
  onSpellSelect,
}) {
  const getVSState = () => {
    if (roundResult) return 'result';
    const hasValidOpponentSpell = opponentSpell && opponentSpell !== 'pending';
    if (playerSpell && hasValidOpponentSpell) return 'ready';
    if (playerSpell || opponentSpell === 'pending') return 'waiting';
    return 'waiting';
  };

  const vsState = getVSState();

  return (
    <div className="spell-duel-arena">
      <div className="patronus-mist" aria-hidden="true"></div>

      <div className="spell-arena-player-side">
        <h3>TUS HECHIZOS</h3>
        <div className="spell-list" role="group" aria-label="Tus hechizos disponibles">
          {AVAILABLE_SPELLS.map((spell) => (
            <SpellCard
              key={spell}
              spell={spell}
              selected={playerSpell === spell}
              disabled={disabled || (playerSpell !== null && playerSpell !== spell)}
              onClick={onSpellSelect}
              result={playerSpell === spell && roundResult ? roundResult : undefined}
            />
          ))}
        </div>
        <SpellStatus status={playerStatus} side="player" />
      </div>

      <div className="spell-arena-vs-divider">
        <div className={`vs-icon ${vsState}`} aria-label="Versus">
          ⚚
        </div>
      </div>

      <div className="spell-arena-opponent-side">
        <h3>OPONENTE</h3>
        <OpponentSpellDisplay
          opponentSpell={opponentSpell}
          opponentStatus={opponentStatus}
          result={roundResult}
        />
        <SpellStatus status={opponentStatus} side="opponent" />
      </div>
    </div>
  );
}

SpellDuelArena.propTypes = {
  playerSpell: PropTypes.string,
  opponentSpell: PropTypes.string,
  playerStatus: PropTypes.oneOf(['choosing', 'ready', 'revealed']).isRequired,
  opponentStatus: PropTypes.oneOf(['choosing', 'ready', 'revealed']).isRequired,
  roundResult: PropTypes.oneOf(['win', 'lose', 'tie']),
  disabled: PropTypes.bool,
  onSpellSelect: PropTypes.func.isRequired,
};
