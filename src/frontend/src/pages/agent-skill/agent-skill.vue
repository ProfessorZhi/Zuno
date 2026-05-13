<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Check, Delete, DocumentAdd, Edit, Plus, Search, View } from '@element-plus/icons-vue'
import skillIcon from '../../assets/skill.svg'
import skillCreatorIcon from '../../assets/skills/skill-creator.svg'
import skillInstallerIcon from '../../assets/skills/skill-installer.svg'
import emptyDataIcon from '../../assets/dashboard/空数据.svg'
import { safeDisplayText } from '../../utils/display-text'
import {
  addAgentSkillFileAPI,
  createAgentSkillAPI,
  deleteAgentSkillAPI,
  deleteAgentSkillFileAPI,
  getAgentSkillsAPI,
  updateAgentSkillFileAPI,
  type AgentSkill,
  type AgentSkillFile,
  type AgentSkillFolder,
} from '../../apis/agent-skill'
import ZunoMiniPager from '../../components/ZunoMiniPager.vue'

type SkillFileEntry = {
  path: string
  name: string
  content: string
}

const loading = ref(false)
const keyword = ref('')
const skills = ref<AgentSkill[]>([])
const LIST_PAGE_SIZE = 6
const listPage = ref(1)

const createDialogVisible = ref(false)
const createLoading = ref(false)
const createForm = ref({ name: '', description: '' })

const detailDialogVisible = ref(false)
const currentSkill = ref<AgentSkill | null>(null)
const selectedFile = ref<SkillFileEntry | null>(null)
const fileContent = ref('')
const savingFile = ref(false)

const addFileDialogVisible = ref(false)
const addFileLoading = ref(false)
const addFileForm = ref({ path: '', name: '' })

const isReadonlySkill = (skill: AgentSkill | null | undefined) =>
  Boolean(skill?.is_readonly || skill?.is_system)

const getSkillSourceLabel = (skill: AgentSkill) => {
  if (skill.source === 'system') return '系统'
  if (skill.source === 'host') return '本地'
  return '我的'
}

const getSkillSourceTagType = (skill: AgentSkill) => {
  if (skill.source === 'system') return 'warning'
  if (skill.source === 'host') return 'success'
  return 'info'
}

const visibleSkills = computed(() => {
  const search = keyword.value.trim().toLowerCase()
  const list = [...skills.value].sort((a, b) => {
    const aTime = new Date(a.update_time || a.create_time).getTime()
    const bTime = new Date(b.update_time || b.create_time).getTime()
    return bTime - aTime
  })
  if (!search) return list
  return list.filter((item) => [item.name, item.description || ''].join(' ').toLowerCase().includes(search))
})
const paginatedSkills = computed(() => visibleSkills.value.slice(
  (listPage.value - 1) * LIST_PAGE_SIZE,
  listPage.value * LIST_PAGE_SIZE,
))

const currentSkillReadonly = computed(() => isReadonlySkill(currentSkill.value))

const getSkillDescription = (skill: AgentSkill) => (
  safeDisplayText(skill.description, '\u6682\u65e0\u8bf4\u660e')
)

const getSkillIcon = (skill: AgentSkill) => {
  const name = skill.name.toLowerCase()
  if (name.includes('skill-creator') || name.includes('creator')) return skillCreatorIcon
  if (name.includes('skill-installer') || name.includes('installer')) return skillInstallerIcon
  return skillIcon
}

const formatSkillTime = (value?: string) => {
  if (!value) return '--'
  const normalized = value.includes('T') ? value : value.replace(' ', 'T')
  const date = new Date(normalized)
  if (Number.isNaN(date.getTime())) return value.replace('T', ' ').slice(0, 16)
  const pad = (num: number) => String(num).padStart(2, '0')
  return `${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}`
}

const flattenFiles = (folder?: AgentSkillFolder): SkillFileEntry[] => {
  if (!folder?.folder) return []
  const result: SkillFileEntry[] = []

  const walk = (items: Array<AgentSkillFile | AgentSkillFolder>) => {
    items.forEach((item) => {
      if (item.type === 'file') {
        result.push({ path: item.path, name: item.name, content: item.content })
        return
      }
      walk(item.folder || [])
    })
  }

  walk(folder.folder)
  return result.sort((a, b) => a.path.localeCompare(b.path, 'zh-CN'))
}

