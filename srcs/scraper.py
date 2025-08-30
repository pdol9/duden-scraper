from duden import get
from bs4 import BeautifulSoup
import unicodedata

OUTPUT_FILE = "german_vocab.md"

def fetch_duden(word: str):

    # Normalize ß and other unicode
    word_normalized = unicodedata.normalize('NFC', word)
    entry = get(word_normalized)
    if entry is None:
        return None

    soup = entry.soup

    # Detailed definitions
    defs = [item.get_text(strip=True) for item in soup.select("div.enumeration__text") if item.get_text(strip=True)]

    # Beispiele (examples inside meanings)
    examples = [ex.get_text(strip=True) for ex in soup.select("ul.note__list li") if ex.get_text(strip=True)]

    # Wendungen, Redensarten, Sprichwörter
    wendungen = [w.get_text(strip=True) for w in soup.select("ul.infobox__examples li") if w.get_text(strip=True)]

    # Only keep meaning_overview if no detailed defs exist
    meaning_overview = None if defs else entry.meaning_overview

    return {
        "title": entry.title,
        "part_of_speech": entry.part_of_speech,
        "grammar": entry.grammar_overview,
        "word_separation": entry.word_separation,
        "meaning_overview": meaning_overview,
        "definitions": defs,
        "examples": examples,
        "wendungen": wendungen,
        "url": f"https://www.duden.de/rechtschreibung/{entry.urlname}" if entry.urlname else None,
    }

def save_entry(duden_data):
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        f.write(f"# {duden_data.get('title', 'Unknown')}\n\n")

        if duden_data.get("part_of_speech"):
            f.write(f"- Part of speech: {duden_data['part_of_speech']}\n")
        if duden_data.get("word_separation"):
            f.write(f"- Separation: {duden_data['word_separation']}\n")
        if duden_data.get("grammar"):
            f.write(f"- Grammar: {duden_data['grammar']}\n")

        f.write("\n")

        # Definitions
        defs = duden_data.get("definitions", [])
        if defs:
            f.write("**Definitions**\n")
            for i, definition in enumerate(defs, 1):
                f.write(f"{i}. {definition}\n")
            f.write("\n")
        elif duden_data.get("meaning_overview"):  # only if no defs
            f.write("**Meaning Overview**\n")
            f.write(duden_data["meaning_overview"] + "\n\n")

        # Examples
        examples = duden_data.get("examples", [])
        if examples:
            f.write("**Examples**\n")
            for ex in examples:
                f.write(f"- {ex}\n")
            f.write("\n")

        # Wendungen
        wendungen = duden_data.get("wendungen", [])
        if wendungen:
            f.write("**Wendungen / Phrases**\n")
            for w in wendungen:
                f.write(f"- {w}\n")
            f.write("\n")

        # Source URL
        if duden_data.get("url"):
            f.write(f"[Duden entry]({duden_data['url']})\n\n")

        f.write("---\n\n")

def main():
    print("German Duden Dictionary Scraper (type 'q' to quit)")
    
    while True:
        word = input("Enter German word: ").strip()
        if word.lower() == "q":
            print("Exiting program.")
            break
        if not word:
            print("Please enter a valid word.")
            continue

        try:
            data = fetch_duden(word)
            if data:
                save_entry(data)
                print(f"Saved entry for '{word}':")
                print(f"Title: {data['title']}")
                print(f"Part of Speech: {data['part_of_speech']}")
                print(f"Definitions: {len(data['definitions'])}")
                print(f"Examples: {len(data['examples'])}")
                print(f"Wendungen: {len(data['wendungen'])}")
                print(f"URL: {data['url']}")
            else:
                print(f"No Duden entry found for '{word}'")
        except Exception as e:
            print(f"Error fetching '{word}': {e}")

if __name__ == "__main__":
    main()
