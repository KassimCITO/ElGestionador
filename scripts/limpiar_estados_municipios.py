import json

INPUT_FILE = r'c:\Prj\ElGestionador\estados-municipios.json'
OUTPUT_FILE = r'c:\Prj\ElGestionador\municipios_limpio.json'

# Mapeo de nombres a IDs oficiales de estados (según INEGI)
ESTADOS_NOMBRES_A_ID = {
    "Aguascalientes": "1",
    "Baja California": "2",
    "Baja California Sur": "3",
    "Campeche": "4",
    "Coahuila": "5",
    "Colima": "6",
    "Chiapas": "7",
    "Chihuahua": "8",
    "Ciudad de Mexico": "9",
    "Durango": "10",
    "Guanajuato": "11",
    "Guerrero": "12",
    "Hidalgo": "13",
    "Jalisco": "14",
    "Estado de Mexico": "15",
    "Michoacan": "16",
    "Morelos": "17",
    "Nayarit": "18",
    "Nuevo Leon": "19",
    "Oaxaca": "20",
    "Puebla": "21",
    "Queretaro": "22",
    "Quintana Roo": "23",
    "San Luis Potosi": "24",
    "Sinaloa": "25",
    "Sonora": "26",
    "Tabasco": "27",
    "Tamaulipas": "28",
    "Tlaxcala": "29",
    "Veracruz": "30",
    "Yucatan": "31",
    "Zacatecas": "32"
}

def limpiar_estados_municipios():
    with open(INPUT_FILE, encoding='utf-8') as f:
        data = json.load(f)

    nuevo = {}
    for estado, municipios in data.items():
        id_estado = ESTADOS_NOMBRES_A_ID.get(estado)
        if not id_estado:
            print(f"Estado no reconocido: {estado}")
            continue
        nuevo[id_estado] = []
        for i, nombre in enumerate(municipios, 1):
            nuevo[id_estado].append({"id": i, "nombre": nombre})

    # Ordenar por ID de estado
    nuevo_ordenado = {k: nuevo[k] for k in sorted(nuevo, key=lambda x: int(x))}

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(nuevo_ordenado, f, ensure_ascii=False, indent=2)

    print(f"Archivo limpio guardado en {OUTPUT_FILE}")

if __name__ == "__main__":
    limpiar_estados_municipios()
