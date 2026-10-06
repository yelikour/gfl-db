<template>
  <n-config-provider :theme="darkTheme" :theme-overrides="themeOverrides">
    <div class="site-header">
      <div class="site-header-inner">
        <RouterLink to="/" class="brand">
          <span class="brand-gfl">GFL</span>
          <span class="brand-name">少女前线资料库</span>
        </RouterLink>
        <nav class="nav">
          <RouterLink to="/">首页</RouterLink>
          <RouterLink to="/dolls">人形图鉴</RouterLink>
          <RouterLink to="/about">关于</RouterLink>
        </nav>
      </div>
    </div>
    <RouterView />
    <footer class="site-footer">
      <div>
        少女前线 Girls' Frontline © 散爆网络 / MICA Team — 本站为玩家自制非官方资料站，资产版权归原权利人所有。
        <RouterLink to="/about">关于与致谢</RouterLink>
      </div>
    </footer>
  </n-config-provider>
</template>

<script setup lang="ts">
import { darkTheme, type GlobalThemeOverrides } from 'naive-ui'
import { RouterLink, RouterView } from 'vue-router'

const themeOverrides: GlobalThemeOverrides = {
  common: {
    primaryColor: '#d4b06a',
    primaryColorHover: '#f0cc7a',
    primaryColorPressed: '#b8964f',
    bodyColor: '#14161a',
    cardColor: '#1d2026',
    modalColor: '#1d2026',
    popoverColor: '#24282f',
    inputColor: '#24282f',
    borderColor: 'rgba(212,176,106,0.25)'
  }
}
</script>

<style scoped>
.site-header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(20, 22, 26, 0.92);
  backdrop-filter: blur(8px);
  border-bottom: 1px solid rgba(212, 176, 106, 0.22);
}
.site-header-inner {
  max-width: 1280px;
  margin: 0 auto;
  padding: 12px 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
}
.brand {
  display: flex;
  align-items: baseline;
  gap: 10px;
  text-decoration: none !important;
}
.brand-gfl {
  font-weight: 900;
  font-size: 22px;
  color: var(--gfl-gold-bright);
  letter-spacing: 2px;
}
.brand-name { font-size: 16px; color: var(--gfl-text); }
.nav { display: flex; gap: 22px; }
.nav a {
  color: var(--gfl-text-dim);
  font-size: 15px;
  text-decoration: none !important;
  padding: 4px 2px;
  border-bottom: 2px solid transparent;
}
.nav a.router-link-active {
  color: var(--gfl-gold-bright);
  border-bottom-color: var(--gfl-gold-bright);
}
.site-footer {
  border-top: 1px solid rgba(212, 176, 106, 0.15);
  color: var(--gfl-text-dim);
  font-size: 12px;
  text-align: center;
  padding: 18px 16px 26px;
  line-height: 1.8;
}
@media (max-width: 640px) {
  .brand-name { display: none; }
}
</style>
