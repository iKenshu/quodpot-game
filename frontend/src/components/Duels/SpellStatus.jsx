import PropTypes from 'prop-types';
import '../../styles/games/duels/duels.css';

export default function SpellStatus({ status, side = 'player' }) {
  const getStatusText = () => {
    if (status === 'choosing') {
      return side === 'player' ? 'Eligiendo...' : 'Eligiendo...';
    }
    if (status === 'ready') {
      return '✓ Elegido';
    }
    if (status === 'revealed') {
      return '';
    }
    return '';
  };

  const statusClass = `spell-status ${status}`;

  return (
    <div className={statusClass} role="status" aria-live="polite">
      {getStatusText()}
    </div>
  );
}

SpellStatus.propTypes = {
  status: PropTypes.oneOf(['choosing', 'ready', 'revealed']).isRequired,
  side: PropTypes.oneOf(['player', 'opponent']),
};
