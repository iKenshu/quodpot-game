import { motion, AnimatePresence } from 'framer-motion';

export function Toast({ message, type = 'info', isVisible, onClose }) {
  const typeStyles = {
    info: 'toast--info',
    success: 'toast--success',
    error: 'toast--error',
    warning: 'toast--warning',
  };

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          className={`toast ${typeStyles[type]}`}
          initial={{ opacity: 0, y: -50, x: '-50%' }}
          animate={{ opacity: 1, y: 0, x: '-50%' }}
          exit={{ opacity: 0, y: -50, x: '-50%' }}
          style={{
            position: 'fixed',
            top: '1rem',
            left: '50%',
            padding: '0.75rem 1.5rem',
            borderRadius: '8px',
            fontFamily: 'var(--font-body)',
            fontSize: '1rem',
            fontWeight: 600,
            zIndex: 1000,
            backgroundColor: type === 'success' ? 'var(--color-success)' :
                            type === 'error' ? 'var(--blood-red)' :
                            type === 'warning' ? 'var(--torch-glow)' :
                            'var(--shadow-purple)',
            color: 'white',
            boxShadow: '0 4px 15px rgba(0, 0, 0, 0.3)',
          }}
          onClick={onClose}
        >
          {message}
        </motion.div>
      )}
    </AnimatePresence>
  );
}

export default Toast;
