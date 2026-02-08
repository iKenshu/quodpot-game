import { useState } from 'react';
import PropTypes from 'prop-types';
// CSS is now imported globally in App.jsx

export default function GameSelector({ onSelectGame }) {
  const [selectedGame, setSelectedGame] = useState(null);
  const [playerName, setPlayerName] = useState('');
  const [gameMode, setGameMode] = useState('pvp');

  const handleGameSelect = (gameType) => {
    setSelectedGame(gameType);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (playerName.trim() && selectedGame) {
      onSelectGame(selectedGame, playerName.trim(), gameMode);
    }
  };

  return (
    <div className="duel-join-screen">
      <h1
        style={{
          fontFamily: 'var(--font-display)',
          fontSize: '3rem',
          color: 'var(--accent-light)',
          textShadow: '0 0 20px var(--accent-primary)',
          marginBottom: 'var(--space-xl)',
          animation: 'slideInUp 0.5s ease',
        }}
      >
        Hogwarts Nocturno
      </h1>

      <p
        style={{
          fontFamily: 'var(--font-body)',
          fontSize: '1.2rem',
          color: 'var(--star-blue)',
          marginBottom: 'var(--space-2xl)',
        }}
      >
        Elige tu aventura mágica
      </p>

      <form onSubmit={handleSubmit} style={{ width: '100%', maxWidth: '500px' }}>
        <div
          style={{
            display: 'flex',
            gap: 'var(--space-lg)',
            marginBottom: 'var(--space-xl)',
          }}
        >
          <button
            type="button"
            onClick={() => handleGameSelect('hangman')}
            className={`result-button ${selectedGame === 'hangman' ? 'primary' : 'secondary'}`}
            style={{
              flex: 1,
              padding: 'var(--space-lg)',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: 'var(--space-sm)',
            }}
          >
            <div style={{ fontSize: '2.5rem' }}>🔥</div>
            <div style={{ fontSize: '1.1rem', fontWeight: 'bold' }}>Quodpot</div>
            <div style={{ fontSize: '0.9rem', opacity: 0.8 }}>Estabiliza la quodpot</div>
          </button>

          <button
            type="button"
            onClick={() => handleGameSelect('duels')}
            className={`result-button ${selectedGame === 'duels' ? 'primary' : 'secondary'}`}
            style={{
              flex: 1,
              padding: 'var(--space-lg)',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: 'var(--space-sm)',
            }}
          >
            <div style={{ fontSize: '2.5rem' }}>⚔️</div>
            <div style={{ fontSize: '1.1rem', fontWeight: 'bold' }}>Duelos</div>
            <div style={{ fontSize: '0.9rem', opacity: 0.8 }}>Combate Arcano</div>
          </button>
        </div>

        {/* Mode selector for Duels */}
        {selectedGame === 'duels' && (
          <div
            style={{
              display: 'flex',
              gap: 'var(--space-sm)',
              marginBottom: 'var(--space-lg)',
              animation: 'slideInUp 0.3s ease',
            }}
          >
            <button
              type="button"
              onClick={() => setGameMode('pvp')}
              className={`result-button ${gameMode === 'pvp' ? 'primary' : 'secondary'}`}
              style={{
                flex: 1,
                padding: 'var(--space-md)',
                fontSize: '0.95rem',
              }}
            >
              <div>Jugador vs Jugador</div>
              <div style={{ fontSize: '0.75rem', opacity: 0.8, marginTop: '4px' }}>
                Duelo en línea
              </div>
            </button>

            <button
              type="button"
              onClick={() => setGameMode('pve')}
              className={`result-button ${gameMode === 'pve' ? 'primary' : 'secondary'}`}
              style={{
                flex: 1,
                padding: 'var(--space-md)',
                fontSize: '0.95rem',
              }}
            >
              <div>Jugador vs Guardián Arcano</div>
              <div style={{ fontSize: '0.75rem', opacity: 0.8, marginTop: '4px' }}>
                Practica solo
              </div>
            </button>
          </div>
        )}

        {/* Name Input */}
        {selectedGame && (
          <>
            <input
              type="text"
              value={playerName}
              onChange={(e) => setPlayerName(e.target.value)}
              placeholder="Ingresa tu nombre..."
              autoFocus
              style={{
                width: '100%',
                padding: 'var(--space-md)',
                fontSize: '1rem',
                fontFamily: 'var(--font-body)',
                background: 'rgba(42, 26, 58, 0.5)',
                border: '2px solid var(--accent-muted)',
                borderRadius: 'var(--radius-md)',
                color: 'var(--star-white)',
                marginBottom: 'var(--space-lg)',
                transition: 'all 0.3s ease',
                animation: 'slideInUp 0.4s ease',
              }}
              onFocus={(e) => {
                e.target.style.borderColor = 'var(--accent-primary)';
                e.target.style.boxShadow = '0 0 15px var(--accent-glow)';
              }}
              onBlur={(e) => {
                e.target.style.borderColor = 'var(--accent-muted)';
                e.target.style.boxShadow = 'none';
              }}
            />

            <button
              type="submit"
              className="result-button primary"
              style={{
                width: '100%',
                fontSize: '1.1rem',
                animation: 'slideInUp 0.5s ease',
              }}
              disabled={!playerName.trim()}
            >
              {selectedGame === 'hangman'
                ? 'Iniciar Aventura'
                : gameMode === 'pvp'
                ? 'Entrar al Salón de Duelos'
                : 'Comenzar Entrenamiento'}
            </button>
          </>
        )}
      </form>
    </div>
  );
}

GameSelector.propTypes = {
  onSelectGame: PropTypes.func.isRequired,
};
