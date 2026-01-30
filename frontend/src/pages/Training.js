import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Bot } from 'lucide-react';

export const Training = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-[#050505] flex items-center justify-center p-4 relative overflow-hidden">
      <div className="absolute inset-0 scanlines opacity-10"></div>

      <div className="relative z-10 max-w-2xl w-full text-center">
        <button
          data-testid="back-btn"
          onClick={() => navigate('/')}
          className="absolute top-0 left-0 flex items-center gap-2 bg-[#1E1E1E] text-white font-press-start px-4 py-3 border-2 border-[#333333] hover:border-[#00FF94] transition-colors text-xs"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>VOLVER</span>
        </button>

        <div className="mb-12 float-animation">
          <Bot className="w-32 h-32 mx-auto mb-6 text-[#00FFFF]" />
          <h1 className="font-press-start text-3xl text-[#00FFFF] mb-4 neon-glow">
            MEE6
          </h1>
          <p className="font-space-mono text-[#AAAAAA]">
            🤖 Creador de Bots para Entrenamiento
          </p>
        </div>

        <div className="bg-[#121212] border-2 border-[#00FFFF] p-8 mb-8 hard-shadow">
          <h2 className="font-press-start text-xl text-white mb-6">
            CENTRO DE ENTRENAMIENTO
          </h2>
          <p className="font-space-mono text-[#AAAAAA] mb-6">
            Próximamente podrás entrenar contra bots con diferentes niveles de dificultad.
            MEE6 está preparando el sistema de entrenamiento.
          </p>
          <div className="text-6xl mb-4">🚧</div>
          <p className="font-vt323 text-[#FFCC00] text-xl">
            EN CONSTRUCCIÓN
          </p>
        </div>

        <button
          data-testid="start-real-game-btn"
          onClick={() => navigate('/character-select')}
          className="bg-[#00FF94] text-black font-press-start px-8 py-4 border-2 border-black hard-shadow hover:translate-y-1 hover:shadow-none transition-all"
        >
          IR A JUEGO REAL
        </button>
      </div>
    </div>
  );
};

export default Training;
