<template>
  <div class="page" v-if="doll">
    <div class="crumbs">
      <RouterLink to="/dolls">人形图鉴</RouterLink>
      <span class="sep">/</span>
      <span>{{ doll.name }}</span>
    </div>

    <div class="layout">
      <!-- LEFT: art viewer -->
      <div class="art panel">
        <div class="art-stage" @click="fullscreen = true">
          <img v-if="currentArt" :src="currentArt" :key="currentArt" :alt="doll.name" />
          <div v-else class="noart">该形态暂无立绘</div>
        </div>
        <div class="art-controls">
          <div class="ctrl-group">
            <button
              v-for="o in formOptions" :key="o.key"
              class="chip" :class="{ active: form === o.key }"
              :disabled="!o.available"
              @click="form = o.key"
            >{{ o.label }}</button>
          </div>
          <div class="ctrl-group">
            <button
              v-if="currentArtSet.damaged"
              class="chip" :class="{ active: damaged }"
              @click="damaged = !damaged"
            >破损</button>
            <button v-if="currentArt" class="chip" @click="downloadArt">下载原图</button>
          </div>
          <div class="hint">点击立绘全屏查看</div>
        </div>
        <div class="art-caption">{{ currentCaption }}</div>
      </div>

      <!-- fullscreen art viewer -->
      <div v-if="fullscreen && currentArt" class="art-fullscreen" @click="fullscreen = false">
        <img :src="currentArt" :alt="doll.name" />
        <div class="fs-hint">点击任意处关闭（Esc）</div>
      </div>

      <!-- RIGHT: info -->
      <div class="info">
        <div class="panel head">
          <div class="title-row">
            <h1>{{ doll.name }}</h1>
            <span class="type-badge" :style="{ background: TYPE_COLOR[doll.type], color: '#14161a' }">{{ doll.type }}</span>
            <span class="stars">{{ '★'.repeat(doll.rarity) }}</span>
          </div>
          <div class="code-line">{{ doll.code }}<template v-if="doll.en_name && doll.en_name !== doll.code"> · {{ doll.en_name }}</template></div>
          <n-descriptions :column="2" size="small" label-placement="left" bordered>
            <n-descriptions-item label="编号">No.{{ doll.id }}</n-descriptions-item>
            <n-descriptions-item label="势力">{{ doll.bg_cn || '—' }}</n-descriptions-item>
            <n-descriptions-item label="枪种">{{ doll.type_cn }}</n-descriptions-item>
            <n-descriptions-item label="实装">{{ doll.launch_date || '—' }}</n-descriptions-item>
            <n-descriptions-item label="画师">{{ doll.illu || '—' }}</n-descriptions-item>
            <n-descriptions-item label="CV">{{ doll.cv || '—' }}</n-descriptions-item>
            <n-descriptions-item label="制造时间">{{ produceTimeFmt(doll.produce_time) }}</n-descriptions-item>
            <n-descriptions-item label="改造">
              <n-tag v-if="doll.mod" size="small" type="error" :bordered="false">可改造</n-tag>
              <span v-else>未开放</span>
            </n-descriptions-item>
          </n-descriptions>
          <div class="obtain">
            <b>获取：</b>{{ doll.obtain.join('；') }}
          </div>
        </div>

        <!-- stats -->
        <div class="panel">
          <h2>数值</h2>
          <table class="stats" v-if="statRows.length">
            <thead>
              <tr>
                <th></th>
                <th>基础 (Lv.100)</th>
                <th v-if="doll.mod">MOD3</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="r in statRows" :key="r.key">
                <td class="k">{{ r.label }}</td>
                <td>{{ r.base ?? '—' }}</td>
                <td v-if="doll.mod">
                  <template v-if="r.mod !== undefined && r.mod !== r.base">
                    <span class="up" v-if="r.mod > r.base">▲</span><span class="down" v-else>▼</span>
                    {{ r.mod }}
                  </template>
                  <template v-else>{{ r.mod ?? r.base ?? '—' }}</template>
                </td>
              </tr>
            </tbody>
          </table>
          <div class="aura" v-if="doll.effects.length">
            <b>光环：</b>
            <n-tag v-for="(e, i) in doll.effects" :key="i" size="small" :bordered="false" class="aura-tag">
              {{ e.type }} +{{ e.value }}%
            </n-tag>
          </div>
        </div>

        <!-- skills -->
        <div class="panel">
          <h2>技能</h2>
          <div v-for="(sk, i) in allSkills" :key="sk.id" class="skill">
            <div class="skill-head">
              <span class="skill-idx">{{ i + 1 }}</span>
              <b>{{ sk.name }}</b>
              <n-tag size="tiny" :bordered="false">{{ sk.from }}</n-tag>
            </div>
            <div class="skill-body">
              <div class="skill-desc">
                <div class="lv-label">Lv.1</div>
                <p>{{ sk.desc_lv1 || '—' }}</p>
                <div class="lv-label">Lv.10</div>
                <p>{{ sk.desc_lv10 || '—' }}</p>
              </div>
              <div class="skill-detail" v-if="sk.detail_lv10">{{ sk.detail_lv10.replace(/\n/g, '　') }}</div>
            </div>
          </div>
          <n-empty v-if="!allSkills.length" description="暂无技能数据" />
        </div>

        <!-- skins -->
        <div class="panel" v-if="doll.skins.length">
          <h2>皮肤（{{ doll.skins.length }}）</h2>
          <div class="skin-grid">
            <div
              v-for="s in doll.skins" :key="s.id"
              class="skin-card" :class="{ active: form === 'skin-' + s.id, noart: !s.has_art }"
              @click="s.has_art && selectSkin(s.id)"
            >
              <img v-if="s.thumbnail || s.normal" :src="s.thumbnail || s.normal" loading="lazy" :alt="s.name" />
              <div v-else class="noimg">无图</div>
              <div class="skin-name">
                {{ s.name || `皮肤 ${s.id}` }}
                <span v-if="s.damaged_only" class="d-only">仅破损立绘</span>
              </div>
            </div>
          </div>
        </div>

        <!-- firearm description -->
        <div class="panel" v-if="doll.desc_en">
          <h2>原型枪械资料 <span class="en-note">(EN)</span></h2>
          <pre class="desc">{{ doll.desc_en }}</pre>
        </div>
      </div>
    </div>
  </div>
  <div class="page" v-else-if="error">
    <n-result status="404" title="未找到该人形" description="可能链接有误">
      <template #footer>
        <n-button @click="$router.push('/dolls')">返回图鉴</n-button>
      </template>
    </n-result>
  </div>
  <div class="page" v-else>
    <n-spin size="large" style="margin-top: 15vh; width: 100%" />
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { loadDoll, TYPE_COLOR, STAT_LABEL, produceTimeFmt, type Doll, type Skill } from '../data'

