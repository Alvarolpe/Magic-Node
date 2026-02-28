import pyfsig
from pythonnet import File 

# signatures = {"pdf": [25, 50, 44, 46, "2D"],
#               "txt": ["EF", "BB", "BF"]}

file_path = "C:/Users/USUARIO/Proyects/HackUDC/dataset/ficha_tecnica_RX400.pdf"
# file_path = "C:/Users/USUARIO/Proyects/HackUDC/dataset/proveedores_activos.txt"
match = pyfsig.find_matches_for_file_path(file_path = file_path)
print(match)

with File.ReadAllBytes(file_path) as f:
    file_header = f.read(32)
    print(file_header)
match = pyfsig.find_matches_for_file_header(file_header= file_header, signatures= pyfsig.SIGNATURES)
print(match)