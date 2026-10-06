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

export default router
