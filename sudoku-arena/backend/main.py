import random
import json
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models
import schemas
from database import engine, get_db

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 啟動時自動建立資料表並寫入種子資料
@app.on_event("startup")
def startup_event():
    models.Base.metadata.create_all(bind=engine)
    db = next(get_db())
    try:
        seed_initial_data(db)
        print("Database startup initialization completed successfully!")
    except Exception as e:
        print(f"Error seeding database: {e}")

def seed_initial_data(db: Session):
    # 1. 檢查是否有英雄種子
    if db.query(models.Hero).count() == 0:
        heroes = [
            models.Hero(name="預言家", element="光", rarity="SSR", skill_name="星象預測", skill_description="被動技 - 開局隨機顯示 2 個隱藏寶箱的正確數字。", is_active=False, weight=30),
            models.Hero(name="狂戰士", element="火", rarity="SR", skill_name="狂暴反擊", skill_description="被動技 - 連續正確填入 5 個數字後進入「狂暴狀態」，下一次填錯免除 HP 懲罰並造成反擊傷害。", is_active=False, weight=170),
            models.Hero(name="時光法師", element="水", rarity="SSR", skill_name="時間停止", skill_description="主動技 - 暫停地牢倒數計時 30 秒，並凍結 Boss 的技能冷卻 (每層限用一次)。", is_active=True, weight=30),
            models.Hero(name="盜賊", element="暗", rarity="R", skill_name="妙手空空", skill_description="被動技 - 解開寶箱格時，有 15% 機率獲得雙倍金幣或代幣。", is_active=False, weight=800),
            models.Hero(name="聖騎士", element="光", rarity="SR", skill_name="神聖護盾", skill_description="主動技 - 開啟聖盾，接下來 3 次填錯數字只扣除 1 點 HP。", is_active=True, weight=170),
            models.Hero(name="幻術師", element="暗", rarity="SSR", skill_name="幻象轉化", skill_description="被動技 - 當盤面上出現陷阱格時，有 50% 機率將其轉化為普通的道具格。", is_active=False, weight=30),
            models.Hero(name="鍊金術士", element="木", rarity="SR", skill_name="藥水調配", skill_description="被動技 - 每成功解開 10 個格子，自動生成一瓶「微型生命藥水」掉落。", is_active=False, weight=170),
            models.Hero(name="龍騎士", element="火", rarity="SSR", skill_name="龍炎爆裂", skill_description="主動技 - 召喚龍炎，強行揭曉並填寫十字範圍（上下左右）內所有空白格的答案。", is_active=True, weight=30),
            models.Hero(name="吟遊詩人", element="風", rarity="R", skill_name="凱旋樂章", skill_description="被動技 - 遊戲背景音樂變更時（如進入 Boss 戰），全隊 HP 恢復 10%。", is_active=False, weight=800),
            models.Hero(name="死靈法師", element="暗", rarity="SSR", skill_name="亡靈護甲", skill_description="被動技 - 盤面上每消滅一隻小怪，就會復活成為骷髏，為玩家抵擋一次 Boss 的技能干擾。", is_active=False, weight=30),
        ]
        db.add_all(heroes)
        print("Hero seeds planted successfully!")

    # 2. 檢查是否有道具種子
    if db.query(models.Item).count() == 0:
        items = [
            models.Item(name="透視放大鏡", description="直接顯示任意一格的正確答案。"),
            models.Item(name="淨化聖水", description="清除盤面上被 Boss 施放的負面狀態。"),
            models.Item(name="時光沙漏", description="增加該層的倒數計時時間 60 秒。"),
            models.Item(name="生命藥水", description="回復玩家 30% 的生命值 (HP)。"),
            models.Item(name="炸彈", description="直接消滅盤面上的任意一隻小怪，不需解開該格子。"),
            models.Item(name="替身草人", description="抵擋下一次填錯數字所受到的 HP 懲罰。"),
            models.Item(name="幸運四葉草", description="使下一次開啟寶箱格時，獲得稀有物品的機率翻倍。"),
            models.Item(name="鉛筆", description="允許在任意格子上做最多 3 個數字的草稿標記，填錯也不會觸發懲罰。"),
            models.Item(name="指南針", description="提示整行或整列中，哪一個數字尚未被填寫。"),
            models.Item(name="封印符咒", description="讓下一個遭遇的陷阱格失效，填錯也不會受罰。"),
        ]
        db.add_all(items)
        print("Item seeds planted successfully!")

    # 3. 檢查是否有成就種子
    if db.query(models.Achievement).count() == 0:
        achievements = [
            # 技術成就
            models.Achievement(title="百步穿楊", description="連續正確填入 50 個數字（無任何失誤）。", category="TECHNICAL"),
            models.Achievement(title="閃電戰", description="在 3 分鐘內通關一層困難級別的地牢。", category="TECHNICAL"),
            models.Achievement(title="盲眼先知", description="在 Boss 施放遮蔽技能期間，連續盲填對 3 個格子。", category="TECHNICAL"),
            models.Achievement(title="數字偏執狂", description="生涯累計填寫特定數字次數居冠。", category="TECHNICAL"),
            models.Achievement(title="完美主義者", description="在一層地牢中不使用 any 道具且無失誤通關。", category="TECHNICAL"),
            models.Achievement(title="千鈞一髮", description="在倒數計時剩餘最後 1 秒時，填入最後一個數字過關。", category="TECHNICAL"),
            models.Achievement(title="極限反殺", description="在 HP 只剩下 1% 的情況下，成功擊敗 Boss。", category="TECHNICAL"),
            models.Achievement(title="試錯大師", description="單局遊戲中填錯 10 次但依然頑強通關。", category="TECHNICAL"),
            models.Achievement(title="獨具慧眼", description="在開局 10 秒內，未經思考連續填對 5 個數字。", category="TECHNICAL"),
            models.Achievement(title="九宮制霸", description="單局內，最先將數字 1 到 9 全數解出。", category="TECHNICAL"),
            # 進度成就
            models.Achievement(title="初出茅廬", description="通關第 1 層地牢。", category="PROGRESS"),
            models.Achievement(title="深淵探險家", description="累計突破地牢第 50 層。", category="PROGRESS"),
            models.Achievement(title="屠龍者", description="擊敗第 100 層的終極 Boss。", category="PROGRESS"),
            models.Achievement(title="地牢常客", description="累計進入地牢 1,000 次。", category="PROGRESS"),
            models.Achievement(title="富甲一方", description="累計獲得 1,000,000 枚金幣。", category="PROGRESS"),
            models.Achievement(title="無盡的挑戰", description="在「無盡模式」中存活超過 50 輪。", category="PROGRESS"),
            models.Achievement(title="怪物獵人", description="累計消滅 10,000 隻盤面小怪。", category="PROGRESS"),
            models.Achievement(title="陷阱迴避者", description="累計成功解除 500 個陷阱格。", category="PROGRESS"),
            models.Achievement(title="寶藏獵人", description="累計開啟 2,000 個寶箱格。", category="PROGRESS"),
            models.Achievement(title="身經百戰", description="遊玩總時長達到 100 小時。", category="PROGRESS"),
            # 收集成就
            models.Achievement(title="運氣爆棚", description="單次十連抽內獲得 2 張以上的 SSR 角色。", category="COLLECTION"),
            models.Achievement(title="全英雄圖鑑", description="收集滿第一賽季的所有英雄。", category="COLLECTION"),
            models.Achievement(title="非洲大酋長", description="連續 50 抽未獲得 any SSR 角色。", category="COLLECTION"),
            models.Achievement(title="滿星強者", description="將任意一名 SSR 角色強化至滿星覺醒狀態。", category="COLLECTION"),
            models.Achievement(title="神裝降臨", description="集齊一套傳說級別的棋子外觀 (Skins)。", category="COLLECTION"),
            models.Achievement(title="寵物大師", description="收集遊戲中所有的跟隨寵物。", category="COLLECTION"),
            models.Achievement(title="囤鼠綜合症", description="背包中同時擁有 99 個未使用的「生命藥水」。", category="COLLECTION"),
            models.Achievement(title="博愛主義", description="所有已解鎖英雄的親密度達到滿級。", category="COLLECTION"),
            models.Achievement(title="時尚達人", description="解鎖並裝備過 10 種不同的棋盤特效。", category="COLLECTION"),
            models.Achievement(title="首抽幸運兒", description="帳號創立後的第一抽就獲得 SSR 角色。", category="COLLECTION"),
        ]
        db.add_all(achievements)
        print("Achievement seeds planted successfully!")
    db.commit()


