import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useGame } from '../context/GameContext';
import { ArrowLeft } from 'lucide-react';

export const MapSelect = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { getMaps } = useGame();
  const [maps, setMaps] = useState([]);
  const [selectedMap, setSelectedMap] = useState(null);
  const character = location.state?.character;

  useEffect(() => {
    if (!character) {
      navigate('/character-select');
      return;
    }
    loadMaps();
  }, []);

  const loadMaps = async () => {
    const mapList = await getMaps();
    setMaps(mapList);
  };

  const handleStartGame = () => {
    if (selectedMap && character) {
      navigate('/game', { state: { character, map: selectedMap } });
    }
  };

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case 'Easy': return '#00FF94';
      case 'Medium': return '#FFCC00';
      case 'Hard': return '#FF00FF';
      case 'Expert': return '#FF3B30';
      default: return '#FFFFFF';
    }
  };

  return (
    <div className="min-h-screen bg-[#050505] p-4 md:p-8 relative overflow-hidden">
      <div className="absolute inset-0 scanlines opacity-5"></div>

      <div className="relative z-10 max-w-7xl mx-auto">
        <button
          data-testid="back-btn"
          onClick={() => navigate('/character-select')}
          className="flex items-center gap-2 bg-[#1E1E1E] text-white font-press-start px-4 py-3 border-2 border-[#333333] hover:border-[#00FF94] transition-colors text-xs mb-8"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>VOLVER</span>
        </button>

        <div className="text-center mb-8">
          <h1 className="font-press-start text-2xl md:text-4xl text-[#00FF94] mb-2 neon-glow">
            SELECCIONA EL MAPA
          </h1>
          <p className="font-space-mono text-[#AAAAAA]">
            Personaje: <span className="text-[#00FF94]">{character?.name}</span>
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          {maps.map((map) => {
            const isSelected = selectedMap?.id === map.id;

            return (
              <button
                key={map.id}
                data-testid={`map-${map.id}`}
                onClick={() => setSelectedMap(map)}
                className={`
                  relative p-6 border-2 transition-all text-left
                  ${isSelected ? 'border-[#00FF94] bg-[#00FF94]/10 scale-105' : 'border-[#333333] bg-[#121212]'}
                  hover:border-[#00FF94] hover:scale-105 cursor-pointer
                  hard-shadow
                `}
              >
                <div className="mb-4 h-32 bg-[#1E1E1E] border border-[#333333] flex items-center justify-center font-press-start text-2xl text-[#00FF94]">
                  {map.name[0]}
                </div>

                <h3 className="font-press-start text-lg text-white mb-2">
                  {map.name}
                </h3>
                <p className="font-space-mono text-sm text-[#AAAAAA] mb-3">
                  {map.theme}
                </p>

                <div className="flex items-center gap-2">
                  <span className="font-vt323 text-sm text-[#AAAAAA]">Dificultad:</span>
                  <span
                    className="font-press-start text-xs px-2 py-1 border"
                    style={{
                      color: getDifficultyColor(map.difficulty),
                      borderColor: getDifficultyColor(map.difficulty)
                    }}
                  >
                    {map.difficulty}
                  </span>
                </div>
              </button>
            );
          })}
        </div>

        <div className="bg-[#1E1E1E] border-2 border-[#333333] p-4 mb-4">
          <p className="font-vt323 text-[#AAAAAA] text-center">
            💬 <span className="text-white">Davo_785</span>: "Oigan, próximamente más mapas"
          </p>
        </div>

        {selectedMap && (
          <div className="text-center">
            <button
              data-testid="start-battle-btn"
              onClick={handleStartGame}
              className="bg-[#00FF94] text-black font-press-start text-lg px-12 py-4 border-2 border-black hard-shadow hover:translate-y-1 hover:shadow-none transition-all glitch"
            >
              ⚔️ INICIAR BATALLA
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default MapSelect;
