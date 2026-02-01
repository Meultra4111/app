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

class PlayerStats(BaseModel):
    model_config = ConfigDict(extra="ignore")
    player_id: str
    total_enemies_killed: int = 0
    total_wins: int = 0
    total_games: int = 0
    total_score: int = 0
    total_bullets_shot: int = 0
    total_special_used: int = 0
    total_coins_spent: int = 0
    characters_played: List[str] = []
    maps_played: List[str] = []

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
    bullets_shot: int = 0
    special_used: int = 0

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
    
    player_id = session['player_id']
    await add_xp(player_id, xp_earned)
    await update_coins(player_id, coins_earned)
    
    stats = await db.player_stats.find_one({"player_id": player_id}, {"_id": 0})
    if not stats:
        stats = {
            "player_id": player_id,
            "total_enemies_killed": 0,
            "total_wins": 0,
            "total_games": 0,
            "total_score": 0,
            "total_bullets_shot": 0,
            "total_special_used": 0,
            "total_coins_spent": 0,
            "characters_played": [],
            "maps_played": []
        }
    
    stats["total_enemies_killed"] = stats.get("total_enemies_killed", 0) + update.enemies_defeated
    stats["total_wins"] = stats.get("total_wins", 0) + (1 if update.victory else 0)
    stats["total_games"] = stats.get("total_games", 0) + 1
    stats["total_score"] = stats.get("total_score", 0) + update.score
    stats["total_bullets_shot"] = stats.get("total_bullets_shot", 0) + update.bullets_shot
    stats["total_special_used"] = stats.get("total_special_used", 0) + update.special_used
    
    if session['character_id'] not in stats.get("characters_played", []):
        if "characters_played" not in stats:
            stats["characters_played"] = []
        stats["characters_played"].append(session['character_id'])
    
    if session['map_id'] not in stats.get("maps_played", []):
        if "maps_played" not in stats:
            stats["maps_played"] = []
        stats["maps_played"].append(session['map_id'])
    
    await db.player_stats.update_one(
        {"player_id": player_id},
        {"$set": stats},
        upsert=True
    )
    
    achievements_to_unlock = []
    
    if stats["total_enemies_killed"] >= 1:
        achievements_to_unlock.append("first_blood")
    if stats["total_enemies_killed"] >= 5:
        achievements_to_unlock.append("kill_5")
    if stats["total_enemies_killed"] >= 10:
        achievements_to_unlock.append("kill_10")
    if stats["total_enemies_killed"] >= 25:
        achievements_to_unlock.append("kill_25")
    if stats["total_enemies_killed"] >= 50:
        achievements_to_unlock.append("kill_50")
    if stats["total_enemies_killed"] >= 100:
        achievements_to_unlock.append("kill_100")
    if stats["total_enemies_killed"] >= 250:
        achievements_to_unlock.append("kill_250")
    if stats["total_enemies_killed"] >= 500:
        achievements_to_unlock.append("kill_500")
    
    if stats["total_wins"] >= 1:
        achievements_to_unlock.append("first_win")
    if stats["total_wins"] >= 5:
        achievements_to_unlock.append("win_5")
    if stats["total_wins"] >= 10:
        achievements_to_unlock.append("win_10")
    if stats["total_wins"] >= 25:
        achievements_to_unlock.append("win_25")
    
    if stats["total_games"] >= 10:
        achievements_to_unlock.append("play_10_games")
    if stats["total_games"] >= 25:
        achievements_to_unlock.append("play_25_games")
    if stats["total_games"] >= 50:
        achievements_to_unlock.append("play_50_games")
    
    if stats["total_score"] >= 10000:
        achievements_to_unlock.append("total_score_10k")
    if stats["total_score"] >= 50000:
        achievements_to_unlock.append("total_score_50k")
    
    if stats["total_special_used"] >= 10:
        achievements_to_unlock.append("special_x10")
    if stats["total_special_used"] >= 50:
        achievements_to_unlock.append("special_x50")
    
    if stats["total_bullets_shot"] >= 100:
        achievements_to_unlock.append("bullets_100")
    if stats["total_bullets_shot"] >= 500:
        achievements_to_unlock.append("bullets_500")
    
    if update.victory and update.duration < 90:
        achievements_to_unlock.append("speed_demon")
    
    if len(stats.get("characters_played", [])) >= 8:
        achievements_to_unlock.append("all_chars")
    
    if len(stats.get("maps_played", [])) >= 4:
        achievements_to_unlock.append("all_maps")
    
    if "roblox" in stats.get("maps_played", []):
        achievements_to_unlock.append("map_roblox")
    if "minecraft" in stats.get("maps_played", []):
        achievements_to_unlock.append("map_minecraft")
    if "youtube" in stats.get("maps_played", []):
        achievements_to_unlock.append("map_youtube")
    if "discord" in stats.get("maps_played", []):
        achievements_to_unlock.append("map_discord")
    
    if update.victory:
        char_id = session['character_id']
        if char_id == "meultra4111":
            achievements_to_unlock.append("meultra_win")
        elif char_id == "olivo_10":
            achievements_to_unlock.append("olivo_win")
        elif char_id == "gato":
            achievements_to_unlock.append("gato_win")
        elif char_id == "jhon":
            achievements_to_unlock.append("jhon_win")
    
    player = await db.players.find_one({"player_id": player_id}, {"_id": 0})
    if player:
        if player.get("level", 1) >= 5:
            achievements_to_unlock.append("level_5")
        if player.get("level", 1) >= 10:
            achievements_to_unlock.append("level_10")
            achievements_to_unlock.append("dlc_unlock")
        if player.get("level", 1) >= 15:
            achievements_to_unlock.append("level_15")
        if player.get("level", 1) >= 20:
            achievements_to_unlock.append("level_20")
        
        if player.get("coins", 0) >= 1000:
            achievements_to_unlock.append("coins_1000")
        if player.get("coins", 0) >= 2500:
            achievements_to_unlock.append("coins_2500")
        if player.get("coins", 0) >= 5000:
            achievements_to_unlock.append("coins_5000")
    
    for ach_id in achievements_to_unlock:
        existing = await db.player_achievements.find_one({
            "player_id": player_id,
            "achievement_id": ach_id
        })
        if not existing:
            pa = PlayerAchievement(player_id=player_id, achievement_id=ach_id, unlocked_at=datetime.now(timezone.utc))
            doc = pa.model_dump()
            doc['unlocked_at'] = doc['unlocked_at'].isoformat()
            await db.player_achievements.insert_one(doc)
    
    return {
        "xp_earned": xp_earned,
        "coins_earned": coins_earned,
        "achievements_unlocked": len(achievements_to_unlock),
        "message": "Session completed"
    }

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
        {"achievement_id": "kill_5", "title": "Novato", "description": "Derrota 5 enemigos", "category": "combat", "icon": "🗡️"},
        {"achievement_id": "kill_10", "title": "Guerrero", "description": "Derrota 10 enemigos", "category": "combat", "icon": "⚡"},
        {"achievement_id": "kill_25", "title": "Cazador", "description": "Derrota 25 enemigos", "category": "combat", "icon": "🏹"},
        {"achievement_id": "kill_50", "title": "Exterminador", "description": "Derrota 50 enemigos", "category": "combat", "icon": "💀"},
        {"achievement_id": "kill_100", "title": "Veterano", "description": "Derrota 100 enemigos", "category": "combat", "icon": "🎖️"},
        {"achievement_id": "kill_250", "title": "Leyenda", "description": "Derrota 250 enemigos", "category": "combat", "icon": "👑"},
        {"achievement_id": "kill_500", "title": "Imparable", "description": "Derrota 500 enemigos", "category": "combat", "icon": "🔥"},
        {"achievement_id": "first_win", "title": "Primera Victoria", "description": "Gana tu primera partida", "category": "victory", "icon": "🏆"},
        {"achievement_id": "win_5", "title": "Ganador", "description": "Gana 5 partidas", "category": "victory", "icon": "🎯"},
        {"achievement_id": "win_10", "title": "Campeón", "description": "Gana 10 partidas", "category": "victory", "icon": "👑"},
        {"achievement_id": "win_25", "title": "Maestro", "description": "Gana 25 partidas", "category": "victory", "icon": "🌟"},
        {"achievement_id": "perfect_game", "title": "Perfecta", "description": "Gana sin recibir daño", "category": "victory", "icon": "💎"},
        {"achievement_id": "speed_demon", "title": "Demonio Veloz", "description": "Gana en menos de 90 segundos", "category": "special", "icon": "⚡"},
        {"achievement_id": "survivor", "title": "Superviviente", "description": "Gana con menos de 10% HP", "category": "special", "icon": "❤️"},
        {"achievement_id": "dlc_unlock", "title": "Mi Historia", "description": "Desbloquea el DLC", "category": "progression", "icon": "📦"},
        {"achievement_id": "level_5", "title": "Nivel 5", "description": "Alcanza nivel 5", "category": "progression", "icon": "⭐"},
        {"achievement_id": "level_10", "title": "Nivel 10", "description": "Alcanza nivel 10", "category": "progression", "icon": "🌟"},
        {"achievement_id": "level_15", "title": "Nivel 15", "description": "Alcanza nivel 15", "category": "progression", "icon": "✨"},
        {"achievement_id": "level_20", "title": "Nivel Máximo", "description": "Alcanza nivel 20", "category": "progression", "icon": "💫"},
        {"achievement_id": "all_chars", "title": "Conoce al Team", "description": "Juega con los 8 personajes principales", "category": "exploration", "icon": "👥"},
        {"achievement_id": "all_dlc_chars", "title": "Leyendas DLC", "description": "Juega con los 3 personajes DLC", "category": "exploration", "icon": "🎭"},
        {"achievement_id": "map_roblox", "title": "Robloxiano", "description": "Juega en Roblox World", "category": "exploration", "icon": "🟦"},
        {"achievement_id": "map_minecraft", "title": "Minero", "description": "Juega en Minecraft Biome", "category": "exploration", "icon": "⛏️"},
        {"achievement_id": "map_youtube", "title": "YouTuber", "description": "Juega en YouTube HQ", "category": "exploration", "icon": "📺"},
        {"achievement_id": "map_discord", "title": "Discorder", "description": "Juega en Discord Server", "category": "exploration", "icon": "💬"},
        {"achievement_id": "all_maps", "title": "Explorador Total", "description": "Juega en todos los mapas", "category": "exploration", "icon": "🗺️"},
        {"achievement_id": "first_purchase", "title": "Primera Compra", "description": "Compra tu primer ítem", "category": "shop", "icon": "🛍️"},
        {"achievement_id": "buy_5", "title": "Comprador", "description": "Compra 5 ítems", "category": "shop", "icon": "🛒"},
        {"achievement_id": "buy_10", "title": "Coleccionista", "description": "Compra 10 ítems", "category": "shop", "icon": "📦"},
        {"achievement_id": "buy_20", "title": "Acaparador", "description": "Compra 20 ítems", "category": "shop", "icon": "💼"},
        {"achievement_id": "buy_weapon", "title": "Armado", "description": "Compra tu primera arma", "category": "shop", "icon": "⚔️"},
        {"achievement_id": "coins_1000", "title": "Ahorrativo", "description": "Acumula 1000 monedas", "category": "coins", "icon": "🪙"},
        {"achievement_id": "coins_2500", "title": "Rico", "description": "Acumula 2500 monedas", "category": "coins", "icon": "💰"},
        {"achievement_id": "coins_5000", "title": "Millonario", "description": "Acumula 5000 monedas", "category": "coins", "icon": "💸"},
        {"achievement_id": "spend_1000", "title": "Gastador", "description": "Gasta 1000 monedas", "category": "coins", "icon": "💵"},
        {"achievement_id": "special_x10", "title": "Habilidoso", "description": "Usa habilidad especial 10 veces", "category": "special", "icon": "✨"},
        {"achievement_id": "special_x50", "title": "Maestro de Habilidades", "description": "Usa habilidad especial 50 veces", "category": "special", "icon": "🌠"},
        {"achievement_id": "bullets_100", "title": "Tirador", "description": "Dispara 100 balas", "category": "special", "icon": "🔫"},
        {"achievement_id": "bullets_500", "title": "Francotirador", "description": "Dispara 500 balas", "category": "special", "icon": "🎯"},
        {"achievement_id": "meultra_win", "title": "Líder Meultra", "description": "Gana con Meultra4111", "category": "characters", "icon": "👑"},
        {"achievement_id": "olivo_win", "title": "Golpe Pesado", "description": "Gana con Olivo_10", "category": "characters", "icon": "🔨"},
        {"achievement_id": "gato_win", "title": "Velocidad Felina", "description": "Gana con Gato", "category": "characters", "icon": "🐱"},
        {"achievement_id": "jhon_win", "title": "Sombra Mortal", "description": "Gana con Jhon", "category": "characters", "icon": "🗡️"},
        {"achievement_id": "play_10_games", "title": "Dedicado", "description": "Juega 10 partidas", "category": "special", "icon": "🎮"},
        {"achievement_id": "play_25_games", "title": "Adicto", "description": "Juega 25 partidas", "category": "special", "icon": "🕹️"},
        {"achievement_id": "play_50_games", "title": "Pro Gamer", "description": "Juega 50 partidas", "category": "special", "icon": "🏅"},
        {"achievement_id": "total_score_10k", "title": "Puntuador", "description": "Acumula 10,000 puntos totales", "category": "special", "icon": "📊"},
        {"achievement_id": "total_score_50k", "title": "Maestro del Score", "description": "Acumula 50,000 puntos totales", "category": "special", "icon": "📈"},
        {"achievement_id": "henryshop_visit", "title": "Cliente de Henry", "description": "Visita la tienda de Henryñuy77", "category": "shop", "icon": "🌌"},
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