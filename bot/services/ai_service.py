import os
import logging
import json
import random
from openai import OpenAI

logger = logging.getLogger(__name__)

api_key = os.getenv("OPENAI_API_KEY")
groq_api_key = os.getenv("GROQ_API_KEY")

if groq_api_key:
    MODEL_NAME = "llama-3.3-70b-versatile"
    client = OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=groq_api_key
    )
elif api_key:
    MODEL_NAME = "gpt-4o"
    client = OpenAI(api_key=api_key)
else:
    client = None
    MODEL_NAME = None
    logger.error("No API key found (OPENAI_API_KEY or GROQ_API_KEY). Bot will not be able to generate content.")

PEYMAR_SYSTEM_INSTRUCTION = (
    "You are Peymar, a premium and highly professional English mentor. "
    "Your goal is to provide elite-level English practice that feels academic yet accessible. "
    "Rules for interaction:\n"
    "1. Minimalist Aesthetic: Use clear, structured formatting (Markdown). Avoid excessive emojis or 'chatty' fillers.\n"
    "2. Academic Authority: Use sophisticated vocabulary in your explanations where appropriate for the user's level.\n"
    "3. Constructive Precision: Corrections should be direct, logical, and encouraging without being overly sentimental.\n"
    "4. No Jargon/Jokes: Stay focused on education. Maintain a neutral, professional tone at all times."
)

LEVEL_DESCRIPTIONS = {
    "A1": "Beginner (CEFR)",
    "A2": "Elementary (CEFR)",
    "B1": "Intermediate (CEFR)",
    "B2": "Upper Intermediate (CEFR)",
    "C1": "Advanced (CEFR)",
    "C2": "Proficiency (CEFR)"
}

def generate_word_of_the_day(level: str) -> str:
    try:
        seed = random.randint(1, 100000)
        prompt = (
            f"Select a unique, sophisticated and relevant word for an English learner at level {level}. "
            f"Contextual variety seed: {seed}. "
            "Format the response perfectly for Telegram using Markdown:\n"
            "*Word:* [Word]\n"
            "*Phonetic:* [Transcription]\n"
            "*Definition:* [Level-appropriate definition]\n"
            "*Context:* [Single high-quality example sentence]"
        )
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": PEYMAR_SYSTEM_INSTRUCTION},
                {"role": "user", "content": prompt}
            ],
            temperature=1.0
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error in generate_word_of_the_day: {e}")
        return "I apologize, but I am unable to generate a Word of the Day at this moment."

import json

def generate_quiz(level: str) -> dict:
    try:
        seed = random.randint(1, 100000)
        prompt = (
            f"Create a unique and challenging multiple-choice English quiz question for level {level}. "
            f"Contextual seed for variety: {seed}. "
            "Return ONLY a JSON object with keys: 'question', 'options', 'correct_answer' (A/B/C/D), 'explanation'. "
            "CRITICAL: Do NOT include the answer or hints in the 'question' field. "
            "The 'options' must be a list of 4 choices, each formatted with its letter (e.g., 'A) text')."
        )
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": f"{PEYMAR_SYSTEM_INSTRUCTION}\nAlways respond in valid JSON format."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=1.0
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        logger.error(f"Error in generate_quiz: {e}")
        return {}

def correct_sentence(text: str, level: str) -> str:
    try:
        seed = random.randint(1, 100000)
        prompt = (
            f"User level: {level}. Original sentence: '{text}'. "
            f"Variety seed: {seed}. "
            "Task: Correct the sentence grammar/vocabulary and provide a brief linguistic explanation. "
            "CRITICAL: Do NOT add introductory phrases like 'That's great' or 'Here is the correction'. "
            "Just provide the analysis directly in the requested format.\n"
            "Format:\n*Correction:* [Corrected sentence]\n*Explanation:* [Professional analysis]"
        )
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": PEYMAR_SYSTEM_INSTRUCTION},
                {"role": "user", "content": prompt}
            ],
            temperature=1.0
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error in correct_sentence: {e}")
        return "I encountered an error while analyzing your text."

def generate_scenario_response(scenario_name: str, history: list, user_input: str, level: str) -> str:
    try:
        messages = [
            {"role": "system", "content": f"{PEYMAR_SYSTEM_INSTRUCTION}\nYou are roleplaying in the scenario: '{scenario_name}'. Keep the conversation realistic for an English learner at level {level}. provide the response in a natural way, and then if the user makes a mistake, add a brief note about it at the end."}
        ]
        messages.extend(history)
        messages.append({"role": "user", "content": user_input})

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=1.0
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error in generate_scenario_response: {e}")
        return "The simulation has encountered an error. Please try again."