@app.get("/")
def read_root():
    return {"message": "數壓競技場 API 啟動成功！"}

# --- 核心成就解鎖輔助函數 ---
def unlock_achievement(db: Session, user: models.User, title: str) -> bool:
    achievement = db.query(models.Achievement).filter(models.Achievement.title == title).first()
    if not achievement:
        return False
    
    # 檢查玩家是否已解鎖
    unlocked = db.query(models.PlayerAchievement).filter(
        models.PlayerAchievement.user_id == user.id,
        models.PlayerAchievement.achievement_id == achievement.id
    ).first()
    
    if not unlocked:
        new_unlock = models.PlayerAchievement(user_id=user.id, achievement_id=achievement.id)
        db.add(new_unlock)
        user.gems += 200  # 獎勵 200 鑽石！
        db.flush()
        print(f"Achievement '{title}' unlocked for User {user.id}! +200 gems rewarded.")
        return True
    return False

# --- 日誌記錄輔助函數 ---
def add_action_log(db: Session, user_id: int, floor: int, action_type: str, message: str):
    log = models.ActionLog(
        user_id=user_id,
        floor=floor,
        action_type=action_type,
        message=message
    )
    db.add(log)
    db.flush()

# --- 變異數獨盤面生成輔助函數 ---
def generate_sudoku_board(difficulty: str):
    base = [
        [5, 3, 4, 6, 7, 8, 9, 1, 2],
        [6, 7, 2, 1, 9, 5, 3, 4, 8],
        [1, 9, 8, 3, 4, 2, 5, 6, 7],
        [8, 5, 9, 7, 6, 1, 4, 2, 3],
        [4, 2, 6, 8, 5, 3, 7, 9, 1],
        [7, 1, 3, 9, 2, 4, 8, 5, 6],
        [9, 6, 1, 5, 3, 7, 2, 8, 4],
        [2, 8, 7, 4, 1, 9, 6, 3, 5],
        [3, 4, 5, 2, 8, 6, 1, 7, 9]
    ]
    
    nums = list(range(1, 10))
    shuffled_nums = list(range(1, 10))
    random.shuffle(shuffled_nums)
    mapping = dict(zip(nums, shuffled_nums))
    
    solution_grid = [[mapping[val] for val in row] for row in base]
    
    for i in range(0, 9, 3):
        indices = [i, i+1, i+2]
        random.shuffle(indices)
        row1, row2, row3 = solution_grid[indices[0]], solution_grid[indices[1]], solution_grid[indices[2]]
        solution_grid[indices[0]] = row1
        solution_grid[indices[1]] = row2
        solution_grid[indices[2]] = row3
        
    for i in range(0, 9, 3):
        indices = [i, i+1, i+2]
        random.shuffle(indices)
        for r in range(9):
            col1, col2, col3 = solution_grid[r][indices[0]], solution_grid[r][indices[1]], solution_grid[r][indices[2]]
            solution_grid[r][indices[0]] = col1
            solution_grid[r][indices[1]] = col2
            solution_grid[r][indices[2]] = col3
            
    if difficulty.upper() == "EASY":
        holes_count = 30
    elif difficulty.upper() == "HARD":
        holes_count = 55
    else:  # MEDIUM
        holes_count = 45
        
    all_coords = [(r, c) for r in range(9) for c in range(9)]
    holes_coords = random.sample(all_coords, holes_count)
    
    events = ["CHEST", "MONSTER", "TRAP", "ALTAR", "PORTAL"]
    
    board_cells = []
    for r in range(9):
        for c in range(9):
            correct_val = solution_grid[r][c]
            is_hole = (r, c) in holes_coords
            
            val = 0 if is_hole else correct_val
            is_given = not is_hole
            
            event_type = None
            if is_hole:
                if random.random() < 0.25:
                    event_type = random.choice(events)
                    
            board_cells.append({
                "row": r,
                "col": c,
                "val": val,
                "solution": correct_val,
                "is_given": is_given,
                "user_val": 0,
                "event_type": event_type,
                "is_triggered": False,
                "is_foggy": False
            })
            
    return board_cells

