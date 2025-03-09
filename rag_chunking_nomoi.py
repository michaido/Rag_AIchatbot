import os
import re
import pdfplumber
import pickle
import pandas as pd
from pypdf import PdfReader

def detect_article_format(pdf_path):
    """Ελέγχει αν το PDF περιέχει 'Άρθρο Χ' και αν ναι, εφαρμόζει chunking με βάση τα άρθρα."""
    with pdfplumber.open(pdf_path) as pdf:
        text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
    return bool(re.search(r"\bΆρθρο\s+\d+", text))

def split_text(text, chunk_size=300):
    """Χωρίζει το κείμενο σε chunks των chunk_size λέξεων, λαμβάνοντας υπόψη την ενότητα."""
    words = text.split()
    chunks_list = []
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i+chunk_size])
        chunks_list.append({"text": chunk})
    return chunks_list

def extract_titles_and_sections(text_lines):
    """Εντοπίζει τίτλους, υπότιτλους και άρθρα από το κείμενο και διαχειρίζεται το chunking σωστά."""
    main_title = None
    current_section = None
    current_subtitle = None
    current_article = None
    chunks = []
    buffer = []
    
    title_pattern = re.compile(r"^([Α-Ω])\.\s*(.+)$")  # Βασικός τίτλος (π.χ. Α. Γενικά)
    subtitle_pattern = re.compile(r"^([Α-Ω])\.(\d+)\s*(.+)$")  # Υπότιτλοι (π.χ. Β.1 Κάτι)
    numbered_section_pattern = re.compile(r"^(\d+)\.\s*(.+)$")  # Αριθμημένες ενότητες (π.χ. 2. Προοίμιο)
    
    for line in text_lines:
        line = line.strip()
        if not line or "Παράρτημα" in line:
            continue

        # Ανίχνευση βασικών τίτλων (π.χ. Α. Γενικά)
        title_match = title_pattern.match(line)
        if title_match:
            if buffer:
                chunks.append({"text": " ".join(buffer), "main_title": main_title, "sub_title": current_subtitle, "section": current_section})
                buffer = []
            main_title = title_match.group(2).strip()
            current_section = main_title
            current_subtitle = None
            continue

        # Ανίχνευση υπότιτλων (π.χ. Β.1 Κάτι)
        subtitle_match = subtitle_pattern.match(line)
        if subtitle_match:
            if buffer:
                chunks.append({"text": " ".join(buffer), "main_title": main_title, "sub_title": current_subtitle, "section": current_section})
                buffer = []
            current_subtitle = f"{subtitle_match.group(1)}.{subtitle_match.group(2)} {subtitle_match.group(3).strip()}"
            continue

        # Ανίχνευση αριθμημένων ενοτήτων (π.χ. 2. Προοίμιο)
        numbered_match = numbered_section_pattern.match(line)
        if numbered_match:
            if buffer:
                chunks.append({"text": " ".join(buffer), "main_title": main_title, "sub_title": current_subtitle, "section": current_section})
                buffer = []
            current_section = f"{numbered_match.group(1)}. {numbered_match.group(2).strip()}"
            current_subtitle = None
            continue

        buffer.append(line)
    
    if buffer:
        chunks.append({"text": " ".join(buffer), "main_title": main_title, "sub_title": current_subtitle, "section": current_section})
    
    return chunks

def chunk_pdf_by_sections(pdf_path):
    """Δημιουργεί chunks ακολουθώντας τη λογική των PDFs χωρίς άρθρα και διατηρώντας τις ενότητες."""
    document = os.path.basename(pdf_path).replace(".pdf", "")
    with pdfplumber.open(pdf_path) as pdf:
        text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
        text_lines = text.split("\n")
    
    chunks = extract_titles_and_sections(text_lines)
    return [{"text": chunk["text"], "document": document, "main_title": chunk["main_title"], "sub_title": chunk["sub_title"], "section": chunk["section"]} for chunk in chunks]

def chunk_all_pdfs(folder_path):
    """Εφαρμόζει το σωστό chunking για κάθε PDF, διατηρώντας τη σωστή διαχείριση αρχείων."""
    pdf_files = [f for f in os.listdir(folder_path) if f.endswith(".pdf")]
    all_chunks = []
    
    for pdf_file in pdf_files:
        pdf_path = os.path.join(folder_path, pdf_file)
        print(f"\n🚀 Επεξεργασία PDF: {pdf_path}")
        
        if detect_article_format(pdf_path):
            print("➡️ Περιέχει άρθρα, εφαρμόζουμε chunking ανά άρθρο.")
            chunks = chunk_pdf_by_sections(pdf_path)
        else:
            print("➡️ Δεν περιέχει άρθρα, εφαρμόζουμε chunking με κεφαλαίους τίτλους.")
            chunks = chunk_pdf_by_sections(pdf_path)
        
        all_chunks.extend(chunks)
        print(f"✅ Ολοκληρώθηκε το chunking για: {pdf_file}, Βρέθηκαν {len(chunks)} chunks.")
    
    return all_chunks

if __name__ == "__main__":
    folder_path = "docs"
    print("🚀 Ξεκινάμε την επεξεργασία όλων των PDF στον φάκελο docs...")
    all_chunks = chunk_all_pdfs(folder_path)
    
    # Αποθήκευση όπως στον παλιό κώδικα
    with open("rag_df.pkl", "wb") as f:
        pickle.dump(all_chunks, f)
    
    print(f"✅ Συνολικά δημιουργήθηκαν {len(all_chunks)} chunks από όλα τα αρχεία.")
    print("💾 Το αρχείο rag_df.pkl αποθηκεύτηκε επιτυχώς.")
