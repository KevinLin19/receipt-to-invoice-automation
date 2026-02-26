import PyPDF2
import os

def merge_and_delete_pdfs(source_folder, output_folder, output_filename):
    """Merges all PDF files from a folder into a single file, saves it to a specific folder, and deletes the original files."""
    merger = PyPDF2.PdfMerger()
    pdf_files = [f for f in os.listdir(source_folder) if f.lower().endswith(".pdf")]
    pdf_files.sort()

    if not pdf_files:
        print("No PDF files found in the source folder.")
        return

    for pdf in pdf_files:
        pdf_path = os.path.join(source_folder, pdf)
        merger.append(pdf_path)
        print(f"Added {pdf} to the merge...")

    # Create output folder if it does not exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Save the merged file
    output_path = os.path.join(output_folder, output_filename)
    merger.write(output_path)
    merger.close()
    print(f"Merging completed: {output_path}")

    # Delete the original PDF files
    for pdf in pdf_files:
        pdf_path = os.path.join(source_folder, pdf)
        os.remove(pdf_path)
        print(f"Deleted: {pdf}")

    print("All source PDF files have been deleted.")