# 建立玩家
@app.post("/users", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = models.User(name=user.name, email=user.email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # 寫入初始日誌
    add_action_log(db, new_user.id, 1, "SYSTEM", f"冒險者 {new_user.name} 踏入了數獨競技場！")
    db.commit()
    return new_user

# 獲取所有玩家
@app.get("/users", response_model=list[schemas.UserResponse])
def get_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()

# 刪除玩家 API
@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    return {"message": f"User {user_id} and all related data deleted successfully"}

# 獲取所有系統英雄
@app.get("/heroes", response_model=list[schemas.HeroResponse])
def get_heroes(db: Session = Depends(get_db)):
    return db.query(models.Hero).all()

# 獲取所有系統道具
@app.get("/items", response_model=list[schemas.ItemResponse])
def get_items(db: Session = Depends(get_db)):
    return db.query(models.Item).all()

# 獲取所有系統成就
@app.get("/achievements", response_model=list[schemas.AchievementResponse])
def get_achievements(db: Session = Depends(get_db)):
    return db.query(models.Achievement).all()

# 獲取玩家最新 50 筆操作日誌
@app.get("/users/{user_id}/logs", response_model=list[schemas.ActionLogResponse])
def get_user_action_logs(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return db.query(models.ActionLog).filter(
        models.ActionLog.user_id == user_id
    ).order_by(
        models.ActionLog.created_at.desc(),
        models.ActionLog.id.desc()
    ).limit(50).all()

# 測試資源儲值 API
@app.post("/users/{user_id}/add-resources", response_model=schemas.UserResponse)
def add_resources(user_id: int, gold: int = 0, gems: int = 0, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.gold += gold
    user.gems += gems
    
    add_action_log(db, user_id, user.current_floor, "SYSTEM", f"測試儲值：金幣 +{gold}，鑽石 +{gems}。")
    db.commit()
    db.refresh(user)
    return user

# 查詢玩家擁有的英雄 API
@app.get("/users/{user_id}/heroes", response_model=list[schemas.PlayerHeroResponse])
def get_player_heroes(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return db.query(models.PlayerHero).filter(models.PlayerHero.user_id == user_id).all()

# 查詢玩家背包 API
@app.get("/users/{user_id}/inventory", response_model=list[schemas.PlayerInventoryResponse])
def get_user_inventory(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return db.query(models.PlayerInventory).filter(models.PlayerInventory.user_id == user_id).all()


# 查詢玩家成就解鎖進度 API
@app.get("/users/{user_id}/achievements/progress", response_model=list[schemas.AchievementProgressResponse])
def get_player_achievements_progress(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    all_achievements = db.query(models.Achievement).all()
    unlocked_records = db.query(models.PlayerAchievement).filter(
        models.PlayerAchievement.user_id == user_id
    ).all()
    
    unlocked_map = {r.achievement_id: r.unlocked_at for r in unlocked_records}
    
    progress = []
    for ach in all_achievements:
        is_unlocked = ach.id in unlocked_map
        progress.append(schemas.AchievementProgressResponse(
            achievement=schemas.AchievementResponse.from_orm(ach),
            is_unlocked=is_unlocked,
            unlocked_at=unlocked_map.get(ach.id) if is_unlocked else None
        ))
    return progress

# 抽卡系統 API (Gacha)
@app.post("/gacha/draw", response_model=schemas.GachaResponse)
def draw_gacha(request: schemas.GachaRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if request.draw_count not in [1, 10]:
        raise HTTPException(status_code=400, detail="Draw count must be 1 or 10")
    
    cost = 100 if request.draw_count == 1 else 1000
    if user.gems < cost:
        raise HTTPException(status_code=400, detail="Insufficient gems")
    
    heroes = db.query(models.Hero).all()
    if not heroes:
        raise HTTPException(status_code=400, detail="No heroes configured in system database")
    
    hero_ids = [h.id for h in heroes]
    hero_weights = [h.weight for h in heroes]
    hero_map = {h.id: h for h in heroes}
    
    drawn_ids = random.choices(population=hero_ids, weights=hero_weights, k=request.draw_count)
    
    results = []
    total_compensation = 0
    
    for hero_id in drawn_ids:
        hero_meta = hero_map[hero_id]
        
        player_hero = db.query(models.PlayerHero).filter(
            models.PlayerHero.user_id == request.user_id,
            models.PlayerHero.hero_id == hero_id
        ).first()
        
        is_new = False
        gems_compensated = 0
        
        if not player_hero:
            player_hero = models.PlayerHero(
                user_id=request.user_id,
                hero_id=hero_id,
                level=1,
                stars=1,
                intimacy=0,
                is_in_team=False
            )
            db.add(player_hero)
            db.flush()
            is_new = True
            stars_after = 1
        else:
            if player_hero.stars < 5:
                player_hero.stars += 1
                stars_after = player_hero.stars
            else:
                gems_compensated = 100
                total_compensation += 100
                stars_after = 5
        
        results.append(schemas.GachaResultItem(
            hero=schemas.HeroResponse.from_orm(hero_meta),
            is_new=is_new,
            stars_after=stars_after,
            gems_compensated=gems_compensated
        ))
        
        # 寫入抽卡日誌
        status_str = "「新獲得」" if is_new else f"「重複(升星至 {stars_after} 星)」"
        comp_str = " (滿星補償 100 鑽石)" if gems_compensated > 0 else ""
        add_action_log(
            db, request.user_id, user.current_floor, "GACHA",
            f"召喚到了 {hero_meta.rarity} 英雄【{hero_meta.name}】！狀態：{status_str}{comp_str}"
        )
    
    user.gems = user.gems - cost + total_compensation
    
    ssr_count = sum(1 for item in results if item.hero.rarity == "SSR")
    if request.draw_count == 10 and ssr_count >= 2:
        unlock_achievement(db, user, "運氣爆棚")
        
    unique_owned = db.query(models.PlayerHero.hero_id).filter(
        models.PlayerHero.user_id == request.user_id
    ).distinct().count()
    if unique_owned >= 10:
        unlock_achievement(db, user, "全英雄圖鑑")
        
    five_star_hero = db.query(models.PlayerHero).filter(
        models.PlayerHero.user_id == request.user_id,
        models.PlayerHero.stars == 5
    ).first()
    if five_star_hero:
        unlock_achievement(db, user, "滿星強者")
        
    db.commit()
    db.refresh(user)
    
    return schemas.GachaResponse(
        results=results,
        gold_remaining=user.gold,
        gems_remaining=user.gems
    )

# --- 模擬事件與成就檢測 API ---
@app.post("/users/{user_id}/simulate-event")
def simulate_game_event(user_id: int, req: schemas.SimulateEventRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    unlocked_titles = []
    
    if req.event_type == "FILL_CORRECT":
        if req.number is None or req.number < 1 or req.number > 9:
            raise HTTPException(status_code=400, detail="Invalid number. Must be 1-9.")
            
        stat = db.query(models.NumberStats).filter(
            models.NumberStats.user_id == user_id,
            models.NumberStats.number == req.number
        ).first()
        
        if not stat:
            stat = models.NumberStats(user_id=user_id, number=req.number, count=1)
            db.add(stat)
        else:
            stat.count += 1
        db.flush()
        
        if stat.count >= 10:
            if unlock_achievement(db, user, "數字偏執狂"):
                unlocked_titles.append("數字偏執狂")
                
        if req.number == 9 and req.hp_percent == 0.5:
            if unlock_achievement(db, user, "百步穿楊"):
                unlocked_titles.append("百步穿楊")
                
        if req.hp_percent == 0.01:
            if unlock_achievement(db, user, "極限反殺"):
                unlocked_titles.append("極限反殺")
                
    elif req.event_type == "STAGE_CLEAR":
        if unlock_achievement(db, user, "初出茅廬"):
            unlocked_titles.append("初出茅廬")
            
        if req.elapsed_time and req.elapsed_time <= 180:
            if unlock_achievement(db, user, "閃電戰"):
                unlocked_titles.append("閃電戰")
                
    else:
        raise HTTPException(status_code=400, detail="Unknown event_type")
        
    db.commit()
    db.refresh(user)
    
    return {
        "message": f"Event {req.event_type} simulated successfully.",
        "unlocked_achievements": unlocked_titles,
        "gems_current": user.gems
    }

# --- 地牢與變異盤面 APIs ---

# 生成變異數獨盤面 API
@app.post("/dungeon/generate-board", response_model=schemas.DungeonBoardResponse)
def generate_dungeon_board(req: schemas.GenerateBoardRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == req.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    if req.difficulty.upper() not in ["EASY", "MEDIUM", "HARD"]:
        raise HTTPException(status_code=400, detail="Difficulty must be EASY, MEDIUM, or HARD")
        
    board_cells = generate_sudoku_board(req.difficulty)
    board_json = json.dumps(board_cells)
    
    progress = db.query(models.DungeonProgress).filter(models.DungeonProgress.user_id == req.user_id).first()
    if not progress:
        progress = models.DungeonProgress(
            user_id=req.user_id,
            current_hp=100,
            max_hp=100,
            elapsed_time=0,
            board_state=board_json,
            boss_name=None,
            boss_hp=0,
            boss_max_hp=0,
            boss_shield=0,
            boss_max_shield=0,
            cursed_number=0
        )
        db.add(progress)
    else:
        progress.current_hp = 100
        progress.max_hp = 100
        progress.elapsed_time = 0
        progress.board_state = board_json
        progress.boss_name = None
        progress.boss_hp = 0
        progress.boss_max_hp = 0
        progress.boss_shield = 0
        progress.boss_max_shield = 0
        progress.cursed_number = 0
        
    # 寫入生成盤面日誌
    add_action_log(db, req.user_id, user.current_floor, "STAGE_START", f"成功生成了全新地牢盤面，難度：{req.difficulty}。")
    db.commit()
    db.refresh(progress)
    
    return schemas.DungeonBoardResponse(
        user_id=progress.user_id,
        current_hp=progress.current_hp,
        max_hp=progress.max_hp,
        boss_name=progress.boss_name,
        boss_hp=progress.boss_hp,
        boss_max_hp=progress.boss_max_hp,
        boss_shield=progress.boss_shield,
        boss_max_shield=progress.boss_max_shield,
        cursed_number=progress.cursed_number,
        cells=board_cells
    )

# 查詢玩家進行中的盤面 API
@app.get("/dungeon/{user_id}/board", response_model=schemas.DungeonBoardResponse)
def get_dungeon_board(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    progress = db.query(models.DungeonProgress).filter(models.DungeonProgress.user_id == user_id).first()
    if not progress or not progress.board_state:
        raise HTTPException(status_code=400, detail="No active dungeon board for this user. Call generate-board first.")
        
    cells_list = json.loads(progress.board_state)
    
    return schemas.DungeonBoardResponse(
        user_id=progress.user_id,
        current_hp=progress.current_hp,
        max_hp=progress.max_hp,
        boss_name=progress.boss_name,
        boss_hp=progress.boss_hp,
        boss_max_hp=progress.boss_max_hp,
        boss_shield=progress.boss_shield,
        boss_max_shield=progress.boss_max_shield,
        cursed_number=progress.cursed_number,
        cells=cells_list
    )

# 測試 Boss 戰盤面生成 API
@app.post("/dungeon/generate-boss-fight", response_model=schemas.DungeonBoardResponse)
def generate_boss_fight(req: schemas.GenerateBoardRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == req.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    if req.difficulty.upper() not in ["EASY", "MEDIUM", "HARD"]:
        raise HTTPException(status_code=400, detail="Difficulty must be EASY, MEDIUM, or HARD")
        
    board_cells = generate_sudoku_board(req.difficulty)
    
    blank_cells = [c for c in board_cells if not c["is_given"]]
    if len(blank_cells) < 3:
         raise HTTPException(status_code=400, detail="Not enough blank cells to generate Boss Fight")
    
    weakness_targets = random.sample(blank_cells, 3)
    for target in weakness_targets:
        target["event_type"] = "WEAKNESS"
        
    board_json = json.dumps(board_cells)
    
    progress = db.query(models.DungeonProgress).filter(models.DungeonProgress.user_id == req.user_id).first()
    if not progress:
        progress = models.DungeonProgress(
            user_id=req.user_id,
            current_hp=100,
            max_hp=100,
            elapsed_time=0,
            board_state=board_json,
            boss_name="黑龍法王",
            boss_hp=500,
            boss_max_hp=500,
            boss_shield=3,
            boss_max_shield=3,
            cursed_number=0
        )
        db.add(progress)
    else:
        progress.current_hp = 100
        progress.max_hp = 100
        progress.elapsed_time = 0
        progress.board_state = board_json
        progress.boss_name = "黑龍法王"
        progress.boss_hp = 500
        progress.boss_max_hp = 500
        progress.boss_shield = 3
        progress.boss_max_shield = 3
        progress.cursed_number = 0
        
    # 寫入 Boss 戰 start log
    add_action_log(db, req.user_id, user.current_floor, "BOSS_START", f"【第 {user.current_floor} 層 Boss 戰開打】強敵【黑龍法王】降臨！(HP: 500 / 護盾: 3)")
    db.commit()
    db.refresh(progress)
    
    return schemas.DungeonBoardResponse(
        user_id=progress.user_id,
        current_hp=progress.current_hp,
        max_hp=progress.max_hp,
        boss_name=progress.boss_name,
        boss_hp=progress.boss_hp,
        boss_max_hp=progress.boss_max_hp,
        boss_shield=progress.boss_shield,
        boss_max_shield=progress.boss_max_shield,
        cursed_number=progress.cursed_number,
        cells=board_cells
    )

# 填寫數獨格子與事件觸發 API
@app.post("/dungeon/submit-value", response_model=schemas.SubmitValueResponse)
def submit_dungeon_value(req: schemas.SubmitValueRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == req.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    progress = db.query(models.DungeonProgress).filter(models.DungeonProgress.user_id == req.user_id).first()
    if not progress or not progress.board_state:
        raise HTTPException(status_code=400, detail="No active dungeon board for this user")
        
    # --- Boss 數字詛咒反噬檢查 ---
    if progress.boss_name and progress.boss_hp > 0 and progress.cursed_number > 0:
        if req.val == progress.cursed_number:
            progress.current_hp -= 15
            add_action_log(
                db, req.user_id, user.current_floor, "BOSS_SKILL",
                f"填寫了被詛咒的數字 {req.val}！遭受 15 點 HP 詛咒反噬傷害。"
            )
            db.flush()
            
            if progress.current_hp <= 0:
                user.gold = max(0, user.gold - 100)
                add_action_log(
                    db, req.user_id, user.current_floor, "DEFEAT",
                    f"挑戰失敗！生命值歸零。地牢進度重置，並扣除 100 金幣（目前賸餘金幣：{user.gold}）"
                )
                
                reset_board = generate_sudoku_board("MEDIUM")
                progress.board_state = json.dumps(reset_board)
                progress.current_hp = 100
                progress.elapsed_time = 0
                progress.boss_name = None
                progress.boss_hp = 0
                progress.boss_max_hp = 0
                progress.boss_shield = 0
                progress.boss_max_shield = 0
                progress.cursed_number = 0
                db.commit()
                raise HTTPException(
                    status_code=400,
                    detail=f"受到 Boss 詛咒反噬 (數字 {req.val})！生命值歸零。進度已重置並扣除 100 金幣。"
                )
            
    cells = json.loads(progress.board_state)
    
    target_cell = None
    for cell in cells:
        if cell["row"] == req.row and cell["col"] == req.col:
            target_cell = cell
            break
            
    if not target_cell:
        raise HTTPException(status_code=404, detail="Cell coordinates not found on board")
        
    if target_cell["is_given"] or target_cell["user_val"] != 0:
        raise HTTPException(status_code=400, detail="This cell is already resolved and cannot be modified")
        
    is_correct = (req.val == target_cell["solution"])
    unlocked_achievements = []
    event_triggered = None
    event_reward = None
    is_cleared = False
    
    if is_correct:
        target_cell["user_val"] = req.val
        
        # 寫入正確填寫基礎日誌
        add_action_log(
            db, req.user_id, user.current_floor, "SUBMIT_CORRECT",
            f"於座標 ({req.row}, {req.col}) 填入正確答案 {req.val}。"
        )
        
        # 觸發特殊事件格效果
        if target_cell["event_type"] and not target_cell["is_triggered"]:
            target_cell["is_triggered"] = True
            event_triggered = target_cell["event_type"]
            
            if event_triggered == "WEAKNESS" and progress.boss_name and progress.boss_hp > 0:
                if progress.boss_shield > 0:
                    progress.boss_shield -= 1
                    event_reward = f"擊中弱點！Boss 護盾值降至 {progress.boss_shield}"
                    shield_msg = f"擊中發光弱點！成功扣除 Boss 護盾 1 點（剩餘護盾：{progress.boss_shield}）。"
                    if progress.boss_shield == 0:
                        event_reward += "。BOSS 護盾已破碎 (BREAK)！此時填字可造成直接重創！"
                        shield_msg += "護盾進入 BREAK 狀態！"
                    add_action_log(db, req.user_id, user.current_floor, "EVENT", shield_msg)
                else:
                    event_reward = "擊中弱點，但 Boss 護盾早已是破碎狀態"
            
            elif event_triggered == "CHEST":
                if random.random() < 0.5:
                    gold_got = random.randint(50, 100)
                    user.gold += gold_got
                    event_reward = f"獲得了 {gold_got} 金幣"
                else:
                    items = db.query(models.Item).all()
                    if items:
                        drawn_item = random.choice(items)
                        inventory = db.query(models.PlayerInventory).filter(
                            models.PlayerInventory.user_id == req.user_id,
                            models.PlayerInventory.item_id == drawn_item.id
                        ).first()
                        if not inventory:
                            inventory = models.PlayerInventory(user_id=req.user_id, item_id=drawn_item.id, quantity=1)
                            db.add(inventory)
                        else:
                            inventory.quantity += 1
                        event_reward = f"獲得道具：{drawn_item.name}"
                add_action_log(db, req.user_id, user.current_floor, "EVENT", f"解鎖寶箱格！{event_reward}。")
            
            elif event_triggered == "MONSTER":
                user.gold += 80
                event_reward = "成功消滅小怪，獲得 80 金幣"
                add_action_log(db, req.user_id, user.current_floor, "EVENT", "遭遇小怪！將其成功消滅，並獲得 80 金幣。")
                
            elif event_triggered == "TRAP":
                user.gold += 50
                event_reward = "成功解除陷阱，獲得 50 金幣"
                add_action_log(db, req.user_id, user.current_floor, "EVENT", "成功拆除陷阱，拆彈專家獲得 50 金幣獎勵。")
                
            elif event_triggered == "PORTAL":
                box_row, box_col = (req.row // 3) * 3, (req.col // 3) * 3
                unresolved_cells = []
                for c in cells:
                    c_r, c_c = c["row"], c["col"]
                    if box_row <= c_r < box_row + 3 and box_col <= c_c < box_col + 3:
                        if not c["is_given"] and c["user_val"] == 0:
                            if not (c_r == req.row and c_c == req.col):
                                unresolved_cells.append(c)
                if unresolved_cells:
                    portal_target = random.choice(unresolved_cells)
                    portal_target["user_val"] = portal_target["solution"]
                    portal_target["is_given"] = True
                    event_reward = f"傳送門發動！直接揭曉座標 ({portal_target['row']}, {portal_target['col']})，答案為 {portal_target['solution']}"
                else:
                    event_reward = "傳送門發動，但同宮格內已無未解格子"
                add_action_log(db, req.user_id, user.current_floor, "EVENT", f"觸發傳送門！{event_reward}。")
                    
            elif event_triggered == "ALTAR":
                progress.current_hp = min(progress.max_hp, progress.current_hp + 20)
                event_reward = "激活祭壇力量，生命值恢復 20 點"
                add_action_log(db, req.user_id, user.current_floor, "EVENT", "活化祭壇力量！祈禱成功，生命值恢復 20 點。")

        # 如果是 Boss 戰，且填對普通格
        if progress.boss_name and progress.boss_hp > 0 and event_triggered != "WEAKNESS":
            if progress.boss_shield == 0:
                damage_to_boss = req.val * 20
                progress.boss_hp = max(0, progress.boss_hp - damage_to_boss)
                boss_msg = f"對 Boss 造成 {damage_to_boss} 點重創傷害！Boss 剩餘 HP: {progress.boss_hp}"
                if event_reward:
                    event_reward = f"{event_reward}，並且{boss_msg}"
                else:
                    event_reward = boss_msg
                add_action_log(db, req.user_id, user.current_floor, "SUBMIT_CORRECT", f"突破防線！對 Boss 造成了 {damage_to_boss} 點重創傷害！")
            else:
                boss_msg = "Boss 護盾依然存在，免疫本次填字傷害！"
                if event_reward:
                    event_reward = f"{event_reward}（{boss_msg}）"
                else:
                    event_reward = boss_msg

        # --- Boss 主動技能反擊 (15% 機率) ---
        if progress.boss_name and progress.boss_hp > 0 and random.random() < 0.15:
            if random.random() < 0.5:
                progress.cursed_number = random.randint(1, 9)
                event_triggered = "BOSS_SKILL"
                event_reward = f"Boss 施放數字詛咒！被詛咒的數字是: {progress.cursed_number}，填入將受 15 反噬傷害！"
                add_action_log(db, req.user_id, user.current_floor, "BOSS_SKILL", f"Boss 反噬咆哮！施放數字詛咒：被詛咒的數字是 {progress.cursed_number}！")
            else:
                resolved_cells = [c for c in cells if not c["is_given"] and c["user_val"] > 0]
                if resolved_cells:
                    spray_targets = random.sample(resolved_cells, min(len(resolved_cells), 3))
                    for tgt in spray_targets:
                        tgt["is_foggy"] = True
                        tgt["user_val"] = 0
                    event_triggered = "BOSS_SKILL"
                    event_reward = "Boss 施放墨汁噴灑！盤面上的部分已解格子被墨汁遮蔽了。"
                    add_action_log(db, req.user_id, user.current_floor, "BOSS_SKILL", "Boss 施放墨汁噴灑！盤面上的 3 個已解開格子被強行遮蔽！")

        # 連動技術成就：數字偏執狂累加
        stat = db.query(models.NumberStats).filter(
            models.NumberStats.user_id == req.user_id,
            models.NumberStats.number == req.val
        ).first()
        if not stat:
            stat = models.NumberStats(user_id=req.user_id, number=req.val, count=1)
            db.add(stat)
        else:
            stat.count += 1
        db.flush()
        
        if stat.count >= 10:
            if unlock_achievement(db, user, "數字偏執狂"):
                unlocked_achievements.append("數字偏執狂")
                add_action_log(db, req.user_id, user.current_floor, "ACHIEVEMENT", "解鎖了技術成就【數字偏執狂】！獲得了 200 鑽石獎勵。")
                
        # 判斷是否通關整張盤面
        all_resolved = True
        for c in cells:
            if not c["is_given"] and c["user_val"] != c["solution"]:
                all_resolved = False
                break
                
        boss_is_dead = (not progress.boss_name) or (progress.boss_hp <= 0)
        
        if all_resolved and boss_is_dead:
            is_cleared = True
            user.gold += 500
            user.current_floor += 1
            user.max_floor = max(user.max_floor, user.current_floor)
            db.flush()
            
            # 寫入通關日誌
            clear_msg = f"地牢通關成功！獲得 500 金幣獎勵，晉升至第 {user.current_floor} 層！"
            if progress.boss_name and progress.boss_hp <= 0:
                clear_msg = f"成功討伐 Boss 黑龍法王！" + clear_msg
                if unlock_achievement(db, user, "屠龍者"):
                    unlocked_achievements.append("屠龍者")
                    add_action_log(db, req.user_id, user.current_floor - 1, "ACHIEVEMENT", "解鎖了冒險成就【屠龍者】！獲得了 200 鑽石獎勵。")
            
            add_action_log(db, req.user_id, user.current_floor - 1, "STAGE_CLEAR", clear_msg)
            
            if unlock_achievement(db, user, "初出茅廬"):
                unlocked_achievements.append("初出茅廬")
                add_action_log(db, req.user_id, user.current_floor - 1, "ACHIEVEMENT", "解鎖了進度成就【初出茅廬】！獲得了 200 鑽石獎勵。")
                
            next_board = generate_sudoku_board("MEDIUM")
            progress.board_state = json.dumps(next_board)
            progress.current_hp = 100
            progress.elapsed_time = 0
            progress.boss_name = None
            progress.boss_hp = 0
            progress.boss_max_hp = 0
            progress.boss_shield = 0
            progress.boss_max_shield = 0
            progress.cursed_number = 0
    else:
        damage = 20 if target_cell["event_type"] == "TRAP" else 10
        progress.current_hp -= damage
        
        # 寫入填錯日誌
        err_msg = f"於座標 ({req.row}, {req.col}) 填入錯誤數字 {req.val}（正確為 {target_cell['solution']}）。"
        if target_cell["event_type"] == "TRAP":
            err_msg += f"觸發陷阱！扣除雙倍生命值 20 點（當前 HP: {progress.current_hp}）。"
        else:
            err_msg += f"扣除生命值 10 點（當前 HP: {progress.current_hp}）。"
        add_action_log(db, req.user_id, user.current_floor, "SUBMIT_WRONG", err_msg)
        
        if progress.current_hp <= 0:
            user.gold = max(0, user.gold - 100)
            
            add_action_log(
                db, req.user_id, user.current_floor, "DEFEAT",
                f"挑戰失敗！生命值歸零。地牢進度已重置，並扣除 100 金幣（賸餘金幣：{user.gold}）"
            )
            
            reset_board = generate_sudoku_board("MEDIUM")
            progress.board_state = json.dumps(reset_board)
            progress.current_hp = 100
            progress.elapsed_time = 0
            progress.boss_name = None
            progress.boss_hp = 0
            progress.boss_max_hp = 0
            progress.boss_shield = 0
            progress.boss_max_shield = 0
            progress.cursed_number = 0
            db.commit()
            
            raise HTTPException(
                status_code=400,
                detail=f"挑戰失敗！生命值歸零。地牢進度已重置，並扣除 100 金幣（目前賸餘金幣：{user.gold}）"
            )
            
    if not is_cleared:
        progress.board_state = json.dumps(cells)
        
    db.commit()
    
    return schemas.SubmitValueResponse(
        is_correct=is_correct,
        current_hp=progress.current_hp,
        is_cleared=is_cleared,
        event_triggered=event_triggered,
        event_reward=event_reward,
        unlocked_achievements=unlocked_achievements
    )

# 道具使用 API
@app.post("/dungeon/use-item", response_model=schemas.UseItemResponse)
def use_dungeon_item(req: schemas.UseItemRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == req.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    progress = db.query(models.DungeonProgress).filter(models.DungeonProgress.user_id == req.user_id).first()
    if not progress or not progress.board_state:
        raise HTTPException(status_code=400, detail="No active dungeon board for this user")
        
    item_meta = db.query(models.Item).filter(models.Item.name == req.item_name).first()
    if not item_meta:
        raise HTTPException(status_code=404, detail=f"Item type '{req.item_name}' not configured in database")
        
    inventory = db.query(models.PlayerInventory).filter(
        models.PlayerInventory.user_id == req.user_id,
        models.PlayerInventory.item_id == item_meta.id
    ).first()
    
    if not inventory or inventory.quantity <= 0:
        raise HTTPException(status_code=400, detail=f"You do not have any '{req.item_name}' in inventory")
        
    cells = json.loads(progress.board_state)
    board_updated = False
    message = ""
    
    if req.item_name == "生命藥水":
        progress.current_hp = min(progress.max_hp, progress.current_hp + 30)
        inventory.quantity -= 1
        message = "成功使用生命藥水，生命值恢復 30 點！"
        
    elif req.item_name == "透視放大鏡":
        if req.row is None or req.col is None:
            raise HTTPException(status_code=400, detail="Using '透視放大鏡' requires 'row' and 'col' coordinates")
        target_cell = None
        for cell in cells:
            if cell["row"] == req.row and cell["col"] == req.col:
                target_cell = cell
                break
        if not target_cell:
            raise HTTPException(status_code=404, detail="Target cell not found")
        if target_cell["is_given"] or target_cell["user_val"] != 0:
            raise HTTPException(status_code=400, detail="Target cell is already resolved")
            
        target_cell["user_val"] = target_cell["solution"]
        target_cell["is_given"] = True
        if target_cell["event_type"]:
            target_cell["is_triggered"] = True
            
        inventory.quantity -= 1
        board_updated = True
        message = f"成功使用透視放大鏡，揭曉座標 ({req.row}, {req.col}) 答案為 {target_cell['solution']}！"
        
    elif req.item_name == "炸彈":
        if req.row is None or req.col is None:
            raise HTTPException(status_code=400, detail="Using '炸彈' requires 'row' and 'col' coordinates")
        target_cell = None
        for cell in cells:
            if cell["row"] == req.row and cell["col"] == req.col:
                target_cell = cell
                break
        if not target_cell:
            raise HTTPException(status_code=404, detail="Target cell not found")
        if not target_cell["event_type"] or target_cell["is_triggered"]:
            raise HTTPException(status_code=400, detail="Target cell does not have an active event")
            
        old_event = target_cell["event_type"]
        target_cell["event_type"] = None
        inventory.quantity -= 1
        board_updated = True
        message = f"成功使用炸彈，排除了座標 ({req.row}, {req.col}) 的 {old_event} 事件格！"
        
    elif req.item_name == "淨化聖水":
        progress.cursed_number = 0
        cleared_count = 0
        for cell in cells:
            if cell.get("is_foggy"):
                cell["is_foggy"] = False
                cell["user_val"] = cell["solution"]
                cleared_count += 1
        
        inventory.quantity -= 1
        board_updated = True
        message = f"成功使用淨化聖水！數字詛咒已解除，被遮蔽的 {cleared_count} 個格子已還原。"
    else:
        raise HTTPException(status_code=400, detail=f"Item '{req.item_name}' logic not implemented yet")
        
    # 寫入使用道具日誌
    add_action_log(db, req.user_id, user.current_floor, "USE_ITEM", message)
    
    if board_updated:
        progress.board_state = json.dumps(cells)
        
    db.commit()
    
    return schemas.UseItemResponse(
        message=message,
        current_hp=progress.current_hp,
        board_updated=board_updated
    )
