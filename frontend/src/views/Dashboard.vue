<template>
  <el-container>
    <el-header>
      <div class="header">
        <h2>许可证管理系统</h2>
        <div class="header-right">
          <el-button type="success" @click="exportLicenses">导出列表</el-button>
          <el-button type="danger" @click="handleLogout">退出登录</el-button>
        </div>
      </div>
    </el-header>
    <el-main>
      <!-- 搜索区域 -->
      <el-card style="margin-bottom: 20px">
        <el-form :inline="true" :model="searchForm">
          <el-form-item label="搜索">
            <el-input v-model="searchForm.query" placeholder="输入许可证密钥搜索" />
          </el-form-item>
          <el-form-item label="状态">
            <el-select v-model="searchForm.status">
              <el-option label="全部" value="" />
              <el-option label="有效" value="active" />
              <el-option label="无效" value="inactive" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="searchLicenses">搜索</el-button>
          </el-form-item>
        </el-form>
      </el-card>

      <!-- 生成许可证表单 -->
      <el-card>
        <template #header>
          <div class="card-header">
            <span>生成许可证</span>
          </div>
        </template>
        <el-form :model="licenseForm" label-width="120px">
          <el-form-item label="最大机器数">
            <el-input-number v-model="licenseForm.max_machines" :min="1" />
          </el-form-item>
          <el-form-item label="有效期(天)">
            <el-input-number v-model="licenseForm.expire_days" :min="1" />
          </el-form-item>
          <el-form-item label="批量生成数量">
            <el-input-number v-model="licenseForm.batch_size" :min="1" />
          </el-form-item>
          <el-form-item label="备注">
            <el-input v-model="licenseForm.notes" type="textarea" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="generateLicense">生成许可证</el-button>
          </el-form-item>
        </el-form>
      </el-card>
      
      <!-- 许可证列表 -->
      <el-card style="margin-top: 20px">
        <template #header>
          <div class="card-header">
            <span>许可证列表</span>
            <div>
              <el-button type="primary" @click="fetchLicenses">刷新</el-button>
              <el-button 
                type="danger" 
                @click="batchDeactivate"
                :disabled="!selectedLicenses.length"
              >
                批量停用
              </el-button>
              <el-button 
                type="success" 
                @click="batchRenew"
                :disabled="!selectedLicenses.length"
              >
                批量续期
              </el-button>
            </div>
          </div>
        </template>
        <el-table 
          :data="licenses" 
          style="width: 100%"
          @selection-change="handleSelectionChange"
          v-loading="loading"
        >
          <el-table-column type="selection" width="55" />
          <el-table-column prop="license_key" label="许可证密钥">
            <template #default="scope">
              <div class="license-key-cell">
                <span>{{ scope.row.license_key }}</span>
                <el-button
                  type="primary"
                  link
                  size="small"
                  @click="copyText(scope.row.license_key)"
                >
                  <el-icon><CopyDocument /></el-icon>
                </el-button>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="is_active" label="状态">
            <template #default="scope">
              <el-tag :type="scope.row.is_active ? 'success' : 'danger'">
                {{ scope.row.is_active ? '有效' : '无效' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="expire_date" label="过期时间">
            <template #default="scope">
              {{ formatDate(scope.row.expire_date) }}
            </template>
          </el-table-column>
          <el-table-column prop="active_machines" label="已绑定机器数" />
          <el-table-column label="备注" width="200">
            <template #default="scope">
              <div class="note-cell">
                <el-input
                  v-if="scope.row.isEditingNote"
                  v-model="scope.row.editingNote"
                  size="small"
                  @blur="saveNote(scope.row)"
                  @keyup.enter="saveNote(scope.row)"
                />
                <div v-else class="note-text" @click="startEditNote(scope.row)">
                  {{ scope.row.notes || '点击添加备注' }}
                </div>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="280">
            <template #default="scope">
              <el-button 
                type="primary" 
                size="small" 
                @click="showDetails(scope.row.license_key)"
              >
                详情
              </el-button>
              <el-button 
                type="danger" 
                size="small" 
                @click="deactivateLicense(scope.row.license_key)"
                :disabled="!scope.row.is_active"
              >
                停用
              </el-button>
              <el-button 
                type="success" 
                size="small" 
                @click="renewLicense(scope.row.license_key)"
              >
                续期
              </el-button>
              <el-button 
                type="info" 
                size="small" 
                @click="startEditNote(scope.row)"
              >
                备注
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        
        <!-- 添加分页组件 -->
        <div class="pagination-container">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="total"
            layout="total, sizes, prev, pager, next"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </el-card>
    </el-main>

    <!-- 许可证详情对话框 -->
    <el-dialog 
      v-model="detailsVisible" 
      title="许可证详情" 
      width="50%"
    >
      <el-descriptions :column="1" border>
        <el-descriptions-item label="许可证密钥">
          <div class="license-key-cell">
            <span>{{ currentDetails?.license_key }}</span>
            <el-button
              type="primary"
              link
              size="small"
              @click="copyText(currentDetails?.license_key)"
            >
              <el-icon><CopyDocument /></el-icon>
            </el-button>
          </div>
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="currentDetails?.is_active ? 'success' : 'danger'">
            {{ currentDetails?.is_active ? '有效' : '无效' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="过期时间">
          {{ formatDate(currentDetails?.expire_date) }}
        </el-descriptions-item>
        <el-descriptions-item label="最大机器数">{{ currentDetails?.max_machines }}</el-descriptions-item>
        <el-descriptions-item label="已绑定机器数">{{ currentDetails?.active_machines }}</el-descriptions-item>
        <el-descriptions-item label="使用次数">{{ currentDetails?.usage_count }}</el-descriptions-item>
        <el-descriptions-item label="绑定的机器">{{ currentDetails?.bound_machines }}</el-descriptions-item>
        <el-descriptions-item label="备注">{{ currentDetails?.notes }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </el-container>
</template>

<script>
import api from '../api'
import dayjs from 'dayjs'
import { CopyDocument } from '@element-plus/icons-vue'

export default {
  name: 'Dashboard',
  components: {
    CopyDocument
  },
  data() {
    return {
      licenseForm: {
        max_machines: 1,
        expire_days: 365,
        batch_size: 1,
        notes: ''
      },
      searchForm: {
        query: '',
        status: ''
      },
      licenses: [],
      selectedLicenses: [],
      detailsVisible: false,
      currentDetails: null,
      currentPage: 1,
      pageSize: 10,
      total: 0,
      loading: false
    }
  },
  methods: {
    async generateLicense() {
      try {
        const response = await api.generateLicense(this.licenseForm)
        this.$message.success('许可证生成成功')
        this.fetchLicenses()
      } catch (error) {
        this.$message.error('生成失败：' + (error.response?.data?.error || '未知错误'))
      }
    },
    async fetchLicenses() {
      try {
        this.loading = true
        const response = await api.getLicenses(this.currentPage, this.pageSize)
        this.licenses = response.data.items.map(license => ({
          ...license,
          isEditingNote: false,
          editingNote: license.notes || ''
        }))
        this.total = response.data.total
      } catch (error) {
        this.$message.error('获取许可证列表失败：' + (error.response?.data?.error || '未知错误'))
      } finally {
        this.loading = false
      }
    },
    async deactivateLicense(licenseKey) {
      try {
        await api.deactivateLicense(licenseKey)
        this.$message.success('许可证已停用')
        this.fetchLicenses()
      } catch (error) {
        this.$message.error('停用失败：' + (error.response?.data?.error || '未知错误'))
      }
    },
    async renewLicense(licenseKey) {
      try {
        await api.renewLicense(licenseKey, 365)
        this.$message.success('许可证已续期')
        this.fetchLicenses()
      } catch (error) {
        this.$message.error('续期失败：' + (error.response?.data?.error || '未知错误'))
      }
    },
    handleLogout() {
      try {
        this.$store.dispatch('logout')
        this.$router.push('/login')
        this.$message.success('退出成功')
      } catch (error) {
        console.error('退出时发生错误:', error)
        this.$message.error('退出失败，请重试')
      }
    },
    async searchLicenses() {
      try {
        this.loading = true
        const response = await api.searchLicenses(this.searchForm, this.currentPage, this.pageSize)
        this.licenses = response.data.items
        this.total = response.data.total
      } catch (error) {
        this.$message.error('搜索失败：' + (error.response?.data?.error || '未知错误'))
      } finally {
        this.loading = false
      }
    },
    async showDetails(licenseKey) {
      try {
        const response = await api.getLicenseDetails(licenseKey)
        this.currentDetails = response.data
        this.detailsVisible = true
      } catch (error) {
        this.$message.error('获取详情失败：' + (error.response?.data?.error || '未知错误'))
      }
    },
    handleSelectionChange(selection) {
      this.selectedLicenses = selection
    },
    async batchDeactivate() {
      try {
        const licenseKeys = this.selectedLicenses.map(license => license.license_key)
        console.log('Deactivating licenses:', licenseKeys)
        await api.batchDeactivate(licenseKeys)
        this.$message.success('批量停用成功')
        await this.fetchLicenses()
      } catch (error) {
        console.error('批量停用错误:', error)
        this.$message.error('批量停用失败：' + (error.response?.data?.error || '未知错误'))
      }
    },
    async batchRenew() {
      try {
        const licenseKeys = this.selectedLicenses.map(license => license.license_key)
        console.log('Renewing licenses:', licenseKeys)
        await api.batchRenew(licenseKeys, 365)
        this.$message.success('批量续期成功')
        await this.fetchLicenses()
      } catch (error) {
        console.error('批量续期错误:', error)
        this.$message.error('批量续期失败：' + (error.response?.data?.error || '未知错误'))
      }
    },
    async exportLicenses() {
      try {
        const response = await api.exportLicenses()
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', 'licenses.csv')
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
      } catch (error) {
        this.$message.error('导出失败：' + (error.response?.data?.error || '未知错误'))
      }
    },
    handleSizeChange(val) {
      this.pageSize = val
      this.fetchLicenses()
    },
    handleCurrentChange(val) {
      this.currentPage = val
      this.fetchLicenses()
    },
    startEditNote(row) {
      row.isEditingNote = true
      row.editingNote = row.notes || ''
      this.$nextTick(() => {
        const input = document.querySelector(`tr[data-row-key="${row.license_key}"] input`)
        if (input) input.focus()
      })
    },
    async saveNote(row) {
      try {
        await api.updateLicenseNote(row.license_key, row.editingNote)
        row.notes = row.editingNote
        row.isEditingNote = false
        this.$message.success('备注已更新')
      } catch (error) {
        this.$message.error('更新备注失败：' + (error.response?.data?.error || '未知错误'))
      }
    },
    formatDate(date) {
      if (!date) return ''
      return dayjs(date).format('YYYY/MM/DD HH:mm')
    },
    async copyText(text) {
      try {
        await navigator.clipboard.writeText(text)
        this.$message.success('复制成功')
      } catch (err) {
        const input = document.createElement('input')
        input.value = text
        document.body.appendChild(input)
        input.select()
        document.execCommand('copy')
        document.body.removeChild(input)
        this.$message.success('复制成功')
      }
    }
  },
  mounted() {
    this.fetchLicenses()
  }
}
</script>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  background-color: #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, .12);
}
.header-right {
  display: flex;
  gap: 10px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
.note-cell {
  position: relative;
}
.note-text {
  min-height: 24px;
  padding: 2px 8px;
  cursor: pointer;
  color: #666;
}
.note-text:hover {
  background-color: #f5f7fa;
}
.note-text:empty::before {
  content: '点击添加备注';
  color: #999;
  font-style: italic;
}
.license-key-cell {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.license-key-cell .el-button {
  opacity: 0;
  transition: opacity 0.2s;
}
.license-key-cell:hover .el-button {
  opacity: 1;
}
</style> 