const route = useRoute()
const doll = ref<Doll | null>(null)
const error = ref(false)
const form = ref<'base' | 'mod' | string>('base')
const damaged = ref(false)
const fullscreen = ref(false)

function onKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape') fullscreen.value = false
}
onMounted(() => window.addEventListener('keydown', onKeydown))
onBeforeUnmount(() => window.removeEventListener('keydown', onKeydown))

const formOptions = computed(() => {
  if (!doll.value) return []
  const d = doll.value
  return [
    { key: 'base', label: '基础', available: !!(d.base.normal || d.base.damaged) },
    { key: 'mod', label: '改造', available: !!(d.mod_base?.normal || d.mod_base?.damaged) },
    ...(d.skins.filter((s) => s.has_art).map((s) => ({ key: 'skin-' + s.id, label: s.name || `皮肤${s.id}`, available: true })))
  ]
})

function selectSkin(id: number) {
  form.value = 'skin-' + id
  damaged.value = false
}

const currentArtSet = computed(() => {
  const d = doll.value
  if (!d) return { normal: '', damaged: '' }
  if (form.value === 'base') return d.base
  if (form.value === 'mod') return d.mod_base
  const sid = Number(String(form.value).slice(5))
  const s = d.skins.find((x) => x.id === sid)
  return s ?? { normal: '', damaged: '' }
})

