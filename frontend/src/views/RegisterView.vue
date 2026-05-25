<template>
  <div class="register-container">
    <div class="register-card">
      <div class="register-header">
        <h2 class="title">加入我们</h2>
        <p class="subtitle">创建您的账户，开启精彩旅程</p>
      </div>
      <a-form
        :model="formState"
        name="register"
        class="register-form"
        @finish="onFinish"
      >
        <a-form-item
          name="userAccount"
          :rules="[
            { required: true, message: '请输入账号' },
            { min: 4, message: '账号不能少于4个字符' }
          ]"
        >
          <a-input v-model:value="formState.userAccount" placeholder="设置账号">
            <template #prefix>
              <UserOutlined />
            </template>
          </a-input>
        </a-form-item>

        <a-form-item
          name="userPassword"
          :rules="[
            { required: true, message: '请输入密码' },
            { min: 8, message: '密码不能少于8个字符' }
          ]"
        >
          <a-input-password v-model:value="formState.userPassword" placeholder="设置密码">
            <template #prefix>
              <LockOutlined />
            </template>
          </a-input-password>
        </a-form-item>

        <a-form-item
          name="checkPassword"
          :rules="[
            { required: true, message: '请确认密码' },
            ({ getFieldValue }) => ({
              validator(_, value) {
                if (!value || getFieldValue('userPassword') === value) {
                  return Promise.resolve();
                }
                return Promise.reject(new Error('两次输入的密码不一致'));
              },
            }),
          ]"
        >
          <a-input-password v-model:value="formState.checkPassword" placeholder="确认密码">
            <template #prefix>
              <CheckCircleOutlined />
            </template>
          </a-input-password>
        </a-form-item>

        <a-form-item>
          <a-button
            type="primary"
            html-type="submit"
            class="register-button"
            :loading="loading"
          >
            注册
          </a-button>
        </a-form-item>

        <div class="login-link">
          已经有账号？<a @click="goToLogin">登录</a>
        </div>
      </a-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { UserOutlined, LockOutlined, CheckCircleOutlined } from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'
import myAxios from '@/request'

const router = useRouter()
const loading = ref(false)

const formState = reactive({
  userAccount: '',
  userPassword: '',
  checkPassword: '',
})

const onFinish = async () => {
  loading.value = true
  try {
    await myAxios.post('/user/register', {
      username: formState.userAccount,
      userPassword: formState.userPassword,
      checkPassword: formState.checkPassword,
    })
    message.success('注册成功，请登录')
    router.push('/user/login')
  } catch (error: any) {
    const msg = error?.response?.data?.message || error?.message || '注册失败'
    message.error(msg)
  } finally {
    loading.value = false
  }
}

const goToLogin = () => {
  router.push('/user/login')
}
</script>

<style scoped>
.register-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: calc(100vh - 64px);
  background: var(--color-bg-page);
}

.register-card {
  width: 400px;
  padding: 40px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border: 1px solid var(--color-border);
}

.register-header {
  text-align: center;
  margin-bottom: 32px;
}

.title {
  font-size: 24px;
  font-weight: 600;
  color: var(--color-text-main);
  margin-bottom: 8px;
}

.subtitle {
  color: var(--color-text-secondary);
  font-size: 14px;
}

.register-form :deep(.ant-input-affix-wrapper) {
  padding: 8px 11px;
}

.register-button {
  width: 100%;
  height: 40px;
  font-size: 16px;
  background-color: var(--color-primary);
  border-color: var(--color-primary);
}

.register-button:hover {
  background-color: var(--color-primary-hover);
}

.login-link {
  text-align: center;
  margin-top: 16px;
  color: var(--color-text-secondary);
}

.login-link a {
  color: var(--color-primary);
  cursor: pointer;
}
</style>
