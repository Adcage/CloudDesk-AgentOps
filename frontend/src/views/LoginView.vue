<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <h2 class="title">CloudDesk</h2>
        <p class="subtitle">智能客服管理系统</p>
      </div>
      <a-form
        :model="formState"
        name="login"
        class="login-form"
        @finish="onFinish"
      >
        <a-form-item
          name="userAccount"
          :rules="[{ required: true, message: '请输入账号' }]"
        >
          <a-input v-model:value="formState.userAccount" placeholder="账号">
            <template #prefix>
              <UserOutlined />
            </template>
          </a-input>
        </a-form-item>

        <a-form-item
          name="userPassword"
          :rules="[{ required: true, message: '请输入密码' }]"
        >
          <a-input-password v-model:value="formState.userPassword" placeholder="密码">
            <template #prefix>
              <LockOutlined />
            </template>
          </a-input-password>
        </a-form-item>

        <a-form-item>
          <a-button
            type="primary"
            html-type="submit"
            class="login-button"
            :loading="loading"
          >
            登录
          </a-button>
        </a-form-item>
      </a-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { UserOutlined, LockOutlined } from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const loading = ref(false)

const formState = reactive({
  userAccount: '',
  userPassword: '',
})

const onFinish = async () => {
  loading.value = true
  try {
    await userStore.login(formState.userAccount, formState.userPassword)
    message.success('登录成功')
    const redirect = (route.query.redirect as string) || '/chat'
    router.push(redirect)
  } catch (error: any) {
    const msg = error?.response?.data?.message || error?.message || '登录失败'
    message.error(msg)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: #f0f2f5;
}

.login-card {
  width: 400px;
  padding: 40px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border: 1px solid #f0f0f0;
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.title {
  font-size: 24px;
  font-weight: 600;
  color: #1f5fae;
  margin-bottom: 8px;
}

.subtitle {
  color: rgba(0, 0, 0, 0.45);
  font-size: 14px;
}

.login-form :deep(.ant-input-affix-wrapper) {
  padding: 8px 11px;
}

.login-button {
  width: 100%;
  height: 40px;
  font-size: 16px;
}
</style>
