import { motion, AnimatePresence } from 'framer-motion';
import { useGameState, useGameActions, GameState } from '../../context/GameContext';
import '../../styles/components/screens.css';

export function GameOverOverlay() {
  const { gameState, winner, playerId, completedWords } = useGameState();
  const { resetGame } = useGameActions();

  const isVisible = gameState === GameState.GAME_OVER;
  const isWinner = winner?.id === playerId;

  const handlePlayAgain = () => {
    resetGame();
  };

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          className="game-over-overlay"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.3 }}
        >
          <motion.div
            className="game-over-card"
            initial={{ opacity: 0, y: 50, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 50, scale: 0.9 }}
            transition={{ delay: 0.2, type: 'spring', stiffness: 200, damping: 20 }}
          >
            <motion.h2
              className="game-over-title"
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
            >
              {isWinner ? '¡Quod Estabilizada!' : 'La Quod Explotó'}
            </motion.h2>

            <motion.div
              className="winner-section"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.5 }}
            >
              <p className="winner-label">
                {isWinner ? '¡Completaste todos los sellos!' : 'Estabilizador'}
              </p>
              <p className={`winner-name ${isWinner ? 'winner-name--self' : ''}`}>
                {winner?.name || 'Desconocido'}
              </p>
            </motion.div>

            {completedWords && completedWords.length > 0 && (
              <motion.div
                className="completed-words"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.6 }}
              >
                <p className="completed-words-title">Sellos completados</p>
                <div className="words-list">
                  {completedWords.map((word, index) => (
                    <motion.span
                      key={index}
                      className="word-chip"
                      initial={{ opacity: 0, scale: 0 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: 0.7 + index * 0.05 }}
                    >
                      {word}
                    </motion.span>
                  ))}
                </div>
              </motion.div>
            )}

            <motion.button
              className="play-again-button"
              onClick={handlePlayAgain}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.8 }}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              Jugar de nuevo
            </motion.button>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

export default GameOverOverlay;
