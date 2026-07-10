<script setup>
import { ref, onMounted, onUnmounted, computed, nextTick } from 'vue'

const API_BASE = 'http://localhost:8000'
const userId = ref(1)
const user = ref({ name: '冒險者', gold: 0, gems: 0, current_floor: 1 })
const board = ref([])
const boardState = ref({ current_hp: 100, max_hp: 100 })
const boss = ref({ name: null, hp: 0, max_hp: 0, shield: 0, max_shield: 0, cursed_number: 0 })

// 道具背包
const inventory = ref([
  { name: '透視放大鏡', icon: '🔍', quantity: 0, description: '直接顯示任意一格的正確答案。' },
  { name: '炸彈', icon: '💣', quantity: 0, description: '直接消滅盤面上的任意一隻小怪，不需解開該格子。' },
  { name: '生命藥水', icon: '🧪', quantity: 0, description: '回復玩家 30% 的生命值 (HP)。' },
  { name: '淨化聖水', icon: '✨', quantity: 0, description: '解除 Boss 施放的數字詛咒，並復原所有被墨汁遮蔽的格子。' },
  { name: '時光沙漏', icon: '⏳', quantity: 0, description: '增加該層的挑戰倒數計時時間 60 秒。' },
  { name: '替身草人', icon: '🌾', quantity: 0, description: '抵擋下一次填錯數字所受到的 HP 懲罰。' },
  { name: '幸運四葉草', icon: '🍀', quantity: 0, description: '使下一次開啟寶箱格時，獲得金幣翻倍且必定獲得道具。' },
  { name: '鉛筆', icon: '✏️', quantity: 0, description: '在空格子上記錄正確答案的 3 個可能候選數作為草稿。' },
  { name: '指南針', icon: '🧭', quantity: 0, description: '提示所選格子所在的整行與整列中，尚未填寫的數字。' },
  { name: '封印符咒', icon: '📜', quantity: 0, description: '讓下一個遭遇的陷阱格失效，填錯免受罰且強制破除。' }
])
const activeItemMode = ref(null) // 目前選中要施放的道具名稱
const hoveredItemName = ref(null)

const timeLeft = ref(180)
const hasStrawman = ref(false)
const hasClover = ref(false)
const hasSeal = ref(false)
let timerId = null

// 啟動定時倒數
const startTimer = () => {
  if (timerId) clearInterval(timerId)
  timerId = setInterval(async () => {
    if (timeLeft.value > 0) {
      timeLeft.value--
      if (timeLeft.value === 0) {
        await handleTimeout()
      }
    }
  }, 1000)
}

const stopTimer = () => {
  if (timerId) {
    clearInterval(timerId)
    timerId = null
  }
}

// 處理超時重置
const handleTimeout = async () => {
  stopTimer()
  try {
    const res = await fetch(`${API_BASE}/dungeon/timeout`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId.value, difficulty: 'MEDIUM' })
    })
    if (res.ok) {
      const data = await res.json()
      updateDungeonState(data)
      await fetchLogs()
      showToast('⏳ 時間到！挑戰超時，地牢盤面已被重置！', 'error')
    }
  } catch (err) {
    console.error('Timeout error:', err)
  }
}

const updateDungeonState = (data) => {
  board.value = data.cells
  boardState.value.current_hp = data.current_hp
  boardState.value.max_hp = data.max_hp
  
  // Boss 資訊
  boss.value.name = data.boss_name
  boss.value.hp = data.boss_hp
  boss.value.max_hp = data.boss_max_hp
  boss.value.shield = data.boss_shield
  boss.value.max_shield = data.boss_max_shield
  boss.value.cursed_number = data.cursed_number
  
  // 增益狀態與賸餘時間
  timeLeft.value = data.time_left ?? 180
  hasStrawman.value = data.has_strawman ?? false
  hasClover.value = data.has_clover ?? false
  hasSeal.value = data.has_seal ?? false
  
  startTimer()
}

const selectedItemInfo = computed(() => {
  const activeName = hoveredItemName.value || activeItemMode.value
  if (!activeName) return null
  return inventory.value.find(item => item.name === activeName)
})

// 英雄卡牌
const ownedHeroes = ref([])
const selectedHeroId = ref(null) // 目前展開能力說明的英雄 ID

