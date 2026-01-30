import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { GameProvider } from './context/GameContext';
import { Toaster } from './components/ui/sonner';
import MainMenu from './pages/MainMenu';
import CharacterSelect from './pages/CharacterSelect';
import MapSelect from './pages/MapSelect';
import GameArena from './pages/GameArena';
import GameOver from './pages/GameOver';
import Achievements from './pages/Achievements';
import Shop from './pages/Shop';
import Training from './pages/Training';
import './App.css';

function App() {
  return (
    <GameProvider>
      <BrowserRouter>
        <div className="App">
          <Routes>
            <Route path="/" element={<MainMenu />} />
            <Route path="/character-select" element={<CharacterSelect />} />
            <Route path="/map-select" element={<MapSelect />} />
            <Route path="/game" element={<GameArena />} />
            <Route path="/game-over" element={<GameOver />} />
            <Route path="/achievements" element={<Achievements />} />
            <Route path="/shop" element={<Shop />} />
            <Route path="/training" element={<Training />} />
          </Routes>
          <Toaster position="top-right" />
        </div>
      </BrowserRouter>
    </GameProvider>
  );
}

export default App;
