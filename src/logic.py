from src.data_model import data_to_csv, data_from_csv
from src.metadata import read_files

def extract_metadata(args):
    return data_to_csv(read_files(args["dir"]))

