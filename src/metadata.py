import PyPDF2 as pdf
import json
import glob
import os
import logic
import datetime 

path = os.getcwd()[:-4]
for doc in glob.glob(f"{path}\dataset\*.pdf"):
    reader = pdf.PdfReader(doc)
    meta = reader.metadata

    contents = list()
    try:
        for page in doc.pages:
            contents.append(page.extract_text())
    except:
        continue

    data = {
        "author": f"{meta.author}",
        "creator": f"{meta.creator}",
        "producer": f"{meta.producer}"
    }

    reader_string = json.dumps(data, indent=4)
    
    logic.dataclass(name= meta.title, contents= contents, creation_time = datetime.fromtimestamp(doc), extra= reader_string)