const toggleHeroDetail = (heroId) => {
  selectedHeroId.value = selectedHeroId.value === heroId ? null : heroId
}

// 成就與日誌
const achievements = ref([])
const showAchievements = ref(false) // 側欄切換為成就
const logs = ref([])
const terminalRef = ref(null)

// 填字選取
const selectedCell = ref(null)

const middleRef = ref(null)
const middleHeight = ref('auto')

const updateSidebarHeights = () => {
  nextTick(() => {
    if (middleRef.value) {
      middleHeight.value = `${middleRef.value.offsetHeight}px`
    }
  })
}

// 抽卡 Modal
const showGachaModal = ref(false)
const gachaResults = ref([])

// Toast 提示
const toastMessage = ref('')
const toastType = ref('info')
let toastTimeout = null

const showToast = (msg, type = 'info') => {
  toastMessage.value = msg
  toastType.value = type
  if (toastTimeout) clearTimeout(toastTimeout)
  toastTimeout = setTimeout(() => {
    toastMessage.value = ''
  }, 3000)
}

// 輔助獲取事件 Emoji
const getEventEmoji = (type) => {
  switch (type) {
    case 'CHEST': return '🎁'
    case 'MONSTER': return '👾'
    case 'TRAP': return '⚠️'
    case 'ALTAR': return '🔮'
    case 'PORTAL': return '🌀'
    case 'WEAKNESS': return '✨'
    default: return ''
  }
}

// 輔助獲取事件名稱
const getEventName = (type) => {
  switch (type) {
    case 'CHEST': return '寶箱'
    case 'MONSTER': return '怪物'
    case 'TRAP': return '陷阱'
    case 'ALTAR': return '祭壇'
    case 'PORTAL': return '傳送門'
    case 'WEAKNESS': return '弱點'
    default: return ''
  }
}

// 初始化/登入玩家
const initUser = async () => {
  try {
    const res = await fetch(`${API_BASE}/users`)
    const users = await res.json()
    let currUser = users.find(u => u.id === userId.value)
    
    if (!currUser) {
      // 建立預設玩家
      const createRes = await fetch(`${API_BASE}/users`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: 'PixelHero', email: 'pixel@example.com' })
      })
      currUser = await createRes.json()
      userId.value = currUser.id
    }
    
    user.value = currUser
    await fetchAllData()
  } catch (err) {
    console.error('Failed to init user:', err)
  }
}

// 獲取所有玩家相關狀態
const fetchAllData = async () => {
  if (!userId.value) return
  await fetchUserStatus()
  await fetchBoard()
  await fetchInventory()
  await fetchHeroes()
  await fetchLogs()
  await fetchAchievements()
  updateSidebarHeights()
}

// 讀取玩家資源
const fetchUserStatus = async () => {
  try {
    const res = await fetch(`${API_BASE}/users`)
    const users = await res.json()
    const currUser = users.find(u => u.id === userId.value)
    if (currUser) user.value = currUser
  } catch (err) {
    console.error(err)
  }
}

// 讀取盤面進度
const fetchBoard = async () => {
  try {
    const res = await fetch(`${API_BASE}/dungeon/${userId.value}/board`)
    if (res.ok) {
      const data = await res.json()
      updateDungeonState(data)
    } else {
      // 若無盤面，則自動生成一個普通盤面
      await generateBoard('MEDIUM')
    }
  } catch (err) {
    console.error(err)
  }
}

