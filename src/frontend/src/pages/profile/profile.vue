<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Check, Close, Edit } from '@element-plus/icons-vue'
import { getUserIconsAPI, getUserInfoAPI, updateUserInfoAPI } from '../../apis/auth'
import defaultAvatar from '../../assets/user.svg'
import { useUserStore } from '../../store/user'
import { apiUrl } from '../../utils/api'
import { zunoAgentAvatar } from '../../utils/brand'

const DEFAULT_DESCRIPTION = '这个用户很懒，还没有留下任何描述'
const PRESET_AVATARS = [defaultAvatar, zunoAgentAvatar]

const userStore = useUserStore()

const loading = ref(false)
const pageLoading = ref(true)
const iconsLoading = ref(false)
const editingDescription = ref(false)
const showAvatarDialog = ref(false)
const uploading = ref(false)

const formData = ref({
  user_avatar: defaultAvatar,
  user_description: DEFAULT_DESCRIPTION,
})

const remoteIcons = ref<string[]>([])
const selectedAvatar = ref(defaultAvatar)

const availableIcons = computed(() => {
  const merged = [...PRESET_AVATARS, ...remoteIcons.value]
  return Array.from(new Set(merged.filter(Boolean)))
})

const loadUserInfo = async () => {
  try {
    const userId = userStore.userInfo?.id
    if (!userId) {
      formData.value = {
        user_avatar: userStore.userInfo?.avatar || defaultAvatar,
        user_description: userStore.userInfo?.description || DEFAULT_DESCRIPTION,
      }
      selectedAvatar.value = formData.value.user_avatar
      return
    }

    const response = await getUserInfoAPI(userId)
    if (response.data.status_code !== 200) return

    const userInfo = response.data.data
    const updatedInfo = {
      id: userInfo.user_id || userInfo.id,
      username: userInfo.user_name || userInfo.username,
      nickname: userInfo.user_name || userInfo.nickname || userInfo.username,
      avatar: userInfo.user_avatar || userInfo.avatar || defaultAvatar,
      description: userInfo.user_description || userInfo.description || DEFAULT_DESCRIPTION,
    }

    userStore.updateUserInfo(updatedInfo)
    formData.value = {
      user_avatar: updatedInfo.avatar,
      user_description: updatedInfo.description,
    }
    selectedAvatar.value = formData.value.user_avatar
  } catch (error) {
    console.error('获取用户信息失败:', error)
    formData.value = {
      user_avatar: userStore.userInfo?.avatar || defaultAvatar,
      user_description: userStore.userInfo?.description || DEFAULT_DESCRIPTION,
    }
    selectedAvatar.value = formData.value.user_avatar
  }
}

const loadAvailableIcons = async () => {
  iconsLoading.value = true
  try {
    const response = await getUserIconsAPI()
    if (response.data.status_code === 200 && Array.isArray(response.data.data)) {
      remoteIcons.value = response.data.data
    }
  } catch (error) {
    console.error('获取头像列表失败:', error)
  } finally {
    iconsLoading.value = false
  }
}

const persistUserInfo = async (avatar: string, description: string) => {
  const userId = userStore.userInfo?.id
  if (!userId) {
    ElMessage.error('用户 ID 不存在')
    return false
  }

  const response = await updateUserInfoAPI(userId, avatar, description)
  if (response.data.status_code !== 200) {
    ElMessage.error(response.data.status_message || '保存失败')
    return false
  }

  userStore.updateUserInfo({ avatar, description })
  formData.value.user_avatar = avatar
  formData.value.user_description = description
  return true
}

const confirmAvatarSelection = async () => {
  try {
    loading.value = true
    const success = await persistUserInfo(selectedAvatar.value, formData.value.user_description)
    if (!success) return

    showAvatarDialog.value = false
    ElMessage.success('头像更新成功')
    window.dispatchEvent(new Event('workspace-session-updated'))
  } catch (error) {
    console.error('头像更新失败:', error)
    ElMessage.error('头像更新失败')
  } finally {
    loading.value = false
  }
}

const saveUserInfo = async () => {
  try {
    loading.value = true
    const success = await persistUserInfo(formData.value.user_avatar, formData.value.user_description)
    if (!success) return

    editingDescription.value = false
    ElMessage.success('保存成功')
  } catch (error) {
    console.error('保存用户信息失败:', error)
    ElMessage.error('保存失败')
  } finally {
    loading.value = false
  }
}

