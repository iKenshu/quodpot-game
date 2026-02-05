import { useCallback } from 'react';
import { motion } from 'framer-motion';

const KEYBOARD_ROWS = [
  ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
  ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', 'Ñ'],
  ['Z', 'X', 'C', 'V', 'B', 'N', 'M'],
];

export function Keyboard({ onKeyPress, guessedLetters, revealed, disabled = false }) {
  // Determine key states
  const getKeyState = useCallback(
    (letter) => {
      if (!guessedLetters.has(letter)) {
        return 'unused';
      }

      // Check if letter is in the revealed word
      const revealedUpper = revealed.toUpperCase();
      if (revealedUpper.includes(letter)) {
        return 'correct';
      }

      return 'wrong';
    },
    [guessedLetters, revealed]
  );

  const handleKeyClick = useCallback(
    (letter) => {
      if (!disabled && !guessedLetters.has(letter)) {
        onKeyPress(letter);
      }
    },
    [disabled, guessedLetters, onKeyPress]
  );

  return (
    <div className="keyboard">
      {KEYBOARD_ROWS.map((row, rowIndex) => (
        <div key={rowIndex} className="keyboard-row">
          {row.map((letter) => {
            const state = getKeyState(letter);
            const isUsed = guessedLetters.has(letter);

            return (
              <motion.button
                key={letter}
                className={`key key--${state} ${isUsed ? 'key--used' : ''}`}
                onClick={() => handleKeyClick(letter)}
                disabled={disabled || isUsed}
                whileHover={!disabled && !isUsed ? { scale: 1.1 } : {}}
                whileTap={!disabled && !isUsed ? { scale: 0.95 } : {}}
              >
                {letter}
              </motion.button>
            );
          })}
        </div>
      ))}
    </div>
  );
}

export default Keyboard;
