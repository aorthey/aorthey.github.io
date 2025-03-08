import os
from pathlib import Path
import re

def check_folder_consistency(bibtex_folder, papers_folder):
    """
    Check consistency between bibtex and papers folders.
    Rules:
    - Same number of files
    - bibtex folder: only .bib files
    - papers folder: only .pdf files
    - Matching filenames with different extensions
    - Format: YYYY-Name-conference
    """

    # Convert paths to Path objects
    bibtex_path = Path(bibtex_folder)
    papers_path = Path(papers_folder)

    # Check if folders exist
    if not bibtex_path.exists() or not bibtex_path.is_dir():
        raise ValueError(f"BibTeX folder '{bibtex_folder}' does not exist or is not a directory")
    if not papers_path.exists() or not papers_path.is_dir():
        raise ValueError(f"Papers folder '{papers_folder}' does not exist or is not a directory")

    # Get list of files
    bibtex_files = list(bibtex_path.glob("*"))
    papers_files = list(papers_path.glob("*"))

    # Check number of files
    if len(bibtex_files) != len(papers_files):
        raise ValueError(f"Number of files mismatch: {len(bibtex_files)} .bib files vs {len(papers_files)} .pdf files")

    # Check file extensions
    for bib_file in bibtex_files:
        if bib_file.suffix.lower() != ".bib":
            raise ValueError(f"Non-.bib file found in bibtex folder: {bib_file.name}")

    for pdf_file in papers_files:
        if pdf_file.suffix.lower() != ".pdf":
            raise ValueError(f"Non-.pdf file found in papers folder: {pdf_file.name}")

    # Check filename format and matching
    filename_pattern = r"^\d{4}-[A-Za-z]+-[A-Za-z]+$"

    # Create sets of base filenames (without extension)
    bibtex_bases = {f.stem for f in bibtex_files}
    papers_bases = {f.stem for f in papers_files}

    # Check if sets match
    if bibtex_bases != papers_bases:
        raise ValueError("Filenames don't match between folders")

    # Check format for each file
    for base_name in bibtex_bases:
        if not re.match(filename_pattern, base_name):
            raise ValueError(f"File '{base_name}' does not match required format 'YYYY-SurnameFirstAuthor-AcronymJournal'")

    print("Everything okay. Found "+str(len(bibtex_bases))+" files.")

def main():
    # Example folder paths - replace with your actual paths
    BIBTEX_FOLDER = "bibtex"
    PAPERS_FOLDER = "papers"

    try:
        check_folder_consistency(BIBTEX_FOLDER, PAPERS_FOLDER)
    except ValueError as e:
        print(f"Error: {str(e)}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    main()

