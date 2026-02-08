import PropTypes from 'prop-types';
import '../../styles/games/duels/duels.css';

const SPELL_ICONS = {
  ignis: '🔥',
  aqua: '💧',
  virel: '🌿',
};

export default function RoundHistory({ rounds }) {
  if (!rounds || rounds.length === 0) {
    return null;
  }

  return (
    <div className="round-history">
      <h3 className="round-history-title">Hechizos Usados:</h3>
      {rounds.map((round, index) => (
        <div key={index} className="round-history-item">
          Ronda {index + 1}: {SPELL_ICONS[round.player]} vs{' '}
          {SPELL_ICONS[round.opponent]} → Ganó{' '}
          {round.winner === 'player' ? 'Tú' : round.winner === 'opponent' ? 'Oponente' : 'Empate'}
        </div>
      ))}
    </div>
  );
}

RoundHistory.propTypes = {
  rounds: PropTypes.arrayOf(
    PropTypes.shape({
      player: PropTypes.string.isRequired,
      opponent: PropTypes.string.isRequired,
      winner: PropTypes.oneOf(['player', 'opponent', 'tie']).isRequired,
    })
  ),
};
