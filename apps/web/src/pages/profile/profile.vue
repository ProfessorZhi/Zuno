<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Check, Close, Edit, Refresh, Upload } from '@element-plus/icons-vue'
import { getUserIconsAPI, getUserInfoAPI, updateUserInfoAPI } from '../../apis/auth'
import { useUserStore } from '../../store/user'
import { apiUrl } from '../../utils/api'
import { DEFAULT_USER_AVATAR, USER_AVATAR_PRESETS, isLegacyRemoteUserAvatar, withUserAvatarVersion } from '../../utils/user-avatars'

const DEFAULT_DESCRIPTION = '这个用户很懒，还没有留下任何描述'
const PRESET_AVATARS = USER_AVATAR_PRESETS

const userStore = useUserStore()

const loading = ref(false)
const pageLoading = ref(true)
const iconsLoading = ref(false)
const editingDescription = ref(false)
const showAvatarDialog = ref(false)
const uploading = ref(false)

const formData = ref({
  user_avatar: DEFAULT_USER_AVATAR,
  user_description: DEFAULT_DESCRIPTION,
})

const remoteIcons = ref<string[]>([])
const selectedAvatar = ref(DEFAULT_USER_AVATAR)

const normalizeAvatarUrl = (avatar?: string) => {
  const raw = String(avatar || '').trim()
  if (!raw || raw.startsWith('/src/assets/') || isLegacyRemoteUserAvatar(raw)) return DEFAULT_USER_AVATAR
  return withUserAvatarVersion(raw)
}

const availableIcons = computed(() => {
  const merged = [...PRESET_AVATARS, ...remoteIcons.value]
  return Array.from(new Set(merged.filter(Boolean)))
})

