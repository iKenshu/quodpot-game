import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useGameState } from '../../context/GameContext';
import { StationTower } from '../Sidebar';
import { HangmanGame } from '../Game';
import { GameOverOverlay } from '../Screens';
import '../../styles/components/layout.css';

export function GameLayout() {
  const { playerName } = useGameState();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const toggleSidebar = () => setSidebarOpen(!sidebarOpen);
  const closeSidebar = () => setSidebarOpen(false);

  const getInitial = (name) => {
    return name ? name.charAt(0).toUpperCase() : '?';
  };

  return (
    <div className="game-layout">
      <AnimatePresence>
        {sidebarOpen && (
          <motion.div
            className="sidebar-overlay sidebar-overlay--visible"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={closeSidebar}
          />
        )}
      </AnimatePresence>

      <motion.div
        className={sidebarOpen ? 'sidebar--open' : ''}
        initial={false}
        animate={{
          x: typeof window !== 'undefined' && window.innerWidth <= 768
            ? (sidebarOpen ? 0 : -280)
            : 0,
        }}
        style={{
          position: typeof window !== 'undefined' && window.innerWidth <= 768 ? 'fixed' : 'relative',
          zIndex: 100,
        }}
      >
        <StationTower />
      </motion.div>

      <div className="game-layout__main">
        <header className="game-header">
          <button
            className="sidebar-toggle"
            onClick={toggleSidebar}
            aria-label="Toggle sidebar"
          >
            &#9776;
          </button>

          <h1 className="game-header__title">
            La Quod Inestable
          </h1>

          <div className="game-header__info">
            <div className="player-info">
              <div className="player-info__avatar">
                {getInitial(playerName)}
              </div>
              <span>{playerName}</span>
            </div>
          </div>
        </header>

        <HangmanGame />
      </div>

      <GameOverOverlay />
    </div>
  );
}

export default GameLayout;
