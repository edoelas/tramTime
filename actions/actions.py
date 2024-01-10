from typing import Any, Text, Dict, List, Union

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

import requests
import re
from datetime import datetime
from unidecode import unidecode #pip install Unidecode

id2names: dict[int, list[str]] = {
    110 : ["À Punt"],
    182 : ["Aeroport"],
    190 : ["Alacant"],
    69 : ["Alameda"],
    60 : ["Albalat dels Sorells"],
    2 : ["Alberic"],
    79 : ["Alboraia Palmaret"],
    56 : ["Alboraia Peris Aragó"],
    128 : ["Alfauir"],
    9 : ["Alginet"],
    57 : ["Almàssera"],
    192 : ["Amado Granell - Montolivet"],
    121 : ["Amistat"],
    25 : ["Àngel Guimerà"],
    120 : ["Aragó"],
    8 : ["Ausiàs March"],
    73 : ["Av. del Cid"],
    122 : ["Ayora"],
    108 : ["Bailén"],
    53 : ["Benaguasil"],
    82 : ["Benicalap"],
    28 : ["Beniferri"],
    67 : ["Benimaclet", "Beni"],
    41 : ["Benimàmet"],
    6 : ["Benimodo"],
    39 : ["Bétera"],
    94 : ["Beteró"],
    30 : ["Burjassot"],
    31 : ["Burjassot Godella"],
    99 : ["Cabanyal"],
    43 : ["Campament"],
    27 : ["Campanar"],
    103 : ["Campus"],
    40 : ["Cantereria"],
    127 : ["Canyamelar"],
    7 : ["Carlet"],
    1 : ["Castelló"],
    194 : ["Ciutat Arts i Ciències - Justícia"],
    70 : ["Colón"],
    16 : ["Col·legi El Vedat"],
    98 : ["Dr. Lluch"],
    48 : ["El Clot"],
    29 : ["Empalme"],
    65 : ["Entrepins"],
    11 : ["Espioca"],
    130 : ["Estadi Ciutat de València"],
    68 : ["Facultats - Manuel Broseta"],
    177 : ["Faitanar"],
    100 : ["Fira València"],
    80 : ["Florista"],
    59 : ["Foios"],
    52 : ["Fondo de Benaguasil"],
    10 : ["Font Almaguer"],
    124 : ["Francesc Cubells"],
    45 : ["Fuente del Jarro"],
    119 : ["Gallipont - Torre del Virrei"],
    81 : ["Garbí"],
    32 : ["Godella"],
    125 : ["Grau La Marina"],
    38 : ["Horta Vella"],
    23 : ["Jesús"],
    5 : ["L'Alcúdia"],
    50 : ["L'Eliana"],
    95 : ["La Cadena"],
    46 : ["La Canyada"],
    92 : ["La Carrasca"],
    113 : ["La Coma"],
    183 : ["La Cova"],
    105 : ["La Granja"],
    63 : ["La Pobla de Farnals"],
    51 : ["La Pobla de Vallbona"],
    184 : ["La Presa"],
    47 : ["La Vallesa"],
    42 : ["Les Carolines - Fira"],
    115 : ["Ll. Llarga - Terramelar"],
    54 : ["Llíria"],
    66 : ["Machado"],
    180 : ["Manises"],
    123 : ["Marítim"],
    84 : ["Marxalenes"],
    114 : ["Mas del Rosari"],
    185 : ["Masia de Traver"],
    37 : ["Masies"],
    3 : ["Massalavés"],
    62 : ["Massamagrell"],
    34 : ["Massarrojos"],
    58 : ["Meliana"],
    75 : ["Mislata"],
    76 : ["Mislata - Almassil"],
    35 : ["Moncada - Alfara"],
    49 : ["Montesol"],
    4 : ["Montortal"],
    196 : ["Moreres"],
    61 : ["Museros"],
    197 : ["Natzaret"],
    126 : ["Neptú"],
    74 : ["Nou d'Octubre"],
    195 : ["Oceanogràfic"],
    12 : ["Omet"],
    129 : ["Orriols"],
    19 : ["Paiporta"],
    55 : ["Palau de Congressos"],
    111 : ["Parc Científic"],
    44 : ["Paterna"],
    22 : ["Patraix"],
    18 : ["Picanya"],
    13 : ["Picassent"],
    24 : ["Pl. Espanya"],
    96 : ["Platja Malva-rosa"],
    97 : ["Platja les Arenes"],
    87 : ["Pont de Fusta"],
    178 : ["Quart de Poblet"],
    193 : ["Quatre Carreres"],
    64 : ["Rafelbunyol"],
    15 : ["Realón"],
    85 : ["Reus"],
    186 : ["Riba-roja de Túria"],
    33 : ["Rocafort"],
    181 : ["Roses"],
    191 : ["Russafa"],
    21 : ["Safranar"],
    86 : ["Sagunt"],
    179 : ["Salt de l'Aigua"],
    78 : ["Sant Isidre"],
    104 : ["Sant Joan"],
    131 : ["Sant Miquel dels Reis"],
    14 : ["Sant Ramon"],
    77 : ["Santa Rita"],
    36 : ["Seminari - CEU"],
    93 : ["Tarongers Ernest Lluch", "Tarongers"],
    112 : ["Tomás y Valiente"],
    17 : ["Torrent"],
    107 : ["Torrent Avinguda"],
    132 : ["Tossal del Rei"],
    83 : ["Trànsits"],
    88 : ["Trinitat"],
    26 : ["Túria"],
    91 : ["Universitat Politècnica", "UPV", "Politécnica", "Poli"],
    20 : ["València Sud"],
    188 : ["València la Vella"],
    102 : ["Vicent Andrés Estellés"],
    90 : ["Vicente Zaragozá"],
    71 : ["Xàtiva"],
}

