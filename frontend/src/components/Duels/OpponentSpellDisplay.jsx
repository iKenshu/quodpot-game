import PropTypes from 'prop-types';
import '../../styles/games/duels/duels.css';

const SPELL_DATA = {
  ignis: {
    icon: '⟡',
    name: 'IGNIS',
    element: 'Fuego',
  },
  aqua: {
    icon: '⟡',
    name: 'AQUA',
    element: 'Agua',
  },
  virel: {
    icon: '⟡',
    name: 'VIREL',
    element: 'Naturaleza',
  },
};

export default function OpponentSpellDisplay({ opponentSpell, opponentStatus, result }) {
  if (opponentStatus === 'choosing') {
    return (
      <div className="opponent-spell-card choosing">
        <div className="opponent-rune">⚚</div>
        <div className="opponent-spell-text">Eligiendo hechizo...</div>
      </div>
    );
  }

  if (opponentStatus === 'ready') {
    return (
      <div className="opponent-spell-card ready">
        <div className="card-back-ornament">✦</div>
        <div className="opponent-spell-text">¡Tu oponente está listo!</div>
      </div>
    );
  }

  if (opponentSpell && opponentSpell !== 'pending' && opponentStatus === 'revealed') {
    const spellData = SPELL_DATA[opponentSpell];
    const resultClass = result ? `result-${result}` : '';

    return (
      <div className={`opponent-spell-card revealed ${resultClass}`}>
        <div className="opponent-spell-revealed-content">
          <div className="spell-card-icon">{spellData.icon}</div>
          <div className="spell-card-info">
            <div className="spell-card-name">{spellData.name}</div>
            <div className="spell-card-element">{spellData.element}</div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="opponent-spell-card choosing">
      <div className="opponent-rune">⚚</div>
      <div className="opponent-spell-text">Esperando...</div>
    </div>
  );
}

OpponentSpellDisplay.propTypes = {
  opponentSpell: PropTypes.string,
  opponentStatus: PropTypes.oneOf(['choosing', 'ready', 'revealed']).isRequired,
  result: PropTypes.oneOf(['win', 'lose', 'tie']),
};
