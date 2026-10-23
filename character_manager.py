import re
import sys
import threading

import g4f

from engiene import load_json, save_json, to_num
from paths import APEX_FILE, CHARACTERS_FILE

VALID_PUBLISHERS = ["DC Comics", "Marvel Comics", "Dark Horse Comics", "Star Wars", "Shueisha", "Hasbro"]
PHYSICAL_STATS = ("strength", "durability", "power")
AI_TIMEOUT = 45  # seconds per AI request


def draw_progress_bar(current, total, status_msg=""):
    total = max(total, 1)
    bar_length = 30
    progress = current / total
    block = int(round(bar_length * progress))
    text = f"\r[{'#' * block}{'-' * (bar_length - block)}] {int(progress * 100)}% | {status_msg[:50]:<50}"
    sys.stdout.write(text)
    sys.stdout.flush()


def _ask_ai(prompt):
    """Ask the AI a question. Returns text, or None on error/timeout (never hangs)."""
    box = {}

    def worker():
        try:
            box["reply"] = g4f.ChatCompletion.create(
                model="gpt-4o", messages=[{"role": "user", "content": prompt}]
            )
        except Exception:
            box["reply"] = None

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()
    thread.join(AI_TIMEOUT)
    reply = box.get("reply")
    return str(reply).strip() if reply else None


def ask_publisher(name, full_name="", alter_egos=""):
    identity = name
    if full_name and full_name != "-" and full_name.lower() != name.lower():
        identity += f" (Real Name: {full_name})"
    if alter_egos and "no alter egos found" not in alter_egos.lower() and alter_egos != "-":
        identity += f" / {alter_egos}"

    reply = _ask_ai(
        f"Which publisher owns the character: {identity}?\n"
        f"Choose EXACTLY and ONLY from this list: {', '.join(VALID_PUBLISHERS)}.\n"
        f"Do not include punctuation, explanations, or markdown formatting."
    )
    if not reply:
        return None
    for pub in VALID_PUBLISHERS:
        if reply.strip().strip(".").lower() == pub.lower():
            return pub
    return None


def _fallback_apex(data):
    """Strongest character by the API's own physical stats (used if the AI fails)."""
    def raw_power(info):
        stats = info.get("powerstats_original") or info.get("powerstats") or {}
        return sum(to_num(stats.get(s)) for s in PHYSICAL_STATS)

    return max(data.values(), key=raw_power).get("name")


def get_apex(data):
    """The 100-point reference character. Chosen once, then remembered."""
    names = [info.get("name") for info in data.values() if info.get("name")]
    saved = load_json(APEX_FILE, {}).get("name")
    if saved in names:
        return saved

    apex = None
    if len(names) > 1:
        reply = _ask_ai(
            f"From this list of characters: [{', '.join(names)}], who is the absolute strongest "
            f"in terms of raw physical power, cosmic capability, or tier scaling?\n"
            f"Respond with ONLY the exact name from the list. No punctuation, no explanations."
        )
        if reply:
            apex = next((n for n in names if n.lower() == reply.strip().strip(".").lower()), None)
    if apex is None:
        apex = _fallback_apex(data)
    save_json(APEX_FILE, {"name": apex})
    return apex


def ask_relative_score(name, apex):
    reply = _ask_ai(
        f"If the character '{apex}' represents a perfect 100 in physical strength, durability, and power, "
        f"what score from 1 to 100 would '{name}' be by comparison?\n"
        f"Consider their canon comic/anime feats. Respond with ONLY a single integer number between 1 and 100. "
        f"Do not include text, percent signs, or formatting."
    )
    match = re.search(r"\d+", reply or "")
    if not match:
        return None  # keep the original stats instead of inventing a number
    return max(1, min(100, int(match.group())))


def update_characters():
    """Calibrate characters that have not been processed yet (new ones only).

    - fills in a missing/unknown publisher
    - rescales strength/durability/power relative to the strongest character
      (the API's original numbers are kept under "powerstats_original")
    Characters the AI could not rate stay pending and are retried next time.
    """
    data = load_json(CHARACTERS_FILE, {})
    pending = [cid for cid, info in data.items() if isinstance(info, dict) and not info.get("cb_processed")]
    if not pending:
        return

    print(f"Calibrating {len(pending)} new character(s) - this needs an internet connection...")
    try:
        # Phase 1: names + publishers
        for idx, cid in enumerate(pending, 1):
            info = data[cid]
            bio = info.setdefault("biography", {})
            name = info.get("name", "Unknown Character")
            draw_progress_bar(idx, len(pending), f"Verifying identity: {name}")

            full_name = bio.get("full-name") or ""
            if "Batman" in name and "(" not in name and full_name and full_name != "-":
                info["name"] = f"Batman ({full_name.split(',')[0]})"
                name = info["name"]

            if bio.get("publisher") not in VALID_PUBLISHERS:
                alter = bio.get("alter-egos") or ""
                publisher = ask_publisher(name, full_name, alter if isinstance(alter, str) else "")
                if publisher:
                    bio["publisher"] = publisher
        sys.stdout.write("\n")

        # Phase 2: power calibration
        apex = get_apex(data)
        for idx, cid in enumerate(pending, 1):
            info = data[cid]
            name = info.get("name", "Unknown Character")
            draw_progress_bar(idx, len(pending), f"Rating power: {name}")

            stats = info.get("powerstats")
            if not isinstance(stats, dict) or not stats:
                info["cb_processed"] = True
                continue

            score = 100 if name == apex else ask_relative_score(name, apex)
            if score is None:
                continue

            info.setdefault("powerstats_original", dict(stats))
            for stat in PHYSICAL_STATS:
                stats[stat] = str(score)
            info["cb_processed"] = True
        sys.stdout.write("\n")
    finally:
        save_json(CHARACTERS_FILE, data)  # keep progress even on Ctrl-C

    left = sum(1 for cid in pending if not data[cid].get("cb_processed"))
    if left:
        print(f"{left} character(s) could not be rated right now and will be retried later.")
    else:
        print("Calibration complete.")


if __name__ == "__main__":
    update_characters()
