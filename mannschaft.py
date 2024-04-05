import re
from datetime import date

import pandas as pd

from date_parsing import date_parsing_from_word_str


class PlayerData:
    """
    Representation of a Player in a Mannschaft.
    """

    def __init__(self, name: str, vorname: str, letztes_spiel: str, platz_ziffer: str, spielernr: str,
                 geburtsjahr: date, altersklasse: str, passnummer: str, rangliste: str, verein: str, verein_show:str=""):
        self.__name = name.strip()
        self.__vorname = vorname.strip()
        self.__letztes_spiel = letztes_spiel.strip()
        self.__platz_ziffer = platz_ziffer.strip()
        self.__spielernr = spielernr.strip()
        self.__geburtsjahr = geburtsjahr
        self.__altersklasse = altersklasse.strip()
        self.__passnummer = passnummer.strip()
        self.__rangliste = rangliste.strip()
        self.__verein = verein.strip()
        self.__verein_show = verein_show.strip()

    @staticmethod
    def create_player_from_csv(row: pd.Series) -> 'PlayerData':
        try:
            date_str = row["Geburtsdatum"]
            geburtsjahr = date_parsing_from_word_str(date_str)
            player = PlayerData(
                name=row["Name"],
                vorname=row["Vorname"],
                letztes_spiel="",
                platz_ziffer="",
                spielernr="",
                geburtsjahr=geburtsjahr,
                altersklasse=row["Altersklasse"],
                passnummer="" if not isinstance(row["Passnummer"], str) and pd.isna(row["Passnummer"]) else row[
                    "Passnummer"],
                rangliste="",
                verein=row["Verein"],
                verein_show= row["Verein_angezeigt"]
            )
        except ValueError:
            raise ValueError(f"Could not parse date {row['Geburtsdatum']} for player {row['Name']} {row['Vorname']}")
        return player

    @staticmethod
    def create_from_dict(player_dict: dict):
        return PlayerData(player_dict["Name"], player_dict["Vorname"], player_dict["Letztes Spiel"],
                          player_dict["Platz-Ziffer"], player_dict["Spielernr."], player_dict["Geburtsjahr"],
                          player_dict["Altersklasse"], player_dict["Passnummer"], player_dict["Rangliste"],
                          player_dict["Verein"], player_dict["Verein_angezeigt"])

    @staticmethod
    def create_platzhalter(number: int = 0):
        return PlayerData(f"Name {number}", f"Vorname {number}", "", "", "", None, "", "", "", "")

    @property
    def name(self) -> str:
        return self.__name

    @property
    def vorname(self) -> str:
        return self.__vorname

    @property
    def letztes_spiel(self):
        return self.__letztes_spiel

    @property
    def platz_ziffer(self):
        return self.__platz_ziffer

    @property
    def spielernr(self):
        return self.__spielernr

    @property
    def geburtsjahr(self) -> date:
        return self.__geburtsjahr

    @property
    def altersklasse(self):
        return self.__altersklasse

    @property
    def passnummer(self):
        return self.__passnummer

    @property
    def rangliste(self):
        return self.__rangliste

    @property
    def verein(self) -> str:
        return self.__verein
    
    @property
    def verein_show(self) -> str:
        return self.__verein_show



    def is_platzhalter(self):
        return re.match(r"Vorname \d+", self.vorname) and re.match(r"Name \d+", self.name)

    @property
    def valid(self) -> bool:
        return self.name != "" and self.vorname != ""

    @property
    def valid_strong(self) -> bool:
        return self.valid and self.geburtsjahr is not None and self.passnummer != ""

    @property
    def valid_all(self) -> bool:
        return self.valid_strong and self.platz_ziffer != "" and self.spielernr != "" and self.rangliste != ""

    def get_geburtsjahr_str(self) -> str:
        """
        :return: Geburtsjahr as string in format dd/mm/yyyy. If no date is set, return empty string
        :rtype: str
        """
        if self.__geburtsjahr is None:
            return ""
        return self.__geburtsjahr.strftime("%d/%m/%Y")

    def __str__(self):
        return f"""{self.name} {self.vorname} {self.geburtsjahr.strftime("%d/%m/%Y")}"""

    @geburtsjahr.setter
    def geburtsjahr(self, value):
        self.__geburtsjahr = value


class GeneralData:
    """
    General information to a 'Mannschaft'.  
    """

    def __init__(self, name: str, spielklasse: str, liga: str, bezirk: str, spielfuehrer: str, betreuer: str,
                 vereins_nummer: str, lv_nummer: str, anzahl_spieler: int, verein: str, verein_kurz: str):
        self.name = name.strip()
        self.spielklasse = spielklasse.strip()
        self.liga = liga.strip()
        self.bezirk = bezirk.strip()
        self.spielfuehrer = spielfuehrer.strip()
        self.betreuer = betreuer.strip()
        self.vereins_nummer = vereins_nummer.strip()
        self.lv_nummer = lv_nummer.strip()
        self.anzahl_spieler = anzahl_spieler
        self.verein = verein.strip()
        self.verein_kurz = verein_kurz.strip()

    def __str__(self):
        return f"""Name={self.name} 
Spielklasse={self.spielklasse}
Liga={self.liga}
Bezirk={self.bezirk}
Spielfuehrer={self.spielfuehrer}
Betreuer={self.betreuer}
Vereinsnummer={self.vereins_nummer}
LV-Nummer={self.lv_nummer}
Anzahl Spieler={self.anzahl_spieler}
Verein={self.verein}
Verein kurz={self.verein_kurz}"""


class MannschaftData:
    """
    The complete informations to the mannschaft. Including GeneralData and all players
    """

    def __init__(self, file_name: str, general_data: GeneralData = None, players: list[PlayerData] = None):
        self._file_name = file_name
        self._general_data: GeneralData = general_data
        self._players: list[PlayerData] = players

    def set_general_data(self, general_data: dict):
        self._general_data = general_data

    def set_players(self, players: list[PlayerData]):
        self._players = players

    def sort(self, function: callable = None):
        if function is None:
            self._players = sorted(self._players, key=lambda x: x.name)
        else:
            self._players = sorted(self._players, key=function)

    def __str__(self):
        player_format = ""
        for player in self._players:
            player_format += f"""\t{player.name} {player.vorname} {player.geburtsjahr}\n"""
        return f"""{self._file_name}
{self._general_data}
{player_format}
"""

    @property
    def players(self):
        return self._players

    @property
    def general_data(self):
        return self._general_data

    @property
    def file_name(self):
        return self._file_name

    @players.setter
    def players(self, value):
        self._players = value

    @file_name.setter
    def file_name(self, value):
        self._file_name = value


class VereinsData:

    def __init__(self, name: str, mannschaften: list[MannschaftData] = None, location: str = None, street: str = None,
                 building: str = None, name_short: str = None):
        self._name = name
        self._name_short = name_short
        self._mannschaften = mannschaften
        self._location = location
        self._street = street
        self._building = building

    @property
    def name(self) -> str:
        return self._name

    @property
    def name_short(self) -> str:
        return self._name_short

    @property
    def mannschaften(self) -> list[MannschaftData]:
        return self._mannschaften
