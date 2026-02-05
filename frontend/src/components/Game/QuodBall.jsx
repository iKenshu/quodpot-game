import { useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './QuodBall.css';

const MAX_ATTEMPTS = 6;

export function QuodBall({ attemptsLeft }) {
  const wrongGuesses = MAX_ATTEMPTS - attemptsLeft;
  const intensity = wrongGuesses / MAX_ATTEMPTS; // 0 to 1

  // Calculate dynamic properties based on intensity
  const config = useMemo(() => ({
    // Pulsation speed increases with danger
    pulseSpeed: 2 - (intensity * 1.5), // 2s -> 0.5s
    // Shake intensity
    shakeAmount: intensity > 0.8 ? 4 : intensity > 0.5 ? 2 : 0,
    // Flame scale
    flameScale: 0.3 + (intensity * 0.7), // 0.3 -> 1.0
    // Glow intensity
    glowOpacity: 0.2 + (intensity * 0.8), // 0.2 -> 1.0
    // Core color shifts from dark to bright
    coreColor: intensity > 0.8 ? '#ff4500' : intensity > 0.5 ? '#ff6b35' : intensity > 0.2 ? '#8b4513' : '#2c1810',
  }), [intensity]);

  const isExploding = attemptsLeft === 0;

  return (
    <div className="quod-container">
      <AnimatePresence mode="wait">
        {isExploding ? (
          <motion.div
            key="explosion"
            className="quod-explosion"
            initial={{ scale: 1, opacity: 1 }}
            animate={{
              scale: [1, 1.5, 2, 2.5],
              opacity: [1, 1, 0.8, 0],
            }}
            transition={{ duration: 0.8, ease: 'easeOut' }}
          >
            <div className="explosion-ring explosion-ring--1" />
            <div className="explosion-ring explosion-ring--2" />
            <div className="explosion-ring explosion-ring--3" />
            <div className="explosion-particles">
              {[...Array(12)].map((_, i) => (
                <motion.div
                  key={i}
                  className="explosion-particle"
                  initial={{ x: 0, y: 0, opacity: 1 }}
                  animate={{
                    x: Math.cos(i * 30 * Math.PI / 180) * 100,
                    y: Math.sin(i * 30 * Math.PI / 180) * 100,
                    opacity: 0,
                  }}
                  transition={{ duration: 0.6, ease: 'easeOut' }}
                />
              ))}
            </div>
          </motion.div>
        ) : (
          <motion.div
            key="quod"
            className="quod-ball"
            animate={{
              scale: [1, 1 + (intensity * 0.1), 1],
              x: config.shakeAmount > 0 ? [0, -config.shakeAmount, config.shakeAmount, -config.shakeAmount, 0] : 0,
            }}
            transition={{
              scale: {
                duration: config.pulseSpeed,
                repeat: Infinity,
                ease: 'easeInOut',
              },
              x: {
                duration: 0.3,
                repeat: Infinity,
                ease: 'easeInOut',
              },
            }}
          >
            {/* Outer glow */}
            <motion.div
              className="quod-glow"
              animate={{ opacity: config.glowOpacity }}
              style={{
                boxShadow: `
                  0 0 ${20 + intensity * 40}px rgba(255, 107, 53, ${config.glowOpacity}),
                  0 0 ${40 + intensity * 60}px rgba(255, 69, 0, ${config.glowOpacity * 0.5})
                `,
              }}
            />

            {/* Main ball SVG */}
            <svg
              viewBox="0 0 120 120"
              className="quod-svg"
              xmlns="http://www.w3.org/2000/svg"
            >
              <defs>
                {/* Ball gradient */}
                <radialGradient id="ballGradient" cx="30%" cy="30%" r="70%">
                  <stop offset="0%" stopColor={config.coreColor} />
                  <stop offset="50%" stopColor="#1a0a0a" />
                  <stop offset="100%" stopColor="#0d0505" />
                </radialGradient>

                {/* Fire gradient */}
                <linearGradient id="fireGradient" x1="0%" y1="100%" x2="0%" y2="0%">
                  <stop offset="0%" stopColor="#ff6b35" />
                  <stop offset="50%" stopColor="#ff4500" />
                  <stop offset="100%" stopColor="#ffcc00" />
                </linearGradient>

                {/* Glow filter */}
                <filter id="fireGlow" x="-50%" y="-50%" width="200%" height="200%">
                  <feGaussianBlur stdDeviation="3" result="blur" />
                  <feMerge>
                    <feMergeNode in="blur" />
                    <feMergeNode in="SourceGraphic" />
                  </feMerge>
                </filter>
              </defs>

              {/* Flames - multiple layers with different animations */}
              <g className="quod-flames" style={{ opacity: intensity > 0 ? 1 : 0 }}>
                {/* Back flames */}
                <motion.path
                  d="M60 70 Q50 50 55 30 Q60 45 65 30 Q70 50 60 70"
                  fill="url(#fireGradient)"
                  filter="url(#fireGlow)"
                  initial={{ scale: 0, y: 0 }}
                  animate={{
                    scale: config.flameScale,
                    y: [-5, 0, -5],
                  }}
                  transition={{
                    scale: { duration: 0.3 },
                    y: { duration: 0.4, repeat: Infinity, ease: 'easeInOut' },
                  }}
                  style={{ transformOrigin: '60px 70px' }}
                />

                {/* Left flame */}
                {intensity > 0.3 && (
                  <motion.path
                    d="M45 65 Q35 50 40 35 Q45 48 50 38 Q52 52 45 65"
                    fill="url(#fireGradient)"
                    filter="url(#fireGlow)"
                    initial={{ scale: 0 }}
                    animate={{
                      scale: config.flameScale * 0.8,
                      y: [-3, 2, -3],
                      rotate: [-5, 5, -5],
                    }}
                    transition={{
                      scale: { duration: 0.3 },
                      y: { duration: 0.35, repeat: Infinity, ease: 'easeInOut' },
                      rotate: { duration: 0.5, repeat: Infinity, ease: 'easeInOut' },
                    }}
                    style={{ transformOrigin: '45px 65px' }}
                  />
                )}

                {/* Right flame */}
                {intensity > 0.3 && (
                  <motion.path
                    d="M75 65 Q85 50 80 35 Q75 48 70 38 Q68 52 75 65"
                    fill="url(#fireGradient)"
                    filter="url(#fireGlow)"
                    initial={{ scale: 0 }}
                    animate={{
                      scale: config.flameScale * 0.8,
                      y: [-2, 3, -2],
                      rotate: [5, -5, 5],
                    }}
                    transition={{
                      scale: { duration: 0.3 },
                      y: { duration: 0.3, repeat: Infinity, ease: 'easeInOut' },
                      rotate: { duration: 0.45, repeat: Infinity, ease: 'easeInOut' },
                    }}
                    style={{ transformOrigin: '75px 65px' }}
                  />
                )}

                {/* Top flame - appears when very dangerous */}
                {intensity > 0.6 && (
                  <motion.path
                    d="M60 55 Q52 35 57 15 Q60 30 63 15 Q68 35 60 55"
                    fill="url(#fireGradient)"
                    filter="url(#fireGlow)"
                    initial={{ scale: 0 }}
                    animate={{
                      scale: config.flameScale,
                      y: [-8, 0, -8],
                    }}
                    transition={{
                      scale: { duration: 0.3 },
                      y: { duration: 0.25, repeat: Infinity, ease: 'easeInOut' },
                    }}
                    style={{ transformOrigin: '60px 55px' }}
                  />
                )}

                {/* Side flames for maximum danger */}
                {intensity > 0.8 && (
                  <>
                    <motion.path
                      d="M35 70 Q20 60 25 45 Q32 55 30 48 Q38 60 35 70"
                      fill="url(#fireGradient)"
                      filter="url(#fireGlow)"
                      animate={{
                        scale: [0.8, 1, 0.8],
                        rotate: [-10, 0, -10],
                      }}
                      transition={{ duration: 0.3, repeat: Infinity }}
                      style={{ transformOrigin: '35px 70px' }}
                    />
                    <motion.path
                      d="M85 70 Q100 60 95 45 Q88 55 90 48 Q82 60 85 70"
                      fill="url(#fireGradient)"
                      filter="url(#fireGlow)"
                      animate={{
                        scale: [0.8, 1, 0.8],
                        rotate: [10, 0, 10],
                      }}
                      transition={{ duration: 0.3, repeat: Infinity }}
                      style={{ transformOrigin: '85px 70px' }}
                    />
                  </>
                )}
              </g>

              {/* The Quod ball itself */}
              <circle
                cx="60"
                cy="70"
                r="28"
                fill="url(#ballGradient)"
                stroke={config.coreColor}
                strokeWidth="2"
              />

              {/* Inner glow on ball */}
              <circle
                cx="52"
                cy="62"
                r="8"
                fill="rgba(255, 255, 255, 0.1)"
              />

              {/* Smoke/steam particles when starting to heat */}
              {intensity > 0 && intensity < 0.5 && (
                <g className="smoke-particles">
                  {[...Array(3)].map((_, i) => (
                    <motion.circle
                      key={i}
                      cx={55 + i * 5}
                      cy={45}
                      r={2}
                      fill="rgba(100, 100, 100, 0.5)"
                      animate={{
                        y: [-10, -30],
                        opacity: [0.5, 0],
                        scale: [1, 2],
                      }}
                      transition={{
                        duration: 1.5,
                        repeat: Infinity,
                        delay: i * 0.3,
                        ease: 'easeOut',
                      }}
                    />
                  ))}
                </g>
              )}
            </svg>

            {/* Ember particles floating up */}
            {intensity > 0.5 && (
              <div className="ember-particles">
                {[...Array(6)].map((_, i) => (
                  <motion.div
                    key={i}
                    className="ember"
                    initial={{ x: 0, y: 0, opacity: 0 }}
                    animate={{
                      x: [0, (Math.random() - 0.5) * 40],
                      y: [0, -60 - Math.random() * 40],
                      opacity: [0, 1, 0],
                    }}
                    transition={{
                      duration: 1 + Math.random() * 0.5,
                      repeat: Infinity,
                      delay: i * 0.2,
                      ease: 'easeOut',
                    }}
                  />
                ))}
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Attempts counter below */}
      <div className="quod-attempts">
        <span className="quod-attempts-label">Oportunidades</span>
        <span className={`quod-attempts-count ${attemptsLeft <= 2 ? 'quod-attempts-count--danger' : ''}`}>
          {attemptsLeft}
        </span>
      </div>
    </div>
  );
}

export default QuodBall;
