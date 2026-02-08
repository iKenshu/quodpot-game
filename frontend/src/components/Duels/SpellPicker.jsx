import PropTypes from 'prop-types';
import SpellButton from './SpellButton';
import '../../styles/games/duels/duels.css';

export default function SpellPicker({ selectedSpell, disabled, onSpellSelect }) {
  return (
    <div className="spell-picker">
      <SpellButton
        spell="ignis"
        selected={selectedSpell === 'ignis'}
        disabled={disabled}
        onClick={onSpellSelect}
      />
      <SpellButton
        spell="aqua"
        selected={selectedSpell === 'aqua'}
        disabled={disabled}
        onClick={onSpellSelect}
      />
      <SpellButton
        spell="virel"
        selected={selectedSpell === 'virel'}
        disabled={disabled}
        onClick={onSpellSelect}
      />
    </div>
  );
}

SpellPicker.propTypes = {
  selectedSpell: PropTypes.string,
  disabled: PropTypes.bool,
  onSpellSelect: PropTypes.func.isRequired,
};
