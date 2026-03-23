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

    # Case 1 + 2 (enumeration)
    for li in soup.select("#bedeutungen li.enumeration__item, #bedeutungen li.enumeration__sub-item"):
        text_el = li.select_one(".enumeration__text")
        if not text_el:
            continue

        meaning = text_el.get_text(strip=True).replace("\xad", "")

        examples = []
        idioms = []

        for dl in li.select("dl.note"):
            title = dl.select_one(".note__title")
            if not title:
                continue

            title_text = title.get_text(strip=True)

            items = [li.get_text(strip=True) for li in dl.select("ul.note__list li")]

            if "Beispiele" in title_text:
                examples.extend(items)
            elif "Wendungen" in title_text:
                idioms.extend(items)

        meanings.append({
            "meaning": meaning,
            "examples": examples,
            "idioms": idioms
        })


    # Case 3 (single meaning)
    if not meanings:
        container = soup.select_one("#bedeutung")

        if container:
            # meaning
            p = container.select_one("p")
            meaning = p.get_text(strip=True).replace("\xad", "") if p else ""

            examples = []
            idioms = []

            for dl in container.select("dl.note"):
                title = dl.select_one(".note__title")
                if not title:
                    continue

                title_text = title.get_text(strip=True)
                items = [li.get_text(strip=True) for li in dl.select("ul.note__list li")]

                if "Beispiele" in title_text:
                    examples.extend(items)
                elif "Wendungen" in title_text:
                    idioms.extend(items)

            meanings.append({
                "meaning": meaning,
                "examples": examples,
                "idioms": idioms
            })

    result["meanings"] = meanings

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

        if m["idioms"]:
            lines.append("Wendungen, Redensarten, Sprichwörter")
            for idiom in m["idioms"]:
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
