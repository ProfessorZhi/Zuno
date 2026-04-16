<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Delete, DocumentAdd, Edit, Plus, Refresh } from '@element-plus/icons-vue'
import skillIcon from '../../assets/skill.svg'
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

type SkillFileEntry = {
  path: string
  name: string
  content: string
}

const loading = ref(false)
const keyword = ref('')
const skills = ref<AgentSkill[]>([])

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

const currentSkillReadonly = computed(() => Boolean(currentSkill.value?.is_system))

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
  createForm.value = { name: '', description: '' }
  createDialogVisible.value = true
}

const handleCreateSkill = async () => {
  if (!createForm.value.name.trim() || !createForm.value.description.trim()) {
    ElMessage.warning('请先填写完整的 Skill 名称和描述')
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
  if (skill.is_system) {
    ElMessage.info('系统 Skill 为只读内置能力，不能删除')
    return
  }

  try {
    await ElMessageBox.confirm(`删除后，Skill “${skill.name}” 和其文件都会被清空。`, '确认删除 Skill', {
      confirmButtonText: '确认删除',
      cancelButtonText: '取消',
      type: 'warning',
    })
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
  currentSkill.value = skill
  const files = flattenFiles(skill.folder)
  selectedFile.value = files[0] || null
  fileContent.value = files[0]?.content || ''
  detailDialogVisible.value = true
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
  if (currentSkill.value.is_system) {
    ElMessage.info('系统 Skill 为只读内置能力，不能修改文件')
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
  if (currentSkill.value.is_system) {
    ElMessage.info('系统 Skill 为只读内置能力，不能新增文件')
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
  if (currentSkill.value.is_system) {
    ElMessage.info('系统 Skill 为只读内置能力，不能删除文件')
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
        <div class="eyebrow">SKILL LIBRARY</div>
        <h1>Skill 管理</h1>
        <p>Skill 用来沉淀可复用的方法、模板和工作流。系统 Skill 为内置只读能力，你创建的 Skill 可以继续编辑和扩展。</p>
      </div>
      <div class="hero-actions">
        <el-button :icon="Refresh" @click="fetchSkills">刷新</el-button>
        <el-button type="primary" :icon="Plus" @click="openCreateDialog">新建 Skill</el-button>
      </div>
    </section>

    <section class="toolbar-card">
      <el-input v-model="keyword" placeholder="搜索 Skill 名称或描述" clearable />
    </section>

    <section class="skill-grid" v-loading="loading">
      <article v-for="skill in visibleSkills" :key="skill.id" class="skill-card">
        <div class="skill-card-head">
          <div class="skill-title-wrap">
            <div class="skill-icon-wrap"><img :src="skillIcon" :alt="skill.name" /></div>
            <div>
              <div class="skill-heading">
                <h3>{{ skill.name }}</h3>
                <el-tag size="small" :type="skill.is_system ? 'warning' : 'info'">
                  {{ skill.is_system ? '系统' : '我的' }}
                </el-tag>
              </div>
              <p>{{ skill.description || '暂无说明' }}</p>
            </div>
          </div>
          <div class="skill-actions">
            <el-button size="small" type="primary" :icon="Edit" @click="openDetailDialog(skill)">
              {{ skill.is_system ? '查看详情' : '编辑文件' }}
            </el-button>
            <el-button
              v-if="!skill.is_system"
              size="small"
              type="danger"
              :icon="Delete"
              @click="handleDeleteSkill(skill)"
            >
              删除
            </el-button>
          </div>
        </div>
        <div class="skill-meta">
          <span>创建时间：{{ skill.create_time || '--' }}</span>
          <span>更新时间：{{ skill.update_time || skill.create_time || '--' }}</span>
        </div>
      </article>
      <el-empty v-if="!visibleSkills.length && !loading" description="暂无 Skill" />
    </section>

    <el-dialog v-model="createDialogVisible" title="新建 Skill" width="560px">
      <el-form label-position="top">
        <el-form-item label="Skill 名称">
          <el-input v-model="createForm.name" placeholder="例如：发布检查助手" />
        </el-form-item>
        <el-form-item label="Skill 描述">
          <el-input
            v-model="createForm.description"
            type="textarea"
            :rows="4"
            placeholder="说明这个 Skill 适合什么场景、能解决什么问题。"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="createLoading" @click="handleCreateSkill">创建</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="detailDialogVisible"
      width="1120px"
      :title="currentSkill ? `${currentSkill.name} · 文件管理` : '文件管理'"
    >
      <div class="detail-layout">
        <aside class="file-sidebar">
          <div class="file-sidebar-head">
            <strong>文件列表</strong>
            <el-button
              size="small"
              :icon="DocumentAdd"
              :disabled="currentSkillReadonly"
              @click="openAddFileDialog"
            >
              新增文件
            </el-button>
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
            <el-button
              type="primary"
              :loading="savingFile"
              :disabled="currentSkillReadonly || !selectedFile"
              @click="handleSaveFile"
            >
              保存文件
            </el-button>
          </div>
          <el-alert
            v-if="currentSkillReadonly"
            type="info"
            :closable="false"
            title="系统 Skill 为内置只读能力，可查看内容，但不能直接修改。"
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
    </el-dialog>

    <el-dialog v-model="addFileDialogVisible" title="新增文件" width="560px">
      <el-form label-position="top">
        <el-form-item label="目录">
          <el-input v-model="addFileForm.path" placeholder="例如：/my-skill/reference" />
        </el-form-item>
        <el-form-item label="文件名">
          <el-input v-model="addFileForm.name" placeholder="例如：README.md" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addFileDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="addFileLoading" @click="handleAddFile">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped lang="scss">
.skill-page { display: grid; gap: 20px; padding: 24px; }
.hero-card, .toolbar-card, .skill-card {
  border-radius: 24px;
  border: 1px solid rgba(214, 132, 70, 0.12);
  background: rgba(255, 252, 248, 0.94);
  box-shadow: 0 18px 36px rgba(120, 80, 42, 0.08);
}
.hero-card, .toolbar-card { padding: 24px 26px; }
.eyebrow { font-size: 12px; letter-spacing: 0.16em; color: #be6d38; }
.hero-card h1 { margin: 12px 0 10px; font-size: 32px; color: #2f241b; }
.hero-card p { margin: 0; color: #786656; line-height: 1.8; }
.hero-actions { margin-top: 18px; display: flex; gap: 12px; flex-wrap: wrap; }
.skill-grid { display: grid; gap: 16px; }
.skill-card { padding: 20px 22px; }
.skill-card-head { display: flex; justify-content: space-between; gap: 16px; align-items: flex-start; }
.skill-title-wrap { display: flex; gap: 14px; }
.skill-heading { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.skill-icon-wrap {
  width: 56px; height: 56px; border-radius: 18px; overflow: hidden; background: #f8efe4;
  border: 1px solid rgba(214, 132, 70, 0.14);
}
.skill-icon-wrap img { width: 100%; height: 100%; object-fit: cover; }
.skill-title-wrap h3 { margin: 0; color: #32261d; }
.skill-title-wrap p, .skill-meta { color: #7b6859; }
.skill-actions { display: flex; gap: 8px; flex-wrap: wrap; }
.skill-meta { margin-top: 14px; display: flex; gap: 20px; flex-wrap: wrap; font-size: 13px; }
.detail-layout { display: grid; grid-template-columns: 320px minmax(0, 1fr); gap: 18px; }
.file-sidebar, .editor-pane {
  border-radius: 18px; border: 1px solid rgba(214, 132, 70, 0.12); background: #fffaf4; padding: 16px;
}
.file-sidebar-head, .editor-head {
  display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 14px;
}
.file-list { display: grid; gap: 8px; }
.file-item {
  display: flex; justify-content: space-between; gap: 12px; width: 100%;
  border: 1px solid rgba(214, 132, 70, 0.1); background: #fff; border-radius: 14px;
  padding: 12px 14px; cursor: pointer; color: #4a392c;
}
.file-item.active { border-color: rgba(198, 112, 52, 0.36); background: #fff5ea; }
.file-delete { color: #c56f36; }
.readonly-alert { margin-bottom: 12px; }

@media (max-width: 960px) {
  .detail-layout { grid-template-columns: 1fr; }
  .skill-card-head { flex-direction: column; }
}
</style>
