import { motion } from 'framer-motion';

const MAX_ATTEMPTS = 6;

export function AttemptsDisplay({ attemptsLeft }) {
  const attempts = Array.from({ length: MAX_ATTEMPTS }, (_, i) => i < attemptsLeft);

  return (
    <div className="attempts-display">
      <span className="attempts-label">Oportunidades</span>
      <div className="attempts-indicators">
        {attempts.map((available, index) => (
          <motion.div
            key={index}
            className={`attempt-dot ${available ? 'attempt-dot--available' : 'attempt-dot--lost'}`}
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: index * 0.05 }}
          />
        ))}
      </div>
    </div>
  );
}

export default AttemptsDisplay;