// 讀取道具背包
const fetchInventory = async () => {
  try {
    const res = await fetch(`${API_BASE}/items`)
    const systemItems = await res.json()
    
    // 假設玩家背包內容：為了查詢，我們可以透過 Gacha 或 Chest 獲得道具，或是直接塞滿
    // 由於我們目前後端有 player_inventories，我們可以透過 endpoint 或直接向 /items 查詢玩家擁有的道具
    // 為了解決前端沒 API 查背包的限制，我們可以建立一個虛擬對齊，或者在後端 submit-value 回傳後把 inventory 也返回
    // 或者乾脆前端發送請求取得。等等，後端有 models.PlayerInventory 嗎？
    // 是的！後端有 models.PlayerInventory！但是剛才後端我們沒有提供獨立 GET /users/{id}/inventory 的 endpoint，
    // 沒關係，我們在 backend main.py 中沒有加它，但我們可以直接加一個 API！
    // 或是藉由 `fetch` 後端時直接取得。既然我們是在 pair-programming，我們可以之後補上 `GET /users/{id}/inventory`
    // 目前我們先向 `/items` 撈系統所有道具，並預設背包含有數量 (由日誌或 chest 獲得)。
    // 等等！我們可以在 backend/main.py 裡快速加上 GET /users/{user_id}/inventory，這最正確！
    // 不過，為了不中斷前端計畫，我們先預設讀取 /items 且 quantity 可以透過 response 拿到。
    // 實際上我們可以直接在後端 App.vue 裡把請求發給 API，等下我們快速去 backend/main.py 加上背包查詢 API 即可！
    // 目前我們先寫 fetchInventory 連接 http://localhost:8000/users/{user_id}/inventory：
    const invRes = await fetch(`${API_BASE}/users/${userId.value}/inventory`)
    if (invRes.ok) {
      const invData = await invRes.json()
      // 將系統 item 名稱與數量進行對應
      inventory.value.forEach(slot => {
        const found = invData.find(i => i.item.name === slot.name)
        slot.quantity = found ? found.quantity : 0
      })
    }
  } catch (err) {
    console.error(err)
  }
}

// 讀取擁有的卡牌
const fetchHeroes = async () => {
  try {
    const res = await fetch(`${API_BASE}/users/${userId.value}/heroes`)
    if (res.ok) {
      ownedHeroes.value = await res.json()
    }
  } catch (err) {
    console.error(err)
  }
}

// 讀取日誌
const fetchLogs = async () => {
  try {
    const res = await fetch(`${API_BASE}/users/${userId.value}/logs`)
    if (res.ok) {
      logs.value = await res.json()
      // 自動滾動到最上方 (因後端日誌為降序排列，最新在最上方)
      nextTick(() => {
        if (terminalRef.value) {
          terminalRef.value.scrollTop = 0
        }
      })
    }
  } catch (err) {
    console.error(err)
  }
}

// 讀取成就進度
const fetchAchievements = async () => {
  try {
    const res = await fetch(`${API_BASE}/users/${userId.value}/achievements/progress`)
    if (res.ok) {
      achievements.value = await res.json()
    }
  } catch (err) {
    console.error(err)
  }
}

// 生成新地牢盤面
const generateBoard = async (diff) => {
  try {
    selectedCell.value = null
    activeItemMode.value = null
    const res = await fetch(`${API_BASE}/dungeon/generate-board`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId.value, difficulty: diff })
    })
    if (res.ok) {
      await fetchAllData()
    }
  } catch (err) {
    console.error(err)
  }
}

// 生成 Boss 戰
const generateBossFight = async () => {
  try {
    selectedCell.value = null
    activeItemMode.value = null
    const res = await fetch(`${API_BASE}/dungeon/generate-boss-fight`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId.value, difficulty: 'MEDIUM' })
    })
    if (res.ok) {
      await fetchAllData()
    }
  } catch (err) {
    console.error(err)
  }
}

// 玩家點擊數獨格子
const handleCellClick = async (cell) => {
  if (activeItemMode.value) {
    // 道具施放模式！
    await useItemOnCell(activeItemMode.value, cell.row, cell.col)
    activeItemMode.value = null
  } else {
    // 普通選取模式
    if (cell.is_given || (cell.user_val > 0 && !cell.is_error)) return
    selectedCell.value = cell
  }
}

// 填寫數字
const submitValue = async (val) => {
  if (!selectedCell.value) return
  const { row, col } = selectedCell.value
  
  try {
    const res = await fetch(`${API_BASE}/dungeon/submit-value`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId.value, row, col, val })
    })
    
    if (res.ok) {
      const data = await res.json()
      selectedCell.value = null
      await fetchAllData()
      
      if (!data.is_correct) {
        alert(`填寫錯誤！扣除 HP。`)
      }
    } else {
      const errData = await res.json()
      alert(errData.detail || '操作失敗')
      selectedCell.value = null
      await fetchAllData()
    }
  } catch (err) {
    console.error(err)
  }
}

