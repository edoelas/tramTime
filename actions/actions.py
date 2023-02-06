from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

import requests
import re
from datetime import datetime
from unidecode import unidecode #pip install Unidecode
from nltk.metrics import distance

name2id = {
    "À Punt" : "110",
    "Aeroport" : "182",
    "Alacant" : "190",
    "Alameda" : "69",
    "Albalat dels Sorells" : "60",
    "Alberic" : "2",
    "Alboraia Palmaret" : "79",
    "Alboraia Peris Aragó" : "56",
    "Alfauir" : "128",
    "Alginet" : "9",
    "Almàssera" : "57",
    "Amado Granell - Montolivet" : "192",
    "Amistat" : "121",
    "Àngel Guimerà" : "25",
    "Aragó" : "120",
    "Ausiàs March" : "8",
    "Av. del Cid" : "73",
    "Ayora" : "122",
    "Bailén" : "108",
    "Benaguasil" : "53",
    "Benicalap" : "82",
    "Beniferri" : "28",
    "Benimaclet" : "67",
    "Benimàmet" : "41",
    "Benimodo" : "6",
    "Bétera" : "39",
    "Beteró" : "94",
    "Burjassot" : "30",
    "Burjassot - Godella" : "31",
    "Cabanyal" : "99",
    "Campament" : "43",
    "Campanar" : "27",
    "Campus" : "103",
    "Cantereria" : "40",
    "Canyamelar" : "127",
    "Carlet" : "7",
    "Castelló" : "1",
    "Ciutat Arts i Ciències - Justícia" : "194",
    "Colón" : "70",
    "Col·legi El Vedat" : "16",
    "Dr. Lluch" : "98",
    "El Clot" : "48",
    "Empalme" : "29",
    "Entrepins" : "65",
    "Espioca" : "11",
    "Estadi Ciutat de València" : "130",
    "Facultats - Manuel Broseta" : "68",
    "Faitanar" : "177",
    "Fira València" : "100",
    "Florista" : "80",
    "Foios" : "59",
    "Fondo de Benaguasil" : "52",
    "Font Almaguer" : "10",
    "Francesc Cubells" : "124",
    "Fuente del Jarro" : "45",
    "Gallipont - Torre del Virrei" : "119",
    "Garbí" : "81",
    "Godella" : "32",
    "Grau - La Marina" : "125",
    "Horta Vella" : "38",
    "Jesús" : "23",
    "L'Alcúdia" : "5",
    "L'Eliana" : "50",
    "La Cadena" : "95",
    "La Canyada" : "46",
    "La Carrasca" : "92",
    "La Coma" : "113",
    "La Cova" : "183",
    "La Granja" : "105",
    "La Pobla de Farnals" : "63",
    "La Pobla de Vallbona" : "51",
    "La Presa" : "184",
    "La Vallesa" : "47",
    "Les Carolines - Fira" : "42",
    "Ll. Llarga - Terramelar" : "115",
    "Llíria" : "54",
    "Machado" : "66",
    "Manises" : "180",
    "Marítim" : "123",
    "Marxalenes" : "84",
    "Mas del Rosari" : "114",
    "Masia de Traver" : "185",
    "Masies" : "37",
    "Massalavés" : "3",
    "Massamagrell" : "62",
    "Massarrojos" : "34",
    "Meliana" : "58",
    "Mislata" : "75",
    "Mislata - Almassil" : "76",
    "Moncada - Alfara" : "35",
    "Montesol" : "49",
    "Montortal" : "4",
    "Moreres" : "196",
    "Museros" : "61",
    "Natzaret" : "197",
    "Neptú" : "126",
    "Nou d'Octubre" : "74",
    "Oceanogràfic" : "195",
    "Omet" : "12",
    "Orriols" : "129",
    "Paiporta" : "19",
    "Palau de Congressos" : "55",
    "Parc Científic" : "111",
    "Paterna" : "44",
    "Patraix" : "22",
    "Picanya" : "18",
    "Picassent" : "13",
    "Pl. Espanya" : "24",
    "Platja Malva-rosa" : "96",
    "Platja les Arenes" : "97",
    "Pont de Fusta" : "87",
    "Quart de Poblet" : "178",
    "Quatre Carreres" : "193",
    "Rafelbunyol" : "64",
    "Realón" : "15",
    "Reus" : "85",
    "Riba-roja de Túria" : "186",
    "Rocafort" : "33",
    "Roses" : "181",
    "Russafa" : "191",
    "Safranar" : "21",
    "Sagunt" : "86",
    "Salt de l'Aigua" : "179",
    "Sant Isidre" : "78",
    "Sant Joan" : "104",
    "Sant Miquel dels Reis" : "131",
    "Sant Ramon" : "14",
    "Santa Rita" : "77",
    "Seminari - CEU" : "36",
    "Tarongers - Ernest Lluch" : "93",
    "Tomás y Valiente" : "112",
    "Torrent" : "17",
    "Torrent Avinguda" : "107",
    "Tossal del Rei" : "132",
    "Trànsits" : "83",
    "Trinitat" : "88",
    "Túria" : "26",
    "Universitat Politècnica" : "91",
    "València Sud" : "20",
    "València la Vella" : "188",
    "Vicent Andrés Estellés" : "102",
    "Vicente Zaragozá" : "90",
    "Xàtiva" : "71"
}

def normalize(word):
    regex = re.compile('[^a-zA-Z ]')
    word = word.lower()
    word = unidecode(word)
    word = regex.sub('', word)
    return word

def get_closest_name(name):
    name = normalize(name)
    closest_name = min(name2id.keys(), key=lambda x: distance.edit_distance(name, x))
    return closest_name


def req_json(origen, destino):
    url = 'https://www.metrovalencia.es/wp-admin/admin-ajax.php'
    myobj = {'action': 'formularios_ajax',
            'data': f"action=horarios-ruta&\
            origen={origen}&\
            destino={destino}&\
            dia={datetime.now().date().strftime('%Y-%m-%d')}&\
            horaDesde={datetime.now().time().strftime('%H:%M')}&\
            horaHasta=23:59"}

    #print(myobj)
    req = requests.post(url, data = myobj)
    
    if req.status_code != 200:
        print(f"ERROR: requesting json with code {req.status_code}")
        return None

    return req.json()



def get_horarios(ori_name, dest_name):
    if ori_name == dest_name:
        return f"Ya has legado, felicidades."

    if ori_name not in name2id:
        return f"No se ha encontrado la estación de origen con nombre \"{ori_name}\"."

    if dest_name not in name2id:
        return f"No se ha encontrado la estación de destino con nombre \"{dest_name}\"."

    json = req_json(name2id[ori_name], name2id[dest_name])
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
        ori_name = get_closest_name(tracker.get_slot("departure"))
        dest_name = get_closest_name(tracker.get_slot("destination"))
        print(f'{ori_name} -> {dest_name}')

        horarios = f'{ori_name} -> {dest_name}:\n'
        horarios += get_horarios(ori_name, dest_name)

        dispatcher.utter_message(text=horarios)
        return []