# edition distance where swapping two characters is considered as one operation
def edit_distance(s1: str, s2: str) -> float:
    l1 = len(s1)
    l2 = len(s2)
    matrix = [list(range(l1 + 1))] * (l2 + 1)
    for zz in list(range(l2 + 1)):
        matrix[zz] = list(range(zz,zz + l1 + 1))
    for zz in list(range(0,l2)):
        for sz in list(range(0,l1)):
            if s1[sz] == s2[zz]:
                matrix[zz+1][sz+1] = min(matrix[zz+1][sz] + 1, matrix[zz][sz+1] + 1, matrix[zz][sz])
            else:
                matrix[zz+1][sz+1] = min(matrix[zz+1][sz] + 1, matrix[zz][sz+1] + 1, matrix[zz][sz] + 1)
        
            if sz and zz and s1[sz]==s2[zz-1] and s1[sz-1] == s2[zz]:
                matrix[zz+1][sz+1] = min (matrix[zz+1][sz+1], matrix[zz-1][sz-1] + 1)

    distance = float(matrix[l2][l1])
    result = 1.0-distance/max(l1,l2) # distancia normalizada
    return distance

def normalize(word: str) -> str:
    regex = re.compile('[^a-zA-Z ]')
    normalized = word.lower()
    normalized = unidecode(normalized)
    normalized = regex.sub('', normalized)
    return normalized

def get_closest_id(sname: str) -> int:
    min_dist: float = float('inf')
    closest_id: Union[int, None] = None

    sname = normalize(sname)

    for id, name_list in id2names.items():
        for name in name_list:
            name = normalize(name)
            new_dist = edit_distance(sname, name)
            if new_dist < min_dist:
                min_dist = new_dist
                closest_id = id

    assert closest_id is not None
    return closest_id


def req_json(origen: int, destino: int):
    url = 'https://www.metrovalencia.es/wp-admin/admin-ajax.php'
    myobj = {'action': 'formularios_ajax',
            'data': f"action=horarios-ruta&\
            origen={origen}&\
            destino={destino}&\
            dia={datetime.now().date().strftime('%Y-%m-%d')}&\
            horaDesde={datetime.now().time().strftime('%H:%M')}&\
            horaHasta=23:59"}

    req = requests.post(url, data = myobj)
    
    if req.status_code != 200:
        print(f"ERROR: requesting json with code {req.status_code}")
        return None

    return req.json()



def get_horarios(ori: int, dest: int) -> str:
    if ori == dest:
        return f"Ya has legado, felicidades."

    if ori not in id2names:
        return f"No se ha encontrado la estación de origen con nombre \"{id2names[ori][0]}\"."

    if dest not in id2names:
        return f"No se ha encontrado la estación de destino con nombre \"{id2names[dest][0]}\"."

    json = req_json(ori, dest)
    if not json or 'horarios' not in json:
        return f"El servidor de Metrovalencia no ha respondido."

    ret = ""
    horarios = json['horarios'][0]

    if len(horarios["horas"]) == 0:
        return "No hay trams disponibles."

    for i in range(4):
        if i >= len(horarios["horas"]):
            break
        horario = horarios["horas"][i]
        tram = horarios["trenes"][horario[1]]
        # linea, horario, destino #, origen, estado
        ret += f"Linea: {tram['linea']}     Hora: {horario[0]}     Destino: {tram['destino']} \n"

    return ret

class ActionTram(Action):
    def name(self) -> Text:
        return "action_tram"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(f'{tracker.get_slot("departure")} -> {tracker.get_slot("destination")}:\n')
        ori = get_closest_id(str(tracker.get_slot("departure")))
        dst = get_closest_id(str(tracker.get_slot("destination")))

        horarios = f'{id2names[ori][0]} -> {id2names[dst][0]}:\n'
        horarios += get_horarios(ori, dst)

        dispatcher.utter_message(text=horarios)
        return []