const cancelEditDescription = () => {
  editingDescription.value = false
  formData.value.user_description = userStore.userInfo?.description || DEFAULT_DESCRIPTION
}

const selectAvatar = (avatarUrl: string) => {
  selectedAvatar.value = avatarUrl
}

const handleImageError = (event: Event) => {
  const target = event.target as HTMLImageElement
  target.src = defaultAvatar
}

const handlePresetImageError = (event: Event) => {
  const target = event.target as HTMLImageElement
  target.src = zunoAgentAvatar
}

const handleCustomUpload = async (event: Event) => {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return

  const isJpgOrPng = ['image/jpeg', 'image/png'].includes(file.type)
  const isLt2M = file.size / 1024 / 1024 < 2
  if (!isJpgOrPng) {
    ElMessage.error('只能上传 JPG 或 PNG 格式的图片')
    input.value = ''
    return
  }
  if (!isLt2M) {
    ElMessage.error('图片大小不能超过 2MB')
    input.value = ''
    return
  }

  uploading.value = true
  try {
    const payload = new FormData()
    payload.append('file', file)
    const response = await fetch(apiUrl('/api/v1/upload'), {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token') || ''}`,
      },
      body: payload,
    })

    if (!response.ok) {
      throw new Error('上传失败')
    }

    const result = await response.json()
    const imageUrl =
      typeof result === 'string'
        ? result
        : result?.data?.url || result?.data?.path || result?.data || result?.url || result?.path

    if (!imageUrl) {
      throw new Error('未获取到头像地址')
    }

    selectedAvatar.value = imageUrl
    ElMessage.success('头像上传成功，请点击“确定选择”保存')
  } catch (error) {
    console.error('上传头像失败:', error)
    ElMessage.error('头像上传失败，请重试')
  } finally {
    uploading.value = false
    input.value = ''
  }
}

onMounted(async () => {
  await Promise.all([loadUserInfo(), loadAvailableIcons()])
  pageLoading.value = false
})
</script>

<template>
  <div class="profile-page" v-loading="pageLoading">
    <div class="profile-header">
      <div>
        <h2>个人资料</h2>
        <p>管理您的个人信息和偏好设置</p>
      </div>
      <el-button type="primary" @click="loadUserInfo" :loading="pageLoading">刷新信息</el-button>
    </div>

    <div v-if="!pageLoading" class="profile-content">
      <div class="profile-card profile-card--main">
        <div class="avatar-section">
          <div class="avatar-wrapper">
            <img :src="formData.user_avatar" alt="用户头像" class="user-avatar" @error="handleImageError" />
            <button class="avatar-edit" type="button" @click="showAvatarDialog = true">
              <el-icon><Edit /></el-icon>
            </button>
          </div>
          <div class="avatar-meta">
            <h3>{{ userStore.userInfo?.nickname || userStore.userInfo?.username || '未命名用户' }}</h3>
            <p class="user-id">ID: {{ userStore.userInfo?.id || '未知' }}</p>
          </div>
        </div>

        <div class="description-section">
          <div class="section-head">
            <h4>个人描述</h4>
            <el-button v-if="!editingDescription" text @click="editingDescription = true">编辑</el-button>
          </div>

          <div v-if="!editingDescription" class="description-preview">
            <p>{{ formData.user_description }}</p>
          </div>

          <div v-else class="description-edit">
            <el-input
              v-model="formData.user_description"
              type="textarea"
              :rows="4"
              placeholder="请输入个人描述"
              maxlength="200"
              show-word-limit
            />
            <div class="edit-actions">
              <el-button size="small" @click="cancelEditDescription">
                <el-icon><Close /></el-icon>
                取消
              </el-button>
              <el-button type="primary" size="small" :loading="loading" @click="saveUserInfo">
                <el-icon><Check /></el-icon>
                保存
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <el-dialog v-model="showAvatarDialog" title="头像设置" width="720px" destroy-on-close>
      <div class="dialog-body">
        <div class="selected-section">
          <h4>当前选择</h4>
          <div class="selected-avatar">
            <img :src="selectedAvatar" alt="选中的头像" @error="handleImageError" />
          </div>
        </div>

        <div class="avatar-grid-section">
          <div class="section-head">
            <h4>预设头像</h4>
            <span v-if="iconsLoading" class="section-tip">加载中...</span>
          </div>
          <div class="avatar-grid">
            <button
              v-for="icon in availableIcons"
              :key="icon"
              type="button"
              class="avatar-option"
              :class="{ active: selectedAvatar === icon }"
              @click="selectAvatar(icon)"
            >
              <img :src="icon" alt="头像选项" @error="handlePresetImageError" />
            </button>
          </div>
        </div>

        <div class="upload-section">
          <h4>上传自定义头像</h4>
          <label class="upload-button" :class="{ disabled: uploading }">
            <input type="file" accept="image/jpeg,image/png" :disabled="uploading" @change="handleCustomUpload" />
            <span>{{ uploading ? '上传中...' : '点击上传头像' }}</span>
          </label>
          <p class="upload-tip">支持 JPG、PNG 格式，文件大小不超过 2MB</p>
        </div>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showAvatarDialog = false">取消</el-button>
          <el-button type="primary" :loading="loading" @click="confirmAvatarSelection">确定选择</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped lang="scss">
