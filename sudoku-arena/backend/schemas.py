from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

# --- User Schemas ---
class UserCreate(BaseModel):
    name: str
    email: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    gold: int
    gems: int
    current_floor: int
    max_floor: int
    play_time: int
    created_at: datetime

    class Config:
        from_attributes = True

# --- Hero Schemas ---
class HeroResponse(BaseModel):
    id: int
    name: str
    element: str
    rarity: str
    skill_name: str
    skill_description: str
    is_active: bool
    weight: int

    class Config:
        from_attributes = True

# --- Item Schemas ---
class ItemResponse(BaseModel):
    id: int
    name: str
    description: str

    class Config:
        from_attributes = True

# --- Achievement Schemas ---
class AchievementResponse(BaseModel):
    id: int
    title: str
    description: str
    category: str

    class Config:
        from_attributes = True

# --- Player Hero Schemas ---
class PlayerHeroResponse(BaseModel):
    id: int
    user_id: int
    hero_id: int
    level: int
    stars: int
    intimacy: int
    is_in_team: bool
    hero: HeroResponse

    class Config:
        from_attributes = True

# --- Gacha Schemas ---
class GachaRequest(BaseModel):
    user_id: int
    draw_count: int  # 1 or 10

class GachaResultItem(BaseModel):
    hero: HeroResponse
    is_new: bool
    stars_after: int
    gems_compensated: int

class GachaResponse(BaseModel):
    results: List[GachaResultItem]
    gold_remaining: int
    gems_remaining: int

# --- Player Achievement Schemas ---
class PlayerAchievementResponse(BaseModel):
    id: int
    user_id: int
    achievement_id: int
    unlocked_at: datetime
    achievement: AchievementResponse

    class Config:
        from_attributes = True

class AchievementProgressResponse(BaseModel):
    achievement: AchievementResponse
    is_unlocked: bool
    unlocked_at: Optional[datetime]

# --- Simulate Event Schemas ---
class SimulateEventRequest(BaseModel):
    event_type: str                    # "FILL_CORRECT", "FILL_INCORRECT", "STAGE_CLEAR"
    number: Optional[int] = None       # 1-9 (用在填字事件)
    elapsed_time: Optional[int] = None # 秒數 (用在通關事件)
    hp_percent: Optional[float] = None # 0.0 - 1.0 (當前 HP 百分比)

# --- Dungeon Board Schemas ---
class BoardCell(BaseModel):
    row: int
    col: int
    val: int                           # 題目給的提示數，若為 0 表示空白
    solution: int                      # 解答數字
    is_given: bool                     # 是否開局提示
    user_val: int                      # 玩家填的數，預設 0
    event_type: Optional[str] = None   # None, "CHEST", "MONSTER", "TRAP", "ALTAR", "PORTAL", "WEAKNESS"
    is_triggered: bool = False         # 事件是否已解開
    is_foggy: bool = False             # 墨汁屏蔽狀態
    is_error: bool = False             # 是否填寫錯誤
    pencil_notes: List[int] = []       # 鉛筆草稿數字標記

class GenerateBoardRequest(BaseModel):
    user_id: int
    difficulty: str                    # "EASY", "MEDIUM", "HARD"

class DungeonBoardResponse(BaseModel):
    user_id: int
    current_hp: int
    max_hp: int
    boss_name: Optional[str] = None
    boss_hp: int = 0
    boss_max_hp: int = 0
    boss_shield: int = 0
    boss_max_shield: int = 0
    cursed_number: int = 0
    time_left: int = 180
    has_strawman: bool = False
    has_clover: bool = False
    has_seal: bool = False
    cells: List[BoardCell]

# --- Submit Value Schemas ---
class SubmitValueRequest(BaseModel):
    user_id: int
    row: int
    col: int
    val: int

class SubmitValueResponse(BaseModel):
    is_correct: bool
    current_hp: int
    is_cleared: bool
    event_triggered: Optional[str] = None
    event_reward: Optional[str] = None
    unlocked_achievements: List[str] = []

# --- Use Item Schemas ---
class UseItemRequest(BaseModel):
    user_id: int
    item_name: str
    row: Optional[int] = None
    col: Optional[int] = None

class UseItemResponse(BaseModel):
    message: str
    current_hp: int
    board_updated: bool

# --- Action Log Schemas ---
class ActionLogResponse(BaseModel):
    id: int
    user_id: int
    floor: int
    action_type: str
    message: str
    created_at: datetime

    class Config:
        from_attributes = True

# --- Inventory Schemas ---
class PlayerInventoryResponse(BaseModel):
    id: int
    user_id: int
    item_id: int
    quantity: int
    item: ItemResponse

    class Config:
        from_attributes = True
