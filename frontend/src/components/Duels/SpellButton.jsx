import PropTypes from 'prop-types';
import '../../styles/games/duels/duels.css';

const SPELL_DATA = {
  ignis: {
    icon: '🔥',
    name: 'Ignis',
    element: 'Fuego',
  },
  aqua: {
    icon: '💧',
    name: 'Aqua',
    element: 'Agua',
  },
  virel: {
    icon: '🌿',
    name: 'Virel',
    element: 'Naturaleza',
  },
};

export default function SpellButton({ spell, selected, disabled, onClick }) {
  const data = SPELL_DATA[spell];

  const handleClick = () => {
    if (!disabled && !selected) {
      onClick(spell);
    }
  };

  const handleKeyDown = (e) => {
    if ((e.key === 'Enter' || e.key === ' ') && !disabled && !selected) {
      e.preventDefault();
      onClick(spell);
    }
  };

  return (
    <button
      className={`spell-button spell-${spell} ${selected ? 'selected' : ''}`}
      onClick={handleClick}
      onKeyDown={handleKeyDown}
      disabled={disabled}
      aria-label={`Select ${data.name} spell, ${data.element}, effective against ${getCounterSpell(spell)}`}
      aria-pressed={selected}
      tabIndex={disabled ? -1 : 0}
    >
      <div className="spell-icon">{data.icon}</div>
      <div className="spell-name">{data.name}</div>
      <div className="spell-element">{data.element}</div>
    </button>
  );
}

function getCounterSpell(spell) {
  const counters = {
    ignis: 'Virel',
    aqua: 'Ignis',
    virel: 'Aqua',
  };
  return counters[spell];
}

SpellButton.propTypes = {
  spell: PropTypes.oneOf(['ignis', 'aqua', 'virel']).isRequired,
  selected: PropTypes.bool,
  disabled: PropTypes.bool,
  onClick: PropTypes.func.isRequired,
};
