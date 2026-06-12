import asyncio
from types import SimpleNamespace


def test_list_host_skills_reads_skill_directory(monkeypatch, tmp_path):
    from agentchat.api.services.agent_skill import AgentSkillService

    root = tmp_path / "zuno-skills"
    skill_dir = root / "release-check"
    reference_dir = skill_dir / "reference"
    scripts_dir = skill_dir / "scripts"
    reference_dir.mkdir(parents=True)
    scripts_dir.mkdir(parents=True)

    (skill_dir / "SKILL.md").write_text(
        "---\nname: release-check\ndescription: Verify release readiness.\n---\n\nUse this skill.",
        encoding="utf-8",
    )
    (reference_dir / "checklist.md").write_text("Checklist content", encoding="utf-8")
    (scripts_dir / "verify.ps1").write_text("Write-Output 'ok'", encoding="utf-8")

    monkeypatch.setenv(AgentSkillService.HOST_SKILL_ROOT_ENV, str(root))

    skills = AgentSkillService.list_host_skills()

    assert len(skills) == 1
    skill = skills[0]
    assert skill.id == "host-skill-release-check"
    assert skill.name == "release-check"
    assert skill.source == "host"
    assert skill.is_readonly is True

    file_names = [item["name"] for item in skill.folder["folder"]]
    assert "SKILL.md" in file_names
    assert "reference" in file_names
    assert "scripts" in file_names


def test_get_agent_skills_by_ids_includes_host_skills(monkeypatch, tmp_path):
    from agentchat.api.services.agent_skill import AgentSkillService

    root = tmp_path / "zuno-skills"
    skill_dir = root / "host-one"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "---\nname: host-one\ndescription: Host skill.\n---\n",
        encoding="utf-8",
    )

    monkeypatch.setenv(AgentSkillService.HOST_SKILL_ROOT_ENV, str(root))

    async def fake_db_skills(_ids):
        return [SimpleNamespace(id="db-skill", name="db-skill")]

    monkeypatch.setattr(
        "agentchat.api.services.agent_skill.AgentSkillDao.get_agent_skills_by_ids",
        fake_db_skills,
    )

    results = asyncio.run(
        AgentSkillService.get_agent_skills_by_ids(["host-skill-host-one", "db-skill"])
    )

    assert [skill.id for skill in results] == ["host-skill-host-one", "db-skill"]


def test_readonly_skill_operations_reject_host_skill():
    from agentchat.api.services.agent_skill import AgentSkillService

    assert AgentSkillService.is_readonly_skill_id("host-skill-demo") is True
