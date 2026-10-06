<template>
  <div class="home">
    <!-- HERO -->
    <section class="hero">
      <div class="hero-art">
        <img
          v-for="(h, i) in heroArts" :key="h.src" :src="h.src"
          :alt="h.name" :loading="i < 2 ? 'eager' : 'lazy'"
          :style="{ animationDelay: `${i * 6}s` }"
        />
      </div>
      <div class="hero-shade"></div>
      <div class="hero-content">
        <p class="kicker">GIRLS' FRONTLINE DATABASE</p>
        <h1>少女前线资料库</h1>
        <p class="lead">
          451 位战术人形的图鉴、立绘、数值与技能数据库<br />
          基础 / 破损 / 改造 / 皮肤立绘 · Lv.100 与 MOD3 数值 · 技能成长
        </p>
        <div class="quick">
          <input
            v-model="q" placeholder="搜索人形：UMP45 / 内格夫 / Kar98k …"
            @keyup.enter="goSearch"
          />
          <button @click="goSearch">搜索</button>
        </div>
        <div class="hero-actions">
          <button class="btn-primary" @click="$router.push('/dolls')">进入人形图鉴</button>
          <button class="btn-ghost" @click="$router.push('/about')">数据来源与说明</button>
        </div>
      </div>
      <div class="hero-artist" v-if="heroArts.length">
        立绘：{{ heroArts[heroIdx % heroArts.length].name }} ·
        {{ heroArts[heroIdx % heroArts.length].label }}
      </div>
      <div class="hero-stats">
        <RouterLink to="/dolls" class="hstat">
          <b>{{ meta.count ?? '—' }}</b><span>人形图鉴</span>
        </RouterLink>
        <div class="hstat"><b>{{ meta.with_skins ?? '—' }}</b><span>拥有皮肤</span></div>
        <div class="hstat"><b>{{ fmtNum(meta.image_files) }}</b><span>立绘图片</span></div>
        <div class="hstat"><b>{{ meta.data_date?.slice(0, 7) ?? '—' }}</b><span>数据版本</span></div>
      </div>
    </section>

    <div class="wrap">
      <!-- 最新实装 -->
      <section class="panel sec">
        <div class="sec-head">
          <h2>最新实装</h2>
          <RouterLink to="/dolls" class="more">查看全部 →</RouterLink>
        </div>
        <div class="mini-grid">
          <RouterLink v-for="d in newest" :key="d.wid" :to="`/dolls/${d.wid}`" class="mini-card">
            <img :src="d.thumb" :alt="d.name" loading="lazy" />
            <span class="type-badge" :style="{ background: TYPE_COLOR[d.type], color: '#14161a' }">{{ d.type }}</span>
            <div class="mini-name">{{ d.name }}</div>
            <div class="mini-date">{{ d.launch_date }}</div>
          </RouterLink>
        </div>
      </section>

      <!-- 随机逛逛 -->
      <section class="panel sec">
        <div class="sec-head">
          <h2>人形速览</h2>
          <button class="more" @click="reshuffle">换一批 ⟳</button>
        </div>
        <div class="mini-grid">
          <RouterLink v-for="d in randomPicks" :key="d.wid" :to="`/dolls/${d.wid}`" class="mini-card">
            <img :src="d.thumb" :alt="d.name" loading="lazy" />
            <span class="type-badge" :style="{ background: TYPE_COLOR[d.type], color: '#14161a' }">{{ d.type }}</span>
            <div class="mini-name">{{ d.name }}</div>
            <div class="mini-date">{{ '★'.repeat(d.rarity) }}</div>
          </RouterLink>
        </div>
      </section>

      <!-- 日志 + 说明 -->
      <section class="two-col">
        <div class="panel">
          <h2>更新日志</h2>
          <ul class="updates">
            <li v-for="u in updates" :key="u.date">
              <span class="date">{{ u.date }}</span> — {{ u.text }}
            </li>
          </ul>
        </div>
        <div class="panel">
          <h2>关于本站</h2>
          <p class="about-p">
            本站为玩家自制、非官方的《少女前线》资料站。数据来自游戏客户端本地配置与
            <a href="https://gfwiki.org" target="_blank" rel="noopener">gfwiki</a>
            公开图鉴模块；立绘自 Steam 客户端标准资源包只读提取。
          </p>
          <p class="about-p dim">
            Girls' Frontline © 散爆网络 / MICA Team。本站仅供玩家交流，不作商业用途；
            如有不适宜展示的内容请联系处理。
          </p>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { loadIndex, TYPE_COLOR, type DollIndex } from '../data'

const router = useRouter()
const meta = ref<any>({})
const dolls = ref<DollIndex[]>([])
const q = ref('')
const heroIdx = ref(0)
let heroTimer: number | undefined

