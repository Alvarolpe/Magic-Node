import pypdf as pdf
import json
import glob
import src.data_model as data_model
import datetime
import os
from pathlib import PurePosixPath, Path 


def data_from_pdf(pdf_data: str):
    reader = pdf.PdfReader(pdf_data)
    meta = reader.metadata

    contents = list()

    for page in reader.pages:
        if page.extract_text() == '':
            contents.append("{image}")
        else:
            contents.append(page.extract_text().strip())

    data = {
        "author": f"{meta.author}",
        "creator": f"{meta.creator}",
        "producer": f"{meta.producer}"
    }
    reader_string = json.dumps(data, separators=(',',':'))

    return data_model.FileData(
        name = meta.title,
        contents = contents,
        creation_date = meta.creation_date,
        extra = reader_string
    )


def data_from_txt(txt_data: str):
    with open(txt_data, "r", encoding="utf-8", errors="ignore") as file:
        contents = [v.strip() for v in file.readlines()]
        return data_model.FileData(
                name= os.path.basename(txt_data),
                contents = contents,
                creation_date = datetime.datetime.fromtimestamp(os.path.getctime(txt_data)))

def data_from_csv (path: str):
    with open(path, "r", encoding="utf-8", errors="ignore") as file:
        contents = [v.strip() for v in file.readlines()]
        return data_model.FileData(
                name = os.path.basename(path),
                contents =  contents,
                creation_date = datetime.datetime.fromtimestamp(os.path.getctime(path)))

def read_files(path):
    data = []
    for doc in glob.glob(f"{path}/*"):
        if PurePosixPath(doc).suffix == ".pdf":
            data.append(data_from_pdf(doc))
        elif PurePosixPath(doc).suffix == ".csv":
            data.append(data_from_csv(doc))
        elif PurePosixPath(doc).suffix == ".txt":
            data.append(data_from_txt(doc))

    return data
