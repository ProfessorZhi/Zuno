# Interview And Study Hubs Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build two repo-local knowledge hubs, one for Zuno interview preparation and one for systematic study, seeded with the user's provided RAG materials plus repository-grounded guidance.

**Architecture:** Use two top-level folders, `interview_hub` and `study_hub`, each with focused Markdown documents. Keep the interview side outcome-oriented and evidence-backed, and keep the study side implementation-oriented and source-code-linked.

**Tech Stack:** Markdown, local repository evidence, extracted PDF/link/image notes

---

### Task 1: Create hub structure and landing pages

**Files:**
- Create: `interview_hub/README.md`
- Create: `study_hub/README.md`

- [ ] **Step 1: Create the interview hub landing page**
- [ ] **Step 2: Create the study hub landing page**
- [ ] **Step 3: Verify both files exist and describe scope clearly**

### Task 2: Ingest user-provided RAG materials into interview-ready notes

**Files:**
- Create: `interview_hub/00_语料整理/2026-04-17_牛客_RAG面试要点.md`
- Create: `interview_hub/00_语料整理/2026-04-17_AI应用工程师岗位JD_RAG重点.md`

- [ ] **Step 1: Convert the NowCoder link content into a concise structured note**
- [ ] **Step 2: Convert the screenshot JD content into a concise structured note**
- [ ] **Step 3: Verify each note distinguishes quoted source ideas from project-specific advice**

### Task 3: Build the Zuno interview track

**Files:**
- Create: `interview_hub/01_Zuno项目面试主线/Zuno项目主线与讲法.md`
- Create: `interview_hub/02_RAG高频问题/RAG高频问题与回答.md`
- Create: `interview_hub/02_RAG高频问题/RAG优化与评估.md`
- Create: `interview_hub/03_MCP_Skill_工具调用/MCP_Skill_工具调用怎么讲.md`
- Create: `interview_hub/04_项目验证结论/Zuno能力验证矩阵.md`

- [ ] **Step 1: Write the project mainline with RAG as the first-class story**
- [ ] **Step 2: Write the high-frequency RAG Q&A sheet**
- [ ] **Step 3: Write the optimization and evaluation sheet**
- [ ] **Step 4: Write the MCP / skill / tool-calling interview sheet**
- [ ] **Step 5: Write a verified-vs-pending capability matrix grounded in repo evidence**

### Task 4: Build the study track

**Files:**
- Create: `study_hub/00_学习地图/README.md`
- Create: `study_hub/01_FastAPI/FastAPI结合Zuno学习路径.md`
- Create: `study_hub/02_RAG原理与实现/RAG从原理到Zuno实现.md`
- Create: `study_hub/03_MCP与Skill/MCP与Skill从概念到代码.md`
- Create: `study_hub/04_Zuno源码拆解/Zuno后端关键链路.md`
- Create: `study_hub/05_实验与验证记录/实验清单.md`

- [ ] **Step 1: Write the study roadmap**
- [ ] **Step 2: Write the FastAPI learning guide linked to Zuno files**
- [ ] **Step 3: Write the RAG implementation study note**
- [ ] **Step 4: Write the MCP and skill study note**
- [ ] **Step 5: Write the backend source-map note**
- [ ] **Step 6: Write an experiment checklist for RAG / GraphRAG / MCP / skill / tools**

### Task 5: Cross-link and sanity check

**Files:**
- Modify: `interview_hub/README.md`
- Modify: `study_hub/README.md`

- [ ] **Step 1: Add cross-links between interview and study hubs**
- [ ] **Step 2: Verify file tree readability and naming consistency**
- [ ] **Step 3: Spot-check factual claims against repository evidence**
