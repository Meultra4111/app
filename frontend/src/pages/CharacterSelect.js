import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useGame } from '../context/GameContext';
import { ArrowLeft, Lock } from 'lucide-react';

export const CharacterSelect = () => {
  const navigate = useNavigate();
  const { player, getCharacters } = useGame();
  const [characters, setCharacters] = useState([]);
  const [selectedCharacter, setSelectedCharacter] = useState(null);

  useEffect(() => {
    loadCharacters();
  }, []);

  const loadCharacters = async () => {
    const chars = await getCharacters();
    setCharacters(chars);
  };

  const handleSelectCharacter = (char) => {
    if (char.is_dlc && !player?.unlocked_dlc) {
      return;
    }
    setSelectedCharacter(char);
  };

  const handleContinue = () => {
    if (selectedCharacter) {
      navigate('/map-select', { state: { character: selectedCharacter } });
    }
  };

  return (
    <div className="min-h-screen bg-[#050505] p-4 md:p-8 relative overflow-hidden">
      <div className="absolute inset-0 scanlines opacity-5"></div>

      <div className="relative z-10 max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <button
            data-testid="back-btn"
            onClick={() => navigate('/')}
            className="flex items-center gap-2 bg-[#1E1E1E] text-white font-press-start px-4 py-3 border-2 border-[#333333] hover:border-[#00FF94] transition-colors text-xs"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>VOLVER</span>
          </button>

          {player && (
            <div className="flex gap-4 font-vt323 text-lg">
              <span className="text-[#FFCC00]">⭐ {player.level}</span>
              <span className="text-[#00FF94]">💰 {player.coins}</span>
            </div>
          )}
        </div>

        <div className="text-center mb-8">
          <h1 className="font-press-start text-2xl md:text-4xl text-[#00FF94] mb-2 neon-glow">
            SELECCIONA TU PERSONAJE
          </h1>
          <p className="font-space-mono text-[#AAAAAA]">
            Cada personaje tiene habilidades y stats únicos
          </p>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 mb-8">
          {characters.map((char) => {
            const isLocked = char.is_dlc && !player?.unlocked_dlc;
            const isSelected = selectedCharacter?.id === char.id;

            return (
              <button
                key={char.id}
                data-testid={`character-${char.id}`}
                onClick={() => handleSelectCharacter(char)}
                disabled={isLocked}
                className={`
                  relative p-4 border-2 transition-all
                  ${isSelected ? 'border-[#00FF94] bg-[#00FF94]/10 scale-105' : 'border-[#333333] bg-[#121212]'}
                  ${isLocked ? 'opacity-50 cursor-not-allowed' : 'hover:border-[#00FF94] hover:scale-105 cursor-pointer'}
                  hard-shadow
                `}
              >
                {isLocked && (
                  <div className="absolute top-2 right-2 bg-[#FF00FF] rounded-full p-1">
                    <Lock className="w-4 h-4 text-white" />
                  </div>
                )}

                <div
                  className="w-full h-32 mb-3 flex items-center justify-center text-6xl font-press-start"
                  style={{ color: char.color }}
                >
                  {char.name[0]}
                </div>

                <h3 className="font-press-start text-xs text-white mb-2 truncate">
                  {char.name}
                </h3>
                <p className="font-space-mono text-[10px] text-[#AAAAAA] mb-3">
                  {char.role}
                </p>

                <div className="space-y-1 text-left">
                  <div className="flex justify-between font-vt323 text-sm">
                    <span className="text-[#AAAAAA]">HP</span>
                    <span className="text-[#FF3B30]">{char.health}</span>
                  </div>
                  <div className="flex justify-between font-vt323 text-sm">
                    <span className="text-[#AAAAAA]">ATK</span>
                    <span className="text-[#00FF94]">{char.attack}</span>
                  </div>
                  <div className="flex justify-between font-vt323 text-sm">
                    <span className="text-[#AAAAAA]">DEF</span>
                    <span className="text-[#00FFFF]">{char.defense}</span>
                  </div>
                  <div className="flex justify-between font-vt323 text-sm">
                    <span className="text-[#AAAAAA]">SPD</span>
                    <span className="text-[#FFCC00]">{char.speed}</span>
                  </div>
                </div>

                {char.is_dlc && (
                  <div className="mt-2 bg-[#FF00FF] text-white font-press-start text-[8px] px-2 py-1 text-center">
                    DLC
                  </div>
                )}
              </button>
            );
          })}
        </div>

        {selectedCharacter && (
          <div className="bg-[#121212] border-2 border-[#00FF94] p-6 mb-8 hard-shadow">
            <div className="flex flex-col md:flex-row gap-6">
              <div
                className="w-24 h-24 flex items-center justify-center text-7xl font-press-start"
                style={{ color: selectedCharacter.color }}
              >
                {selectedCharacter.name[0]}
              </div>

              <div className="flex-1">
                <h2 className="font-press-start text-xl text-[#00FF94] mb-2">
                  {selectedCharacter.name}
                </h2>
                <p className="font-space-mono text-[#AAAAAA] mb-3">
                  {selectedCharacter.desc}
                </p>
                <p className="font-vt323 text-[#FFCC00] text-lg">
                  ⚡ Habilidad: {selectedCharacter.special_ability}
                </p>
              </div>

              <button
                data-testid="continue-btn"
                onClick={handleContinue}
                className="bg-[#00FF94] text-black font-press-start px-8 py-4 border-2 border-black hard-shadow hover:translate-y-1 hover:shadow-none transition-all"
              >
                CONTINUAR →
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CharacterSelect;