const currentArt = computed(() =>
  damaged.value ? currentArtSet.value.damaged : (currentArtSet.value.normal || currentArtSet.value.damaged)
)

const currentCaption = computed(() => {
  const d = doll.value
  if (!d) return ''
  if (form.value === 'base') return damaged.value ? `${d.name} · 基础（破损）` : `${d.name} · 基础`
  if (form.value === 'mod') return damaged.value ? `${d.name} · 改造（破损）` : `${d.name} · 改造`
  const s = d.skins.find((x) => 'skin-' + x.id === form.value)
  return s ? `${d.name} · ${s.name || '皮肤'}${damaged.value ? '（破损）' : ''}` : ''
})

const statRows = computed(() => {
  const d = doll.value
  if (!d) return []
  const keys = new Set([...Object.keys(d.stats), ...(d.mod?.stats_merged ? Object.keys(d.mod.stats_merged) : [])])
  return [...keys]
    .filter((k) => STAT_LABEL[k])
    .map((k) => ({
      key: k,
      label: STAT_LABEL[k],
      base: (d.stats as any)[k],
      mod: d.mod ? (d.mod.stats_merged as any)[k] : undefined
    }))
})

const allSkills = computed(() => {
  const d = doll.value
  if (!d) return []
  const out: (Skill & { from: string })[] = d.skills.map((s) => ({ ...s, from: '基础' }))
  if (d.mod) {
    for (const s of d.mod.skills) {
      if (!out.some((x) => x.id === s.id)) out.push({ ...s, from: 'MOD' })
    }
  }
  return out
})

function downloadArt() {
  if (!currentArt.value) return
  const a = document.createElement('a')
  a.href = currentArt.value
  a.download = currentArt.value.split('/').pop() || 'portrait.webp'
  a.click()
}

watch(form, () => { fullscreen.value = false })
watch(damaged, (v) => {
  // if switching to damaged with no damaged art, snap back
  if (v && !currentArtSet.value.damaged) damaged.value = false
})

onMounted(async () => {
  const wid = Number(route.params.wid)
  const d = await loadDoll(wid)
  if (!d) { error.value = true; return }
  doll.value = d
  if (!d.base.normal && !d.base.damaged) {
    if (d.mod_base?.normal) form.value = 'mod'
    else {
      const first = d.skins.find((s) => s.has_art)
      if (first) form.value = 'skin-' + first.id
    }
  }
  document.title = `${d.name} - 少女前线资料库`
})
</script>

<style scoped>
.crumbs { color: var(--gfl-text-dim); margin-bottom: 14px; font-size: 14px; }
.crumbs .sep { margin: 0 8px; }
.layout {
  display: grid;
  grid-template-columns: minmax(300px, 430px) 1fr;
  gap: 16px;
  align-items: start;
}
.art { position: sticky; top: 76px; padding: 12px; }
.art-stage {
  position: relative;
  aspect-ratio: 1 / 1.12;
  border-radius: 8px;
  overflow: hidden;
  background:
    radial-gradient(80% 60% at 50% 0%, rgba(212,176,106,0.10), transparent),
    linear-gradient(180deg, #191c21, #101216);
  display: flex;
  align-items: flex-end;
  justify-content: center;
  cursor: zoom-in;
}
.art-stage img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  object-position: bottom center;
}
.noart { align-self: center; color: var(--gfl-text-dim); }

