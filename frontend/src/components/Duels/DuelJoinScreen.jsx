import { useState } from 'react';
import PropTypes from 'prop-types';
import '../../styles/games/duels/duels.css';

export default function DuelJoinScreen({ onJoin }) {
  const [name, setName] = useState('');
  const [mode, setMode] = useState('pvp'); // 'pvp' or 'pve'

  const handleSubmit = (e) => {
    e.preventDefault();
    if (name.trim()) {
      onJoin(name.trim(), mode);
    }
  };

  return (
    <div className="duel-join-screen">
      <svg
        className="duel-wands-decoration"
        viewBox="0 0 100 100"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <line x1="20" y1="80" x2="80" y2="20" stroke="currentColor" strokeWidth="3" />
        <line x1="80" y1="80" x2="20" y2="20" stroke="currentColor" strokeWidth="3" />
        <circle cx="20" cy="80" r="4" fill="currentColor" />
        <circle cx="80" cy="20" r="4" fill="currentColor" />
        <circle cx="80" cy="80" r="4" fill="currentColor" />
        <circle cx="20" cy="20" r="4" fill="currentColor" />
      </svg>

      <h1 className="duel-join-title">Duelistas Arcanos</h1>
      <p className="duel-join-subtitle">El arte ancestral del combate mágico</p>

      <form onSubmit={handleSubmit} style={{ width: '100%', maxWidth: '400px' }}>
        {/* Mode selector */}
        <div style={{
          display: 'flex',
          gap: 'var(--space-sm)',
          marginBottom: 'var(--space-lg)',
          width: '100%'
        }}>
          <button
            type="button"
            onClick={() => setMode('pvp')}
            className="mode-selector-button"
            style={{
              flex: 1,
              padding: 'var(--space-md)',
              fontSize: '0.95rem',
              fontFamily: 'var(--font-body)',
              background: mode === 'pvp' ? 'var(--accent-primary)' : 'rgba(42, 26, 58, 0.5)',
              border: `2px solid ${mode === 'pvp' ? 'var(--accent-primary)' : 'var(--accent-muted)'}`,
              borderRadius: 'var(--radius-md)',
              color: 'var(--star-white)',
              cursor: 'pointer',
              transition: 'all 0.3s ease',
            }}
          >
            <div>Jugador vs Jugador</div>
            <div style={{ fontSize: '0.75rem', opacity: 0.8, marginTop: '4px' }}>
              Duelo en línea
            </div>
          </button>

          <button
            type="button"
            onClick={() => setMode('pve')}
            className="mode-selector-button"
            style={{
              flex: 1,
              padding: 'var(--space-md)',
              fontSize: '0.95rem',
              fontFamily: 'var(--font-body)',
              background: mode === 'pve' ? 'var(--accent-primary)' : 'rgba(42, 26, 58, 0.5)',
              border: `2px solid ${mode === 'pve' ? 'var(--accent-primary)' : 'var(--accent-muted)'}`,
              borderRadius: 'var(--radius-md)',
              color: 'var(--star-white)',
              cursor: 'pointer',
              transition: 'all 0.3s ease',
            }}
          >
            <div>Jugador vs Guardián Arcano</div>
            <div style={{ fontSize: '0.75rem', opacity: 0.8, marginTop: '4px' }}>
              Practica solo
            </div>
          </button>
        </div>

        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Ingresa tu nombre de mago..."
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
          }}
          disabled={!name.trim()}
        >
          {mode === 'pvp' ? 'Entrar al Salón de Duelos' : 'Comenzar Entrenamiento'}
        </button>
      </form>
    </div>
  );
}

DuelJoinScreen.propTypes = {
  onJoin: PropTypes.func.isRequired,
};
