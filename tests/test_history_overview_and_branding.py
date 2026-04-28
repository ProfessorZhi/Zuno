from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_conversation_history_page_uses_workspace_sessions_and_timestamps():
    conversation_page = (REPO_ROOT / 'src/frontend/src/pages/conversation/conversation.vue').read_text(encoding='utf-8')
    history_card = (REPO_ROOT / 'src/frontend/src/components/historyCard/histortCard.vue').read_text(encoding='utf-8')
    brand_utils = (REPO_ROOT / 'src/frontend/src/utils/brand.ts').read_text(encoding='utf-8')

    assert 'getWorkspaceSessionsAPI' in conversation_page
    assert 'sourceType' in conversation_page
    assert 'updatedTime' in conversation_page
    assert 'workspace-session-updated' in conversation_page
    assert 'failedSources' in conversation_page
    assert 'absoluteTime' in history_card
    assert 'robot.svg' in brand_utils


def test_auth_and_profile_pages_stop_using_legacy_zuno_assets():
    login_page = (REPO_ROOT / 'src/frontend/src/pages/login/login.vue').read_text(encoding='utf-8')
    register_page = (REPO_ROOT / 'src/frontend/src/pages/login/register.vue').read_text(encoding='utf-8')
    profile_page = (REPO_ROOT / 'src/frontend/src/pages/profile/profile.vue').read_text(encoding='utf-8')
    index_page = (REPO_ROOT / 'src/frontend/src/pages/index.vue').read_text(encoding='utf-8')

    assert 'zuno-mark.svg' not in login_page
    assert 'zuno-avatar.svg' not in register_page
    assert 'robot1.svg' not in profile_page
    assert 'robot2.svg' not in profile_page
    assert 'zuno-avatar.svg' not in profile_page
    assert 'zuno-mark.svg' not in index_page
    assert '../../utils/brand' in login_page
    assert '../../utils/brand' in register_page
    assert '../../utils/brand' in profile_page
    assert '../utils/brand' in index_page


def test_dialog_updates_touch_update_time_instead_of_create_time():
    dialog_dao = (REPO_ROOT / 'src/backend/agentchat/database/dao/dialog.py').read_text(encoding='utf-8')

    assert 'values(update_time=' in dialog_dao
    assert 'values(create_time=' not in dialog_dao


def test_mysql_to_postgres_migration_script_exists_for_legacy_data_recovery():
    migration_script = REPO_ROOT / 'scripts/migrate_mysql_to_postgres.py'
    assert migration_script.exists(), 'expected legacy migration script to exist'
    script_text = migration_script.read_text(encoding='utf-8')
    assert 'mysql' in script_text.lower()
    assert 'postgres' in script_text.lower()
    assert 'bool(' in script_text
