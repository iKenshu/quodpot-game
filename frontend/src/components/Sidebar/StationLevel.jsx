import { motion } from 'framer-motion';

// Función para obtener el nombre del sello
const getSealName = (stationNumber, totalStations) => {
  // Si es la última estación, es el Sello Final
  if (stationNumber === totalStations) {
    return { label: 'Sello', name: 'Final' };
  }

  const ordinals = {
    1: 'Primer',
    2: 'Segundo',
    3: 'Tercer',
    4: 'Cuarto',
    5: 'Quinto',
    6: 'Sexto',
    7: 'Séptimo',
    8: 'Octavo',
    9: 'Noveno',
    10: 'Décimo',
  };

  const ordinal = ordinals[stationNumber] || `${stationNumber}°`;
  return { label: ordinal, name: 'Sello' };
};

export function StationLevel({
  stationNumber,
  players = [],
  isCurrent = false,
  currentPlayerId,
  totalStations,
}) {
  const hasPlayers = players.length > 0;
  const seal = getSealName(stationNumber, totalStations);

  return (
    <motion.div
      className={`station-level ${isCurrent ? 'station-level--current' : ''} ${hasPlayers ? 'station-level--active' : ''}`}
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: (totalStations - stationNumber) * 0.05 }}
    >
      {isCurrent && <div className="current-marker" />}

      <div className="station-number">
        <span className="station-number-label">{seal.label}</span>
        <span className="station-number-value">{seal.name}</span>
      </div>

      <div className="station-players">
        {players.map((player, index) => (
          <motion.div
            key={player.id || index}
            className={`player-dot ${player.id === currentPlayerId ? 'player-dot--self' : ''}`}
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: index * 0.1 }}
            title={player.name || `Jugador ${index + 1}`}
          />
        ))}
      </div>

      <span className="player-count">
        {players.length > 0 ? players.length : ''}
      </span>

      <div className="torch-glow" />
    </motion.div>
  );
}

export default StationLevel;
