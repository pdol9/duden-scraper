import requests
from bs4 import BeautifulSoup

OUTPUT_FILE = "saved_words.md"

BASE_URL = "https://www.duden.de/rechtschreibung/{}"

def standardize_query_word(word: str) -> str:
    """process German special characters for querying"""
    return (
        word.replace("ß", "sz")
            .replace("ä", "ae")
            .replace("ö", "oe")
            .replace("ü", "ue")
            .replace("Ä", "Ae")
            .replace("Ö", "Oe")
            .replace("Ü", "Ue")
    )


def validate_input_word(word: str) -> BeautifulSoup:
    """Request Duden entry page and return parsed HTML (BeautifulSoup) or None if request fails."""
    url = BASE_URL.format(word)
    r = requests.get(url)
    if r.status_code != 200:
        return None
    soup = BeautifulSoup(r.text, "html.parser")
    return soup

# 

def fetch_duden_word(word: str):
    """ retrieve meanings and use cases of a German word """
    result = {}
    soup = validate_input_word(word)
    if not soup:
        return result

    # Title (Straße, die)
    title = soup.find("h1")
    raw = title.get_text(strip=True) if title else ""
    cleaned = raw.replace("\xad", "").replace(",", ", ")
    result["title"] = cleaned

    # Bedeutungen
    meanings = []
    for li in soup.select("ol.enumeration li.enumeration__item"):
        meaning_text = li.find("div", class_="enumeration__text")
        meaning = meaning_text.get_text(strip=True) if meaning_text else ""

        # Examples
        examples = []
        for ex in li.select("ul.note__list li"):
            examples.append(ex.get_text(strip=True))

        meanings.append({
            "meaning": meaning,
            "examples": examples
        })

    result["meanings"] = meanings

    # Wendungen (idioms)
    idioms = []
    for item in soup.select("section#redewendungen li"):
        idioms.append(item.get_text(strip=True))

    result["idioms"] = idioms

    return result

#########################################################################

def format_entry(data):
    lines = []
    lines.append(data["title"])
    lines.append("*" * 20)
    lines.append("Bedeutungen:")

    for i, m in enumerate(data["meanings"], 1):
        lines.append(f"{i} -> {m['meaning']}")
        if m["examples"]:
            lines.append("Beispiele")
            for ex in m["examples"]:
                lines.append(f"+ {ex}")

    if data["idioms"]:
        lines.append("Wendungen, Redensarten, Sprichwörter")
        for idiom in data["idioms"]:
            lines.append(f"- {idiom}")

    return "\n".join(lines)

##############################################################################


def main():
    print("German Duden Dictionary Scraper (type 'q' to quit)")
    try:
        while True:
            word = input("Enter German word: ").strip()

            if word.lower() == "q":
                print("Exiting program.")
                break

            if not word.isalpha():
                print("Please enter a (single) valid word.")
                continue

            normalized = standardize_query_word(word)
            data = fetch_duden_word(normalized)

            if not data:
                print(f"No entry found for '{word}'.")
                continue

            formatted = format_entry(data)

            print(formatted)  # show in terminal

            # append to file
            with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
                f.write(formatted + "\n\n")

    except Exception as e:
        print(f"Error fetching '{word}': {e}")

if __name__ == '__main__':
    main()
