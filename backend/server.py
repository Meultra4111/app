from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict
import uuid
from datetime import datetime, timezone


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# ==================== MODELS ====================

class Character(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    name: str
    role: str
    desc: str
    color: str
    health: int = 100
    attack: int = 15
    defense: int = 10
    speed: int = 5
    special_ability: str = "Special Attack"
    is_dlc: bool = False

class Player(BaseModel):
    model_config = ConfigDict(extra="ignore")
    player_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    level: int = 1
    xp: int = 0
    coins: int = 1000
    unlocked_dlc: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Achievement(BaseModel):
    model_config = ConfigDict(extra="ignore")
    achievement_id: str
    title: str
    description: str
    category: str
    icon: str = "🏆"
    unlocked: bool = False

class PlayerAchievement(BaseModel):
    model_config = ConfigDict(extra="ignore")
    player_id: str
    achievement_id: str
    unlocked_at: Optional[datetime] = None

class GameSession(BaseModel):
    model_config = ConfigDict(extra="ignore")
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    player_id: str
    character_id: str
    map_id: str
    score: int = 0
    enemies_defeated: int = 0
    victory: bool = False
    xp_earned: int = 0
    coins_earned: int = 0
    duration: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ShopItem(BaseModel):
    model_config = ConfigDict(extra="ignore")
    item_id: str
    name: str
    description: str
    price: int
    type: str
    stats_boost: Dict = {}

class PlayerInventory(BaseModel):
    model_config = ConfigDict(extra="ignore")
    player_id: str
    item_id: str
    quantity: int = 1
    purchased_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# ==================== INPUT MODELS ====================

class PlayerCreate(BaseModel):
    username: str

class GameSessionCreate(BaseModel):
    player_id: str
    character_id: str
    map_id: str

class GameSessionUpdate(BaseModel):
    score: int
    enemies_defeated: int
    victory: bool
    duration: int

class PurchaseItem(BaseModel):
    player_id: str
    item_id: str


# ==================== ROUTES ====================

@api_router.get("/")
async def root():
    return {"message": "Team Meultra Battle Arena API"}

# ===== CHARACTERS =====
@api_router.get("/characters", response_model=List[Character])
async def get_characters():
    characters = [
        Character(id="meultra4111", name="Meultra4111", role="Leader", desc="Fuerte y balanceado. Espada de Minecraft.", color="#00FF94", health=120, attack=18, defense=12, speed=6, special_ability="Thunder Strike"),
        Character(id="olivo_10", name="Olivo_10", role="Striker", desc="Elegante con mazo. Daño pesado.", color="#FFFF00", health=150, attack=25, defense=8, speed=3, special_ability="Ground Slam"),
        Character(id="gato", name="Gato", role="Speedster", desc="Rápido, estilo Roblox.", color="#FFA500", health=80, attack=12, defense=8, speed=10, special_ability="Quick Dash"),
        Character(id="jhon", name="Jhon", role="Assassin", desc="Sigiloso, espadas negras.", color="#FFFFFF", health=90, attack=20, defense=6, speed=8, special_ability="Shadow Strike"),
        Character(id="riptor", name="Riptor", role="Fighter", desc="Combate cercano.", color="#FF0000", health=110, attack=16, defense=14, speed=5, special_ability="Rampage"),
        Character(id="martin", name="Martin", role="Mage", desc="Misterioso, ataques a distancia.", color="#A020F0", health=70, attack=22, defense=5, speed=4, special_ability="Magic Blast"),
        Character(id="botsito", name="Botsito", role="Tank", desc="Resistente, forma humanoide.", color="#0000FF", health=180, attack=10, defense=20, speed=2, special_ability="Iron Wall"),
        Character(id="brayan", name="Brayan", role="Beast", desc="Salvaje, perro alemán.", color="#8B4513", health=130, attack=19, defense=11, speed=7, special_ability="Beast Mode"),
        Character(id="thisand", name="Thisand", role="Boss", desc="Aura blanca intensa. Lanza peces.", color="#FFFFFF", health=300, attack=35, defense=25, speed=6, special_ability="Fish Storm", is_dlc=True),
        Character(id="notfik", name="Notfik", role="DLC Warrior", desc="Guerrero del DLC.", color="#FF00FF", health=140, attack=23, defense=13, speed=6, special_ability="Chaos Wave", is_dlc=True),
        Character(id="nooblord", name="Nooblord", role="DLC Tank", desc="Tank del DLC.", color="#00FFFF", health=160, attack=14, defense=18, speed=4, special_ability="Noob Shield", is_dlc=True),
    ]
    return characters

@api_router.get("/characters/{character_id}", response_model=Character)
async def get_character(character_id: str):
    characters = await get_characters()
    for char in characters:
        if char.id == character_id:
            return char
    raise HTTPException(status_code=404, detail="Character not found")

# ===== PLAYERS =====
@api_router.post("/players", response_model=Player)
async def create_player(player_input: PlayerCreate):
    player = Player(username=player_input.username)
    doc = player.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.players.insert_one(doc)
    return player

@api_router.get("/players/{player_id}", response_model=Player)
async def get_player(player_id: str):
    player = await db.players.find_one({"player_id": player_id}, {"_id": 0})
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    if isinstance(player.get('created_at'), str):
        player['created_at'] = datetime.fromisoformat(player['created_at'])
    return Player(**player)

@api_router.put("/players/{player_id}/xp")
async def add_xp(player_id: str, xp: int):
    player = await db.players.find_one({"player_id": player_id}, {"_id": 0})
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    new_xp = player['xp'] + xp
    new_level = player['level']
    xp_for_next_level = new_level * 100
    
    if new_xp >= xp_for_next_level:
        new_level += 1
        new_xp = new_xp - xp_for_next_level
    
    if new_level >= 10 and not player.get('unlocked_dlc', False):
        await db.players.update_one(
            {"player_id": player_id},
            {"$set": {"xp": new_xp, "level": new_level, "unlocked_dlc": True}}
        )
    else:
        await db.players.update_one(
            {"player_id": player_id},
            {"$set": {"xp": new_xp, "level": new_level}}
        )
    
    updated_player = await db.players.find_one({"player_id": player_id}, {"_id": 0})
    if isinstance(updated_player.get('created_at'), str):
        updated_player['created_at'] = datetime.fromisoformat(updated_player['created_at'])
    return Player(**updated_player)

@api_router.put("/players/{player_id}/coins")
async def update_coins(player_id: str, amount: int):
    player = await db.players.find_one({"player_id": player_id}, {"_id": 0})
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    new_coins = player['coins'] + amount
    if new_coins < 0:
        raise HTTPException(status_code=400, detail="Insufficient coins")
    
    await db.players.update_one(
        {"player_id": player_id},
        {"$set": {"coins": new_coins}}
    )
    
    updated_player = await db.players.find_one({"player_id": player_id}, {"_id": 0})
    if isinstance(updated_player.get('created_at'), str):
        updated_player['created_at'] = datetime.fromisoformat(updated_player['created_at'])
    return Player(**updated_player)

# ===== GAME SESSIONS =====
@api_router.post("/game/session", response_model=GameSession)
async def create_game_session(session_input: GameSessionCreate):
    session = GameSession(
        player_id=session_input.player_id,
        character_id=session_input.character_id,
        map_id=session_input.map_id
    )
    doc = session.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.game_sessions.insert_one(doc)
    return session

@api_router.put("/game/session/{session_id}")
async def update_game_session(session_id: str, update: GameSessionUpdate):
    session = await db.game_sessions.find_one({"session_id": session_id}, {"_id": 0})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    xp_earned = update.enemies_defeated * 10 + (50 if update.victory else 0)
    coins_earned = update.enemies_defeated * 5 + (100 if update.victory else 25)
    
    await db.game_sessions.update_one(
        {"session_id": session_id},
        {"$set": {
            "score": update.score,
            "enemies_defeated": update.enemies_defeated,
            "victory": update.victory,
            "duration": update.duration,
            "xp_earned": xp_earned,
            "coins_earned": coins_earned
        }}
    )
    
    await add_xp(session['player_id'], xp_earned)
    await update_coins(session['player_id'], coins_earned)
    
    return {"xp_earned": xp_earned, "coins_earned": coins_earned, "message": "Session completed"}

@api_router.get("/game/sessions/{player_id}", response_model=List[GameSession])
async def get_player_sessions(player_id: str):
    sessions = await db.game_sessions.find({"player_id": player_id}, {"_id": 0}).to_list(100)
    for session in sessions:
        if isinstance(session.get('created_at'), str):
            session['created_at'] = datetime.fromisoformat(session['created_at'])
    return [GameSession(**s) for s in sessions]

# ===== ACHIEVEMENTS =====
@api_router.get("/achievements")
async def get_achievements():
    achievements = [
        {"achievement_id": "first_blood", "title": "Primera Sangre", "description": "Derrota tu primer enemigo", "category": "combat", "icon": "⚔️"},
        {"achievement_id": "veteran", "title": "Veterano", "description": "Derrota 100 enemigos", "category": "combat", "icon": "🎖️"},
        {"achievement_id": "unstoppable", "title": "Imparable", "description": "Gana 10 partidas seguidas", "category": "victory", "icon": "🔥"},
        {"achievement_id": "dlc_unlock", "title": "Historia Desbloqueada", "description": "Desbloquea el DLC 'Mi Historia'", "category": "progression", "icon": "📦"},
        {"achievement_id": "boss_slayer", "title": "Asesino de Jefes", "description": "Derrota a Thisand", "category": "combat", "icon": "👑"},
        {"achievement_id": "speed_demon", "title": "Demonio Veloz", "description": "Completa una partida en menos de 2 minutos", "category": "special", "icon": "⚡"},
        {"achievement_id": "collector", "title": "Coleccionista", "description": "Compra 20 ítems en las tiendas", "category": "shop", "icon": "🛒"},
        {"achievement_id": "rich", "title": "Rico", "description": "Acumula 5000 monedas", "category": "coins", "icon": "💰"},
        {"achievement_id": "max_level", "title": "Nivel Máximo", "description": "Alcanza nivel 20", "category": "progression", "icon": "⭐"},
        {"achievement_id": "explorer", "title": "Explorador", "description": "Juega en los 4 mapas", "category": "exploration", "icon": "🗺️"},
    ]
    return achievements

@api_router.get("/achievements/{player_id}")
async def get_player_achievements(player_id: str):
    player_achievements = await db.player_achievements.find({"player_id": player_id}, {"_id": 0}).to_list(100)
    all_achievements = await get_achievements()
    
    unlocked_ids = {pa['achievement_id'] for pa in player_achievements}
    
    result = []
    for ach in all_achievements:
        ach['unlocked'] = ach['achievement_id'] in unlocked_ids
        result.append(ach)
    
    return result

@api_router.post("/achievements/{player_id}/{achievement_id}")
async def unlock_achievement(player_id: str, achievement_id: str):
    existing = await db.player_achievements.find_one({
        "player_id": player_id,
        "achievement_id": achievement_id
    }, {"_id": 0})
    
    if existing:
        return {"message": "Achievement already unlocked"}
    
    pa = PlayerAchievement(player_id=player_id, achievement_id=achievement_id, unlocked_at=datetime.now(timezone.utc))
    doc = pa.model_dump()
    doc['unlocked_at'] = doc['unlocked_at'].isoformat()
    await db.player_achievements.insert_one(doc)
    
    return {"message": "Achievement unlocked!"}

# ===== SHOP =====
@api_router.get("/shop/items")
async def get_shop_items():
    items = [
        {"item_id": "health_potion", "name": "Poción de Vida", "description": "+50 HP", "price": 100, "type": "consumable", "stats_boost": {"health": 50}},
        {"item_id": "speed_boots", "name": "Botas de Velocidad", "description": "+2 Velocidad", "price": 250, "type": "equipment", "stats_boost": {"speed": 2}},
        {"item_id": "shield", "name": "Escudo", "description": "+5 Defensa", "price": 300, "type": "equipment", "stats_boost": {"defense": 5}},
        {"item_id": "power_gem", "name": "Gema de Poder", "description": "+3 Ataque", "price": 200, "type": "equipment", "stats_boost": {"attack": 3}},
        {"item_id": "lucky_coin", "name": "Moneda de la Suerte", "description": "x2 monedas en partida", "price": 500, "type": "special", "stats_boost": {}},
    ]
    return items

@api_router.get("/shop/weapons")
async def get_shop_weapons():
    weapons = [
        {"item_id": "diamond_sword", "name": "Espada de Diamante", "description": "+10 Ataque", "price": 600, "type": "weapon", "stats_boost": {"attack": 10}},
        {"item_id": "iron_axe", "name": "Hacha de Hierro", "description": "+8 Ataque, +2 Defensa", "price": 500, "type": "weapon", "stats_boost": {"attack": 8, "defense": 2}},
        {"item_id": "golden_bow", "name": "Arco Dorado", "description": "+7 Ataque, +3 Velocidad", "price": 550, "type": "weapon", "stats_boost": {"attack": 7, "speed": 3}},
        {"item_id": "magic_staff", "name": "Bastón Mágico", "description": "+12 Ataque especial", "price": 700, "type": "weapon", "stats_boost": {"attack": 12}},
        {"item_id": "legendary_hammer", "name": "Martillo Legendario", "description": "+15 Ataque, -1 Velocidad", "price": 900, "type": "weapon", "stats_boost": {"attack": 15, "speed": -1}},
    ]
    return weapons

@api_router.post("/shop/purchase")
async def purchase_item(purchase: PurchaseItem):
    player = await db.players.find_one({"player_id": purchase.player_id}, {"_id": 0})
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    all_items = await get_shop_items() + await get_shop_weapons()
    item = next((i for i in all_items if i['item_id'] == purchase.item_id), None)
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    if player['coins'] < item['price']:
        raise HTTPException(status_code=400, detail="Insufficient coins")
    
    await update_coins(purchase.player_id, -item['price'])
    
    inventory_item = PlayerInventory(player_id=purchase.player_id, item_id=purchase.item_id)
    doc = inventory_item.model_dump()
    doc['purchased_at'] = doc['purchased_at'].isoformat()
    await db.player_inventory.insert_one(doc)
    
    return {"message": "Item purchased successfully", "item": item}

@api_router.get("/shop/inventory/{player_id}")
async def get_player_inventory(player_id: str):
    inventory = await db.player_inventory.find({"player_id": player_id}, {"_id": 0}).to_list(100)
    return inventory

# ===== MAPS =====
@api_router.get("/maps")
async def get_maps():
    maps = [
        {"id": "roblox", "name": "Roblox World", "theme": "Blocky, Plastic textures", "difficulty": "Easy"},
        {"id": "minecraft", "name": "Minecraft Biome", "theme": "Voxel, Pixelated nature", "difficulty": "Medium"},
        {"id": "youtube", "name": "YouTube HQ", "theme": "Red/White, Video screens", "difficulty": "Hard"},
        {"id": "discord", "name": "Discord Server", "theme": "Blurple, Chat bubbles", "difficulty": "Expert"},
    ]
    return maps

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()