from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    gold = Column(Integer, default=0)
    gems = Column(Integer, default=0)
    current_floor = Column(Integer, default=1)
    max_floor = Column(Integer, default=1)
    play_time = Column(Integer, default=0)  # 累計遊玩秒數
    created_at = Column(DateTime, default=datetime.utcnow)

    # 關聯
    heroes = relationship("PlayerHero", back_populates="user", cascade="all, delete-orphan")
    items = relationship("PlayerInventory", back_populates="user", cascade="all, delete-orphan")
    achievements = relationship("PlayerAchievement", back_populates="user", cascade="all, delete-orphan")
    number_stats = relationship("NumberStats", back_populates="user", cascade="all, delete-orphan")
    dungeon_progress = relationship("DungeonProgress", back_populates="user", uselist=False, cascade="all, delete-orphan")
    action_logs = relationship("ActionLog", back_populates="user", cascade="all, delete-orphan")


class Hero(Base):
    __tablename__ = "heroes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    element = Column(String(20), nullable=False)      # 火, 水, 木, 光, 暗, 風
    rarity = Column(String(10), nullable=False)        # R, SR, SSR
    skill_name = Column(String(100), nullable=False)
    skill_description = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=False)         # 是否為主動技能
    weight = Column(Integer, default=100)              # 抽卡加權機率（R=800, SR=170, SSR=30）


class PlayerHero(Base):
    __tablename__ = "player_heroes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    hero_id = Column(Integer, ForeignKey("heroes.id"), nullable=False)
    level = Column(Integer, default=1)
    stars = Column(Integer, default=1)
    intimacy = Column(Integer, default=0)
    is_in_team = Column(Boolean, default=False)        # 是否在出戰隊伍中 (最多三人)

    user = relationship("User", back_populates="heroes")
    hero = relationship("Hero")


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    description = Column(String(255), nullable=False)


class PlayerInventory(Base):
    __tablename__ = "player_inventories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    quantity = Column(Integer, default=0)

    user = relationship("User", back_populates="items")
    item = relationship("Item")


class Achievement(Base):
    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(50), nullable=False)
    description = Column(String(255), nullable=False)
    category = Column(String(20), nullable=False)      # TECHNICAL, PROGRESS, COLLECTION


class PlayerAchievement(Base):
    __tablename__ = "player_achievements"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    achievement_id = Column(Integer, ForeignKey("achievements.id"), nullable=False)
    unlocked_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="achievements")
    achievement = relationship("Achievement")


class NumberStats(Base):
    __tablename__ = "number_stats"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    number = Column(Integer, nullable=False)           # 數字 1-9
    count = Column(Integer, default=0)                 # 填對的次數

    user = relationship("User", back_populates="number_stats")


class DungeonProgress(Base):
    __tablename__ = "dungeon_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    current_hp = Column(Integer, default=100)
    max_hp = Column(Integer, default=100)
    elapsed_time = Column(Integer, default=0)          # 本層探索已耗費時間 (秒)
    board_state = Column(Text, nullable=True)          # 儲存數獨盤面 JSON 格式
    boss_name = Column(String(50), nullable=True)
    boss_hp = Column(Integer, default=0)
    boss_max_hp = Column(Integer, default=0)
    boss_shield = Column(Integer, default=0)
    boss_max_shield = Column(Integer, default=0)
    cursed_number = Column(Integer, default=0)         # 目前被詛咒的數字 (0代表無)

    user = relationship("User", back_populates="dungeon_progress")


class ActionLog(Base):
    __tablename__ = "action_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    floor = Column(Integer, default=1)
    action_type = Column(String(30), nullable=False)  # SUBMIT_CORRECT, SUBMIT_WRONG, EVENT, BOSS_SKILL, USE_ITEM, DEFEAT, STAGE_CLEAR
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="action_logs")
