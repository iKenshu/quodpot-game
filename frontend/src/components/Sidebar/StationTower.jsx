import { useMemo } from 'react';
import { motion } from 'framer-motion';
import { useGameState } from '../../context/GameContext';
import StationLevel from './StationLevel';
import '../../styles/components/sidebar.css';

export function StationTower() {
  const {
    totalStations,
    currentStation,
    playerId,
    players,
    stationStatus,
    isConnected,
  } = useGameState();

  // Build station data from players and station status
  const stationData = useMemo(() => {
    const data = [];

    for (let i = totalStations; i >= 1; i--) {
      // Get players at this station
      let stationPlayers = [];

      // First try stationStatus (server-provided)
      if (stationStatus[i]) {
        stationPlayers = stationStatus[i].map((name, idx) => ({
          id: `status-${i}-${idx}`,
          name,
        }));
      } else {
        // Fall back to local player list
        stationPlayers = players.filter(p => p.station === i);
      }

      data.push({
        stationNumber: i,
        players: stationPlayers,
        isCurrent: i === currentStation,
      });
    }

    return data;
  }, [totalStations, currentStation, players, stationStatus]);

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <h2 className="sidebar-title">Los Sellos</h2>
      </div>

      <motion.div
        className="station-tower"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5 }}
      >
        {stationData.map(({ stationNumber, players: stationPlayers, isCurrent }) => (
          <StationLevel
            key={stationNumber}
            stationNumber={stationNumber}
            players={stationPlayers}
            isCurrent={isCurrent}
            currentPlayerId={playerId}
            totalStations={totalStations}
          />
        ))}
      </motion.div>

      <div className="sidebar-footer">
        <div className="connection-status">
          <span className={`connection-dot ${isConnected ? 'connection-dot--connected' : ''}`} />
          <span>{isConnected ? 'Conectado' : 'Desconectado'}</span>
        </div>
      </div>
    </aside>
  );
}

export default StationTower;