const selectedFiles = computed(() => flattenFiles(currentSkill.value?.folder))

const fetchSkills = async () => {
  loading.value = true
  try {
    const response = await getAgentSkillsAPI()
    if (response.data.status_code === 200) {
      skills.value = response.data.data || []
      return
    }
    ElMessage.error(response.data.status_message || '加载 Skill 列表失败')
  } catch (error) {
    console.error('加载 Skill 列表失败:', error)
    ElMessage.error('加载 Skill 列表失败')
  } finally {
    loading.value = false
  }
}

const openCreateDialog = () => {
  if (createDialogVisible.value) {
    createDialogVisible.value = false
    return
  }
  createForm.value = { name: '', description: '' }
  createDialogVisible.value = true
}

const handleCreateSkill = async () => {
  if (!createForm.value.name.trim() || !createForm.value.description.trim()) {
    createDialogVisible.value = false
    return
  }

  createLoading.value = true
  try {
    const response = await createAgentSkillAPI({
      name: createForm.value.name.trim(),
      description: createForm.value.description.trim(),
    })
    if (response.data.status_code === 200) {
      ElMessage.success('Skill 已创建')
      createDialogVisible.value = false
      await fetchSkills()
      return
    }
    ElMessage.error(response.data.status_message || '创建 Skill 失败')
  } catch (error) {
    console.error('创建 Skill 失败:', error)
    ElMessage.error('创建 Skill 失败')
  } finally {
    createLoading.value = false
  }
}

