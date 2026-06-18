import json
import g4f

# Fixed: Added quotes to make it a proper string
FILE_NAME = "characters.json" 
VALID_PUBLISHERS = ["DC Comics", "Marvel Comics", "Dark Horse Comics", "Star Wars", "Shueisha", "Hasbro"]

def characters_manager(character_name: str) -> str:
    """Uses G4F to classify a character into one of the allowed publishers."""
    allowed_list = ", ".join(VALID_PUBLISHERS)
    prompt = (
        f"Which publisher owns the character {character_name}?\n"
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
    except Exception as e:
        print(f"AI Error for {character_name}: {e}")
        return "Unknown"

def update_characters():
    try:
        with open(FILE_NAME, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: {FILE_NAME} not found.")
        return

    has_changes = False

    for char_id, char_info in data.items():
        if "biography" not in char_info:
            continue
        
        biography = char_info["biography"]
        current_publisher = biography.get("publisher", "")
        name = char_info.get("name", "Unknown Character")

        if current_publisher not in ["Marvel Comics", "DC Comics"]:
            print(f"Checking {name} (Current Publisher: {current_publisher})...")
            
            # Fixed: Changed from ask_ai_for_publisher to characters_manager
            new_publisher = characters_manager(name) 
            
            if new_publisher in VALID_PUBLISHERS:
                biography["publisher"] = new_publisher
                has_changes = True
                print(f"-> Updated {name} field to {new_publisher}")
            else:
                print(f"-> Skipped. AI returned invalid publisher: {new_publisher}")

    if has_changes:
        with open(FILE_NAME, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        print("\nChanges saved successfully.")
    else:
        print("\nNo changes needed. File was not rewritten.")

if __name__ == "__main__":
    update_characters()
