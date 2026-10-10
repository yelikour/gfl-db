<template>
  <div class="page">
    <div class="panel filters">
      <div class="filter-row">
        <n-input
          v-model:value="search"
          placeholder="搜索：名称 / 代号 / 英文名（如 UMP45、内格夫、Negev）"
          clearable
          size="large"
        >
          <template #prefix>🔍</template>
        </n-input>
        <n-select v-model:value="sortKey" :options="sortOptions" size="large" style="width: 190px" />
      </div>
      <div class="filter-row wrap">
        <div class="filter-group">
          <span class="flabel">枪种</span>
          <button
            v-for="t in types" :key="t"
            class="chip" :class="{ active: activeTypes.has(t) }"
            :style="activeTypes.has(t) ? { borderColor: TYPE_COLOR[t], color: TYPE_COLOR[t] } : {}"
            @click="toggle('type', t)"
          >{{ t }}</button>
        </div>
        <div class="filter-group">
          <span class="flabel">稀有度</span>
          <button
            v-for="r in [5, 4, 3, 2]" :key="r"
            class="chip stars" :class="{ active: activeRarities.has(r) }"
            @click="toggle('rarity', r)"
          >{{ '★'.repeat(r) }}</button>
        </div>
        <div class="filter-group">
          <span class="flabel">改造</span>
          <button class="chip" :class="{ active: modFilter === true }" @click="modFilter = modFilter === true ? null : true">可改造</button>
          <button class="chip" :class="{ active: modFilter === false }" @click="modFilter = modFilter === false ? null : false">未开放</button>
        </div>
        <div class="filter-group grow">
          <span class="flabel">势力</span>
          <n-select
            v-model:value="bgFilter" :options="bgOptions" clearable size="small"
            placeholder="全部" style="width: 150px"
          />
        </div>
        <span v-if="activeCount" class="clear-btn" @click="clearAll">清空筛选（{{ activeCount }}）</span>
      </div>
    </div>

    <div class="result-info">
      共 <b>{{ filtered.length }}</b> 名人形
      <template v-if="activeCount">（已筛选，全部 {{ all.length }} 名）</template>
    </div>

    <div class="grid">
      <RouterLink v-for="d in filtered" :key="d.wid" :to="`/dolls/${d.wid}`" class="card panel">
        <div class="thumb-wrap" :style="{ background: thumbBg(d.type) }">
          <img v-if="d.thumb" :src="d.thumb" loading="lazy" :alt="d.name" />
          <div v-else class="noimg">无立绘</div>
          <span class="type-badge" :style="{ background: TYPE_COLOR[d.type], color: '#14161a' }">{{ d.type }}</span>
          <span v-if="d.has_mod" class="mod-flag">MOD</span>
        </div>
        <div class="card-body">
          <div class="name">{{ d.name }}</div>
          <div class="code">{{ d.code || d.en_name }}</div>
          <div class="meta-row">
            <span class="stars">{{ '★'.repeat(d.rarity) }}</span>
            <span class="skins" v-if="d.skin_count">{{ d.skin_count }} 皮肤</span>
          </div>
        </div>
      </RouterLink>
    </div>

    <n-back-top :right="40" :bottom="40" />
  </div>
</template>

