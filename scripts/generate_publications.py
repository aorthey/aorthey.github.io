#!/usr/bin/env python3

import os
from pathlib import Path
import bibtexparser
from datetime import datetime

# Define paths relative to the script location
BASE_DIR = Path(__file__).resolve().parent.parent  # Root of the Jekyll site
PAPERS_DIR = BASE_DIR / "papers"
BIBTEX_DIR = BASE_DIR / "bibtex"
OUTPUT_FILE = BASE_DIR / "src" / "publications.md"

def parse_bibtex_file(bibtex_file):
    """Parse a BibTeX file and return relevant fields and raw content."""
    with open(bibtex_file, 'r', encoding='utf-8') as f:
        raw_content = f.read()  # Store raw BibTeX content
        bib_database = bibtexparser.load(f)
    entry = bib_database.entries[0]  # Assume one entry per file
    authors = entry.get('author', 'Unknown Authors')
    title = entry.get('title', 'Untitled')
    #journal = entry.get('journal', 'Unknown Journal')
    venue = entry.journal&.to_s || entry.booktitle&.to_s || entry.publisher&.to_s || 'Unknown Venue'

    year = entry.get('year', 'Unknown Year')

    # Simplify author list to "Names et al" if more than two authors
    author_list = authors.split(' and ')
    if len(author_list) > 2:
        authors = f"{author_list[0].split(',')[0]} et al"
    elif len(author_list) == 2:
        authors = f"{author_list[0].split(',')[0]} and {author_list[1].split(',')[0]}"
    else:
        authors = author_list[0].split(',')[0]

    return authors, title, venue, year, raw_content

def get_publications():
    """Collect publication data from BibTeX files and sort by year."""
    publications = []

    # Iterate over all BibTeX files
    for bib_file in BIBTEX_DIR.glob("*.bib"):
        filename = bib_file.stem  # e.g., "paper1" from "paper1.bib"
        pdf_file = PAPERS_DIR / f"{filename}.pdf"

        if pdf_file.exists():
            authors, title, venue, year, bibtex_content = parse_bibtex_file(bib_file)
            publications.append({
                'authors': authors,
                'title': title,
                'venue': venue,
                'year': year,
                'bibtex_content': bibtex_content.strip(),  # Remove leading/trailing whitespace
                'pdf_link': f"/papers/{filename}.pdf"
            })

    # Sort publications by year (descending)
    publications.sort(key=lambda x: x['year'], reverse=True)
    return publications

def write_publications_md(publications):
    """Write the publications to publications.md with embedded BibTeX."""
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        # Write the front matter header
        f.write("---\n")
        f.write("title: Publications\n")
        f.write("layout: home\n")
        f.write("nav_order: 2\n")
        f.write("---\n\n")

        # Write the publications section
        f.write("# Publications\n\n")
        for pub in publications:
            # Publication line with PDF link
            f.write(f"- {pub['authors']}, *{pub['title']}*, {pub['venue']}, {pub['year']} "
                    f"[[PDF]]({pub['pdf_link']})\n")
            # Embed BibTeX in a collapsible details block
            f.write("  <details>\n")
            f.write("    <summary>View BibTeX</summary>\n")
            f.write("    <pre><code>\n")
            f.write(f"{pub['bibtex_content']}\n")
            f.write("    </code></pre>\n")
            f.write("  </details>\n\n")

def main():
    # Ensure required directories exist
    if not PAPERS_DIR.exists() or not BIBTEX_DIR.exists():
        print("Error: 'papers/' or 'bibtex/' directory not found.")
        return

    publications = get_publications()
    if not publications:
        print("No publications found.")
        return

    write_publications_md(publications)
    print(f"Generated {OUTPUT_FILE} with {len(publications)} publications.")

if __name__ == "__main__":
    main()
