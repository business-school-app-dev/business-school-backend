# Requires: requests, beautifulsoup4

from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs
import requests
import re
import json

START_URL = "https://www.rhsmith.umd.edu/events"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; SmithEventsScraper/1.0)"
}

def text(el):
    """Get clean text or ''."""
    if not el:
        return ""
    return " ".join(el.get_text(strip=True, separator=" ").split())

def get_date_time(div_with_br):
    """
    Example HTML:
      <div class="mb-2">
        Monday, November 10, 2025<br>
        5:00 PM EST
      </div>
    We split across <br> via stripped_strings.
    """
    if not div_with_br:
        return "", ""
    parts = list(div_with_br.stripped_strings)
    if len(parts) >= 2:
        return parts[0], parts[1]
    elif len(parts) == 1:
        return parts[0], ""
    return "", ""

def parse_max_page_from_pager(soup):
    """Find the largest ?page=N value from the pager."""
    pager = soup.select_one("nav.pager")
    if not pager:
        return 0
    max_page = 0
    for a in pager.select("a[href*='?page=']"):
        href = a.get("href", "")
        m = re.search(r"[?&]page=(\d+)", href)
        if m:
            n = int(m.group(1))
            if n > max_page:
                max_page = n
    return max_page

def _next_mb2_after(node):
    """Find the next sibling <div class='mb-2'> after the given node."""
    cur = node
    while cur is not None:
        cur = cur.find_next_sibling()
        if cur and cur.name == "div" and "mb-2" in (cur.get("class") or []):
            return cur
    return None

def scrape_events_one_page(url=START_URL):
    print(f"Scraping: {url}")
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # Main container (has dynamic js-view-dom-id + "row list-group")
    container = soup.select_one("div.row.list-group")
    if not container:
        print("No container found on page.")
        return [], soup

    # First .col-12 = search form, last .col-12 = pager
    cols = container.select(".col-12")
    if len(cols) <= 2:
        print("No events found on this page.")
        return [], soup

    events = []
    for card in cols[1:-1]:  # skip search + pager
        # Title div
        title_div = card.select_one("div.h3.mb-2")
        title = text(title_div)

        # Date/time is the NEXT sibling mb-2 after the title
        date_div = _next_mb2_after(title_div) if title_div else None
        date_str, time_str = get_date_time(date_div)

        # Description is the NEXT sibling mb-2 after the date block
        desc_div = _next_mb2_after(date_div) if date_div else None
        # Prefer <p> inside it (per your screenshot)
        description = ""
        if desc_div:
            p = desc_div.find("p")
            description = text(p) if p else text(desc_div)

        # URL is the View Event anchor
        link_el = card.select_one("a.fancy-link[href]")
        url_abs = urljoin(url, link_el["href"]) if link_el and link_el.has_attr("href") else ""

        # Skip malformed
        if not title and not url_abs:
            continue

        event = {
            "title": title,
            "date": date_str,      # date only (time stays separate below)
            "time": time_str,      # separate; keep it for completeness
            "description": description,
            "url": url_abs
        }
        events.append(event)
        print(event)

    print(f"Found {len(events)} events on this page.\n")
    return events, soup

def scrape_all_pages(base=START_URL):
    print("Starting full scrape...")
    first_events, first_soup = scrape_events_one_page(base)
    max_page = parse_max_page_from_pager(first_soup)
    print(f"Detected {max_page + 1} page(s) total.\n")

    all_events = list(first_events)
    for p in range(1, max_page + 1):
        page_url = f"{base}?page={p}"
        page_events, _ = scrape_events_one_page(page_url)
        all_events.extend(page_events)

    print(f"Finished scraping {len(all_events)} total events across {max_page + 1} pages.\n")
    return all_events

if __name__ == "__main__":
    data = scrape_all_pages()

    # Print summary
    for row in data:
        print(row)
    print(f"\nTotal events: {len(data)}")

    # Save as JSON
    with open("events.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("\nSaved all events to 'events.json'")