<script setup lang="ts">
import { NBackTop, NInput, NSelect } from 'naive-ui'
import { computed, onMounted, ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { loadIndex, TYPE_COLOR, type DollIndex } from '../data'

const route = useRoute()
const all = ref<DollIndex[]>([])
const search = ref('')
const sortKey = ref('id-asc')
const activeTypes = ref(new Set<string>())
const activeRarities = ref(new Set<number>())
const modFilter = ref<boolean | null>(null)
const bgFilter = ref<string | null>(null)

const types = ['HG', 'SMG', 'AR', 'RF', 'MG', 'SG']
const sortOptions = [
  { label: '编号 升序', value: 'id-asc' },
  { label: '编号 降序', value: 'id-desc' },
  { label: '实装日期 新→旧', value: 'date-desc' },
  { label: '实装日期 旧→新', value: 'date-asc' },
  { label: '皮肤数 多→少', value: 'skins-desc' },
  { label: '名称 A→Z', value: 'name-asc' }
]

const bgOptions = computed(() => {
  const m = new Map<string, string>()
  for (const d of all.value) if (d.bg_cn) m.set(d.bg, d.bg_cn)
  return [...m.entries()].map(([v, l]) => ({ value: v, label: l }))
})

function toggle(kind: 'type' | 'rarity', v: string | number) {
  const refSet = kind === 'type' ? activeTypes : activeRarities
  const s = new Set(refSet.value)
  if (s.has(v as any)) s.delete(v as any)
  else s.add(v as any)
  refSet.value = s
}

const activeCount = computed(
  () => activeTypes.value.size + activeRarities.value.size + (modFilter.value !== null ? 1 : 0) + (bgFilter.value ? 1 : 0)
)

function clearAll() {
  activeTypes.value = new Set()
  activeRarities.value = new Set()
  modFilter.value = null
  bgFilter.value = null
}

const filtered = computed(() => {
  const q = search.value.trim().toLowerCase()
  let list = all.value.filter((d) => {
    if (activeTypes.value.size && !activeTypes.value.has(d.type)) return false
    if (activeRarities.value.size && !activeRarities.value.has(d.rarity)) return false
    if (modFilter.value !== null && d.has_mod !== modFilter.value) return false
    if (bgFilter.value && d.bg !== bgFilter.value) return false
    if (q) {
      const hay = `${d.name} ${d.code} ${d.en_name}`.toLowerCase()
      if (!hay.includes(q)) return false
    }
    return true
  })
  const by: Record<string, (a: DollIndex, b: DollIndex) => number> = {
    'id-asc': (a, b) => a.id - b.id,
    'id-desc': (a, b) => b.id - a.id,
    'date-desc': (a, b) => (b.launch_date || '').localeCompare(a.launch_date || '') || a.id - b.id,
    'date-asc': (a, b) => (a.launch_date || '').localeCompare(b.launch_date || '') || a.id - b.id,
    'skins-desc': (a, b) => b.skin_count - a.skin_count || a.id - b.id,
    'name-asc': (a, b) => `${a.name}`.localeCompare(`${b.name}`, 'zh')
  }
  list = [...list].sort(by[sortKey.value] ?? by['id-asc'])
  return list
})

function thumbBg(type: string) {
  return `linear-gradient(160deg, rgba(212,176,106,0.10), rgba(0,0,0,0.25) 70%)`
}

onMounted(async () => {
  all.value = await loadIndex()
  const q = route.query.q
  if (typeof q === 'string' && q) search.value = q
})
</script>

<style scoped>
.filters { margin-bottom: 14px; }
.filter-row { display: flex; gap: 12px; align-items: center; }
.filter-row.wrap { flex-wrap: wrap; margin-top: 12px; }
.filter-group { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
.filter-group.grow { flex: 1; justify-content: flex-end; }
.flabel { color: var(--gfl-text-dim); font-size: 13px; margin-right: 2px; }
.chip {
  background: transparent;
  color: var(--gfl-text-dim);
  border: 1px solid #3a3f47;
  border-radius: 6px;
  padding: 3px 10px;
  font-size: 13px;
  cursor: pointer;
  font-weight: 600;
}
.chip:hover { border-color: var(--gfl-gold); color: var(--gfl-gold-bright); }
.chip.active { border-color: var(--gfl-gold-bright); color: var(--gfl-gold-bright); background: rgba(212,176,106,0.08); }
.clear-btn { color: var(--gfl-text-dim); font-size: 13px; cursor: pointer; text-decoration: underline; }
.clear-btn:hover { color: var(--gfl-gold-bright); }
.result-info { color: var(--gfl-text-dim); margin: 0 4px 12px; font-size: 14px; }
.result-info b { color: var(--gfl-gold-bright); }

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(158px, 1fr));
  gap: 14px;
}
.card {
  padding: 0 !important;
  overflow: hidden;
  transition: transform 0.15s ease, border-color 0.15s ease;
  text-decoration: none !important;
  color: inherit;
  display: block;
}
.card:hover { transform: translateY(-3px); border-color: rgba(212,176,106,0.55); }
.thumb-wrap {
  position: relative;
  aspect-ratio: 1 / 1.05;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  overflow: hidden;
}
.thumb-wrap img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: top center;
}
.noimg {
  color: var(--gfl-text-dim);
  align-self: center;
  font-size: 13px;
}
.type-badge {
  position: absolute;
  top: 8px;
  left: 8px;
  z-index: 2;
}
.mod-flag {
  position: absolute;
  top: 8px;
  right: 8px;
  z-index: 2;
  background: rgba(20, 22, 26, 0.85);
  color: #f28a8a;
  border: 1px solid #f28a8a;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 800;
  padding: 1px 5px;
}
.card-body { padding: 10px 12px 12px; }
.name { font-weight: 700; font-size: 15px; }
.code { color: var(--gfl-text-dim); font-size: 12px; margin-top: 1px; }
.meta-row { display: flex; justify-content: space-between; align-items: center; margin-top: 6px; }
.meta-row .stars { font-size: 11px; }
.skins { color: var(--gfl-text-dim); font-size: 11px; }
</style>
