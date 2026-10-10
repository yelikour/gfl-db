import { createRouter, createWebHashHistory } from 'vue-router'

const Home = () => import('../pages/Home.vue')
const DollList = () => import('../pages/DollList.vue')
const DollDetail = () => import('../pages/DollDetail.vue')
const About = () => import('../pages/About.vue')

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: '/', name: 'home', component: Home },
    { path: '/dolls', name: 'dolls', component: DollList },
    { path: '/dolls/:wid', name: 'doll', component: DollDetail },
    { path: '/about', name: 'about', component: About },
    { path: '/:pathMatch(.*)*', redirect: '/' }
  ],
  scrollBehavior(to, from, saved) {
    if (saved) return saved
    return { top: 0 }
  }
})

const TITLES: Record<string, string> = {
  home: '少女前线资料库 GFL DB',
  dolls: '人形图鉴 · 少女前线资料库',
  about: '关于 · 少女前线资料库'
}
router.afterEach((to) => {
  if (to.name === 'doll') return // 详情页在数据加载后自行设置
  document.title = TITLES[String(to.name)] || TITLES.home
})

export default router
