import json
import g4f
import hashlib
import os
import sys
import time

FILE_NAME = "characters.json" 
CACHE_FILE = ".hash_cache"
VALID_PUBLISHERS = ["DC Comics", "Marvel Comics", "Dark Horse Comics", "Star Wars", "Shueisha", "Hasbro"]

def get_file_hash(filepath: str) -> str:
    """Generates an MD5 hash of the file to check for structural updates."""
    if not os.path.exists(filepath):
        return ""
    hasher = hashlib.md5()
    with open(filepath, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def draw_progress_bar(current: int, total: int, status_msg: str = ""):
    """Renders a clean terminal loading bar tracking processing status."""
    bar_length = 30
    progress = current / total
    block = int(round(bar_length * progress))
    text = f"\r[{'#' * block}{'-' * (bar_length - block)}] {int(progress * 100)}% | {status_msg}"
    sys.stdout.write(text)
    sys.stdout.flush()

def ask_ai_for_ranking(character_pool_names: list) -> str:
    """Asks the AI to pick the single absolute strongest character from the current pool."""
    pool_str = ", ".join(character_pool_names)
    prompt = (
        f"From this list of characters: [{pool_str}], who is the absolute strongest "
        f"in terms of raw physical power, cosmic capability, or tier scaling?\n"
        f"Respond with ONLY the exact name from the list. No punctuation, no explanations."
    )
    try:
        response = g4f.ChatCompletion.create(
            model=g4f.models.gpt_4o,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.strip()
    except Exception:
        return character_pool_names[0]

def ask_ai_for_relative_score(char_name: str, apex_name: str) -> int:
    """Asks the AI to score a character's physical power relative to the apex character (0-100)."""
    prompt = (
        f"If the character '{apex_name}' represents a perfect 100 in physical strength, durability, and power, "
        f"what score from 1 to 100 would '{char_name}' be by comparison?\n"
        f"Consider their canon comic/anime feats. Respond with ONLY a single integer number between 1 and 100. "
        f"Do not include text, percent signs, or formatting."
    )
    try:
        response = g4f.ChatCompletion.create(
            model=g4f.models.gpt_4o,
            messages=[{"role": "user", "content": prompt}],
        )
        clean_num = "".join(filter(str.isdigit, response.strip()))
        return max(1, min(100, int(clean_num)))
    except Exception:
        return 50

def characters_manager(character_name: str, full_name: str = "", alter_egos: str = "") -> str:
    """Uses G4F to classify a character into one of the allowed publishers."""
    allowed_list = ", ".join(VALID_PUBLISHERS)
    identity_context = character_name
    if full_name and full_name != "-" and full_name.lower() != character_name.lower():
        identity_context += f" (Real Name: {full_name})"
    if alter_egos and "no alter egos found" not in alter_egos.lower() and alter_egos != "-":
        identity_context += f" / {alter_egos}"

    prompt = (
        f"Which publisher owns the character: {identity_context}?\n"
        f"Choose EXACTLY and ONLY from this list: {allowed_list}.\n"
        f"Do not include punctuation, explanations, or markdown formatting."
    )
    try:
        response = g4f.ChatCompletion.create(
            model=g4f.models.gpt_4o,
            messages=[{"role": "user", "content": prompt}],
        )
        cleaned_response = response.strip().title()
        for pub in VALID_PUBLISHERS:
            if cleaned_response == pub.title():
                return pub
        return "Unknown"
    except Exception:
        return "Unknown"

def update_characters():
    if not os.path.exists(FILE_NAME):
        print(f"Error: {FILE_NAME} not found.")
        return

    # Check if file has actually changed since last time
    current_hash = get_file_hash(FILE_NAME)
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as cf:
            saved_hash = cf.read().strip()
        if current_hash == saved_hash:
            print("⚡ No changes detected in characters.json since last run. Skipping execution.")
            return

    try:
        with open(FILE_NAME, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Failed to read JSON: {e}")
        return

    total_characters = len(data)
    if total_characters == 0:
        print("Dataset is empty.")
        return

    print("🚀 Initializing data processing sequence...")
    
    # Phase 1: Name fixing & Publisher checking
    for idx, (char_id, char_info) in enumerate(data.items(), 1):
        if "biography" not in char_info:
            continue
        
        biography = char_info["biography"]
        current_publisher = biography.get("publisher", "")
        name = char_info.get("name", "Unknown Character")
        full_name = biography.get("full-name", "")
        alter_egos = biography.get("alter-egos", "")

        # Draw progress for verification phase
        draw_progress_bar(idx, total_characters, f"Verifying Identity: {name}")

        if "Batman" in name and full_name and full_name != "-":
            clean_full_name = full_name.split(",")[0]
            char_info["name"] = f"Batman ({clean_full_name})"
            name = char_info["name"]

        if current_publisher not in VALID_PUBLISHERS:
            new_publisher = characters_manager(name, full_name, alter_egos) 
            if new_publisher in VALID_PUBLISHERS:
                biography["publisher"] = new_publisher
                
    sys.stdout.write("\n") # Break the line after tracking verification stage

    # Phase 2: Power Ranking Optimization
    character_names = [char_info.get("name") for char_info in data.values()]
    print("🤖 Consulting AI for Tier Ceiling...")
    apex_character = ask_ai_for_ranking(character_names)

    # Phase 3: Recalculate stats with Loading Bar Output
    for idx, (char_id, char_info) in enumerate(data.items(), 1):
        name = char_info.get("name")
        if "powerstats" not in char_info:
            continue

        # Display the custom message requested while executing AI tasks
        draw_progress_bar(idx, total_characters, f"Recalculating Character Power Stats ({name})")

        if name == apex_character:
            new_score = 100
        else:
            new_score = ask_ai_for_relative_score(name, apex_character)

        for stat in ["strength", "durability", "power"]:
            char_info["powerstats"][stat] = str(new_score)

    sys.stdout.write("\n\n✨ Recalculation Complete! Saving updates...")
    
    # Save modified data back to file
    with open(FILE_NAME, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    # Update cache hash so it skips next time unless edited
    new_hash = get_file_hash(FILE_NAME)
    with open(CACHE_FILE, 'w') as cf:
        cf.write(new_hash)
        
    print("\n💾 Dataset written to disk successfully.")
    os.system('cls' if os.name == 'nt' else 'clear')
if __name__ == "__main__":
    update_characters()