const updates = [
  { date: '2026-10-05', text: '首个版本：451 名人形、立绘 / 破损 / 改造 / 皮肤、Lv.100 与 MOD3 数值、技能 Lv1/Lv10、光环与获取信息；全屏立绘查看器上线。' }
]

// 主视觉：经典人形（优先改造立绘）
const HERO = [
  { wid: 55, name: 'M4A1', label: 'MOD 立绘', mod: true },
  { wid: 103, name: 'UMP45', label: 'MOD 立绘', mod: true },
  { wid: 65, name: 'HK416', label: 'MOD 立绘', mod: true },
  { wid: 206, name: 'AK-12', label: '基础立绘', mod: false },
  { wid: 48, name: 'WA2000', label: '基础立绘', mod: false },
  { wid: 366, name: 'SPAS-15', label: '基础立绘', mod: false }
]

const heroArts = computed(() =>
  HERO.map((h) => {
    const d = dolls.value.find((x) => x.wid === h.wid)
    const src = d ? (h.mod ? d.mod_normal || d.normal : d.normal) : ''
    return src ? { ...h, src } : null
  }).filter(Boolean as any) as { wid: number; name: string; label: string; src: string }[]
)

const newest = computed(() =>
  [...dolls.value]
    .filter((d) => d.thumb && d.launch_date)
    .sort((a, b) => b.launch_date.localeCompare(a.launch_date))
    .slice(0, 12)
)

const randomPicks = ref<DollIndex[]>([])
function reshuffle() {
  const pool = dolls.value.filter((d) => d.thumb)
  const picks: DollIndex[] = []
  const used = new Set<number>()
  while (picks.length < Math.min(12, pool.length)) {
    const i = Math.floor(Math.random() * pool.length)
    if (!used.has(i)) {
      used.add(i)
      picks.push(pool[i])
    }
  }
  randomPicks.value = picks
}

function goSearch() {
  router.push({ path: '/dolls', query: q.value.trim() ? { q: q.value.trim() } : {} })
}

function fmtNum(n?: number) {
  return typeof n === 'number' ? n >= 1000 ? (n / 1000).toFixed(1).replace(/\.0$/, '') + 'k' : n : '—'
}

onMounted(async () => {
  try {
    const [m, idx] = await Promise.all([fetch('data/meta.json').then((r) => r.json()), loadIndex()])
    meta.value = m
    dolls.value = idx
    reshuffle()
  } catch {
    /* offline dev without data */
  }
  heroTimer = window.setInterval(() => { heroIdx.value++ }, 6000)
})
onUnmounted(() => window.clearInterval(heroTimer))
</script>

<style scoped>
.home { margin: 0; }
.wrap { max-width: 1280px; margin: 0 auto; padding: 0 16px; }

