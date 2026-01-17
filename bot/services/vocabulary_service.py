from services import user_service

def save_last_word(user_id: int) -> bool:
    last_word = user_service.get_last_generated_word(user_id)
    if not last_word:
        return False
    
    user_service.add_word_to_vocabulary(user_id, last_word)
    return True

def format_vocabulary_list(user_id: int) -> str:
    vocab = user_service.get_user_vocabulary(user_id)
    if not vocab:
        return "Your personal vocabulary is empty. Use /save after generating a Word of the Day to add it here."
    output = f"<b>My Vocabulary ({len(vocab)} words)</b>\n\n"
    for i, entry in enumerate(vocab[-5:]):
        lines = entry.split('\n')
        word_line = next((line for line in lines if "*Word:*" in line), "Unknown Word")
        output += f"{i+1}. {word_line.replace('*Word:*', '').strip()}\n"
        
    output += "\n<i>(Showing last 5 saved words)</i>"
    return output