const loadUserInfo = async () => {
  try {
    const userId = userStore.userInfo?.id
    if (!userId) {
      formData.value = {
        user_avatar: normalizeAvatarUrl(userStore.userInfo?.avatar),
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
      avatar: normalizeAvatarUrl(userInfo.user_avatar || userInfo.avatar),
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
      user_avatar: normalizeAvatarUrl(userStore.userInfo?.avatar),
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
      remoteIcons.value = response.data.data.map(normalizeAvatarUrl)
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
  target.src = DEFAULT_USER_AVATAR
}

const handlePresetImageError = (event: Event) => {
  const target = event.target as HTMLImageElement
  target.src = DEFAULT_USER_AVATAR
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
  formData.value = {
    user_avatar: normalizeAvatarUrl(userStore.userInfo?.avatar),
    user_description: userStore.userInfo?.description || DEFAULT_DESCRIPTION,
  }
  selectedAvatar.value = formData.value.user_avatar
  pageLoading.value = false
  await Promise.all([loadUserInfo(), loadAvailableIcons()])
})
</script>

<template>
  <div class="profile-page" v-loading="pageLoading">
    <header class="page-header">
      <div class="title-block">
        <img :src="formData.user_avatar" alt="" class="page-icon" @error="handleImageError" />
        <div>
          <h1>个人资料</h1>
        </div>
      </div>
      <button class="profile-icon-button profile-refresh" type="button" :disabled="pageLoading" aria-label="刷新" @click="loadUserInfo">
        <el-icon><Refresh /></el-icon>
      </button>
    </header>

    <div v-if="!pageLoading" class="profile-content">
      <section class="profile-panel">
        <div class="avatar-section">
          <div class="avatar-wrapper">
            <img :src="formData.user_avatar" alt="用户头像" class="user-avatar" @error="handleImageError" />
            <button class="avatar-edit" type="button" @click="showAvatarDialog = true">
              <el-icon><Edit /></el-icon>
            </button>
          </div>
          <div class="avatar-meta">
            <span>当前用户</span>
            <strong>{{ userStore.userInfo?.nickname || userStore.userInfo?.username || '未命名用户' }}</strong>
            <p>ID {{ userStore.userInfo?.id || '未知' }}</p>
          </div>
        </div>

        <div class="description-section">
          <div class="section-head">
            <h4>个人描述</h4>
            <button
              class="profile-icon-button section-toggle"
              type="button"
              :aria-label="editingDescription ? '收起编辑' : '编辑描述'"
              @click="editingDescription ? cancelEditDescription() : (editingDescription = true)"
            >
              <el-icon>
                <Close v-if="editingDescription" />
                <Edit v-else />
              </el-icon>
            </button>
          </div>

          <div v-if="!editingDescription" class="description-preview">
            <p>{{ formData.user_description }}</p>
          </div>

          <div v-else class="description-edit">
            <el-input
              v-model="formData.user_description"
              type="textarea"
              :autosize="{ minRows: 1, maxRows: 4 }"
              placeholder="请输入个人描述"
              maxlength="200"
              show-word-limit
            />
            <div class="edit-actions">
              <button class="profile-icon-button save-inline" type="button" :disabled="loading" aria-label="保存描述" @click="saveUserInfo">
                <el-icon><Check /></el-icon>
              </button>
            </div>
          </div>
        </div>
      </section>
    </div>

    <el-dialog v-model="showAvatarDialog" class="profile-avatar-dialog" title="头像设置" width="720px" destroy-on-close>
      <div class="dialog-body">
        <div class="selected-section">
          <div class="selected-current">
            <h4>当前选择</h4>
            <div class="selected-avatar">
              <img :src="selectedAvatar" alt="选中的头像" @error="handleImageError" />
            </div>
          </div>

          <div class="avatar-dialog-actions">
            <label
              class="avatar-action icon-only upload-action"
              :class="{ disabled: uploading }"
              :aria-label="uploading ? '头像上传中' : '上传自定义头像'"
            >
              <input type="file" accept="image/jpeg,image/png" :disabled="uploading" @change="handleCustomUpload" />
              <el-icon><Upload /></el-icon>
              <span class="sr-only">{{ uploading ? '上传中' : '自定义头像' }}</span>
            </label>
            <button class="avatar-action icon-only muted" type="button" aria-label="取消选择" @click="showAvatarDialog = false">
              <el-icon><Close /></el-icon>
              <span class="sr-only">取消</span>
            </button>
            <button class="avatar-action icon-only primary" type="button" :disabled="loading" aria-label="确定选择" @click="confirmAvatarSelection">
              <el-icon><Check /></el-icon>
              <span class="sr-only">确定选择</span>
            </button>
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

      </div>
    </el-dialog>
  </div>
</template>

<style scoped lang="scss">
.profile-page {
  display: grid;
  gap: 16px;
  min-height: 0;
  color: #0f172a;
  background: transparent;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  padding: 0;

  h1 {
    margin: 0;
    font-size: 24px;
    font-weight: 680;
    letter-spacing: 0;
    color: #0f172a;
  }

}

.title-block {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
}

.page-icon {
  width: 32px;
  height: 32px;
  border-radius: 999px;
  object-fit: cover;
  background: rgba(245, 158, 11, 0.08);
}

.profile-icon-button,
.text-action {
  border: 0;
  background: transparent;
  color: #b45309;
  font: inherit;
  font-size: 13px;
  font-weight: 620;
  cursor: pointer;
}

.profile-icon-button {
  width: 34px;
  height: 34px;
  padding: 0;
  border-radius: 999px;
  display: inline-grid;
  place-items: center;
  color: #94a3b8;
  transition:
    color 0.18s ease,
    background 0.18s ease,
    transform 0.18s cubic-bezier(0.2, 0.78, 0.22, 1);

  &:hover {
    color: #b45309;
    background: rgba(245, 158, 11, 0.08);
  }

  &:active {
    transform: scale(0.96);
  }

  &:disabled {
    opacity: 0.5;
    cursor: progress;
  }
}

.profile-refresh {
  flex: 0 0 auto;
}

.profile-content,
.profile-panel {
  min-width: 0;
  background: transparent;
  border: 0;
  box-shadow: none;
}

.profile-panel {
  display: grid;
  grid-template-columns: minmax(220px, 0.75fr) minmax(260px, 1.25fr);
  align-items: start;
  gap: 28px;
  padding: 0;
}

.avatar-section {
  display: flex;
  align-items: center;
  gap: 16px;
  min-width: 0;
}

.avatar-wrapper {
  position: relative;
  flex: 0 0 72px;
  width: 72px;
  height: 72px;
}

.user-avatar {
  width: 100%;
  height: 100%;
  border-radius: 20px;
  object-fit: cover;
  background: rgba(245, 158, 11, 0.08);
}

.avatar-edit {
  position: absolute;
  right: -4px;
  bottom: -4px;
  width: 28px;
  height: 28px;
  border: 0;
  border-radius: 999px;
  background: #f59e0b;
  color: white;
  cursor: pointer;
  display: inline-grid;
  place-items: center;
  box-shadow: 0 12px 24px rgba(245, 158, 11, 0.18);
}

.avatar-meta {
  display: grid;
  gap: 4px;
  min-width: 0;
}

.avatar-meta span {
  color: #94a3b8;
  font-size: 12px;
}

.avatar-meta strong {
  margin: 0;
  color: #0f172a;
  font-size: 20px;
  font-weight: 680;
}

.avatar-meta p {
  margin: 0;
  color: #64748b;
  font-size: 13px;
}

.description-section {
  display: grid;
  gap: 8px;
  min-width: 0;
}

.section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  min-height: 34px;

  h4 {
    margin: 0;
    color: #0f172a;
    font-size: 15px;
    font-weight: 650;
  }
}

.section-toggle {
  width: 28px;
  height: 28px;
}

.description-preview,
.description-edit,
.dialog-body {
  color: #475569;
}

.description-preview {
  min-height: 34px;
  padding: 0 0 9px;
  background: transparent;
  box-shadow: none;

  p {
    margin: 0;
    color: #475569;
    line-height: 1.7;
  }
}

.description-edit :deep(.el-textarea__inner) {
  min-height: 34px !important;
  padding: 0 0 7px !important;
  border: 0 !important;
  border-radius: 0 !important;
  background: transparent !important;
  box-shadow: inset 0 -1px 0 rgba(148, 163, 184, 0.26) !important;
  resize: vertical;
}

.edit-actions,
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 14px;
  margin-top: 8px;
}

