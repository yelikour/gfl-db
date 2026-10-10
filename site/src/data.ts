export interface Skill {
  id: number
  name: string
  desc_lv1: string
  desc_lv10: string
  detail_lv10: string
}

export interface Skin {
  id: number
  name: string
  has_art: boolean
  damaged_only: boolean
  thumbnail?: string
  normal?: string
  damaged?: string
}

export interface Stats {
  life?: number
  power?: number
  rate?: number
  hit?: number
  dodge?: number
  growth?: number
  rec?: number
  armor?: number
  crit?: number
  max_rate?: number
  round?: number
}

export interface Doll {
  id: number
  wid: number
  name: string
  en_name: string
  code: string
  type: string
  type_cn: string
  rarity: number
  illu: string
  cv: string
  produce_time: number
  launch_date: string
  bg: string
  bg_cn: string
  obtain: string[]
  stats: Stats
  grid_pos: number[]
  grid_center: number | null
  effects: { type: string; value: number }[]
  skills: Skill[]
  mod: { stats: Stats; stats_merged: Stats; skills: Skill[]; has_art: boolean } | null
  base: { thumbnail?: string; normal?: string; damaged?: string }
  mod_base: { thumbnail?: string; normal?: string; damaged?: string }
  skins: Skin[]
  desc_en: string
}

export interface DollIndex {
  id: number
  wid: number
  name: string
  code: string
  en_name: string
  type: string
  rarity: number
  launch_date: string
  bg: string
  bg_cn: string
  thumb: string
  mod_thumb: string
  skin_count: number
  has_mod: boolean
}

let indexCache: DollIndex[] | null = null
let dollsCache: Map<number, Doll> | null = null

export async function loadIndex(): Promise<DollIndex[]> {
  if (indexCache) return indexCache
  const r = await fetch('data/index.json')
  indexCache = (await r.json()) as DollIndex[]
  return indexCache
}

export async function loadDoll(wid: number): Promise<Doll | null> {
  if (!dollsCache) {
    const r = await fetch('data/dolls.json')
    const list = (await r.json()) as Doll[]
    dollsCache = new Map(list.map((d) => [d.wid, d]))
  }
  return dollsCache.get(wid) ?? null
}

/** 全量人形（按 wid 排序），用于上一人/下一人导航。 */
export async function loadAll(): Promise<Doll[]> {
  await loadDoll(0)
  return [...(dollsCache ?? new Map())].map(([, d]) => d).sort((a, b) => a.wid - b.wid)
}

export const TYPE_COLOR: Record<string, string> = {
  HG: 'var(--type-hg)',
  SMG: 'var(--type-smg)',
  AR: 'var(--type-ar)',
  RF: 'var(--type-rf)',
  MG: 'var(--type-mg)',
  SG: 'var(--type-sg)'
}

export const TYPE_LABEL: Record<string, string> = {
  HG: '手枪', SMG: '冲锋枪', AR: '步枪', RF: '步枪', MG: '机枪', SG: '霰弹枪'
}

export const STAT_LABEL: Record<string, string> = {
  life: '生命', power: '伤害', rate: '射速', hit: '命中', dodge: '回避',
  growth: '成长', rec: '修复', armor: '护甲', crit: '暴击', max_rate: '满级射速', round: '弹链/弹容'
}

export function produceTimeFmt(sec: number): string {
  if (!sec) return '—'
  const h = Math.floor(sec / 3600)
  const m = Math.floor((sec % 3600) / 60)
  const s = sec % 60
  return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
}
