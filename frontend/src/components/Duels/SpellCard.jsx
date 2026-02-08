import PropTypes from 'prop-types';
import '../../styles/games/duels/duels.css';

const SPELL_DATA = {
  ignis: {
    icon: '⟡',
    name: 'IGNIS',
    element: 'Fuego',
    color: 'ignis',
  },
  aqua: {
    icon: '⟡',
    name: 'AQUA',
    element: 'Agua',
    color: 'aqua',
  },
  virel: {
    icon: '⟡',
    name: 'VIREL',
    element: 'Naturaleza',
    color: 'virel',
  },
};

export default function SpellCard({ spell, selected, disabled, onClick, variant = 'normal', result }) {
  const data = SPELL_DATA[spell];

  const handleClick = () => {
    if (!disabled && !selected && variant === 'normal') {
      onClick?.(spell);
    }
  };

  const handleKeyDown = (e) => {
    if ((e.key === 'Enter' || e.key === ' ') && !disabled && !selected && variant === 'normal') {
      e.preventDefault();
      onClick?.(spell);
    }
  };

  if (variant === 'mystery') {
    return (
      <div className="spell-card mystery" role="presentation">
        <div className="spell-card-icon mystery-icon">?</div>
        <div className="spell-card-info">
          <div className="spell-card-name">Misterio</div>
        </div>
      </div>
    );
  }

  const resultClass = result ? `result-${result}` : '';

  return (
    <div
      className={`spell-card ${data.color} ${selected ? 'selected' : ''} ${disabled ? 'disabled' : ''} ${resultClass}`}
      role="button"
      tabIndex={disabled ? -1 : 0}
      onClick={handleClick}
      onKeyDown={handleKeyDown}
      aria-label={`Hechizo ${data.name}. ${data.element}. ${selected ? 'Seleccionado' : 'Presiona Enter para seleccionar'}`}
      aria-pressed={selected}
      aria-disabled={disabled}
    >
      <div className="spell-card-icon">{data.icon}</div>
      <div className="spell-card-info">
        <div className="spell-card-name">{data.name}</div>
        <div className="spell-card-element">{data.element}</div>
      </div>
    </div>
  );
}

SpellCard.propTypes = {
  spell: PropTypes.oneOf(['ignis', 'aqua', 'virel']).isRequired,
  selected: PropTypes.bool,
  disabled: PropTypes.bool,
  onClick: PropTypes.func,
  variant: PropTypes.oneOf(['normal', 'mystery']),
  result: PropTypes.oneOf(['win', 'lose', 'tie']),
};
