<template>
  <div class="page about">
    <div class="panel">
      <h2>关于本站</h2>
      <p>
        本站是一个<strong>玩家自制、非官方</strong>的《少女前线》资料数据库，提供人形图鉴、立绘浏览、
        数值与技能查询等功能。灵感与页面形态参考了
        <a href="https://github.com/Nikke-db/nikke-db-vue" target="_blank" rel="noopener">nikke-db</a> 项目。
      </p>
      <h2>数据来源</h2>
      <ul>
        <li>数值 / 技能 / 皮肤数据：游戏客户端本地配置表与 <a href="https://gfwiki.org" target="_blank" rel="noopener">少女前线中文维基（gfwiki）</a> 公开的图鉴数据模块（MediaWiki Lua 模块）。</li>
        <li>立绘：从 Steam 版《少女前线》客户端标准 UnityFS 资源包中离线提取（只读解析，不涉及任何运行时修改）。</li>
        <li>技能与光环文本：游戏本地文本表。</li>
      </ul>
      <h2>版权声明</h2>
      <p>
        Girls' Frontline（少女前线）及其全部角色立绘、名称、设定之版权归
        <strong>散爆网络 / MICA Team / 云母组</strong> 所有。本站仅出于玩家交流与资料查询目的进行展示，
        不用于任何商业用途。如果版权方认为本站内容不适宜展示，请与我联系，我会第一时间处理下架。
      </p>
      <h2>技术说明</h2>
      <ul>
        <li>前端：Vue 3 + Vite + naive-ui，纯静态站点，无后端、无统计脚本。</li>
        <li>数据管线：Python（UnityPy）从只读游戏目录提取资源 → 生成 JSON 数据与 WebP 图像。</li>
        <li>数值均为图鉴基础值（Lv.100）与 MOD3 满级值，具体以游戏内实际为准。</li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.about { max-width: 860px; }
.about h2 { color: var(--gfl-gold); font-size: 18px; margin: 22px 0 10px; }
.about h2:first-child { margin-top: 0; }
.about p, .about li { line-height: 2; color: var(--gfl-text); font-size: 14.5px; }
.about ul { padding-left: 22px; margin: 6px 0; }
</style>
