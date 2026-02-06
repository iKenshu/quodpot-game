import { useState } from 'react';
import { motion } from 'framer-motion';
import { useGameState, useGameActions } from '../../context/GameContext';
import '../../styles/components/screens.css';

export function JoinScreen() {
  const [playerName, setPlayerName] = useState('');
  const { isConnected } = useGameState();
  const { joinGame } = useGameActions();

  const handleSubmit = (e) => {
    e.preventDefault();
    if (playerName.trim() && isConnected) {
      joinGame(playerName.trim());
    }
  };

  return (
    <div className="screen join-screen">
      <motion.div
        className="join-card"
        initial={{ opacity: 0, y: 20, scale: 0.95 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.5, ease: 'easeOut' }}
      >
        <div className="game-logo">
          <motion.h1
            className="game-title"
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            La Quod Inestable
          </motion.h1>
          <motion.p
            className="game-subtitle"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4 }}
          >
            Sella cada nivel antes de que explote
          </motion.p>
        </div>

        <motion.form
          className="join-form"
          onSubmit={handleSubmit}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
        >
          <div className="input-group">
            <label className="input-label" htmlFor="playerName">
              Tu nombre de aventurero
            </label>
            <input
              id="playerName"
              type="text"
              className="input-field"
              placeholder="Ingresa tu nombre..."
              value={playerName}
              onChange={(e) => setPlayerName(e.target.value)}
              maxLength={20}
              autoComplete="off"
              autoFocus
            />
          </div>

          <motion.button
            type="submit"
            className="join-button"
            disabled={!playerName.trim() || !isConnected}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            {isConnected ? 'Estabilizar la Quod' : 'Conectando...'}
          </motion.button>
        </motion.form>

        {!isConnected && (
          <motion.p
            style={{ marginTop: '1rem', fontSize: '0.85rem', color: 'var(--blood-red)' }}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
          >
            Conectando al servidor...
          </motion.p>
        )}
      </motion.div>
    </div>
  );
}

export default JoinScreen;
