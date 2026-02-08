import PropTypes from 'prop-types';
import ScoreDisplay from './ScoreDisplay';
import '../../styles/games/duels/duels.css';

export default function DuelPlayer({ player, score, status, isActive }) {
  const getInitial = (name) => name ? name.charAt(0).toUpperCase() : '?';

  const statusText = status === 'waiting'
    ? 'Esperando...'
    : status === 'choosing'
    ? 'Eligiendo...'
    : '¡Eligió!';

  return (
    <div className="player-info">
      <div className={`player-avatar ${isActive ? 'active' : ''}`}>
        {getInitial(player.name)}
      </div>
      <div className="player-name">{player.name || 'Jugador'}</div>
      <div className={`player-status ${status}`}>
        {statusText}
      </div>
      <ScoreDisplay score={score} />
    </div>
  );
}

DuelPlayer.propTypes = {
  player: PropTypes.shape({
    id: PropTypes.string,
    name: PropTypes.string,
  }).isRequired,
  score: PropTypes.arrayOf(PropTypes.string).isRequired,
  status: PropTypes.oneOf(['waiting', 'choosing', 'ready']).isRequired,
  isActive: PropTypes.bool,
};