// 背包點擊道具
const selectItem = async (itemName) => {
  const immediateItems = ['生命藥水', '淨化聖水', '時光沙漏', '替身草人', '幸運四葉草', '封印符咒']
  if (immediateItems.includes(itemName)) {
    // 立即使用道具，不需要選擇座標
    await useItemOnCell(itemName, null, null)
  } else {
    // 進入座標施放模式
    if (activeItemMode.value === itemName) {
      activeItemMode.value = null // 取消
    } else {
      activeItemMode.value = itemName
      showToast(`請點選盤面上的一格以施放【${itemName}】！`, 'info')
    }
  }
}

// 使用道具
const useItemOnCell = async (itemName, row, col) => {
  try {
    const res = await fetch(`${API_BASE}/dungeon/use-item`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: userId.value,
        item_name: itemName,
        row,
        col
      })
    })
    
    if (res.ok) {
      const data = await res.json()
      showToast(data.message, 'success')
      await fetchAllData()
    } else {
      const err = await res.json()
      showToast(err.detail || '使用失敗', 'error')
    }
  } catch (err) {
    console.error(err)
  }
}

// 召喚英雄 (Gacha)
const drawGacha = async (count) => {
  try {
    const res = await fetch(`${API_BASE}/gacha/draw`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId.value, draw_count: count })
    })
    
    if (res.ok) {
      const data = await res.json()
      gachaResults.value = data.results
      showGachaModal.value = true
      await fetchAllData()
    } else {
      const err = await res.json()
      showToast(err.detail || '召喚失敗', 'error')
    }
  } catch (err) {
    console.error(err)
  }
}

// 測試儲值金幣與鑽石
const cheatResources = async () => {
  try {
    const res = await fetch(`${API_BASE}/users/${userId.value}/add-resources?gold=500&gems=1000`, {
      method: 'POST'
    })
    if (res.ok) {
      await fetchAllData()
      showToast('已充值：金幣 +500，鑽石 +1000！', 'success')
    }
  } catch (err) {
    console.error(err)
  }
}

let resizeObserver = null

onMounted(() => {
  initUser()
  window.addEventListener('resize', updateSidebarHeights)
  
  if (middleRef.value) {
    resizeObserver = new ResizeObserver(() => {
      updateSidebarHeights()
    })
    resizeObserver.observe(middleRef.value)
  }
})

onUnmounted(() => {
  window.removeEventListener('resize', updateSidebarHeights)
  if (resizeObserver) {
    resizeObserver.disconnect()
  }
  stopTimer()
})
</script>