const handleDeleteSkill = async (skill: AgentSkill) => {
  if (isReadonlySkill(skill)) {
    ElMessage.info('只读 Skill 不能删除')
    return
  }

  try {
    await ElMessageBox.confirm(
      `删除后，Skill “${skill.name}” 和其文件都会被清空。`,
      '确认删除 Skill',
      {
        confirmButtonText: '确认删除',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
  } catch {
    return
  }

  try {
    const response = await deleteAgentSkillAPI({ agent_skill_id: skill.id })
    if (response.data.status_code === 200) {
      ElMessage.success('Skill 已删除')
      await fetchSkills()
      return
    }
    ElMessage.error(response.data.status_message || '删除 Skill 失败')
  } catch (error) {
    console.error('删除 Skill 失败:', error)
    ElMessage.error('删除 Skill 失败')
  }
}

const openDetailDialog = (skill: AgentSkill) => {
  if (currentSkill.value?.id === skill.id && detailDialogVisible.value) {
    detailDialogVisible.value = false
    addFileDialogVisible.value = false
    return
  }
  currentSkill.value = skill
  const files = flattenFiles(skill.folder)
  selectedFile.value = files[0] || null
  fileContent.value = files[0]?.content || ''
  detailDialogVisible.value = true
  addFileDialogVisible.value = false
}

const selectFile = (file: SkillFileEntry) => {
  selectedFile.value = file
  fileContent.value = file.content
}

const refreshCurrentSkill = async (skillId: string) => {
  await fetchSkills()
  const target = skills.value.find((item) => item.id === skillId) || null
  currentSkill.value = target
  if (!target) {
    detailDialogVisible.value = false
    return
  }

  const files = flattenFiles(target.folder)
  if (selectedFile.value) {
    const latest = files.find((file) => file.path === selectedFile.value?.path) || files[0] || null
    selectedFile.value = latest
    fileContent.value = latest?.content || ''
    return
  }

  selectedFile.value = files[0] || null
  fileContent.value = files[0]?.content || ''
}

const handleSaveFile = async () => {
  if (!currentSkill.value || !selectedFile.value) {
    ElMessage.warning('请先选择一个文件')
    return
  }
  if (isReadonlySkill(currentSkill.value)) {
    ElMessage.info('只读 Skill 不能修改文件')
    return
  }

  savingFile.value = true
  try {
    const response = await updateAgentSkillFileAPI({
      agent_skill_id: currentSkill.value.id,
      path: selectedFile.value.path,
      content: fileContent.value,
    })
    if (response.data.status_code === 200) {
      ElMessage.success('文件已保存')
      await refreshCurrentSkill(currentSkill.value.id)
      return
    }
    ElMessage.error(response.data.status_message || '保存文件失败')
  } catch (error) {
    console.error('保存文件失败:', error)
    ElMessage.error('保存文件失败')
  } finally {
    savingFile.value = false
  }
}

const openAddFileDialog = () => {
  if (!currentSkill.value) {
    ElMessage.warning('请先打开一个 Skill')
    return
  }
  if (isReadonlySkill(currentSkill.value)) {
    ElMessage.info('只读 Skill 不能新增文件')
    return
  }
  if (addFileDialogVisible.value) {
    addFileDialogVisible.value = false
    return
  }
  addFileForm.value = { path: '', name: '' }
  addFileDialogVisible.value = true
}

const handleAddFile = async () => {
  if (!currentSkill.value) return
  if (!addFileForm.value.path.trim() || !addFileForm.value.name.trim()) {
    ElMessage.warning('请填写目录和文件名')
    return
  }

  addFileLoading.value = true
  try {
    const response = await addAgentSkillFileAPI({
      agent_skill_id: currentSkill.value.id,
      path: addFileForm.value.path.trim(),
      name: addFileForm.value.name.trim(),
    })
    if (response.data.status_code === 200) {
      ElMessage.success('文件已创建')
      addFileDialogVisible.value = false
      await refreshCurrentSkill(currentSkill.value.id)
      return
    }
    ElMessage.error(response.data.status_message || '创建文件失败')
  } catch (error) {
    console.error('创建文件失败:', error)
    ElMessage.error('创建文件失败')
  } finally {
    addFileLoading.value = false
  }
}

const handleDeleteFile = async (file: SkillFileEntry) => {
  if (!currentSkill.value) return
  if (isReadonlySkill(currentSkill.value)) {
    ElMessage.info('只读 Skill 不能删除文件')
    return
  }

  try {
    await ElMessageBox.confirm(`确认删除文件 “${file.path}” 吗？`, '删除文件', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消',
    })
  } catch {
    return
  }

  try {
    const response = await deleteAgentSkillFileAPI({
      agent_skill_id: currentSkill.value.id,
      path: file.path.substring(0, file.path.lastIndexOf('/')),
      name: file.name,
    })
    if (response.data.status_code === 200) {
      ElMessage.success('文件已删除')
      await refreshCurrentSkill(currentSkill.value.id)
      return
    }
    ElMessage.error(response.data.status_message || '删除文件失败')
  } catch (error) {
    console.error('删除文件失败:', error)
    ElMessage.error('删除文件失败')
  }
}

onMounted(fetchSkills)
</script>

<template>
  <div class="skill-page">
    <section class="hero-card">
      <div>
        <div class="settings-title-row">
          <img :src="skillIcon" alt="Skill" class="page-icon" />
          <h1>Skill</h1>
        </div>
      </div>
      <div class="hero-actions">
        <el-button
          :class="['settings-icon-button', { 'is-create-open': createDialogVisible }]"
          type="primary"
          :icon="Plus"
          circle
          :title="createDialogVisible ? '收起新建 Skill' : '新建 Skill'"
          :aria-label="createDialogVisible ? '收起新建 Skill' : '新建 Skill'"
          @click="openCreateDialog"
        />
      </div>
    </section>

    <section class="toolbar-card">
      <el-input v-model="keyword" placeholder="搜索 Skill 名称或描述" clearable>
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
    </section>

    <section class="skill-grid" v-loading="loading">
      <article v-for="skill in paginatedSkills" :key="skill.id" class="skill-card">
        <div class="skill-card-head">
          <div class="skill-title-wrap">
            <div class="skill-icon-wrap"><img :src="getSkillIcon(skill)" :alt="skill.name" /></div>
            <div class="skill-main">
              <div class="skill-heading">
                <h3 :title="skill.name">{{ skill.name }}</h3>
                <p :title="getSkillDescription(skill)">{{ getSkillDescription(skill) }}</p>
              </div>
              <div class="skill-meta">
                <span class="skill-pill">{{ getSkillSourceLabel(skill) }}</span>
                <span class="skill-pill">创建 {{ formatSkillTime(skill.create_time) }}</span>
                <span class="skill-pill">更新 {{ formatSkillTime(skill.update_time || skill.create_time) }}</span>
              </div>
            </div>
          </div>
          <div class="skill-actions">
            <el-button
              class="skill-icon-button"
              type="primary"
              :icon="isReadonlySkill(skill) ? View : Edit"
              circle
              :title="isReadonlySkill(skill) ? '查看详情' : '编辑文件'"
              :aria-label="isReadonlySkill(skill) ? '查看详情' : '编辑文件'"
              @click="openDetailDialog(skill)"
            />
            <el-button
              v-if="!isReadonlySkill(skill)"
              class="skill-icon-button danger"
              type="danger"
              :icon="Delete"
              circle
              title="删除"
              aria-label="删除"
              @click="handleDeleteSkill(skill)"
            />
          </div>
        </div>
      </article>
      <div v-if="!visibleSkills.length && !loading" class="empty-state settings-empty-hint">
        <img :src="emptyDataIcon" alt="空数据" class="empty-state-icon" />
        {{ keyword ? '没有匹配到 Skill，换个关键词试试看吧 (´･_･`)' : 'Skill 小书架还空着，点右上角 + 收纳第一招吧 (๑˃̵ᴗ˂̵)و' }}
      </div>
      <ZunoMiniPager v-model:page="listPage" class="settings-list-pager" :total="visibleSkills.length" :page-size="LIST_PAGE_SIZE" />
    </section>

    <Transition name="settings-panel">
      <section v-if="createDialogVisible" class="inline-panel create-panel">
        <div class="inline-panel-head">
          <div>
            <h2>新建 Skill</h2>
          </div>
          <div class="panel-actions">
            <el-button class="skill-icon-button" type="primary" :icon="Check" circle :loading="createLoading" title="创建" aria-label="创建" @click="handleCreateSkill" />
          </div>
        </div>
        <el-form label-position="top" class="compact-form">
          <el-form-item label="Skill 名称">
            <el-input v-model="createForm.name" placeholder="例如：发布检查助手" />
          </el-form-item>
          <el-form-item label="Skill 描述">
            <el-input
              v-model="createForm.description"
              type="textarea"
              :autosize="{ minRows: 1, maxRows: 4 }"
              resize="none"
              placeholder="一句话说明它适合什么场景。"
            />
          </el-form-item>
        </el-form>
      </section>
    </Transition>

    <Transition name="settings-panel">
      <section
        v-if="detailDialogVisible"
        class="inline-panel detail-panel"
        :class="{ readonly: currentSkillReadonly }"
      >
        <div class="inline-panel-head">
          <div>
            <h2>{{ currentSkill?.name || '文件管理' }}</h2>
          </div>
          <div class="panel-actions">
            <el-button
              class="skill-icon-button ghost"
              :icon="DocumentAdd"
              circle
              :disabled="currentSkillReadonly"
              :title="addFileDialogVisible ? '收起新增文件' : '新增文件'"
              :aria-label="addFileDialogVisible ? '收起新增文件' : '新增文件'"
              @click="openAddFileDialog"
            />
            <el-button
              class="skill-icon-button"
              type="primary"
              :icon="Check"
              circle
              :loading="savingFile"
              :disabled="currentSkillReadonly || !selectedFile"
              title="保存文件"
              aria-label="保存文件"
              @click="handleSaveFile"
            />
          </div>
        </div>

        <Transition name="settings-panel">
          <div v-if="addFileDialogVisible" class="add-file-strip">
            <el-input v-model="addFileForm.path" placeholder="目录，例如：my-skill/reference" />
            <el-input v-model="addFileForm.name" placeholder="文件名，例如：README.md" />
            <el-button class="skill-icon-button" type="primary" :icon="Check" circle :loading="addFileLoading" title="创建文件" aria-label="创建文件" @click="handleAddFile" />
          </div>
        </Transition>

      <div class="detail-layout">
        <aside class="file-sidebar">
          <div class="file-sidebar-head">
            <strong>文件列表</strong>
          </div>

          <div v-if="selectedFiles.length" class="file-list">
            <button
              v-for="file in selectedFiles"
              :key="file.path"
              type="button"
              class="file-item"
              :class="{ active: selectedFile?.path === file.path }"
              @click="selectFile(file)"
            >
              <span>{{ file.path }}</span>
              <el-icon v-if="!currentSkillReadonly" class="file-delete" @click.stop="handleDeleteFile(file)">
                <Delete />
              </el-icon>
            </button>
          </div>
          <el-empty v-else description="当前 Skill 还没有文件" />
        </aside>

        <section class="editor-pane">
          <div class="editor-head">
            <strong>{{ selectedFile?.path || '未选择文件' }}</strong>
          </div>
          <el-alert
            v-if="currentSkillReadonly"
            type="info"
            :closable="false"
            title="这是只读 Skill，可以查看内容，但不能直接修改。"
            class="readonly-alert"
          />
          <el-input
            v-model="fileContent"
            type="textarea"
            :rows="24"
            resize="none"
            :readonly="currentSkillReadonly"
            placeholder="在这里编辑 Skill 文件内容"
          />
        </section>
      </div>
      </section>
    </Transition>
  </div>
</template>

<style scoped lang="scss">
.skill-page { display: grid; gap: 20px; padding: 24px; }
.hero-card { order: 0; }
.toolbar-card { order: 1; }
.create-panel { order: 2; }
.skill-grid { order: 3; }
.detail-panel { order: 4; }
.hero-card, .toolbar-card, .skill-card {
  border-radius: 24px;
  border: 1px solid rgba(214, 132, 70, 0.12);
  background: rgba(255, 252, 248, 0.94);
  box-shadow: 0 18px 36px rgba(120, 80, 42, 0.08);
}
.hero-card, .toolbar-card { padding: 24px 26px; }
.eyebrow { font-size: 12px; letter-spacing: 0.16em; color: #be6d38; }
.settings-title-row {
  display: flex;
  align-items: center;
  gap: 14px;
}
.page-icon {
  width: 40px;
  height: 40px;
  object-fit: contain;
}
.hero-card h1 { margin: 0; font-size: 32px; color: #2f241b; }
.hero-card p { margin: 0; color: #786656; line-height: 1.8; }
.hero-actions { margin-top: 18px; display: flex; gap: 12px; flex-wrap: wrap; }
.skill-grid { display: grid; gap: 0; }
.inline-panel {
  display: grid;
  gap: 14px;
  margin-top: 2px;
  padding: 18px 20px;
  border-radius: 24px;
  border: 1px solid rgba(148, 163, 184, 0.18);
  background: rgba(255, 255, 255, 0.78);
  box-shadow: 0 18px 44px rgba(15, 23, 42, 0.08);
  backdrop-filter: blur(22px);
}
.inline-panel-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}
.inline-panel-head h2 {
  margin: 0;
  color: #0f172a;
  font-size: 18px;
  line-height: 1.25;
}
.inline-panel-head p {
  margin: 4px 0 0;
  color: #94a3b8;
  font-size: 12px;
  line-height: 1.45;
}
.panel-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 7px;
  flex-wrap: nowrap;
}
.panel-actions :deep(.el-button + .el-button) { margin-left: 0; }
.compact-form {
  display: grid;
  grid-template-columns: minmax(180px, 260px) minmax(0, 1fr);
  gap: 12px;
  align-items: start;
}
.compact-form :deep(.el-form-item) { margin-bottom: 0; }
.compact-form :deep(.el-form-item__label) {
  margin-bottom: 4px;
  color: #64748b;
  font-size: 12px;
}
.add-file-strip {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(160px, 240px) auto;
  gap: 10px;
  align-items: center;
  padding: 10px 12px;
  border-radius: 18px;
  background: rgba(248, 250, 252, 0.72);
  border: 1px solid rgba(148, 163, 184, 0.16);
}
.skill-card {
  padding: 12px 4px;
  border: 0;
  border-bottom: 1px solid rgba(148, 163, 184, 0.22);
  border-radius: 0;
  background: transparent;
  box-shadow: none;
}
.skill-card:last-of-type { border-bottom: 0; }
.skill-card-head {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 16px;
  align-items: center;
}
.skill-title-wrap {
  display: grid;
  grid-template-columns: 28px minmax(0, 1fr);
  gap: 16px;
  align-items: center;
  min-width: 0;
}
.skill-main {
  display: grid;
  gap: 4px;
  min-width: 0;
}
.skill-heading {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
}
.skill-icon-wrap {
  width: 27px;
  height: 27px;
  min-width: 27px;
  min-height: 27px;
  border-radius: 9px;
  overflow: hidden;
  background: transparent;
  border: 0;
  box-shadow: none;
}
.skill-icon-wrap img { width: 100%; height: 100%; object-fit: contain; display: block; }
.skill-title-wrap h3 {
  flex: 0 1 auto;
  max-width: min(34vw, 240px);
  margin: 0;
  color: #0f172a;
  font-size: 15px;
  font-weight: 680;
  line-height: 1.2;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.skill-title-wrap p {
  flex: 1 1 auto;
  min-width: 0;
  margin: 0;
  color: #64748b;
  font-size: 12px;
  line-height: 1.35;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.skill-actions {
  display: flex;
  justify-content: flex-end;
  gap: 6px;
  flex-wrap: nowrap;
}
.skill-actions :deep(.el-button + .el-button) { margin-left: 0; }
.skill-icon-button {
  width: 28px;
  height: 28px;
  min-width: 28px;
  padding: 0;
  border-radius: 999px;
  border: 1px solid rgba(245, 158, 11, 0.22);
  background: rgba(245, 158, 11, 0.1);
  color: #b45309;
}
.skill-icon-button.ghost {
  border-color: rgba(148, 163, 184, 0.22);
  background: rgba(255, 255, 255, 0.72);
  color: #64748b;
}
.settings-icon-button.is-create-open :deep(.el-icon) {
  transform: rotate(45deg);
}
.settings-icon-button :deep(.el-icon) {
  transition: transform 0.22s ease;
}
.skill-icon-button.danger {
  border-color: rgba(239, 68, 68, 0.16);
  background: rgba(239, 68, 68, 0.07);
  color: #b91c1c;
}
.skill-meta {
  display: flex;
  align-items: center;
  gap: 5px;
  flex-wrap: wrap;
  color: #7b6859;
  font-size: 11px;
}
.skill-pill {
  display: inline-flex;
  align-items: center;
  min-height: 18px;
  padding: 0 7px;
  border-radius: 999px;
  background: rgba(245, 158, 11, 0.06);
  color: #8a6a45;
  font-size: 10.5px;
  line-height: 18px;
}
.detail-layout { display: grid; grid-template-columns: minmax(180px, 280px) minmax(0, 1fr); gap: 14px; }
.file-sidebar, .editor-pane {
  border-radius: 18px; border: 1px solid rgba(148, 163, 184, 0.16); background: rgba(255, 255, 255, 0.58); padding: 14px;
}
.file-sidebar-head, .editor-head {
  display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 14px;
}
.file-list { display: grid; gap: 6px; }
.file-item {
  display: flex; justify-content: space-between; gap: 12px; width: 100%;
  border: 0; border-bottom: 1px solid rgba(148, 163, 184, 0.12); background: transparent; border-radius: 0;
  padding: 9px 4px; cursor: pointer; color: #475569;
  text-align: left;
}
.file-item.active { color: #b45309; background: rgba(245, 158, 11, 0.06); border-radius: 12px; padding-inline: 10px; }
.file-delete { color: #c56f36; }
.readonly-alert { margin-bottom: 12px; }
.editor-pane :deep(.el-textarea__inner) {
  min-height: 420px !important;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.72);
  box-shadow: none;
}
.settings-panel-enter-active,
.settings-panel-leave-active {
  transition: opacity 0.2s ease, transform 0.22s ease, max-height 0.24s ease;
  overflow: hidden;
}
.settings-panel-enter-from,
.settings-panel-leave-to {
  opacity: 0;
  transform: translateY(-8px);
  max-height: 0;
}
.settings-panel-enter-to,
.settings-panel-leave-from {
  opacity: 1;
  transform: translateY(0);
  max-height: 720px;
}

@media (max-width: 960px) {
  .detail-layout { grid-template-columns: 1fr; }
  .skill-card-head { flex-direction: column; }
  .compact-form,
  .add-file-strip {
    grid-template-columns: 1fr;
  }
}
</style>
