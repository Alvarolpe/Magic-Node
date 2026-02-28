import PyPDF2 as pdf
import json
import glob
import logic
import datetime 
from pathlib import PurePosixPath, Path

def data_from_pdf(pdf_data: str):
    reader = pdf.PdfReader(pdf_data)
    meta = reader.metadata

    contents = list()
    
    for page in doc.pages:
        if page.extract_text() == '':
            contents.append("{image}")
        else:
            contents.append(page.extract_text())

    data = {
        "author": f"{meta.author}",
        "creator": f"{meta.creator}",
        "producer": f"{meta.producer}"
    }
    reader_string = json.dumps(data, indent=4)
    
    logic.FileData(name= meta.title, contents= contents, creation_time = datetime.fromtimestamp(pdf_data), extra= reader_string)

def data_from_txt(txt_data: str):
    with open(txt_data, "r") as t:
        contents = []
        for line in t[1:]:
            contents.append[line]
        logic.FileData(name= t[0], contents = contents, creation_time = datetime.fromtimestamp(txt_data))

DATASET_DIR = Path(__file__).parent.parent / "dataset"

for doc in glob.glob(f"{DATASET_DIR}/*"):
    if PurePosixPath(*doc).suffix == ".pdf":
        data_from_pdf
    elif PurePosixPath(*doc).suffix == ".csv":
        logic.data_from_csv(doc)
    elif PurePosixPath(*doc).suffix == ".txt":
        data_from_txt(doc)