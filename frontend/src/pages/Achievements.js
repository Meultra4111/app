import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useGame } from '../context/GameContext';
import { ArrowLeft, Lock, Check } from 'lucide-react';

export const Achievements = () => {
  const navigate = useNavigate();
  const { player, loading, getAchievements } = useGame();
  const [achievements, setAchievements] = useState([]);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    if (!loading && player) {
      loadAchievements();
    }
  }, [loading, player]);

  const loadAchievements = async () => {
    const achs = await getAchievements();
    setAchievements(achs);
  };

  const categories = ['all', 'combat', 'victory', 'progression', 'special', 'shop', 'coins', 'exploration', 'characters'];

  const filteredAchievements = filter === 'all'
    ? achievements
    : achievements.filter(a => a.category === filter);

  const unlockedCount = achievements.filter(a => a.unlocked).length;
  const totalCount = achievements.length;
  const completionPercent = totalCount > 0 ? Math.floor((unlockedCount / totalCount) * 100) : 0;

  return (
    <div className="min-h-screen bg-[#050505] p-4 md:p-8 relative overflow-hidden">
      <div className="absolute inset-0 scanlines opacity-5"></div>

      <div className="relative z-10 max-w-6xl mx-auto">
        <button
          data-testid="back-btn"
          onClick={() => navigate('/')}
          className="flex items-center gap-2 bg-[#1E1E1E] text-white font-press-start px-4 py-3 border-2 border-[#333333] hover:border-[#00FF94] transition-colors text-xs mb-8"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>VOLVER</span>
        </button>

        <div className="text-center mb-8">
          <h1 className="font-press-start text-2xl md:text-4xl text-[#00FF94] mb-4 neon-glow">
            LOGROS
          </h1>
          <div className="flex items-center justify-center gap-4 font-vt323 text-2xl">
            <span className="text-[#FFCC00]" data-testid="achievements-unlocked">
              🏆 {unlockedCount} / {totalCount}
            </span>
            <span className="text-[#AAAAAA]">·</span>
            <span className="text-[#00FF94]" data-testid="achievements-completion">
              {completionPercent}% Completado
            </span>
          </div>
        </div>

        <div className="bg-[#121212] border-2 border-[#00FF94] p-4 mb-8">
          <div className="w-full h-8 bg-[#1E1E1E] border border-[#333333]">
            <div
              className="h-full bg-gradient-to-r from-[#00FF94] to-[#00FFFF] transition-all duration-500"
              style={{ width: `${completionPercent}%` }}
            ></div>
          </div>
        </div>

        <div className="flex flex-wrap gap-2 mb-8 justify-center">
          {categories.map(cat => (
            <button
              key={cat}
              data-testid={`filter-${cat}`}
              onClick={() => setFilter(cat)}
              className={`
                px-4 py-2 font-space-mono text-xs border-2 transition-all
                ${filter === cat
                  ? 'bg-[#00FF94] text-black border-[#00FF94]'
                  : 'bg-[#1E1E1E] text-white border-[#333333] hover:border-[#00FF94]'
                }
              `}
            >
              {cat.toUpperCase()}
            </button>
          ))}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredAchievements.map((achievement) => (
            <div
              key={achievement.achievement_id}
              data-testid={`achievement-${achievement.achievement_id}`}
              className={`
                relative p-6 border-2 transition-all
                ${achievement.unlocked
                  ? 'bg-[#00FF94]/10 border-[#00FF94]'
                  : 'bg-[#121212] border-[#333333] opacity-60'
                }
              `}
            >
              {achievement.unlocked ? (
                <div className="absolute top-2 right-2 bg-[#00FF94] rounded-full p-1">
                  <Check className="w-4 h-4 text-black" />
                </div>
              ) : (
                <div className="absolute top-2 right-2 bg-[#333333] rounded-full p-1">
                  <Lock className="w-4 h-4 text-[#666666]" />
                </div>
              )}

              <div className="text-5xl mb-4 text-center">
                {achievement.icon}
              </div>

              <h3 className="font-press-start text-xs text-white mb-2 text-center">
                {achievement.title}
              </h3>

              <p className="font-space-mono text-[10px] text-[#AAAAAA] text-center mb-3">
                {achievement.description}
              </p>

              <div className="text-center">
                <span className="inline-block px-2 py-1 bg-[#1E1E1E] border border-[#333333] font-vt323 text-xs text-[#AAAAAA]">
                  {achievement.category}
                </span>
              </div>
            </div>
          ))}
        </div>

        {filteredAchievements.length === 0 && (
          <div className="text-center py-12">
            <p className="font-space-mono text-[#AAAAAA]">
              No hay logros en esta categoría
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Achievements;
