from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_conversation_history_page_uses_workspace_sessions_and_timestamps():
    workspace_page = (REPO_ROOT / 'apps/web/src/pages/workspace/workspace.vue').read_text(encoding='utf-8')
    archive_page = (REPO_ROOT / 'apps/web/src/pages/account/conversation-archive.vue').read_text(encoding='utf-8')
    brand_utils = (REPO_ROOT / 'apps/web/src/utils/brand.ts').read_text(encoding='utf-8')

    assert 'getWorkspaceSessionsAPI' in workspace_page
    assert 'workspace-session-updated' in workspace_page
    assert 'getWorkspaceSessionsAPI' in archive_page
    assert 'messageCount' in archive_page
    assert 'createTime' in archive_page
    assert 'zuno-favicon.svg' in brand_utils


def test_auth_and_profile_pages_stop_using_legacy_zuno_assets():
    auth_conversation = (REPO_ROOT / 'apps/web/src/pages/login/AuthConversation.vue').read_text(encoding='utf-8')
    login_page = (REPO_ROOT / 'apps/web/src/pages/login/login.vue').read_text(encoding='utf-8')
    register_page = (REPO_ROOT / 'apps/web/src/pages/login/register.vue').read_text(encoding='utf-8')
    profile_page = (REPO_ROOT / 'apps/web/src/pages/profile/profile.vue').read_text(encoding='utf-8')
    index_page = (REPO_ROOT / 'apps/web/src/pages/index.vue').read_text(encoding='utf-8')

    assert 'zuno-mark.svg' not in auth_conversation
    assert 'zuno-avatar.svg' not in auth_conversation
    assert 'robot1.svg' not in profile_page
    assert 'robot2.svg' not in profile_page
    assert 'zuno-avatar.svg' not in profile_page
    assert 'zuno-mark.svg' not in index_page
    assert '../../utils/brand' in auth_conversation
    assert 'AuthConversation' in login_page
    assert 'AuthConversation' in register_page
    assert '../../utils/user-avatars' in profile_page
    assert '../utils/brand' in index_page


def test_dialog_updates_touch_update_time_instead_of_create_time():
    dialog_dao = (
        REPO_ROOT / 'src/backend/zuno/platform/database/dao/dialog.py'
    ).read_text(encoding='utf-8')

    assert 'values(update_time=' in dialog_dao
    assert 'values(create_time=' not in dialog_dao


def test_mysql_to_postgres_migration_script_exists_for_legacy_data_recovery():
    migration_script = REPO_ROOT / 'tools/migrations/migrate_mysql_to_postgres.py'
    assert migration_script.exists(), 'expected legacy migration script to exist'
    script_text = migration_script.read_text(encoding='utf-8')
    assert 'mysql' in script_text.lower()
    assert 'postgres' in script_text.lower()
    assert 'bool(' in script_text
