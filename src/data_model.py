from dataclasses import dataclass, asdict, fields
from datetime import datetime
import csv
import io
import ast

@dataclass
class FileData:
    """Data stored from the file parsing"""

    name: str
    contents: list
    creation_date: datetime
    extra: str = "{}" # JSON serialized

    def __str__(self):
        return f"\n{name} - {date}: \n contents\n\n"

def data_to_csv(files: list):
    """Takes in a list of FileData objects and returns a csv representation of the data contained"""
    output = io.StringIO()

    writer = csv.DictWriter(output, fieldnames = [field.name for field in fields(FileData)])

    writer.writeheader()
    for file in files:
        # Convert contents list to string for CSV
        file_dict = asdict(file)
        file_dict['contents'] = str(file_dict['contents'])
        writer.writerow(file_dict)

    return output.getvalue()


def data_from_csv(csv_data: str) -> list:
    """Takes in a csv string of datafiles (name, contents, creation_date, extra) and returns a list of FileData"""
    # Handle encoding issues
    if isinstance(csv_data, bytes):
        csv_data = csv_data.decode('utf-8', errors='replace')
    
    virt_file = io.StringIO(csv_data)
    reader = csv.DictReader(virt_file)

    acc = []
    for file in reader:
        # Parse contents string back to list
        contents = file["contents"]
        try:
            contents = ast.literal_eval(contents)
        except:
            contents = [contents]
        
        acc.append(FileData(
            file["name"], 
            contents, 
            file["creation_date"], 
            file["extra"]
        ))

    return acc
