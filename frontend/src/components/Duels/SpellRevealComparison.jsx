import { useEffect, useState, useRef } from 'react';
import PropTypes from 'prop-types';
import '../../styles/games/duels/duels.css';

const SPELL_DATA = {
  ignis: { icon: '🔥', name: 'IGNIS', defeats: 'virel' },
  aqua: { icon: '💧', name: 'AQUA', defeats: 'ignis' },
  virel: { icon: '🌿', name: 'VIREL', defeats: 'aqua' },
};

const STAGE_DURATION = {
  suspense: 600,
  reveal: 1000,
  result: 1400,
};

export default function SpellRevealComparison({
  playerSpell,
  opponentSpell,
  result,
  onComplete,
}) {
  const [stage, setStage] = useState('suspense');
  const onCompleteRef = useRef(onComplete);

  useEffect(() => {
    onCompleteRef.current = onComplete;
  }, [onComplete]);

  useEffect(() => {
    const totalDuration = STAGE_DURATION.suspense + STAGE_DURATION.reveal + STAGE_DURATION.result;

    const timers = [
      setTimeout(() => setStage('reveal'), STAGE_DURATION.suspense),
      setTimeout(() => setStage('result'), STAGE_DURATION.suspense + STAGE_DURATION.reveal),
      setTimeout(() => {
        if (onCompleteRef.current) onCompleteRef.current();
      }, totalDuration),
    ];

    return () => timers.forEach(clearTimeout);
  }, []);

  const playerData = SPELL_DATA[playerSpell];
  const opponentData = SPELL_DATA[opponentSpell];

  const getVersusContent = () => {
    if (result === 'tie') {
      return {
        symbol: '=',
        text: 'Empate',
      };
    }
    return {
      symbol: result === 'win' ? '>' : '<',
      text: result === 'win' ? 'vence a' : 'pierde ante',
    };
  };

  const getResultMessage = () => {
    if (result === 'win') return 'Victoria';
    if (result === 'lose') return 'Derrota';
    return 'Empate';
  };

  const versusContent = getVersusContent();

  return (
    <div className={`spell-reveal-comparison stage-${stage} result-${result}`}>
      <div className="spell-matchup">
        <div className={`spell-reveal-card player ${stage !== 'suspense' ? 'revealed' : ''}`}>
          <div className="spell-reveal-icon">{playerData.icon}</div>
          <div className="spell-reveal-name">{playerData.name}</div>
          {stage === 'result' && <div className="spell-label">Tu hechizo</div>}
        </div>

        <div className="versus-indicator">
          {stage === 'suspense' && <div className="versus-symbol">VS</div>}
          {(stage === 'reveal' || stage === 'result') && (
            <div className="versus-content">
              <div className="versus-symbol-large">{versusContent.symbol}</div>
              <div className="versus-label">{versusContent.text}</div>
            </div>
          )}
        </div>

        <div className={`spell-reveal-card opponent ${stage !== 'suspense' ? 'revealed' : ''}`}>
          <div className="spell-reveal-icon">{opponentData.icon}</div>
          <div className="spell-reveal-name">{opponentData.name}</div>
          {stage === 'result' && <div className="spell-label">Oponente</div>}
        </div>
      </div>

      {stage === 'result' && (
        <div className="round-result-badge">
          {getResultMessage()}
        </div>
      )}
    </div>
  );
}

SpellRevealComparison.propTypes = {
  playerSpell: PropTypes.oneOf(['ignis', 'aqua', 'virel']).isRequired,
  opponentSpell: PropTypes.oneOf(['ignis', 'aqua', 'virel']).isRequired,
  result: PropTypes.oneOf(['win', 'lose', 'tie']).isRequired,
  onComplete: PropTypes.func,
};