.art-fullscreen {
  position: fixed;
  inset: 0;
  z-index: 2000;
  background: rgba(6, 7, 9, 0.96);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: zoom-out;
}
.art-fullscreen img {
  max-width: 100vw;
  max-height: 100vh;
  object-fit: contain;
}
.fs-hint {
  position: absolute;
  bottom: 16px;
  left: 50%;
  transform: translateX(-50%);
  color: var(--gfl-text-dim);
  font-size: 13px;
  letter-spacing: 1px;
}
.art-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
  margin-top: 10px;
  flex-wrap: wrap;
}
.ctrl-group { display: flex; gap: 6px; flex-wrap: wrap; }
.chip {
  background: transparent;
  color: var(--gfl-text-dim);
  border: 1px solid #3a3f47;
  border-radius: 6px;
  padding: 3px 10px;
  font-size: 12.5px;
  cursor: pointer;
}
.chip:hover:not(:disabled) { border-color: var(--gfl-gold); color: var(--gfl-gold-bright); }
.chip.active { border-color: var(--gfl-gold-bright); color: var(--gfl-gold-bright); background: rgba(212,176,106,0.10); }
.chip:disabled { opacity: 0.35; cursor: not-allowed; }
.hint { color: var(--gfl-text-dim); font-size: 11px; width: 100%; text-align: right; margin-top: 2px; }
.art-caption { text-align: center; color: var(--gfl-text-dim); font-size: 13px; margin-top: 6px; }

.info { display: flex; flex-direction: column; gap: 16px; min-width: 0; }
.head h1 { margin: 0; font-size: 26px; }
.title-row { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.title-row .stars { font-size: 16px; }
.code-line { color: var(--gfl-text-dim); margin: 4px 0 14px; letter-spacing: 1px; }
.obtain { margin-top: 12px; font-size: 13.5px; line-height: 1.8; }

h2 { font-size: 17px; margin: 0 0 12px; color: var(--gfl-gold); }
.en-note { font-size: 12px; color: var(--gfl-text-dim); font-weight: 400; }

.stats { width: 100%; border-collapse: collapse; font-size: 14px; }
.stats th, .stats td { padding: 7px 10px; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.05); }
.stats th { color: var(--gfl-text-dim); font-weight: 600; font-size: 12.5px; }
.stats .k { color: var(--gfl-text-dim); }
.up { color: #7ee29a; font-size: 11px; }
.down { color: #f28a8a; font-size: 11px; }
.aura { margin-top: 12px; font-size: 13.5px; }
.aura-tag { margin-right: 6px; background: rgba(212,176,106,0.12); color: var(--gfl-gold-bright); }

.skill { border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; padding: 12px 14px; margin-bottom: 10px; }
.skill-head { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
.skill-idx {
  width: 22px; height: 22px; border-radius: 50%;
  background: rgba(212,176,106,0.15); color: var(--gfl-gold-bright);
  display: inline-flex; align-items: center; justify-content: center;
  font-size: 12px; font-weight: 700;
}
.skill-body { display: flex; gap: 18px; flex-wrap: wrap; }
.skill-desc { flex: 1; min-width: 260px; }
.skill-desc p { margin: 2px 0 8px; line-height: 1.7; font-size: 13.5px; }
.lv-label { color: var(--gfl-gold); font-size: 11.5px; font-weight: 700; }
.skill-detail { color: var(--gfl-text-dim); font-size: 12.5px; min-width: 180px; align-self: flex-end; white-space: pre-wrap; }

.skin-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)); gap: 10px; }
.skin-card {
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: border-color 0.15s;
}
.skin-card:hover { border-color: rgba(212,176,106,0.5); }
.skin-card.active { border-color: var(--gfl-gold-bright); box-shadow: 0 0 0 1px var(--gfl-gold-bright); }
.skin-card.noart { opacity: 0.55; cursor: default; }
.skin-card img { width: 100%; aspect-ratio: 1/1.05; object-fit: cover; object-position: top center; display: block; }
.noimg { color: var(--gfl-text-dim); font-size: 12px; padding: 30px 0; text-align: center; }
.skin-name { padding: 6px 8px; font-size: 12.5px; }
.d-only { color: var(--gfl-text-dim); font-size: 10.5px; display: block; }

.desc {
  white-space: pre-wrap;
  font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
  font-size: 13px;
  line-height: 1.8;
  color: var(--gfl-text-dim);
  margin: 0;
  max-height: 320px;
  overflow-y: auto;
}

@media (max-width: 900px) {
  .layout { grid-template-columns: 1fr; }
  .art { position: static; }
}
</style>
