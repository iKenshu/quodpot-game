import { motion } from 'framer-motion';
import { useGame } from '../../context/GameContext';
import '../../styles/components/screens.css';

export function WaitingScreen() {
  const { playersInQueue, waitingMessage, playerName } = useGame();

  return (
    <div className="screen waiting-screen">
      <motion.div
        className="waiting-card"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <motion.h2
          className="waiting-title"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
        >
          Bienvenido, {playerName}
        </motion.h2>

        <motion.div
          className="waiting-spinner"
          initial={{ opacity: 0, scale: 0 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.3 }}
        />

        <motion.p
          className="waiting-message"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
        >
          {waitingMessage || 'La Quod se desestabiliza...'}
        </motion.p>

        <motion.div
          className="waiting-count"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.5 }}
        >
          <span>Magos preparados:</span>
          <span className="waiting-count-number">{playersInQueue}</span>
        </motion.div>
      </motion.div>
    </div>
  );
}

export default WaitingScreen;
