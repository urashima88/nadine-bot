from typing import Dict, List

admin_user_data_show_sessions: Dict[int, Dict] = {}

def admin_user_data_show_get_session(user_id: int) -> Dict | None:
    return admin_user_data_show_sessions.get(user_id)

def admin_user_data_show_set_session(user_id: int, users: List[Dict]):
    admin_user_data_show_sessions[user_id] = {
        'users': users,
        'total': len(users),
        'sent': 0,
    }
    
def admin_user_data_show_delete_session(user_id: int):
    if user_id in admin_user_data_show_sessions:
        del admin_user_data_show_sessions[user_id]