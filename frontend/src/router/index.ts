import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/HomeView.vue'),
      meta: { title: 'MyChordHub - 吉他譜編輯平台' },
    },
    {
      path: '/browse',
      name: 'browse',
      component: () => import('@/pages/Browse/BrowsePage.vue'),
      meta: { title: '瀏覽歌曲' },
    },
    {
      path: '/song/:id',
      name: 'song',
      component: () => import('@/pages/Browse/SongDetailPage.vue'),
      props: true,
      meta: { title: '歌曲詳情' },
    },
    {
      path: '/edit/:id?',
      name: 'edit',
      component: () => import('@/pages/Edit/EditPage.vue'),
      props: true,
      meta: {
        title: '編輯歌曲',
        requiresAuth: true,
      },
    },
    {
      path: '/auth',
      name: 'auth',
      redirect: '/auth/login',
      children: [
        {
          path: 'login',
          name: 'login',
          component: () => import('@/pages/Auth/LoginPage.vue'),
          meta: {
            title: '登入',
            guestOnly: true,
          },
        },
        {
          path: 'register',
          name: 'register',
          component: () => import('@/pages/Auth/RegisterPage.vue'),
          meta: {
            title: '註冊',
            guestOnly: true,
          },
        },
        {
          path: 'forgot-password',
          name: 'forgot-password',
          component: () => import('@/pages/Auth/ForgotPasswordPage.vue'),
          meta: {
            title: '忘記密碼',
            guestOnly: true,
          },
        },
        {
          path: 'reset-password',
          name: 'reset-password',
          component: () => import('@/pages/Auth/ResetPasswordPage.vue'),
          meta: {
            title: '重設密碼',
            guestOnly: true,
          },
        },
        {
          path: 'verify-email',
          name: 'verify-email',
          component: () => import('@/pages/Auth/VerifyEmailPage.vue'),
          meta: { title: '驗證郵箱' },
        },
      ],
    },
    {
      path: '/profile',
      name: 'profile',
      redirect: '/profile/overview',
      meta: { requiresAuth: true },
      children: [
        {
          path: 'overview',
          name: 'profile-overview',
          component: () => import('@/pages/Profile/ProfileOverviewPage.vue'),
          meta: {
            title: '個人資料',
            requiresAuth: true,
          },
        },
        {
          path: 'songs',
          name: 'profile-songs',
          component: () => import('@/pages/Profile/MySongsPage.vue'),
          meta: {
            title: '我的歌曲',
            requiresAuth: true,
          },
        },
        {
          path: 'collections',
          name: 'profile-collections',
          component: () => import('@/pages/Profile/MyCollectionsPage.vue'),
          meta: {
            title: '我的收藏',
            requiresAuth: true,
          },
        },
        {
          path: 'settings',
          name: 'profile-settings',
          component: () => import('@/pages/Profile/SettingsPage.vue'),
          meta: {
            title: '設定',
            requiresAuth: true,
          },
        },
      ],
    },
    {
      path: '/about',
      name: 'about',
      component: () => import('@/views/AboutView.vue'),
      meta: { title: '關於我們' },
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: () => import('@/pages/NotFoundPage.vue'),
      meta: { title: '頁面不存在' },
    },
  ],
})

// 全局路由守衛
router.beforeEach(async (to, _from, next) => {
  const authStore = useAuthStore()

  // 設定頁面標題
  if (to.meta.title) {
    document.title = to.meta.title as string
  }

  // 檢查是否需要認證
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({
      name: 'login',
      query: { redirect: to.fullPath },
    })
    return
  }

  // 檢查是否僅允許訪客訪問
  if (to.meta.guestOnly && authStore.isAuthenticated) {
    next({ name: 'home' })
    return
  }

  next()
})

export default router
