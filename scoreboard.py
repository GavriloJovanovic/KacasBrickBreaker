"""
Scoreboard — read and write scores/highscore.txt.

File format (one entry per line):
    PlayerName:9999

Entries are always kept sorted descending by score, max 10 entries.
All writes are atomic (write temp → rename) to prevent corruption.
"""
import os

SCORES_PATH = os.path.join("scores", "highscore.txt")
MAX_ENTRIES = 10


# ------------------------------------------------------------------ #
# Read                                                                #
# ------------------------------------------------------------------ #

def load_scores() -> list[tuple[str, int]]:
    """
    Return a list of (name, score) tuples sorted highest-first.
    Returns an empty list if the file is missing or empty.
    """
    entries = []
    try:
        with open(SCORES_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                # Split on the LAST colon so names containing colons still work
                parts = line.rsplit(":", 1)
                if len(parts) == 2:
                    name, score_str = parts
                    try:
                        entries.append((name.strip(), int(score_str.strip())))
                    except ValueError:
                        pass   # ignore malformed lines
    except (FileNotFoundError, OSError):
        pass

    entries.sort(key=lambda e: e[1], reverse=True)
    return entries[:MAX_ENTRIES]


def qualifies(score: int) -> bool:
    """
    Return True if score earns a spot in the top-10 table.
    A score of 0 never qualifies.
    """
    if score <= 0:
        return False
    entries = load_scores()
    if len(entries) < MAX_ENTRIES:
        return True                          # table not full yet
    return score > entries[-1][1]            # beat the lowest entry


# ------------------------------------------------------------------ #
# Write                                                               #
# ------------------------------------------------------------------ #

def save_score(name: str, score: int) -> int:
    """
    Insert (name, score), re-sort, trim to top 10, persist.

    Returns the 0-based rank index of the new entry in the saved list
    (0 = highest score).  Used by the leaderboard to highlight the row.
    """
    entries = load_scores()
    entries.append((name, score))
    entries.sort(key=lambda e: e[1], reverse=True)
    entries = entries[:MAX_ENTRIES]

    # Find the rank of the newly added entry.
    # If there are ties we match on both name AND score (first occurrence).
    rank = 0
    for i, (n, s) in enumerate(entries):
        if n == name and s == score:
            rank = i
            break

    # Atomic write
    tmp = SCORES_PATH + ".tmp"
    try:
        os.makedirs("scores", exist_ok=True)
        with open(tmp, "w", encoding="utf-8") as f:
            for n, s in entries:
                f.write(f"{n}:{s}\n")
        os.replace(tmp, SCORES_PATH)
    except OSError:
        pass   # write failure is non-fatal; game continues

    return rank
