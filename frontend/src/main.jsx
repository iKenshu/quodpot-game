import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
// CSS imports are now handled in App.jsx
import App from './App.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
