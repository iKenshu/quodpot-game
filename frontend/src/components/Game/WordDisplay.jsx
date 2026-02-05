import { motion } from 'framer-motion';

export function WordDisplay({ revealed }) {
  // revealed is a string like "_ A _ _ O _" with spaces between letters
  const letters = revealed.split(' ');

  return (
    <div className="word-display">
      {letters.map((letter, index) => (
        <motion.div
          key={index}
          className={`letter-slot ${letter !== '_' ? 'letter-slot--revealed' : ''}`}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.05 }}
        >
          {letter !== '_' && (
            <motion.span
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: 'spring', stiffness: 500, damping: 25 }}
            >
              {letter}
            </motion.span>
          )}
        </motion.div>
      ))}
    </div>
  );
}

export default WordDisplay;
