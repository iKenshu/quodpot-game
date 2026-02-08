import PropTypes from 'prop-types';
import '../../styles/games/duels/duels.css';

const SPELL_ICONS = {
  ignis: '🔥',
  aqua: '💧',
  virel: '🌿',
};

export default function ScoreDisplay({ score, maxRounds = 3 }) {
  const orbs = [];

  for (let i = 0; i < maxRounds; i++) {
    const wonRound = score[i];
    orbs.push(
      <div
        key={i}
        className={`score-orb ${wonRound ? 'won' : 'empty'}`}
        aria-label={wonRound ? `Round ${i + 1} won with ${wonRound}` : `Round ${i + 1} not won`}
      >
        {wonRound && SPELL_ICONS[wonRound]}
        {!wonRound && '⚪'}
      </div>
    );
  }

  return <div className="score-display">{orbs}</div>;
}

ScoreDisplay.propTypes = {
  score: PropTypes.arrayOf(PropTypes.string),
  maxRounds: PropTypes.number,
};
