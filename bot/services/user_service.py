import json
import os
from typing import Optional, Dict, List
from datetime import datetime

USERS_FILE = 'users.json'

def _load_users() -> Dict[str, dict]:
    if not os.path.exists(USERS_FILE):
        return {}
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def _save_users(users: Dict[str, dict]):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

def get_user_level(user_id: int) -> Optional[str]:
    users = _load_users()
    user_str = str(user_id)
    return users.get(user_str, {}).get('level')

def set_user_level(user_id: int, level: str):
    users = _load_users()
    user_str = str(user_id)
    if user_str not in users:
        users[user_str] = {}
    users[user_str]['level'] = level
    _save_users(users)

def set_pending_quiz(user_id: int, quiz_data: Optional[dict]):
    users = _load_users()
    user_str = str(user_id)
    if user_str not in users:
        users[user_str] = {}
    users[user_str]['pending_quiz'] = quiz_data
    _save_users(users)

def get_pending_quiz(user_id: int) -> Optional[dict]:
    users = _load_users()
    user_str = str(user_id)
    return users.get(user_str, {}).get('pending_quiz')

def set_active_scenario(user_id: int, scenario_context: Optional[dict]):
    users = _load_users()
    user_str = str(user_id)
    if user_str not in users:
        users[user_str] = {}
    users[user_str]['active_scenario'] = scenario_context
    _save_users(users)

def get_active_scenario(user_id: int) -> Optional[dict]:
    users = _load_users()
    user_str = str(user_id)
    return users.get(user_str, {}).get('active_scenario')


def set_last_generated_word(user_id: int, word_data: str):
    users = _load_users()
    user_str = str(user_id)
    if user_str not in users:
        users[user_str] = {}
    users[user_str]['last_word'] = word_data
    _save_users(users)

def get_last_generated_word(user_id: int) -> Optional[str]:
    users = _load_users()
    return users.get(str(user_id), {}).get('last_word')

def add_word_to_vocabulary(user_id: int, word_content: str):
    users = _load_users()
    user_str = str(user_id)
    if user_str not in users:
        users[user_str] = {}
    
    vocab = users[user_str].get('vocabulary', [])
    if word_content not in vocab:
        vocab.append(word_content)
        users[user_str]['vocabulary'] = vocab
        _save_users(users)

def get_user_vocabulary(user_id: int) -> List[str]:
    users = _load_users()
    return users.get(str(user_id), {}).get('vocabulary', [])


def update_xp(user_id: int, amount: int):
    users = _load_users()
    user_str = str(user_id)
    if user_str not in users:
        users[user_str] = {}
    
    current_xp = users[user_str].get('xp', 0)
    users[user_str]['xp'] = current_xp + amount
    _save_users(users)

def get_user_stats(user_id: int) -> Dict:
    users = _load_users()
    data = users.get(str(user_id), {})
    return {
        "xp": data.get('xp', 0),
        "streak": data.get('streak', 0),
        "vocab_count": len(data.get('vocabulary', []))
    }