/* ---------- HERO ---------- */
.hero {
  position: relative;
  min-height: min(92vh, 900px);
  display: flex;
  align-items: center;
  overflow: hidden;
}
.hero-art { position: absolute; inset: 0; }
.hero-art img {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: 72% 18%;
  opacity: 0;
  animation: heroFade 36s infinite;
}
@keyframes heroFade {
  0%, 15% { opacity: 1; }
  25%, 100% { opacity: 0; }
}
.hero-shade {
  position: absolute;
  inset: 0;
  background:
    linear-gradient(90deg, rgba(13, 14, 17, 0.94) 0%, rgba(13, 14, 17, 0.72) 34%, rgba(13, 14, 17, 0.10) 70%),
    linear-gradient(0deg, rgba(13, 14, 17, 0.95) 0%, rgba(13, 14, 17, 0) 34%),
    linear-gradient(180deg, rgba(13, 14, 17, 0.55) 0%, rgba(13, 14, 17, 0) 22%);
}
.hero-content {
  position: relative;
  z-index: 2;
  width: min(1280px, 100%);
  margin: 0 auto;
  padding: 110px 24px 140px;
}
.kicker {
  color: var(--gfl-gold);
  letter-spacing: 6px;
  font-size: 13px;
  font-weight: 700;
  margin: 0 0 10px;
  opacity: 0.9;
}
h1 {
  margin: 0 0 18px;
  font-size: clamp(38px, 6vw, 64px);
  font-weight: 900;
  letter-spacing: 12px;
  line-height: 1.15;
  background: linear-gradient(180deg, #f7e6b8 15%, #e8c877 55%, #b8964f 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  text-shadow: 0 8px 40px rgba(212, 176, 106, 0.15);
}
.lead {
  color: var(--gfl-text);
  line-height: 2;
  margin: 0 0 26px;
  font-size: 15.5px;
  max-width: 560px;
}
.quick {
  display: flex;
  gap: 10px;
  max-width: 480px;
  margin-bottom: 20px;
}
.quick input {
  flex: 1;
  background: rgba(20, 22, 26, 0.75);
  border: 1px solid rgba(212, 176, 106, 0.35);
  border-radius: 8px;
  padding: 11px 16px;
  color: var(--gfl-text);
  font-size: 14px;
  outline: none;
  backdrop-filter: blur(6px);
}
.quick input:focus { border-color: var(--gfl-gold-bright); }
.quick input::placeholder { color: #6d6a62; }
.quick button {
  background: linear-gradient(180deg, #e8c877, #c9a458);
  color: #14161a;
  font-weight: 700;
  border: none;
  border-radius: 8px;
  padding: 0 24px;
  font-size: 14.5px;
  cursor: pointer;
}
.quick button:hover { filter: brightness(1.08); }
.hero-actions { display: flex; gap: 12px; }
.btn-primary, .btn-ghost {
  border-radius: 8px;
  padding: 10px 26px;
  font-size: 14.5px;
  cursor: pointer;
  font-weight: 600;
  letter-spacing: 1px;
}
.btn-primary {
  background: linear-gradient(180deg, #e8c877, #c9a458);
  color: #14161a;
  border: none;
  font-weight: 800;
}
.btn-primary:hover { filter: brightness(1.08); }
.btn-ghost {
  background: rgba(20, 22, 26, 0.6);
  color: var(--gfl-gold-bright);
  border: 1px solid rgba(212, 176, 106, 0.4);
}
.btn-ghost:hover { border-color: var(--gfl-gold-bright); }

.hero-artist {
  position: absolute;
  right: 20px;
  bottom: 84px;
  z-index: 2;
  color: rgba(232, 230, 224, 0.5);
  font-size: 12px;
  letter-spacing: 1px;
  text-shadow: 0 1px 6px rgba(0, 0, 0, 0.8);
}
.hero-stats {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 3;
  display: flex;
  justify-content: center;
  gap: clamp(24px, 6vw, 90px);
  padding: 16px 20px 18px;
  background: rgba(13, 14, 17, 0.55);
  border-top: 1px solid rgba(212, 176, 106, 0.22);
  backdrop-filter: blur(10px);
}
.hstat { text-align: center; color: inherit; text-decoration: none !important; }
.hstat b {
  display: block;
  font-size: clamp(20px, 2.6vw, 28px);
  font-weight: 800;
  color: var(--gfl-gold-bright);
}
.hstat span { font-size: 12px; color: var(--gfl-text-dim); letter-spacing: 2px; }

/* ---------- SECTIONS ---------- */
.sec { margin-top: 22px; }
.sec-head {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 14px;
}
.sec-head h2 {
  margin: 0;
  font-size: 18px;
  color: var(--gfl-gold);
  letter-spacing: 2px;
}
.more {
  color: var(--gfl-text-dim);
  font-size: 13px;
  cursor: pointer;
  background: none;
  border: none;
  text-decoration: none;
  font-family: inherit;
}
.more:hover { color: var(--gfl-gold-bright); }

.mini-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(128px, 1fr));
  gap: 12px;
}
.mini-card {
  position: relative;
  border-radius: 10px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.07);
  text-decoration: none !important;
  color: inherit;
  display: block;
  transition: transform 0.15s ease, border-color 0.15s ease;
  background: linear-gradient(180deg, #191c21, #101216);
}
.mini-card:hover { transform: translateY(-3px); border-color: rgba(212, 176, 106, 0.5); }
.mini-card img {
  width: 100%;
  aspect-ratio: 1 / 1.1;
  object-fit: cover;
  object-position: top center;
  display: block;
}
.mini-card .type-badge {
  position: absolute;
  top: 8px;
  left: 8px;
  font-size: 11px;
}
.mini-name {
  font-size: 13.5px;
  font-weight: 700;
  padding: 7px 10px 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.mini-date {
  color: var(--gfl-text-dim);
  font-size: 11px;
  padding: 2px 10px 9px;
  letter-spacing: 0.5px;
}

/* ---------- TWO COL ---------- */
.two-col {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-top: 22px;
}
.two-col h2 {
  margin: 0 0 12px;
  font-size: 17px;
  color: var(--gfl-gold);
}
.updates { margin: 0; padding-left: 20px; line-height: 2; font-size: 14px; }
.updates .date { color: var(--gfl-gold-bright); font-weight: 700; }
.about-p { line-height: 2; font-size: 14px; margin: 0 0 10px; }
.about-p.dim { color: var(--gfl-text-dim); font-size: 13px; }

@media (max-width: 760px) {
  .hero-art img { object-position: 78% 10%; }
  .hero-content { padding: 90px 20px 150px; }
  .lead { font-size: 14px; }
  .two-col { grid-template-columns: 1fr; }
  .hero-artist { display: none; }
  .mini-grid { grid-template-columns: repeat(3, 1fr); }
}
</style>
