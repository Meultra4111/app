import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const GameContext = createContext();

export const useGame = () => {
  const context = useContext(GameContext);
  if (!context) {
    throw new Error('useGame must be used within GameProvider');
  }
  return context;
};

export const GameProvider = ({ children }) => {
  const [player, setPlayer] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    initializePlayer();
  }, []);

  const initializePlayer = async () => {
    try {
      let playerId = localStorage.getItem('player_id');
      
      if (!playerId) {
        const username = `Player_${Math.floor(Math.random() * 10000)}`;
        const response = await axios.post(`${API}/players`, { username });
        playerId = response.data.player_id;
        localStorage.setItem('player_id', playerId);
        setPlayer(response.data);
      } else {
        const response = await axios.get(`${API}/players/${playerId}`);
        setPlayer(response.data);
      }
    } catch (error) {
      console.error('Error initializing player:', error);
      localStorage.removeItem('player_id');
      const username = `Player_${Math.floor(Math.random() * 10000)}`;
      const response = await axios.post(`${API}/players`, { username });
      localStorage.setItem('player_id', response.data.player_id);
      setPlayer(response.data);
    } finally {
      setLoading(false);
    }
  };

  const refreshPlayer = async () => {
    try {
      const playerId = localStorage.getItem('player_id');
      if (playerId) {
        const response = await axios.get(`${API}/players/${playerId}`);
        setPlayer(response.data);
      }
    } catch (error) {
      console.error('Error refreshing player:', error);
    }
  };

  const getCharacters = async () => {
    try {
      const response = await axios.get(`${API}/characters`);
      return response.data;
    } catch (error) {
      console.error('Error fetching characters:', error);
      return [];
    }
  };

  const getMaps = async () => {
    try {
      const response = await axios.get(`${API}/maps`);
      return response.data;
    } catch (error) {
      console.error('Error fetching maps:', error);
      return [];
    }
  };

  const createGameSession = async (characterId, mapId) => {
    try {
      const response = await axios.post(`${API}/game/session`, {
        player_id: player.player_id,
        character_id: characterId,
        map_id: mapId
      });
      return response.data;
    } catch (error) {
      console.error('Error creating game session:', error);
      return null;
    }
  };

  const completeGameSession = async (sessionId, gameData) => {
    try {
      const response = await axios.put(`${API}/game/session/${sessionId}`, gameData);
      await refreshPlayer();
      return response.data;
    } catch (error) {
      console.error('Error completing game session:', error);
      return null;
    }
  };

  const getAchievements = async () => {
    try {
      const response = await axios.get(`${API}/achievements/${player.player_id}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching achievements:', error);
      return [];
    }
  };

  const unlockAchievement = async (achievementId) => {
    try {
      await axios.post(`${API}/achievements/${player.player_id}/${achievementId}`);
    } catch (error) {
      console.error('Error unlocking achievement:', error);
    }
  };

  const getShopItems = async () => {
    try {
      const response = await axios.get(`${API}/shop/items`);
      return response.data;
    } catch (error) {
      console.error('Error fetching shop items:', error);
      return [];
    }
  };

  const getShopWeapons = async () => {
    try {
      const response = await axios.get(`${API}/shop/weapons`);
      return response.data;
    } catch (error) {
      console.error('Error fetching shop weapons:', error);
      return [];
    }
  };

  const purchaseItem = async (itemId) => {
    try {
      const response = await axios.post(`${API}/shop/purchase`, {
        player_id: player.player_id,
        item_id: itemId
      });
      await refreshPlayer();
      return response.data;
    } catch (error) {
      console.error('Error purchasing item:', error);
      throw error;
    }
  };

  const value = {
    player,
    loading,
    refreshPlayer,
    getCharacters,
    getMaps,
    createGameSession,
    completeGameSession,
    getAchievements,
    unlockAchievement,
    getShopItems,
    getShopWeapons,
    purchaseItem
  };

  return <GameContext.Provider value={value}>{children}</GameContext.Provider>;
};
