import datetime
import logging
import re
from pathlib import Path

import pandas as pd

from date_parsing import date_parsing_from_word_str, date_parsing_from_str
from exceptions import FileIncompleteError
from mannschaft import PlayerData, MannschaftData, GeneralData


def _correct_str(string: str, with_underscore=None, remove=None, with_space=None) -> str:
    """
    Correct a string and replace special characters with underscores, space or remove them.
    By default, the following characters are replaced with underscores: r"[:/\?<>|\"*]"
    By default, the following characters are removed: r"[\.]"
    By default, the following characters are replaced with spaces: r"[\s]+"

    :param string: string to correct
    :type string:
    :param with_underscore:  regex pattern to replace special characters with underscores. Default is r"[:/\?<>|\"*]"
    :type with_underscore: r-string
    :param remove:  regex pattern to remove special characters. Default is r"[\.]"
    :type remove:  r-string
    :param with_space:  regex pattern to replace special characters with spaces. Default is r"[\s]+"
    :type with_space:  r-string
    :return:  corrected string
    :rtype:  str
    """
    if string is None:
        return ""
    with_underscore = r"[:/\?<>|\"*]" if with_underscore is None else with_underscore
    remove = r"[\.]" if remove is None else remove
    with_space = r"[\s]+" if with_space is None else with_space
    temp = re.sub(with_underscore, "_", string).strip()
    temp = re.sub(with_space, " ", temp)
    return re.sub(remove, "", temp)


def get_player_str(number: int, player: PlayerData, date_format: str = "%d/%m/%Y") -> str:
    if not player.valid:
        raise ValueError("Player is not valid")
    geburtsjahr = player.geburtsjahr
    geburtsjahr_str = player.geburtsjahr.strftime(date_format) if geburtsjahr is not None else ""
    if geburtsjahr is not None and geburtsjahr >= datetime.date(2000, 1, 1):
        logging.info(f"Date of birth for player {player.name} {player.vorname} is after 2000. Write complete.")
        geburtsjahr_str = geburtsjahr.strftime("%m/%Y")
    return f"""[Spieler {number}]
Name={player.name}
Vorname={player.vorname}
Letztes Spiel={player.letztes_spiel}
Platz-Ziffer={player.platz_ziffer}
Spielernr.={player.spielernr}
Geb.-Jahr={geburtsjahr_str}
Altersklasse={player.altersklasse}
Pass-Nr.={player.passnummer}
Rangliste={player.rangliste}
Verein={player.verein if player.verein_show == "" else player.verein_show}
"""


def get_player_str_from_csv(number: int, data: pd.Series) -> str:
    if data is None or pd.isna(data).max():
        raise ValueError("Data is empty or contains NaN values")
    name = data["Nachname"]
    vorname = data["Vorname"]
    date_str = data["Geburtsdatum"]
    geburtsjahr: datetime.date = date_parsing_from_word_str(date_str)
    passnummer = data["Passnummer"]
    altersklasse = data["Altersklasse"]
    verein = data["Verein"] if data["Verein_angezeigt"] == "" else data["Verein_angezeigt"]
    geburtsjahr_str = geburtsjahr.strftime("%d/%m/%Y") if geburtsjahr is not None else ""
    if geburtsjahr is not None and geburtsjahr >= datetime.date(2000, 1, 1):
        logging.info(f"Date of birth for player {name} {vorname} is after 2000. Write complete.")
        geburtsjahr_str = geburtsjahr.strftime("%d/%m/%YYYY")
    return f"""[Spieler {number}]
Name={name}
Vorname={vorname}
Letztes Spiel=
Platz-Ziffer=
Spielernr.=
Geb.-Jahr={geburtsjahr_str}
Altersklasse={altersklasse}
Pass-Nr.={passnummer}
Rangliste=
Verein={verein}
"""


def get_general_info_str_from_mannschaft_data(mannschaft: MannschaftData) -> str:
    name = _correct_str(mannschaft.general_data.name, with_underscore=r"[_/]", remove=r"[\n]",
                        with_space=r"[\s]+|[\|*+]")
    return f"""[Allgemein]
Name={name}
Spielklasse={mannschaft.general_data.spielklasse}
Liga={mannschaft.general_data.liga}
Bezirk={mannschaft.general_data.bezirk}
Spielführer={mannschaft.general_data.spielfuehrer}
Betreuer 1={mannschaft.general_data.betreuer}
Vereins-Nr={mannschaft.general_data.vereins_nummer}
LV-Nr={mannschaft.general_data.lv_nummer}
Anzahl Spieler={mannschaft.general_data.anzahl_spieler}
"""


