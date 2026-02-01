import React, { useEffect, useRef, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useGame } from '../context/GameContext';

export const GameArena = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const canvasRef = useRef(null);
  const { player, createGameSession, completeGameSession } = useGame();
  
  const character = location.state?.character;
  const map = location.state?.map;
  
  const [gameState, setGameState] = useState({
    health: 100,
    enemiesDefeated: 0,
    score: 0,
    gameOver: false,
    victory: false,
    timeElapsed: 0
  });
  
  const gameDataRef = useRef({
    sessionId: null,
    player: null,
    enemies: [],
    bullets: [],
    particles: [],
    keys: {},
    lastTime: 0,
    startTime: Date.now(),
    bulletsShot: 0,
    specialUsed: 0
  });

  useEffect(() => {
    if (!character || !map) {
      navigate('/');
      return;
    }

    initGame();
    
    return () => {
      const canvas = canvasRef.current;
      if (canvas) {
        canvas.removeEventListener('mousemove', handleMouseMove);
        canvas.removeEventListener('click', handleClick);
      }
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('keyup', handleKeyUp);
    };
  }, []);

  const initGame = async () => {
    const session = await createGameSession(character.id, map.id);
    gameDataRef.current.sessionId = session?.session_id;

    const canvas = canvasRef.current;
    canvas.width = 1200;
    canvas.height = 600;

    gameDataRef.current.player = {
      x: canvas.width / 2,
      y: canvas.height / 2,
      width: 32,
      height: 32,
      speed: character.speed * 2,
      color: character.color,
      health: character.health,
      maxHealth: character.health,
      attack: character.attack,
      mouseX: canvas.width / 2,
      mouseY: canvas.height / 2
    };

    setGameState(prev => ({
      ...prev,
      health: character.health
    }));

    spawnEnemies();

    canvas.addEventListener('mousemove', handleMouseMove);
    canvas.addEventListener('click', handleClick);
    window.addEventListener('keydown', handleKeyDown);
    window.addEventListener('keyup', handleKeyUp);

    requestAnimationFrame(gameLoop);
  };

  const handleMouseMove = (e) => {
    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    
    gameDataRef.current.player.mouseX = (e.clientX - rect.left) * scaleX;
    gameDataRef.current.player.mouseY = (e.clientY - rect.top) * scaleY;
  };

  const handleClick = () => {
    shoot();
  };

  const handleKeyDown = (e) => {
    gameDataRef.current.keys[e.key.toLowerCase()] = true;
    
    if (e.key === ' ') {
      e.preventDefault();
      useSpecialAbility();
    }
  };

  const handleKeyUp = (e) => {
    gameDataRef.current.keys[e.key.toLowerCase()] = false;
  };

  const shoot = () => {
    const p = gameDataRef.current.player;
    const angle = Math.atan2(p.mouseY - p.y, p.mouseX - p.x);
    
    gameDataRef.current.bullets.push({
      x: p.x,
      y: p.y,
      vx: Math.cos(angle) * 10,
      vy: Math.sin(angle) * 10,
      damage: character.attack,
      size: 8,
      color: character.color,
      isPlayer: true
    });
  };

  const useSpecialAbility = () => {
    const p = gameDataRef.current.player;
    const enemies = gameDataRef.current.enemies;
    
    enemies.forEach(enemy => {
      const dx = enemy.x - p.x;
      const dy = enemy.y - p.y;
      const distance = Math.sqrt(dx * dx + dy * dy);
      
      if (distance < 150) {
        enemy.health -= character.attack * 2;
        createParticles(enemy.x, enemy.y, character.color);
      }
    });
  };

  const spawnEnemies = () => {
    const canvas = canvasRef.current;
    const count = 5 + Math.floor(Math.random() * 3);
    
    for (let i = 0; i < count; i++) {
      const edge = Math.floor(Math.random() * 4);
      let x, y;
      
      switch (edge) {
        case 0: x = Math.random() * canvas.width; y = 0; break;
        case 1: x = canvas.width; y = Math.random() * canvas.height; break;
        case 2: x = Math.random() * canvas.width; y = canvas.height; break;
        case 3: x = 0; y = Math.random() * canvas.height; break;
      }
      
      gameDataRef.current.enemies.push({
        x,
        y,
        width: 28,
        height: 28,
        speed: 1 + Math.random() * 1.5,
        health: 30 + Math.random() * 20,
        maxHealth: 50,
        color: '#FF3B30',
        lastShot: 0
      });
    }
  };

  const createParticles = (x, y, color) => {
    for (let i = 0; i < 8; i++) {
      const angle = (Math.PI * 2 * i) / 8;
      gameDataRef.current.particles.push({
        x, y,
        vx: Math.cos(angle) * 3,
        vy: Math.sin(angle) * 3,
        size: 4,
        color,
        life: 30
      });
    }
  };

  const gameLoop = (currentTime) => {
    const deltaTime = currentTime - gameDataRef.current.lastTime;
    gameDataRef.current.lastTime = currentTime;

    update(deltaTime);
    render();

    if (!gameState.gameOver) {
      requestAnimationFrame(gameLoop);
    }
  };

  const update = (deltaTime) => {
    const canvas = canvasRef.current;
    const p = gameDataRef.current.player;
    const keys = gameDataRef.current.keys;

    if (keys['w'] || keys['arrowup']) p.y -= p.speed;
    if (keys['s'] || keys['arrowdown']) p.y += p.speed;
    if (keys['a'] || keys['arrowleft']) p.x -= p.speed;
    if (keys['d'] || keys['arrowright']) p.x += p.speed;

    p.x = Math.max(p.width / 2, Math.min(canvas.width - p.width / 2, p.x));
    p.y = Math.max(p.height / 2, Math.min(canvas.height - p.height / 2, p.y));

    gameDataRef.current.bullets = gameDataRef.current.bullets.filter(bullet => {
      bullet.x += bullet.vx;
      bullet.y += bullet.vy;
      return bullet.x > 0 && bullet.x < canvas.width && bullet.y > 0 && bullet.y < canvas.height;
    });

    gameDataRef.current.enemies = gameDataRef.current.enemies.filter(enemy => {
      const dx = p.x - enemy.x;
      const dy = p.y - enemy.y;
      const distance = Math.sqrt(dx * dx + dy * dy);
      
      enemy.x += (dx / distance) * enemy.speed;
      enemy.y += (dy / distance) * enemy.speed;

      if (distance < 200 && Date.now() - enemy.lastShot > 1000) {
        const angle = Math.atan2(p.y - enemy.y, p.x - enemy.x);
        gameDataRef.current.bullets.push({
          x: enemy.x,
          y: enemy.y,
          vx: Math.cos(angle) * 5,
          vy: Math.sin(angle) * 5,
          damage: 5,
          size: 6,
          color: '#FF3B30',
          isPlayer: false
        });
        enemy.lastShot = Date.now();
      }

      if (distance < 40) {
        p.health -= 0.5;
      }

      gameDataRef.current.bullets.forEach((bullet, bIndex) => {
        if (bullet.isPlayer) {
          const bDist = Math.sqrt((bullet.x - enemy.x) ** 2 + (bullet.y - enemy.y) ** 2);
          if (bDist < 20) {
            enemy.health -= bullet.damage;
            createParticles(bullet.x, bullet.y, character.color);
            gameDataRef.current.bullets.splice(bIndex, 1);
          }
        }
      });

      if (enemy.health <= 0) {
        createParticles(enemy.x, enemy.y, '#FFCC00');
        setGameState(prev => ({
          ...prev,
          enemiesDefeated: prev.enemiesDefeated + 1,
          score: prev.score + 100
        }));
        
        if (gameDataRef.current.enemies.length <= 1) {
          setTimeout(spawnEnemies, 1000);
        }
        
        return false;
      }

      return true;
    });

    gameDataRef.current.bullets.forEach((bullet, index) => {
      if (!bullet.isPlayer) {
        const bDist = Math.sqrt((bullet.x - p.x) ** 2 + (bullet.y - p.y) ** 2);
        if (bDist < 20) {
          p.health -= bullet.damage;
          createParticles(bullet.x, bullet.y, '#FF3B30');
          gameDataRef.current.bullets.splice(index, 1);
        }
      }
    });

    gameDataRef.current.particles = gameDataRef.current.particles.filter(particle => {
      particle.x += particle.vx;
      particle.y += particle.vy;
      particle.life--;
      return particle.life > 0;
    });

    setGameState(prev => ({
      ...prev,
      health: Math.max(0, p.health),
      timeElapsed: Math.floor((Date.now() - gameDataRef.current.startTime) / 1000)
    }));

    if (p.health <= 0) {
      endGame(false);
    }

    if (gameState.enemiesDefeated >= 20) {
      endGame(true);
    }
  };

  const render = () => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    
    ctx.fillStyle = '#0a0a0a';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    ctx.strokeStyle = '#1a1a1a';
    ctx.lineWidth = 1;
    for (let i = 0; i < canvas.width; i += 40) {
      ctx.beginPath();
      ctx.moveTo(i, 0);
      ctx.lineTo(i, canvas.height);
      ctx.stroke();
    }
    for (let i = 0; i < canvas.height; i += 40) {
      ctx.beginPath();
      ctx.moveTo(0, i);
      ctx.lineTo(canvas.width, i);
      ctx.stroke();
    }

    const p = gameDataRef.current.player;
    ctx.fillStyle = p.color;
    ctx.fillRect(p.x - p.width / 2, p.y - p.height / 2, p.width, p.height);
    ctx.strokeStyle = '#FFFFFF';
    ctx.lineWidth = 2;
    ctx.strokeRect(p.x - p.width / 2, p.y - p.height / 2, p.width, p.height);

    gameDataRef.current.enemies.forEach(enemy => {
      ctx.fillStyle = enemy.color;
      ctx.fillRect(enemy.x - enemy.width / 2, enemy.y - enemy.height / 2, enemy.width, enemy.height);
      
      const healthBarWidth = enemy.width;
      const healthPercent = enemy.health / enemy.maxHealth;
      ctx.fillStyle = '#333';
      ctx.fillRect(enemy.x - healthBarWidth / 2, enemy.y - enemy.height / 2 - 8, healthBarWidth, 4);
      ctx.fillStyle = '#00FF94';
      ctx.fillRect(enemy.x - healthBarWidth / 2, enemy.y - enemy.height / 2 - 8, healthBarWidth * healthPercent, 4);
    });

    gameDataRef.current.bullets.forEach(bullet => {
      ctx.fillStyle = bullet.color;
      ctx.beginPath();
      ctx.arc(bullet.x, bullet.y, bullet.size, 0, Math.PI * 2);
      ctx.fill();
    });

    gameDataRef.current.particles.forEach(particle => {
      ctx.fillStyle = particle.color;
      ctx.globalAlpha = particle.life / 30;
      ctx.fillRect(particle.x, particle.y, particle.size, particle.size);
      ctx.globalAlpha = 1;
    });
  };

  const endGame = async (victory) => {
    setGameState(prev => ({ ...prev, gameOver: true, victory }));
    
    const duration = Math.floor((Date.now() - gameDataRef.current.startTime) / 1000);
    
    if (gameDataRef.current.sessionId) {
      const result = await completeGameSession(gameDataRef.current.sessionId, {
        score: gameState.score,
        enemies_defeated: gameState.enemiesDefeated,
        victory,
        duration
      });
      
      setTimeout(() => {
        navigate('/game-over', {
          state: {
            victory,
            score: gameState.score,
            enemiesDefeated: gameState.enemiesDefeated,
            xpEarned: result?.xp_earned || 0,
            coinsEarned: result?.coins_earned || 0,
            duration
          }
        });
      }, 2000);
    }
  };

  return (
    <div className="min-h-screen bg-[#050505] flex flex-col items-center justify-center p-4 relative overflow-hidden">
      <div className="hud top-4 left-4 right-4 flex justify-between items-start">
        <div className="bg-[#121212]/90 border-2 border-[#00FF94] p-3" data-testid="game-hud-stats">
          <div className="text-[#FFFFFF] text-2xl mb-2">❤️ HP: {Math.floor(gameState.health)}/{character?.health}</div>
          <div className="w-64 h-6 bg-[#333333] border border-[#00FF94]">
            <div
              className="h-full bg-[#00FF94] transition-all"
              style={{ width: `${(gameState.health / character?.health) * 100}%` }}
            ></div>
          </div>
        </div>

        <div className="bg-[#121212]/90 border-2 border-[#FFCC00] p-3 text-right" data-testid="game-hud-score">
          <div className="text-[#FFFFFF] text-xl">⚔️ ENEMIGOS: {gameState.enemiesDefeated}</div>
          <div className="text-[#FFCC00] text-xl">⭐ SCORE: {gameState.score}</div>
          <div className="text-[#AAAAAA] text-lg">⏱️ {gameState.timeElapsed}s</div>
        </div>
      </div>

      <div className="relative">
        <canvas
          ref={canvasRef}
          data-testid="game-canvas"
          className="border-4 border-[#00FF94] shadow-[0_0_30px_rgba(0,255,148,0.3)]"
        />
        
        {gameState.gameOver && (
          <div className="absolute inset-0 bg-black/80 flex items-center justify-center">
            <div className="text-center">
              <h1 className={`font-press-start text-4xl mb-4 ${gameState.victory ? 'text-[#00FF94] neon-glow' : 'text-[#FF3B30]'}`}>
                {gameState.victory ? '¡VICTORIA!' : 'DERROTA'}
              </h1>
              <p className="font-vt323 text-white text-2xl">Redirigiendo...</p>
            </div>
          </div>
        )}
      </div>

      <div className="mt-4 bg-[#121212]/90 border-2 border-[#333333] p-4 max-w-2xl" data-testid="game-controls">
        <div className="font-space-mono text-sm text-[#AAAAAA] grid grid-cols-2 gap-4">
          <div>
            <span className="text-[#00FF94]">WASD</span> - Mover
          </div>
          <div>
            <span className="text-[#00FF94]">CLICK</span> - Disparar
          </div>
          <div>
            <span className="text-[#00FF94]">ESPACIO</span> - Habilidad Especial
          </div>
          <div>
            <span className="text-[#FFCC00]">Meta</span> - 20 Enemigos
          </div>
        </div>
      </div>
    </div>
  );
};

export default GameArena;
