from dataclasses import dataclass, asdict, fields
from datetime import datetime
import csv
import io

@dataclass
class FileData:
    """Data stored from the file parsing"""

    name: str
    contents: list[str]
    creation_date: datetime
    extras: str = "{}" # JSON serialized

    def __str__(self):
        return f"\n{name} - {date}: \n contents\n\n"

def data_to_csv(files: list[FileData]):
    """Takes in a list of FileData objects and returns a csv representation of the data contained"""
    output = io.StringIO()

    writer = csv.DictWriter(output, fieldnames = [field.name for field in fields(FileData)])

    writer.writeheader()
    for file in files:
        writer.writerow(asdict(file))

    return output.getvalue()


def data_from_csv(csv_data: str) -> list[FileData]:
    """Takes in a csv string of datafiles (name, contents, creation_date, extras) and returns a list of FileData"""
    virt_file = io.StringIO(csv_data)
    reader = csv.DictReader(virt_file)

    acc = []
    for file in reader:
        acc.append(FileData(file["name"], file["contents"], file["creation_date"], file["extras"]))

    return acc