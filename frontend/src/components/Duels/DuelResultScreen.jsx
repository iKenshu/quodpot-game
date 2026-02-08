import PropTypes from 'prop-types';
import RoundHistory from './RoundHistory';
import '../../styles/games/duels/duels.css';

export default function DuelResultScreen({
  isVictory,
  winner,
  finalScore,
  rounds,
  onRematch,
  onExit,
}) {
  const getInitial = (name) => name ? name.charAt(0).toUpperCase() : '?';

  return (
    <div className="duel-result-screen">
      <div className="duel-result-card">
        <div className={`result-icon ${isVictory ? 'victory' : ''}`}>
          {isVictory ? '⭐' : '💀'}
        </div>

        <h1 className={`result-title ${isVictory ? 'victory' : 'defeat'}`}>
          {isVictory ? '¡VICTORIA!' : 'DERROTA'}
        </h1>
        <div className="winner-card">
          <div className="winner-avatar">
            {getInitial(winner.name)}
          </div>
          <div className="winner-name">{winner.name}</div>
          <div className="final-score">
            Score Final: {finalScore.player} - {finalScore.opponent}
          </div>
        </div>

        <RoundHistory rounds={rounds} />

        <div className="result-actions">
          <button className="result-button primary" onClick={onRematch}>
            Duelo de Revancha
          </button>
          <button className="result-button secondary" onClick={onExit}>
            Salir del Salón
          </button>
        </div>
      </div>
    </div>
  );
}

DuelResultScreen.propTypes = {
  isVictory: PropTypes.bool.isRequired,
  winner: PropTypes.shape({
    id: PropTypes.string,
    name: PropTypes.string,
  }).isRequired,
  finalScore: PropTypes.shape({
    player: PropTypes.number.isRequired,
    opponent: PropTypes.number.isRequired,
  }).isRequired,
  rounds: PropTypes.arrayOf(
    PropTypes.shape({
      player: PropTypes.string.isRequired,
      opponent: PropTypes.string.isRequired,
      winner: PropTypes.oneOf(['player', 'opponent', 'tie']).isRequired,
    })
  ),
  onRematch: PropTypes.func.isRequired,
  onExit: PropTypes.func.isRequired,
};
