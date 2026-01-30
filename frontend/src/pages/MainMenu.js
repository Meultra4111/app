import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useGame } from '../context/GameContext';
import { Swords, Trophy, ShoppingBag, User, Target } from 'lucide-react';

export const MainMenu = () => {
  const navigate = useNavigate();
  const { player } = useGame();

  return (
    <div className="min-h-screen bg-[#050505] flex flex-col items-center justify-center p-4 relative overflow-hidden">
      <div className="absolute inset-0 scanlines opacity-10"></div>
      
      <div className="absolute top-0 left-0 w-full h-full bg-gradient-to-b from-transparent via-[#00FF94]/5 to-transparent"></div>

      <div className="relative z-10 max-w-4xl w-full">
        <div className="text-center mb-12 float-animation">
          <h1 
            className="font-press-start text-3xl md:text-5xl lg:text-6xl text-[#00FF94] mb-4 pulse-neon"
            data-testid="game-title"
          >
            TEAM MEULTRA
          </h1>
          <h2 className="font-press-start text-lg md:text-2xl text-[#FF00FF] neon-glow-secondary">
            BATTLE ARENA
          </h2>
          <p className="font-space-mono text-[#AAAAAA] mt-4 text-sm md:text-base">
            Combate PvP · Pixel Art Retro · Acción Caótica
          </p>
        </div>

        {player && (
          <div className="bg-[#121212] border-2 border-[#00FF94] p-4 mb-8 hard-shadow">
            <div className="flex items-center justify-between font-vt323 text-xl">
              <span className="text-[#FFFFFF]" data-testid="player-username">👤 {player.username}</span>
              <div className="flex gap-6">
                <span className="text-[#FFCC00]" data-testid="player-level">⭐ LVL {player.level}</span>
                <span className="text-[#00FFFF]" data-testid="player-xp">✨ {player.xp} XP</span>
                <span className="text-[#00FF94]" data-testid="player-coins">💰 {player.coins}</span>
              </div>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <button
            data-testid="start-game-btn"
            onClick={() => navigate('/character-select')}
            className="bg-[#00FF94] text-black font-press-start p-6 border-2 border-black hard-shadow hover:translate-y-1 hover:shadow-none transition-all group"
          >
            <Swords className="w-8 h-8 mx-auto mb-3" />
            <span className="text-sm">JUGAR</span>
          </button>

          <button
            data-testid="achievements-btn"
            onClick={() => navigate('/achievements')}
            className="bg-[#FFCC00] text-black font-press-start p-6 border-2 border-black hard-shadow hover:translate-y-1 hover:shadow-none transition-all"
          >
            <Trophy className="w-8 h-8 mx-auto mb-3" />
            <span className="text-sm">LOGROS</span>
          </button>

          <button
            data-testid="shop-btn"
            onClick={() => navigate('/shop')}
            className="bg-[#FF00FF] text-white font-press-start p-6 border-2 border-black hard-shadow hover:translate-y-1 hover:shadow-none transition-all"
          >
            <ShoppingBag className="w-8 h-8 mx-auto mb-3" />
            <span className="text-sm">TIENDA</span>
          </button>

          <button
            data-testid="training-btn"
            onClick={() => navigate('/training')}
            className="bg-[#00FFFF] text-black font-press-start p-6 border-2 border-black hard-shadow hover:translate-y-1 hover:shadow-none transition-all"
          >
            <Target className="w-8 h-8 mx-auto mb-3" />
            <span className="text-sm">ENTRENAMIENTO</span>
          </button>
        </div>

        {player?.unlocked_dlc && (
          <div className="bg-gradient-to-r from-[#FF00FF] to-[#00FFFF] p-1 mb-8">
            <div className="bg-[#050505] p-6 text-center">
              <p className="font-press-start text-[#FFFFFF] text-sm mb-2 glitch">
                📦 DLC DESBLOQUEADO
              </p>
              <p className="font-space-mono text-[#AAAAAA] text-xs">
                "Mi Historia" - Nuevos personajes y jefe Thisand disponibles
              </p>
            </div>
          </div>
        )}

        <div className="text-center">
          <p className="font-vt323 text-[#666666] text-sm">
            Construido por Team Meultra · v1.0
          </p>
        </div>
      </div>
    </div>
  );
};

export default MainMenu;
