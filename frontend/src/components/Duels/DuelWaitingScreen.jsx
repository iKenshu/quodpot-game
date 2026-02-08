import PropTypes from 'prop-types';
import '../../styles/games/duels/duels.css';

export default function DuelWaitingScreen({ playerName, playersInQueue }) {
  const getInitial = (name) => name ? name.charAt(0).toUpperCase() : '?';

  return (
    <div className="duel-waiting-screen">
      <h2
        style={{
          fontFamily: 'var(--font-display)',
          fontSize: '2rem',
          color: 'var(--accent-light)',
          marginBottom: 'var(--space-md)',
        }}
      >
        Buscando Contrincante...
      </h2>

      <div className="duel-spinner"></div>

      <p
        style={{
          fontFamily: 'var(--font-body)',
          fontSize: '1.1rem',
          color: 'var(--star-blue)',
          marginBottom: 'var(--space-xl)',
        }}
      >
        Duelistas en cola: {playersInQueue}
      </p>

      <div className="duel-player-avatar">
        {getInitial(playerName)}
      </div>

      <p
        style={{
          fontFamily: 'var(--font-body)',
          fontSize: '1.2rem',
          color: 'var(--star-white)',
          marginTop: 'var(--space-md)',
        }}
      >
        {playerName}
      </p>
    </div>
  );
}

DuelWaitingScreen.propTypes = {
  playerName: PropTypes.string.isRequired,
  playersInQueue: PropTypes.number,
};