<template>
  <div class="game-container">
    <!-- Toast 提示 -->
    <div v-if="toastMessage" class="toast-pixel border-pixel" :class="toastType">
      {{ toastMessage }}
    </div>

    <!-- Header 狀態列 -->
    <header class="game-header border-pixel">
      <h1 class="header-title">
        <span class="icon-pixel">🏰</span> SDOKU DUNGEON
      </h1>
      
      <div class="player-status-group">
        <!-- Floor -->
        <div class="status-item">
          <span class="icon-pixel">🧗</span>
          <span>第 {{ user.current_floor }} 層</span>
        </div>
        
        <!-- Time Left -->
        <div class="status-item timer-item" :class="{ 'warning-time': timeLeft <= 30 }">
          <span class="icon-pixel">⏳</span>
          <span>{{ timeLeft }} 秒</span>
        </div>

        <!-- Buffs -->
        <div v-if="hasStrawman || hasClover || hasSeal" class="status-item" style="gap: 4px;">
          <div v-if="hasStrawman" class="buff-badge border-pixel" style="background-color: #fef08a;" title="替身草人：免除填錯傷害">🌾 草人</div>
          <div v-if="hasClover" class="buff-badge border-pixel" style="background-color: #bbf7d0;" title="幸運四葉草：寶箱翻倍+必得道具">🍀 四葉草</div>
          <div v-if="hasSeal" class="buff-badge border-pixel" style="background-color: #fed7aa;" title="封印符咒：免除填錯陷阱格傷害並直接破解">📜 封印</div>
        </div>
        
        <!-- HP 血條 -->
        <div class="hp-bar-container">
          <span class="icon-pixel">❤️</span>
          <div class="hp-bar-outer">
            <div class="hp-bar-inner" :style="{ width: `${boardState.current_hp}%` }"></div>
            <div class="hp-text">HP: {{ boardState.current_hp }}/100</div>
          </div>
        </div>
        
        <!-- 金幣 -->
        <div class="status-item">
          <span class="icon-pixel">🪙</span>
          <span>{{ user.gold }}</span>
        </div>
        
        <!-- 鑽石 -->
        <div class="status-item">
          <span class="icon-pixel">💎</span>
          <span>{{ user.gems }}</span>
        </div>

        <button class="btn-pixel green" style="font-size: 12px; padding: 6px 10px;" @click="cheatResources">
          🧪 測試儲值
        </button>
      </div>
    </header>

    <!-- Boss 戰血條條 banner -->
    <div v-if="boss.name && boss.hp > 0" class="boss-banner border-pixel">
      <div class="boss-title">👹 BOSS: {{ boss.name }}</div>
      
      <!-- 護盾 -->
      <div class="boss-shield-group">
        <span>🛡️</span>
        <span v-for="n in boss.shield" :key="n">⭐</span>
        <span v-if="boss.shield === 0" style="color: #ff3344; font-size: 14px; font-family: var(--font-pixel);">BREAK!</span>
      </div>

      <!-- Boss HP -->
      <div class="boss-hp-outer">
        <div class="boss-hp-inner" :style="{ width: `${(boss.hp / boss.max_hp) * 100}%` }"></div>
        <div class="boss-hp-text">HP: {{ boss.hp }}/{{ boss.max_hp }}</div>
      </div>
      
      <div v-if="boss.cursed_number > 0" style="font-size: 14px; color: #ff3344; font-weight: bold;">
        ⚠️ 數字詛咒: {{ boss.cursed_number }}
      </div>
    </div>

    <!-- 主要大區 -->
    <main class="game-main-area">
      <!-- 左側欄：卡牌與背包 -->
      <aside class="left-panel" :style="{ height: middleHeight }">
        <!-- 道具背包 -->
        <section class="section-card border-pixel">
          <h2 class="panel-title">🎒 道具背包</h2>
          <div class="inventory-grid">
            <div 
              v-for="item in inventory" 
              :key="item.name"
              class="item-slot"
              :class="{ selected: activeItemMode === item.name }"
              :title="item.name"
              @click="selectItem(item.name)"
              @mouseenter="hoveredItemName = item.name"
              @mouseleave="hoveredItemName = null"
            >
              <div class="item-icon">{{ item.icon }}</div>
            </div>
          </div>
          
          <!-- 道具說明 -->
          <div style="margin-top: 10px; padding: 8px; border: 2px dashed #000; background: #fff; font-size: 11px; line-height: 1.4; border-radius: 4px; min-height: 52px; box-sizing: border-box; display: flex; flex-direction: column; justify-content: center;">
            <div v-if="selectedItemInfo">
              <div style="font-weight: 700; border-bottom: 1px dashed #ccc; padding-bottom: 2px; margin-bottom: 4px; display: flex; justify-content: space-between; font-size: 12px;">
                <span>{{ selectedItemInfo.icon }} {{ selectedItemInfo.name }}</span>
                <span style="color: var(--btn-blue);">擁有: {{ selectedItemInfo.quantity }}</span>
              </div>
              <div style="color: #555; font-size: 11px;">{{ selectedItemInfo.description }}</div>
            </div>
            <div v-else style="color: #888; text-align: center; font-size: 11px;">
              💡 點選道具可查看說明與數量
            </div>
          </div>

          <div v-if="activeItemMode" style="margin-top: 8px; font-size: 11px; color: var(--btn-blue); font-weight: bold; text-align: center;">
            🎯 道具施放中... 點選盤面格子
          </div>
        </section>

        <!-- 英雄卡池與召喚 -->
        <section class="section-card border-pixel">
          <h2 class="panel-title">🧙 英雄召喚</h2>
          <div style="display: flex; gap: 8px; margin-bottom: 16px;">
            <button class="btn-pixel" style="flex: 1; font-size: 12px;" @click="drawGacha(1)">
              召喚 1 次<br>(100💎)
            </button>
            <button class="btn-pixel blue" style="flex: 1; font-size: 12px;" @click="drawGacha(10)">
              召喚 10 次<br>(1000💎)
            </button>
          </div>
          
          <h3 style="font-size: 14px; margin-bottom: 8px;">已解鎖英雄 ({{ ownedHeroes.length }})</h3>
          <div class="gacha-hero-list">
            <div
              v-for="ph in ownedHeroes"
              :key="ph.id"
              class="hero-strip"
              :class="{ 'hero-strip--expanded': selectedHeroId === ph.id }"
              @click="toggleHeroDetail(ph.id)"
            >
              <div style="width: 100%;">
                <div class="hero-strip-header">
                  <div class="hero-name-group">
                    <span class="hero-tag" :class="ph.hero.rarity.toLowerCase()">
                      {{ ph.hero.rarity }}
                    </span>
                    <span style="font-weight: 700; font-size: 14px; margin-top: 4px;">
                      {{ ph.hero.name }} ({{ ph.hero.element }})
                    </span>
                  </div>
                  <div style="display: flex; align-items: center; gap: 6px;">
                    <div class="star-rating">
                      <span v-for="s in ph.stars" :key="s">★</span>
                    </div>
                    <span class="hero-expand-arrow" :class="{ rotated: selectedHeroId === ph.id }">▼</span>
                  </div>
                </div>

                <!-- 展開的能力說明 -->
                <Transition name="hero-detail">
                  <div v-if="selectedHeroId === ph.id" class="hero-skill-panel">
                    <div class="hero-skill-name">
                      <span :class="ph.hero.is_active ? 'skill-badge active' : 'skill-badge passive'">
                        {{ ph.hero.is_active ? '主動技' : '被動技' }}
                      </span>
                      ⚔️ {{ ph.hero.skill_name }}
                    </div>
                    <div class="hero-skill-desc">{{ ph.hero.skill_description }}</div>
                  </div>
                </Transition>
              </div>
            </div>
          </div>
        </section>

      </aside>

      <!-- 中間：數獨盤面 -->
      <section ref="middleRef" class="sudoku-wrapper border-pixel">
        <div style="display: flex; gap: 10px; margin-bottom: 16px; width: 100%; max-width: 500px;">
          <button class="btn-pixel green" style="flex: 1; font-size: 12px;" @click="generateBoard('MEDIUM')">
            🆕 新普通關卡
          </button>
          <button class="btn-pixel red" style="flex: 1; font-size: 12px;" @click="generateBossFight">
            👹 挑戰 Boss
          </button>
        </div>

        <div class="sudoku-grid">
          <div 
            v-for="(cell, index) in board" 
            :key="index"
            class="sudoku-cell"
            :class="{ 
              given: cell.is_given, 
              selected: selectedCell && selectedCell.row === cell.row && selectedCell.col === cell.col,
              weakness: cell.event_type === 'WEAKNESS',
              foggy: cell.is_foggy
            }"
            @click="handleCellClick(cell)"
          >
            <!-- 數字呈現 -->
            <span v-if="cell.user_val > 0 && !cell.is_foggy" :style="{ color: cell.is_error ? '#ff4757' : '#2ecc71' }" style="font-weight: 700;">
              {{ cell.user_val }}
            </span>
            <span v-else-if="cell.val > 0 && !cell.is_foggy">
              {{ cell.val }}
            </span>
            <!-- ✏️ 鉛筆草稿數字 -->
            <div v-else-if="cell.pencil_notes && cell.pencil_notes.length > 0 && !cell.is_foggy" class="pencil-notes-container">
              <span v-for="note in cell.pencil_notes" :key="note" class="pencil-note">{{ note }}</span>
            </div>
            
            <!-- 事件圖標 -->
            <div v-if="cell.event_type && !cell.is_triggered" class="cell-event" :title="getEventName(cell.event_type)">
              {{ getEventEmoji(cell.event_type) }}
            </div>
          </div>
        </div>

        <!-- 數字鍵盤 -->
        <div class="keyboard-panel">
          <button 
            v-for="num in 9" 
            :key="num"
            class="key-btn"
            @click="submitValue(num)"
          >
            {{ num }}
          </button>
        </div>
      </section>

      <!-- 右側：日誌與成就 -->
      <aside class="right-panel" :style="{ height: middleHeight }">
        <!-- 分頁切換 -->
        <div style="display: flex; gap: 8px;">
          <button class="btn-pixel" :class="{ disabled: !showAchievements }" style="flex: 1; font-size: 12px;" @click="showAchievements = false">
            📜 冒險日誌
          </button>
          <button class="btn-pixel blue" :class="{ disabled: showAchievements }" style="flex: 1; font-size: 12px;" @click="showAchievements = true">
            🏆 成就獎章
          </button>
        </div>

        <!-- 戰鬥日誌 (預設) -->
        <section v-if="!showAchievements" class="section-card" style="flex: 1; display: flex; flex-direction: column;">
          <h2 class="panel-title" style="margin-bottom: 10px;">📜 戰鬥日誌 console</h2>
          <div ref="terminalRef" class="log-terminal">
            <div 
              v-for="log in logs" 
              :key="log.id"
              class="log-line"
              :class="log.action_type.toLowerCase()"
            >
              [{{ log.created_at.split('T')[1].split('.')[0] }}] {{ log.message }}
            </div>
          </div>
        </section>

        <!-- 成就面板 -->
        <section v-else class="section-card" style="flex: 1; display: flex; flex-direction: column;">
          <h2 class="panel-title" style="margin-bottom: 10px;">🏆 成就圖鑑</h2>
          <div class="achievement-list">
            <div 
              v-for="ach in achievements" 
              :key="ach.achievement.id" 
              class="achievement-item"
              :class="{ locked: !ach.is_unlocked }"
            >
              <div class="ach-icon">
                {{ ach.is_unlocked ? '🏆' : '🔒' }}
              </div>
              <div class="ach-info">
                <div class="ach-title">{{ ach.achievement.title }}</div>
                <div class="ach-desc">{{ ach.achievement.description }}</div>
              </div>
            </div>
          </div>
        </section>
        <!-- 地牢事件說明 -->
        <section class="section-card" style="padding: 12px 0 0 0; font-size: 11px; line-height: 1.5; margin-top: 10px;">
          <h2 class="panel-title" style="margin-bottom: 8px; font-size: 14px; border-bottom: 2px solid #000; padding-bottom: 4px;">👾 地牢事件指南</h2>
          <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 6px;">
            <div>🎁 <strong>寶箱</strong>: 隨機金幣/道具</div>
            <div>👾 <strong>怪物</strong>: 擊殺獲得 80🪙</div>
            <div>⚠️ <strong>陷阱</strong>: 填錯扣雙倍HP</div>
            <div>🌀 <strong>傳送門</strong>: 自動揭一空格</div>
            <div>🔮 <strong>祭壇</strong>: 恢復 20點 HP</div>
            <div>✨ <strong>弱點</strong>: 削弱 Boss 護盾</div>
          </div>
        </section>
      </aside>
    </main>

    <!-- 抽卡展示 Modal -->
    <div v-if="showGachaModal" class="modal-overlay">
      <div class="gacha-modal-card border-pixel">
        <h2 style="font-family: var(--font-pixel); color: var(--btn-yellow);">✨ 召喚結果 ✨</h2>
        
        <div class="gacha-reveal-container">
          <div 
            v-for="(result, idx) in gachaResults" 
            :key="idx"
            class="card-item"
            :class="{ ssr: result.hero.rarity === 'SSR' }"
          >
            <span class="hero-tag" :class="result.hero.rarity.toLowerCase()">
              {{ result.hero.rarity }}
            </span>
            <span style="font-weight: bold; font-size: 13px; margin-top: 6px; word-break: break-all;">
              {{ result.hero.name }}
            </span>
            <div class="star-rating" style="margin-top: 4px;">
              <span v-for="s in result.stars_after" :key="s">★</span>
            </div>
            <div v-if="result.gems_compensated > 0" style="color: var(--btn-yellow); font-size: 9px; font-weight: bold; margin-top: 4px;">
              💎+100
            </div>
            <div v-else-if="result.is_new" style="color: var(--btn-green); font-size: 9px; font-weight: bold; margin-top: 4px;">
              NEW!
            </div>
          </div>
        </div>
        
        <button class="btn-pixel red" style="margin-top: 20px;" @click="showGachaModal = false">
          確認離開
        </button>
      </div>
    </div>
  </div>
</template>
