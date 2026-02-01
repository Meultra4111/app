import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Trophy, Coins, Target, Home } from 'lucide-react';

export const GameOver = () => {
  const navigate = useNavigate();
  const location = useLocation();
  
  const {
    victory = false,
    score = 0,
    enemiesDefeated = 0,
    xpEarned = 0,
    coinsEarned = 0,
    achievementsUnlocked = 0,
    duration = 0
  } = location.state || {};

  return (
    <div className="min-h-screen bg-[#050505] flex items-center justify-center p-4 relative overflow-hidden">
      <div className="absolute inset-0 scanlines opacity-10"></div>

      <div className="relative z-10 max-w-2xl w-full">
        <div className="text-center mb-12">
          <h1
            data-testid="game-result-title"
            className={`font-press-start text-5xl mb-4 ${
              victory ? 'text-[#00FF94] pulse-neon' : 'text-[#FF3B30]'
            }`}
          >
            {victory ? '¡VICTORIA!' : 'DERROTA'}
          </h1>
          <p className="font-space-mono text-[#AAAAAA] text-lg">
            {victory
              ? '¡Increíble! Has derrotado a todos los enemigos'
              : 'No te rindas, inténtalo de nuevo'}
          </p>
        </div>

        <div className="bg-[#121212] border-2 border-[#00FF94] p-8 mb-8 hard-shadow">
          <div className="grid grid-cols-2 gap-6 font-vt323 text-2xl">
            <div className="text-center p-4 bg-[#1E1E1E] border border-[#333333]">
              <div className="text-[#AAAAAA] text-lg mb-2">SCORE</div>
              <div className="text-[#FFCC00]" data-testid="final-score">⭐ {score}</div>
            </div>
            
            <div className="text-center p-4 bg-[#1E1E1E] border border-[#333333]">
              <div className="text-[#AAAAAA] text-lg mb-2">ENEMIGOS</div>
              <div className="text-[#FF3B30]" data-testid="final-enemies">⚔️ {enemiesDefeated}</div>
            </div>
            
            <div className="text-center p-4 bg-[#1E1E1E] border border-[#333333]">
              <div className="text-[#AAAAAA] text-lg mb-2">TIEMPO</div>
              <div className="text-[#00FFFF]" data-testid="final-time">⏱️ {duration}s</div>
            </div>
            
            <div className="text-center p-4 bg-[#1E1E1E] border border-[#333333]">
              <div className="text-[#AAAAAA] text-lg mb-2">XP</div>
              <div className="text-[#FF00FF]" data-testid="final-xp">✨ +{xpEarned}</div>
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-r from-[#00FF94] to-[#00FFFF] p-1 mb-8">
          <div className="bg-[#121212] p-6">
            <div className="flex items-center justify-center gap-8 font-vt323 text-3xl">
              <div className="flex items-center gap-2">
                <Coins className="w-8 h-8 text-[#FFCC00]" />
                <span className="text-[#FFCC00]" data-testid="coins-earned">+{coinsEarned}</span>
              </div>
              {achievementsUnlocked > 0 && (
                <div className="flex items-center gap-2">
                  <Trophy className="w-8 h-8 text-[#FF00FF]" />
                  <span className="text-[#FF00FF]" data-testid="achievements-unlocked">+{achievementsUnlocked} Logros</span>
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button
            data-testid="play-again-btn"
            onClick={() => navigate('/character-select')}
            className="bg-[#00FF94] text-black font-press-start p-4 border-2 border-black hard-shadow hover:translate-y-1 hover:shadow-none transition-all flex items-center justify-center gap-2"
          >
            <Target className="w-5 h-5" />
            <span className="text-xs">JUGAR DE NUEVO</span>
          </button>

          <button
            data-testid="view-achievements-btn"
            onClick={() => navigate('/achievements')}
            className="bg-[#FFCC00] text-black font-press-start p-4 border-2 border-black hard-shadow hover:translate-y-1 hover:shadow-none transition-all flex items-center justify-center gap-2"
          >
            <Trophy className="w-5 h-5" />
            <span className="text-xs">LOGROS</span>
          </button>

          <button
            data-testid="back-home-btn"
            onClick={() => navigate('/')}
            className="bg-[#FF00FF] text-white font-press-start p-4 border-2 border-black hard-shadow hover:translate-y-1 hover:shadow-none transition-all flex items-center justify-center gap-2"
          >
            <Home className="w-5 h-5" />
            <span className="text-xs">MENÚ</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default GameOver;