def get_general_info_str_from_input(name: str) -> str:
    """
    Get the general information for a .ini file from the user
    :param name: the name of Mannschaft
    :type name: str
    :return: complete config string for the general information
    :rtype:     str
    """
    spielklasse = input("Spielklasse: ")
    liga = input("Liga: ")
    bezirk = input("Bezirk: ")
    spielfuehrer = input("Spielführer: ")
    betreuer = input("Betreuer: ")
    vereinsnummer = input("Vereinsnummer: ")
    lvnummer = input("LV-Nummer: ")
    anzahl_spieler = input("Anzahl Spieler: ")
    if not anzahl_spieler.isdigit() or int(anzahl_spieler) < 1:
        logging.warning("Number of players must be greater than 0. Setting to 10")
        anzahl_spieler = "10"

    return f"""[Allgemein]
Name={_correct_str(name)}
Spielklasse={spielklasse}
Liga={liga}
Bezirk={bezirk}
Spielführer={spielfuehrer}
Betreuer 1={betreuer}
Vereins-Nr={vereinsnummer}
LV-Nr={lvnummer}
Anzahl Spieler={anzahl_spieler}
"""


def platzhalter_player_str(player_number: int) -> str:
    """
    Return a string with the player information for a player that is not in the csv file. Only to fill the .ini file
    for minimal players
    :param player_number: number of the player
    :type player_number: int
    :return: Config string for the platzhalter player
    :rtype: str
    """
    return f"""[Spieler {player_number}]
Name=Name{player_number}
Vorname=Vorname{player_number}
Letztes Spiel=
Platz-Ziffer=
Spielernr.=
Geb.-Jahr=
Altersklasse=
Pass-Nr.=
Rangliste=
Verein=
"""


def read_finished_mannschaften(file: Path) -> MannschaftData:
    """
    Read a .ini file with the given name and return a MannschaftData object
    :param file: path to the .ini file
    :type file: Path
    :return: MannschaftData object
    :rtype:  MannschaftData
    """
    lines: list
    if file.suffix != ".ini":
        logging.error(f"File {file} is not a .ini file")
        raise ValueError("File is not a .ini file")
    with open(file, "r") as f:
        lines = f.read().splitlines()
    # general info
    if len(lines) < 11:
        logging.error(f"File {file} has not enough lines")
        raise FileIncompleteError("File has not enough lines")
    general_data = lines[1:10]
    name, spielklasse, liga, bezirk, spielfuehrer, betreuer, vereinsnummer, lvnummer, anzahl_spieler = \
        [line.split("=")[1] for line in general_data]
    general_data = GeneralData(name, spielklasse, liga, bezirk, spielfuehrer, betreuer, vereinsnummer, lvnummer,
                               int(anzahl_spieler), "", "")
    # players
    players = []
    for i in range(10, len(lines), 11):
        player_data: list[str] = lines[i:i + 11]
        geburtsjahr_str: str
        (name, vorname, letztes_spiel, platz_ziffer, spielernr, geburtsjahr_str, altersklasse, passnummer, rangliste,
         verein) = [line.split("=")[1].strip() for i, line in enumerate(player_data) if i != 0]
        try:
            geburtsjahr = date_parsing_from_str(geburtsjahr_str)
        except ValueError:
            logging.warning(f"Could not parse date {geburtsjahr_str} for player {name} {vorname}. Setting to None.")
            geburtsjahr = None
        players.append(PlayerData(name, vorname, letztes_spiel, platz_ziffer, spielernr, geburtsjahr,
                                  altersklasse, passnummer, rangliste, verein)
                       )
    return MannschaftData(file_name=file.stem, general_data=general_data, players=players)


def write_mannschaft_file_from_mannschaft_data(name: str, mannschaft: MannschaftData, sort: bool = True,
                                               platzhalter_am_ende: bool = True, encoding="utf-8",
                                               date_format: str = "%m/%y") -> None:
    """
    Write a .ini file with the given name and the given MannschaftData object
    :param date_format:  format of the date. Default is mm/yy
    :type date_format:  str
    :param name: Name of the .ini file
    :type name: str
    :param mannschaft: complete MannschaftData object
    :type mannschaft: MannschaftData
    :param sort: sort the players by their name. Default is True
    :type sort: bool
    :param platzhalter_am_ende:
    :type platzhalter_am_ende:
    :param encoding: encoding of the file. Default is utf-8
    :type encoding: str
    :return: nothing
    :rtype: None
    """
    file_name = _correct_str(name)
    if file_name.endswith(".ini"):
        file_name = file_name[:-4]
    if not Path("out").exists():
        Path("out").mkdir()
    if Path(f"out/{file_name}.ini").exists():
        logging.warning(f"File {file_name}.ini already exists. Overwriting.")
    with open(f"out/{file_name}.ini", "w", encoding=encoding) as f:
        f.write(get_general_info_str_from_mannschaft_data(mannschaft))
        if platzhalter_am_ende and sort:
            normal_players = [player for player in mannschaft.players if not player.is_platzhalter()]
            platzhalter_player = [player for player in mannschaft.players if player.is_platzhalter()]
            platzhalter_player = sorted(platzhalter_player, key=lambda x: x.name)
            mannschaft.players = normal_players
            mannschaft.sort()
            mannschaft.players.extend(platzhalter_player)
        elif sort:
            mannschaft.sort()
        for number, player in enumerate(mannschaft.players):
            f.write(get_player_str(number, player, date_format))
