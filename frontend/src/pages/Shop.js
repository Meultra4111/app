import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useGame } from '../context/GameContext';
import { ArrowLeft, ShoppingBag, Sword } from 'lucide-react';
import { toast } from 'sonner';

export const Shop = () => {
  const navigate = useNavigate();
  const { player, loading, getShopItems, getShopWeapons, purchaseItem } = useGame();
  const [activeTab, setActiveTab] = useState('items');
  const [items, setItems] = useState([]);
  const [weapons, setWeapons] = useState([]);

  useEffect(() => {
    if (!loading) {
      loadShopData();
    }
  }, [loading]);

  const loadShopData = async () => {
    const itemsList = await getShopItems();
    const weaponsList = await getShopWeapons();
    setItems(itemsList);
    setWeapons(weaponsList);
  };

  const handlePurchase = async (itemId, itemName, price) => {
    try {
      await purchaseItem(itemId);
      toast.success(`¡Compraste ${itemName}!`, {
        description: `Has gastado ${price} monedas`
      });
    } catch (error) {
      if (error.response?.status === 400) {
        toast.error('Monedas insuficientes');
      } else {
        toast.error('Error al comprar');
      }
    }
  };

  const currentItems = activeTab === 'items' ? items : weapons;
  const npcName = activeTab === 'items' ? 'Henryñuy77' : 'Lorenzo13xd';
  const npcDesc = activeTab === 'items' ? '🌌 Vendedor de Ítems' : '🔫 Vendedor de Armas';

  return (
    <div className="min-h-screen bg-[#050505] p-4 md:p-8 relative overflow-hidden">
      <div className="absolute inset-0 scanlines opacity-5"></div>

      <div className="relative z-10 max-w-6xl mx-auto">
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
            <div className="bg-[#121212] border-2 border-[#00FF94] px-6 py-3 font-vt323 text-2xl text-[#00FF94]" data-testid="player-coins-display">
              💰 {player.coins}
            </div>
          )}
        </div>

        <div className="text-center mb-8">
          <h1 className="font-press-start text-2xl md:text-4xl text-[#00FF94] mb-2 neon-glow">
            TIENDA
          </h1>
        </div>

        <div className="bg-[#121212] border-2 border-[#FF00FF] p-6 mb-8">
          <div className="flex items-center gap-4">
            <div className="text-5xl">
              {activeTab === 'items' ? '🌌' : '🔫'}
            </div>
            <div>
              <h2 className="font-press-start text-lg text-[#FF00FF] mb-1">
                {npcName}
              </h2>
              <p className="font-space-mono text-sm text-[#AAAAAA]">
                {npcDesc}
              </p>
            </div>
          </div>
        </div>

        <div className="flex gap-4 mb-8">
          <button
            data-testid="tab-items"
            onClick={() => setActiveTab('items')}
            className={`flex-1 flex items-center justify-center gap-3 py-4 font-press-start border-2 transition-all ${activeTab === 'items' ? 'bg-[#00FF94] text-black border-[#00FF94]' : 'bg-[#1E1E1E] text-white border-[#333333] hover:border-[#00FF94]'}`}
          >
            <ShoppingBag className="w-5 h-5" />
            <span className="text-sm">ÍTEMS</span>
          </button>

          <button
            data-testid="tab-weapons"
            onClick={() => setActiveTab('weapons')}
            className={`flex-1 flex items-center justify-center gap-3 py-4 font-press-start border-2 transition-all ${activeTab === 'weapons' ? 'bg-[#00FF94] text-black border-[#00FF94]' : 'bg-[#1E1E1E] text-white border-[#333333] hover:border-[#00FF94]'}`}
          >
            <Sword className="w-5 h-5" />
            <span className="text-sm">ARMAS</span>
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {currentItems.map((item) => {
            const canAfford = player && player.coins >= item.price;

            return (
              <div key={item.item_id} data-testid={`shop-item-${item.item_id}`} className={`bg-[#121212] border-2 p-6 transition-all ${canAfford ? 'border-[#00FF94] hover:scale-105' : 'border-[#333333] opacity-60'} hard-shadow`}>
                <div className="mb-4 h-24 bg-[#1E1E1E] border border-[#333333] flex items-center justify-center">
                  <div className="text-5xl">{activeTab === 'items' ? '📦' : '⚔️'}</div>
                </div>

                <h3 className="font-press-start text-sm text-white mb-2">{item.name}</h3>
                <p className="font-space-mono text-xs text-[#AAAAAA] mb-4">{item.description}</p>

                {Object.keys(item.stats_boost).length > 0 && (
                  <div className="mb-4 space-y-1">
                    {Object.entries(item.stats_boost).map(([stat, value]) => (
                      <div key={stat} className="flex justify-between font-vt323 text-sm">
                        <span className="text-[#AAAAAA]">{stat.toUpperCase()}</span>
                        <span className="text-[#00FF94]">+{value}</span>
                      </div>
                    ))}
                  </div>
                )}

                <div className="flex items-center justify-between mb-4">
                  <span className="font-vt323 text-2xl text-[#FFCC00]">💰 {item.price}</span>
                </div>

                <button
                  data-testid={`buy-${item.item_id}`}
                  onClick={() => handlePurchase(item.item_id, item.name, item.price)}
                  disabled={!canAfford}
                  className={`w-full font-press-start text-xs py-3 border-2 transition-all ${canAfford ? 'bg-[#00FF94] text-black border-black hover:translate-y-1 cursor-pointer' : 'bg-[#333333] text-[#666666] border-[#1E1E1E] cursor-not-allowed'}`}
                >
                  {canAfford ? 'COMPRAR' : 'SIN FONDOS'}
                </button>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default Shop;
