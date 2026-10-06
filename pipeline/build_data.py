# -*- coding: utf-8 -*-
"""Build site data (dolls.json / index.json / meta.json) from workspace sources.

Sources joined:
  cache/gfwiki/Gun_info_data_0..4.lua   base doll stats (451)
  cache/gfwiki/Gun_info_data_extra.lua  collab dolls (id>=1001)
  cache/gfwiki/Gun_info_data_mod.lua    MOD3 max stats (key 20000+id)
  cache/gfwiki/Gun_info_obtain_data.lua obtain text (id -> str)
  cache/texttable_all/gun.txt           per gun: 1=CN name 4=illu//cCV 5=EN firearm desc
  cache/texttable_all/battle_skill_config.txt  skill name/desc/detail per level
  manifests/portraits_by_name.csv       portrait files per (wiki_id, skin_dir, kind)
  manifests/skins.csv                   skin_id -> name

Output: site/data/*.json  (image paths point to /images/*.webp produced by build_images.py)
"""
import csv
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lua_table import parse

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
GF = os.path.join(ROOT, 'cache', 'gfwiki')
TT = os.path.join(ROOT, 'cache', 'texttable_all')
MAN = os.path.join(ROOT, 'manifests')
OUT = os.path.join(ROOT, 'site', 'data')

GUN_TYPES = {1: 'HG', 2: 'SMG', 3: 'AR', 4: 'RF', 5: 'MG', 6: 'SG'}


def seq(x):
    """Lua array-like (LuaTable with int keys) or python list -> list of values."""
    if x is None:
        return []
    if isinstance(x, dict):
        return [v for k, v in sorted(x.items(), key=lambda kv: int(kv[0]))]
    if isinstance(x, (list, tuple)):
        return list(x)
    return [x]
GUN_TYPES_CN = {'HG': '手枪', 'SMG': '冲锋枪', 'AR': '步枪', 'RF': '反坦克步枪' if False else '步枪(RF)', 'MG': '机枪', 'SG': '霰弹枪'}
BG_CN = {
    'nation_US': '美国', 'nation_USSR': '苏联', 'nation_GER': '德国', 'nation_DE': '德国',
    'nation_CN': '中国', 'nation_UK': '英国', 'nation_FR': '法国', 'nation_JP': '日本',
    'nation_IT': '意大利', 'nation_IL': '以色列', 'nation_KR': '韩国', 'nation_BE': '比利时',
    'nation_CZ': '捷克', 'nation_CH': '瑞士', 'nation_AT': '奥地利', 'nation_AU': '澳大利亚',
    'nation_FI': '芬兰', 'nation_DK': '丹麦', 'nation_SE': '瑞典', 'nation_ES': '西班牙',
    'nation_CA': '加拿大', 'nation_ZA': '南非', 'nation_PL': '波兰', 'nation_HU': '匈牙利',
    'nation_RO': '罗马尼亚', 'nation_YU': '南斯拉夫', 'nation_BR': '巴西', 'nation_MX': '墨西哥',
    'nation_TR': '土耳其', 'nation_AR': '阿根廷', 'nation_NO': '挪威', 'nation_PT': '葡萄牙',
    'nation_IN': '印度', 'nation_TH': '泰国', 'nation_PH': '菲律宾', 'nation_SG': '新加坡',
    'collab': '联动', 'etc': '其他', 'none': '其他',
    # wiki uses full English country names for some entries
    'nation_Belgium': '比利时', 'nation_China': '中国', 'nation_German': '德国',
    'nation_Italy': '意大利', 'nation_Russia': '俄罗斯', 'nation_America': '美国',
    'nation_Japan': '日本', 'nation_France': '法国', 'nation_Britain': '英国',
    'team_404': '404小队', 'team_ar': 'AR小队', 'team_defy': 'Defy小队',
}
EFFECT_TYPES = {1: '伤害', 2: '射速', 3: '命中', 4: '回避', 5: '暴击', 6: '移速', 7: '护甲', 8: '穿透'}


