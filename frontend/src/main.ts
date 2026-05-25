import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router, { initRouterGuards } from './router'

import Antd from 'ant-design-vue'
import 'ant-design-vue/dist/reset.css'
import './styles/theme.css'

import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { faHouse, faGear, faUser } from '@fortawesome/free-solid-svg-icons'

library.add(faHouse, faGear, faUser)

const app = createApp(App)

const pinia = createPinia()

app.use(pinia)
initRouterGuards()
app.use(router)
app.use(Antd)
app.component('font-awesome-icon', FontAwesomeIcon)

app.mount('#app')
