<template>
  <div class="login-container">
    <el-card class="login-card">
      <h2>许可证管理系统</h2>
      <el-form :model="loginForm" @submit.prevent="handleLogin">
        <el-form-item>
          <el-input v-model="loginForm.username" placeholder="用户名" />
        </el-form-item>
        <el-form-item>
          <el-input v-model="loginForm.password" type="password" placeholder="密码" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleLogin" style="width: 100%">登录</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script>
import api from '../api'

export default {
  data() {
    return {
      loginForm: {
        username: '',
        password: ''
      }
    }
  },
  methods: {
    async handleLogin() {
      try {
        const response = await api.login(this.loginForm.username, this.loginForm.password)
        localStorage.setItem('token', response.data.token)
        this.$router.push('/dashboard')
        this.$message.success('登录成功')
      } catch (error) {
        this.$message.error('登录失败：' + (error.response?.data?.error || '未知错误'))
      }
    }
  }
}
</script>

<style scoped>
.login-container {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f5f5f5;
}
.login-card {
  width: 400px;
}
</style> 