def load_lua(name):
    with open(os.path.join(GF, name), encoding='utf-8') as f:
        return parse(f.read())


def load_texttable(name):
    """texttable format: key,value per line; //c = line break inside value."""
    out = {}
    with open(os.path.join(TT, name), encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\n')
            if not line:
                continue
            k, _, v = line.partition(',')
            out[k] = v.replace('//c', '\n').replace('//n', '\n')
    return out


def main():
    os.makedirs(OUT, exist_ok=True)

    # --- gfwiki base + extra dolls ---
    dolls = {}
    for i in list(range(5)):
        t = load_lua(f'Gun_info_data_{i}.lua')
        for k, v in t.items():
            if isinstance(v, dict):
                dolls[int(k)] = dict(v)
    extra = load_lua('Gun_info_data_extra.lua')
    for k, v in extra.items():
        if isinstance(v, dict):
            dolls[int(k)] = dict(v)
    mods = load_lua('Gun_info_data_mod.lua')
    obtain_tab = load_lua('Gun_info_obtain_data.lua')

    # --- gun.txt: prefix+id(07d) -> text ---
    gun_txt = load_texttable('gun.txt')
    gun_name, gun_illucv, gun_desc = {}, {}, {}
    for k, v in gun_txt.items():
        num = k.split('-', 1)[1]
        pre, sid = num[0], int(num[1:])
        if pre == '1':
            gun_name[sid] = v
        elif pre == '4':
            parts = v.split('\n')
            gun_illucv[sid] = {'illu': parts[0].strip(), 'cv': parts[1].strip() if len(parts) > 1 else ''}
        elif pre == '5':
            gun_desc[sid] = v

    # --- skills: key = prefix + skillid + level(2) ---
    sk_txt = load_texttable('battle_skill_config.txt')
    skills = {}
    for k, v in sk_txt.items():
        num = k.split('-', 1)[1]
        pre, sid, lv = num[0], num[1:-2], num[-2:]
        d = skills.setdefault(sid, {})
        if pre == '1':
            d['name'] = v
        elif pre == '2':
            d.setdefault('desc', {})[int(lv)] = v
        elif pre == '3':
            d.setdefault('detail', {})[int(lv)] = v

    def skill_payload(sid):
        if sid is None:
            return None
        s = skills.get(str(sid))
        if not s or not s.get('name'):
            return None
        desc = s.get('desc', {})
        det = s.get('detail', {})
        lv1, lvmax = desc.get(1, ''), desc.get(10, '')
        return {
            'id': sid, 'name': s['name'],
            'desc_lv1': lv1, 'desc_lv10': lvmax,
            'detail_lv10': det.get(10, ''),
        }

    # --- skins.csv ---
    skins_csv = {}
    with open(os.path.join(MAN, 'skins.csv'), encoding='utf-8') as f:
        for r in csv.DictReader(f):
            skins_csv[int(r['skin_id'])] = r

    # --- portraits manifest ---
    portraits = {}  # (wiki_id:int, skin_id:int|0, is_mod:bool) -> {normal, damaged, thumbnail, src...}
    with open(os.path.join(MAN, 'portraits_by_name.csv'), encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):
            kind = r['kind']
            if 'conflict' in kind:
                continue
            try:
                wid = int(r['wiki_id'])
            except (ValueError, TypeError):
                continue
            skin_dir = r['skin_dir'] or ''
            m = re.match(r'^(\d+)_', skin_dir)
            skin_id = int(m.group(1)) if m else 0
            is_mod = r['codename'].endswith('mod') or '_MOD_' in r['collected_as']
            key = (wid, skin_id, is_mod)
            slot = portraits.setdefault(key, {})
            # thumbnail_mod 是 MOD 版 UI 缩略图（正常+破损并排），单独存放，不作基础缩略图
            base_kind = kind if kind.startswith('thumbnail') else kind
            if base_kind in slot:
                continue
            slot[base_kind] = r['collected_as']

    def img_paths(wid, skin_id, is_mod):
        slot = portraits.get((wid, skin_id, is_mod))
        if not slot:
            return None
        suffix = '_mod' if is_mod else ''
        sk = f'_{skin_id}' if skin_id else ''
        out = {}
        # 缩略图统一从 normal 全图重渲染（与 build_images 一致），thumbnail_mod 源不使用
        if 'normal' in slot:
            out['thumbnail'] = f'images/{wid}{sk}{suffix}_thumbnail.webp'
            out['normal'] = f'images/{wid}{sk}{suffix}_normal.webp'
        if 'damaged' in slot:
            out['damaged'] = f'images/{wid}{sk}{suffix}_damaged.webp'
        return out

    # --- assemble ---
    result = []
    for wid in sorted(dolls):
        d = dolls[wid]
        gtype = GUN_TYPES.get(d.get('guntype'), '?')
        gid = d['id']
        mod_tab = mods.get(20000 + gid, {}) if (mods and d.get('mod')) else {}

        obtain_ids = seq(d.get('obtain'))
        obtain_texts = [obtain_tab.get(o, '') for o in obtain_ids if obtain_tab.get(o)]
        if not obtain_texts:
            obtain_texts = ['暂时无法获取']

        eff = seq(d.get('effect'))
        effects = []
        for j in range(0, len(eff) - 1, 2):
            effects.append({'type': EFFECT_TYPES.get(eff[j], str(eff[j])), 'value': eff[j + 1]})

        def stats_payload(tab):
            keys = ('life', 'pow' if False else 'power', 'rate', 'hit', 'dodge', 'growth', 'rec',
                    'armor', 'crit', 'max_rate', 'round')
            return {k: tab[k] for k in keys if k in tab and tab[k]}

        base_img = img_paths(wid, 0, False)
        mod_img = img_paths(wid, 0, True)

        skin_ids = []
        for s in seq(d.get('skins')) + seq(d.get('skins_d')):
            if s and s not in skin_ids:
                skin_ids.append(s)
        # 提取流水线里有立绘、但 wiki 皮肤清单没列出的皮肤（如联动皮肤 5000 段）一并收录
        extra_pids = sorted({s2 for (w2, s2, m2) in portraits if w2 == wid and s2 and not m2
                             and s2 not in skin_ids})
        skin_ids += extra_pids
        skins_out = []
        for sid in sorted(skin_ids):
            imgs = img_paths(wid, sid, False)
            name_cn = ''
            if sid in skins_csv:
                name_cn = skins_csv[sid]['skin_name_cn'] or ''
            if not name_cn and (sid, False, False) in portraits:
                # from skin_dir
                for (w2, s2, m2), slot in portraits.items():
                    if w2 == wid and s2 == sid and not m2:
                        pass
            skins_out.append({'id': sid, 'name': name_cn, 'has_art': bool(imgs),
                              'damaged_only': sid in seq(d.get('skins_d')) and sid not in seq(d.get('skins')),
                              **(imgs or {})})

        skills_out = [s for s in (skill_payload(d.get('skill1')), skill_payload(d.get('skill2'))) if s]

        entry = {
            'id': gid,
            'wid': wid,
            'name': d.get('name', ''),
            'en_name': d.get('en_name', ''),
            'code': d.get('code', ''),
            'type': gtype,
            'type_cn': GUN_TYPES_CN.get(gtype, gtype),
            'rarity': d.get('rank', 0),
            'illu': d.get('illu', '') or gun_illucv.get(gid, {}).get('illu', ''),
            'cv': d.get('cv', '') or gun_illucv.get(gid, {}).get('cv', ''),
            'produce_time': d.get('produce_time', 0),
            'launch_date': d.get('launch_date', ''),
            'bg': d.get('bg', ''),
            'bg_cn': BG_CN.get(d.get('bg', ''), d.get('bg', '')),
            'obtain': obtain_texts,
            'stats': stats_payload(d),
            'grid_pos': seq(d.get('grid_pos')),
            'grid_center': d.get('grid_center'),
            'effects': effects,
            'skills': skills_out,
            'mod': None,
            'base': base_img or {},
            'mod_base': mod_img or {},
            'skins': skins_out,
            'desc_en': (gun_desc.get(gid, '') or '')[:4000],
        }
        if d.get('mod') and mod_tab:
            mod_skills = [s for s in (skill_payload(mod_tab.get('skill1')), skill_payload(mod_tab.get('skill2'))) if s]
            # mod table lists only fields that change; merged = final MOD3 values
            merged = dict(entry['stats'])
            merged.update({k: v for k, v in stats_payload(mod_tab).items() if v})
            entry['mod'] = {
                'stats': stats_payload(mod_tab),
                'stats_merged': merged,
                'skills': mod_skills,
                'has_art': bool(mod_img),
            }
        result.append(entry)

    # wallpaper of sources: keep file slim — desc_en only where short
    with open(os.path.join(OUT, 'dolls.json'), 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, separators=(',', ':'))

    # image jobs for build_images.py: src paths -> output webp paths
    jobs = []
    for (wid, skin_id, is_mod), slot in portraits.items():
        suffix = '_mod' if is_mod else ''
        sk = f'_{skin_id}' if skin_id else ''
        job = {'src': {}, 'out': {}}
        for kind in ('thumbnail', 'normal', 'damaged'):
            if kind in slot:
                job['src'][kind] = slot[kind]
        # thumbnails re-rendered from the full normal art for a clean single image
        if 'normal' in job['src']:
            job['out']['thumb'] = f'images/{wid}{sk}{suffix}_thumbnail.webp'
            job['out']['normal'] = f'images/{wid}{sk}{suffix}_normal.webp'
        if 'damaged' in job['src']:
            job['out']['damaged'] = f'images/{wid}{sk}{suffix}_damaged.webp'
        if job['out']:
            jobs.append(job)
    with open(os.path.join(OUT, 'image_jobs.json'), 'w', encoding='utf-8') as f:
        json.dump(jobs, f, ensure_ascii=False, separators=(',', ':'))

    index = [{
        'id': e['id'], 'wid': e['wid'], 'name': e['name'], 'code': e['code'], 'en_name': e['en_name'],
        'type': e['type'], 'rarity': e['rarity'], 'launch_date': e['launch_date'],
        'bg': e['bg'], 'bg_cn': e['bg_cn'],
        'thumb': e['base'].get('thumbnail') or e['base'].get('normal')
                  or next((s.get('thumbnail') or s.get('normal') for s in e['skins'] if s.get('thumbnail') or s.get('normal')), ''),
        'normal': e['base'].get('normal') or next((s.get('normal') for s in e['skins'] if s.get('normal')), ''),
        'mod_thumb': e['mod_base'].get('thumbnail') or '',
        'mod_normal': e['mod_base'].get('normal') or '',
        'skin_count': len(e['skins']),
        'has_mod': bool(e['mod']),
    } for e in result]
    with open(os.path.join(OUT, 'index.json'), 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, separators=(',', ':'))

    meta = {
        'count': len(result),
        'types': sorted({e['type'] for e in result}),
        'rarities': sorted({e['rarity'] for e in result}),
        'bgs': sorted({(e['bg'], e['bg_cn']) for e in result}),
        'with_portrait': sum(1 for e in result if e['base'].get('normal')),
        'with_skins': sum(1 for e in result if e['skins']),
        'skill_coverage': sum(1 for e in result if e['skills']) / len(result),
        'image_files': sum(len(j['out']) for j in jobs),
        'data_date': max((e['launch_date'] for e in result if e['launch_date']), default=''),
    }
    with open(os.path.join(OUT, 'meta.json'), 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(json.dumps(meta, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
