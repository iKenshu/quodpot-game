import { useEffect, useCallback, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useGameState, useGameActions } from '../../context/GameContext';
import WordDisplay from './WordDisplay';
import Keyboard from './Keyboard';
import QuodBall from './QuodBall';
import '../../styles/components/game.css';

// Función para obtener el nombre del sello
const getSealName = (stationNumber, totalStations) => {
  if (stationNumber === totalStations) {
    return 'Sello Final';
  }

  const ordinals = {
    1: 'Primer',
    2: 'Segundo',
    3: 'Tercer',
    4: 'Cuarto',
    5: 'Quinto',
    6: 'Sexto',
    7: 'Séptimo',
    8: 'Octavo',
    9: 'Noveno',
    10: 'Décimo',
  };

  const ordinal = ordinals[stationNumber] || `${stationNumber}°`;
  return `${ordinal} Sello`;
};

export function HangmanGame() {
  const {
    currentStation,
    totalStations,
    revealed,
    attemptsLeft,
    guessedLetters,
    lastGuess,
  } = useGameState();
  const { guessLetter } = useGameActions();

  const sealName = useMemo(
    () => getSealName(currentStation, totalStations),
    [currentStation, totalStations]
  );

  useEffect(() => {
    const handleKeyDown = (e) => {
      const letter = e.key.toUpperCase();
      if (/^[A-ZÑ]$/.test(letter) && !guessedLetters.has(letter)) {
        guessLetter(letter);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [guessLetter, guessedLetters]);

  const handleKeyPress = useCallback(
    (letter) => {
      guessLetter(letter);
    },
    [guessLetter]
  );

  return (
    <main className="game-area">
      {/* Magical mist layer for extra depth */}
      <div className="stars-layer-3" aria-hidden="true" />

      <div className="station-header">
        <motion.div
          className="station-badge"
          key={currentStation}
          initial={{ scale: 0, rotate: -10 }}
          animate={{ scale: 1, rotate: 0 }}
          transition={{ type: 'spring', stiffness: 300, damping: 20 }}
        >
          {sealName}
        </motion.div>
      </div>

      <div className="hangman-container">
        <QuodBall attemptsLeft={attemptsLeft} />

        <WordDisplay revealed={revealed} />

        <Keyboard
          onKeyPress={handleKeyPress}
          guessedLetters={guessedLetters}
          revealed={revealed}
          disabled={attemptsLeft <= 0}
        />
      </div>

      <AnimatePresence>
        {lastGuess && (
          <motion.div
            className={`feedback-message feedback-message--${lastGuess.correct ? 'correct' : 'wrong'}`}
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
          >
            {lastGuess.correct ? '¡Correcto!' : '¡Incorrecto!'}
          </motion.div>
        )}
      </AnimatePresence>
    </main>
  );
}

export default HangmanGame;