.save-inline {
  width: 34px;
  height: 34px;
  color: #ffffff;
  background: #f59e0b;
  box-shadow: 0 10px 22px rgba(245, 158, 11, 0.14);

  &:hover {
    color: #ffffff;
    background: #e89105;
  }
}

.text-action {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 0;

  &.muted {
    color: #94a3b8;
  }

  &.primary {
    color: #b45309;
  }

  &:disabled {
    opacity: 0.55;
    cursor: progress;
  }
}

.selected-section,
.avatar-grid-section {
  & + & {
    margin-top: 18px;
  }
}

.selected-section {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 22px;
}

.selected-current {
  display: flex;
  align-items: center;
  gap: 16px;

  h4 {
    margin: 0;
    min-width: 70px;
  }
}

.selected-avatar {
  width: 86px;
  height: 86px;
  display: grid;
  place-items: center;
  border-radius: 0;
  overflow: visible;
  background: transparent;

  img {
    width: 100%;
    height: 100%;
    object-fit: contain;
  }
}

.avatar-dialog-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  flex-wrap: wrap;
  gap: 10px;
}

.avatar-action {
  width: 36px;
  height: 36px;
  min-height: 36px;
  border: 0;
  border-radius: 999px;
  background: transparent;
  color: #64748b;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 0;
  font: inherit;
  font-size: 13px;
  font-weight: 620;
  box-shadow: inset 0 0 0 1px rgba(148, 163, 184, 0.2);
  transition:
    color 0.18s ease,
    background 0.18s ease,
    box-shadow 0.18s ease,
    transform 0.18s cubic-bezier(0.2, 0.78, 0.22, 1);

  input {
    display: none;
  }

  &:hover {
    color: #b45309;
    background: rgba(245, 158, 11, 0.08);
    box-shadow: inset 0 0 0 1px rgba(245, 158, 11, 0.34);
  }

  &:active {
    transform: translateY(1px);
  }

  &.primary {
    color: #ffffff;
    background: #f59e0b;
    box-shadow: none;
  }

  &.primary:hover {
    color: #ffffff;
    background: #e89105;
    box-shadow: none;
  }

  &.disabled,
  &:disabled {
    opacity: 0.55;
    cursor: progress;
  }
}

.avatar-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(68px, 1fr));
  gap: 14px 12px;
}

.avatar-option {
  position: relative;
  border: 0;
  border-radius: 0;
  background: transparent;
  padding: 0;
  cursor: pointer;
  display: grid;
  place-items: center;
  min-height: 68px;
  isolation: isolate;

  img {
    width: min(68px, 100%);
    aspect-ratio: 1;
    border-radius: 0;
    object-fit: contain;
    background: transparent;
    box-shadow: none;
    transition: transform 0.18s cubic-bezier(0.2, 0.78, 0.22, 1), filter 0.18s ease;
  }

  &::after {
    content: '';
    position: absolute;
    left: 13px;
    right: 13px;
    bottom: 0;
    height: 2px;
    border-radius: 999px;
    background: #f59e0b;
    opacity: 0;
    transform: scaleX(0.45);
    transition: opacity 0.18s ease, transform 0.18s cubic-bezier(0.2, 0.78, 0.22, 1);
  }

  &:hover img {
    transform: translateY(-1px);
    filter: drop-shadow(0 8px 16px rgba(15, 23, 42, 0.08));
  }

  &.active {
    &::after {
      opacity: 1;
      transform: scaleX(1);
    }

    img {
      filter: drop-shadow(0 10px 20px rgba(245, 158, 11, 0.18));
    }
  }
}

.upload-tip,
.section-tip {
  margin: 10px 0 0;
  color: #94a3b8;
  font-size: 13px;
}

:deep(.profile-avatar-dialog) {
  background: rgba(255, 255, 255, 0.34) !important;
  border-color: rgba(226, 232, 240, 0.48) !important;
  box-shadow: none !important;
}

:deep(.profile-avatar-dialog .el-dialog__header),
:deep(.profile-avatar-dialog .el-dialog__body),
:deep(.profile-avatar-dialog .el-dialog__footer) {
  background: transparent !important;
  border-color: rgba(226, 232, 240, 0.42) !important;
}

:deep(.profile-avatar-dialog .el-dialog__footer) {
  display: none !important;
  padding: 0 !important;
  border: 0 !important;
}

:deep(.profile-avatar-dialog .el-dialog__title) {
  font-size: 15px;
  font-weight: 650;
  color: #0f172a;
}

@media (max-width: 768px) {
  .profile-panel {
    grid-template-columns: 1fr;
    gap: 18px;
  }

  .avatar-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}
</style>