.profile-page {
  min-height: 100%;
  padding: 24px;
  background: linear-gradient(180deg, #f7f2ea 0%, #fbf8f3 100%);
}

.profile-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 20px;

  h2 {
    margin: 0;
    font-size: 30px;
    color: #2f241b;
  }

  p {
    margin: 8px 0 0;
    color: #7a6a5a;
  }
}

.profile-content {
  max-width: 920px;
}

.profile-card {
  border-radius: 28px;
  border: 1px solid rgba(214, 132, 70, 0.12);
  background: rgba(255, 252, 248, 0.92);
  box-shadow: 0 18px 40px rgba(120, 80, 42, 0.08);
}

.profile-card--main {
  padding: 28px;
}

.avatar-section {
  display: flex;
  align-items: center;
  gap: 20px;
  padding-bottom: 24px;
  border-bottom: 1px solid rgba(214, 132, 70, 0.1);
}

.avatar-wrapper {
  position: relative;
  width: 120px;
  height: 120px;
}

.user-avatar {
  width: 100%;
  height: 100%;
  border-radius: 30px;
  object-fit: cover;
  border: 1px solid rgba(214, 132, 70, 0.18);
}

.avatar-edit {
  position: absolute;
  right: 10px;
  bottom: 10px;
  width: 36px;
  height: 36px;
  border: 0;
  border-radius: 12px;
  background: linear-gradient(135deg, #da8749 0%, #c96d31 100%);
  color: white;
  cursor: pointer;
}

.avatar-meta h3 {
  margin: 0;
  font-size: 24px;
  color: #2f241b;
}

.user-id {
  margin: 8px 0 0;
  color: #8b7865;
}

.description-section {
  padding-top: 24px;
}

.section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;

  h4 {
    margin: 0;
    color: #433428;
    font-size: 18px;
  }
}

.description-preview,
.description-edit,
.dialog-body {
  color: #5f5144;
}

.description-preview {
  min-height: 96px;
  padding: 18px;
  border-radius: 20px;
  background: #fffaf5;
  border: 1px solid rgba(214, 132, 70, 0.12);
}

.edit-actions,
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 16px;
}

.selected-section,
.avatar-grid-section,
.upload-section {
  & + & {
    margin-top: 24px;
  }
}

.selected-avatar {
  width: 96px;
  height: 96px;
  border-radius: 26px;
  overflow: hidden;
  border: 1px solid rgba(214, 132, 70, 0.14);

  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
}

.avatar-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(88px, 1fr));
  gap: 12px;
}

.avatar-option {
  border: 1px solid rgba(214, 132, 70, 0.14);
  border-radius: 20px;
  background: white;
  padding: 8px;
  cursor: pointer;

  img {
    width: 100%;
    aspect-ratio: 1;
    border-radius: 16px;
    object-fit: cover;
  }

  &.active {
    border-color: #c96d31;
    box-shadow: 0 0 0 3px rgba(201, 109, 49, 0.14);
  }
}

.upload-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 44px;
  padding: 0 18px;
  border-radius: 14px;
  background: #fff7ef;
  border: 1px dashed rgba(201, 109, 49, 0.4);
  color: #b76735;
  cursor: pointer;

  input {
    display: none;
  }

  &.disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
}

.upload-tip,
.section-tip {
  margin: 10px 0 0;
  color: #8b7865;
  font-size: 13px;
}

@media (max-width: 768px) {
  .profile-page {
    padding: 16px;
  }

  .profile-header,
  .avatar-section {
    flex-direction: column;
    align-items: flex-start;
  }

  .avatar-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}
</style>
