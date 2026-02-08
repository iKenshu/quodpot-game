import PropTypes from 'prop-types';
import '../../styles/games/duels/duels.css';

const SPELL_ICONS = {
  ignis: '🔥',
  aqua: '💧',
  virel: '🌿',
};

const SPELL_NAMES = {
  ignis: 'IGNIS',
  aqua: 'AQUA',
  virel: 'VIREL',
};

export default function VSBadge({ state, playerSpell, opponentSpell, result }) {
  const getBadgeClass = () => {
    if (result) {
      if (result === 'win') return 'result-win';
      if (result === 'lose') return 'result-lose';
      if (result === 'tie') return 'result-tie';
    }
    if (state === 'revealing') return 'revealing';
    if (state === 'ready') return 'ready';
    return 'waiting';
  };

  const renderContent = () => {
    // Initial state - just VS
    if (state === 'waiting') {
      return (
        <div className="vs-text">
          ⚔️ VS
        </div>
      );
    }

    // Ready state - both players chose, building suspense
    if (state === 'ready') {
      return (
        <div className="vs-text">
          ⚔️ VS
        </div>
      );
    }

    // Revealing or result state - show spells
    if (state === 'revealing' || result) {
      return (
        <>
          {opponentSpell && (
            <div className="vs-spell top">
              {SPELL_ICONS[opponentSpell]} {SPELL_NAMES[opponentSpell]}
            </div>
          )}
          <div className="vs-clash-icon">⚡</div>
          {playerSpell && (
            <div className="vs-spell bottom">
              {SPELL_ICONS[playerSpell]} {SPELL_NAMES[playerSpell]}
            </div>
          )}
          {result && (
            <div className="vs-result-text">
              {result === 'win' && '¡VICTORIA!'}
              {result === 'lose' && 'DERROTA'}
              {result === 'tie' && 'EMPATE'}
            </div>
          )}
        </>
      );
    }

    return null;
  };

  return (
    <div className="vs-badge-container">
      <div className={`vs-badge ${getBadgeClass()}`}>
        {renderContent()}
      </div>
    </div>
  );
}

VSBadge.propTypes = {
  state: PropTypes.oneOf(['waiting', 'ready', 'revealing', 'result']).isRequired,
  playerSpell: PropTypes.string,
  opponentSpell: PropTypes.string,
  result: PropTypes.oneOf(['win', 'lose', 'tie']),
};
