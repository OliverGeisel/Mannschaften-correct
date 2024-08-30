import logging
import pathlib
from pathlib import Path

import pandas as pd

from csv_files import read_csv, write_csv_from_mannschaft_data, write_csv_with_all_mannschaften
from exceptions import FileIncompleteError
from ini_files import get_general_info_str_from_input, get_player_str, platzhalter_player_str, \
    read_finished_mannschaften, write_mannschaft_file_from_mannschaft_data
from mannschaft import MannschaftData, PlayerData, VereinsData, GeneralData

NAME_DER_MANNSCHAFT_ = "Name der Mannschaft: "

GREEN = "\033[92m"
RED = "\033[91m"
BLUE = "\033[94m"
ENDC = "\033[0m"

DEFAULT_DATA_PATH = r"C:\Control Center Kegeln\Einstellungen\Mannschaften"


def load_mannschaften_csv(sep=";") -> pd.DataFrame:
    return read_csv(sep=sep)


def load_spieler_csv(sep=";") -> pd.DataFrame:
    return read_csv("Spieler", sep=sep)


def read_folder_mannschaften(folder_name: str, print_teams: bool = False) -> list[MannschaftData]:
    """
    Read all .ini files in the given folder and return a list of MannschaftData objects
    :param print_teams:  if True, print the MannschaftData objects. Default is False
    :type print_teams: bool
    :param folder_name: name of the folder to read the .ini files from. The path is absolute or relative to the current
    working directory
    :type folder_name: str
    :return: list of MannschaftData objects
    :rtype: list[MannschaftData]
    :raises FileNotFoundError: if the folder does not exist
    """
    folder = Path(folder_name)
    if not folder.exists():
        logging.error(f"Folder {folder} does not exist")
        raise FileNotFoundError(f"Folder {folder} does not exist")
    files = [file for file in folder.iterdir() if file.suffix == ".ini"]
    mannschaften_list = []
    for file in files:
        try:
            mannschaften_list.append(read_finished_mannschaften(file))
        except (FileIncompleteError, ValueError):
            continue
    if print_teams:
        for mannschaft in mannschaften_list:
            print(mannschaft)
    return mannschaften_list


def write_mannschaft_file_input(file_name: str, csv_name: str = "Mannschaften",
                                sort: bool = True, encoding="utf-8", date_format="%m/%y") -> None:
    if file_name.endswith(".ini"):
        file_name = file_name[:-4]
    if not Path("out").exists():
        Path("out").mkdir()
    if Path(f"out/{file_name}.ini").exists():
        logging.warning(f"File {file_name}.ini already exists. Overwriting?")
        response = input("Will you continue? Otherwise press 'n' and enter\n")
        if response.lower() == "n":
            return
    with open(f"out/{file_name}.ini", "w", encoding=encoding) as file:
        general_info = get_general_info_str_from_input(file_name)
        anzahl_spieler = int(general_info.splitlines()[9].split("=")[1])
        file.write(general_info)
        players: list = []
        if not pathlib.Path(f"{csv_name}.csv").exists():
            logging.error(f"File {csv_name}.csv does not exist. All players will be Platzhalter players")
        else:
            players = iter_csv_player(anzahl_spieler, csv_name, date_format, file, sort)
        num_players = len(players)
        if num_players < anzahl_spieler:  # add Platzhalter players
            n = 1
            for _ in range(num_players, anzahl_spieler):
                file.write(platzhalter_player_str(n))
                n += 1


def iter_csv_player(anzahl_spieler, csv_name, date_format, file, sort) -> list[PlayerData]:
    """
    Iterate through the csv file and write the players to the file
    :param anzahl_spieler: number of players to write
    :type anzahl_spieler: int
    :param csv_name: name of the csv file
    :type csv_name: str
    :param date_format: format of the date
    :type date_format: str
    :param file: file object to write the players to
    :type file: file
    :param sort: sort the players by their name
    :type sort: bool
    :return: players written
    """
    back = []
    for index, row in read_csv(csv_name).iterrows():
        if len(back) >= anzahl_spieler:
            break
        if pd.isna(row).max():  # check if there are any NaN values in the row
            continue
        try:
            back.append(PlayerData.create_player_from_csv(row))
        except ValueError:
            continue
    # sort and complete with platzhalter players
    if sort:
        back = sorted(back, key=lambda x: x.name)
    for j, player in enumerate(back):
        try:
            file.write(get_player_str(j, player, date_format))
        except ValueError:
            logging.warning(
                f"Could not write player {player.name} {player.vorname} {player.geburtsjahr}. Date format "
                f"is unknown \nSkipping player.")
            continue
    return back


def rewrite_mannschaft_file(name: str, new_name: str = None) -> None:
    """
    Rewrite a .ini file with the given name. If new_name is not None, the new file will be named new_name.ini
    :param name: name of the .ini file to rewrite. The path is absolute or relative to the current working directory.
    The .ini ending is not included
    :type name: str
    :param new_name: new name of the .ini file
    :type new_name: str
    :return: None
    :rtype: None
    """
    if name.endswith(".ini"):
        name = name[:-4]
    if not Path(f"{name}.ini").exists():
        logging.error(f"File {name}.ini does not exist")
        raise FileNotFoundError(f"File {name}.ini does not exist")
    mannschaft = read_finished_mannschaften(Path(f"{name}.ini"))
    new_name = name if new_name is None else new_name
    write_mannschaft_file_from_mannschaft_data(new_name, mannschaft, encoding="windows-1252")


def create_new_mannschaft():
    name = input(NAME_DER_MANNSCHAFT_)
    write_mannschaft_file_input(name, "Spieler", encoding="windows-1252")


def rewrite_mannschaft():
    """
    Rewrite a Mannschaft file with a new name
    """
    name = input(NAME_DER_MANNSCHAFT_)
    new_name = input("Neuer Name (Leer == alter name): ")
    if new_name == "":
        new_name = name
    rewrite_mannschaft_file(name, new_name)


def get_final_name_for_mannschaften_file(vereins_name: str, mannschaft_name: str) -> str:
    if mannschaft_name.startswith("U18") or mannschaft_name.startswith("U14"):
        return f"{mannschaft_name} {vereins_name}"
    else:
        return f"{vereins_name} {mannschaft_name}"


def import_single_mannschaft(vereins_name: str, mannschaft_name: str, num_min_players: int = 10):
    """
    Import a single Mannschaft from csv file
    :param vereins_name: Name of the Verein
    :type vereins_name: str
    :param mannschaft_name: Name of the Mannschaft
    :type mannschaft_name:  str
    :param num_min_players: Minimum number of players. If the number of players in the csv file is less than
    this number, Platzhalter players will be added. Default is 10
    :type num_min_players: int
    :return: None
    :rtype: None
    """

    spieler_csv = load_spieler_csv()
    players = list()
    general_data_str = get_general_info_str_from_input(mannschaft_name)
    general_data = general_data_str.split("\n")[1:10]
    name, spielklasse, liga, bezirk, spielfuehrer, betreuer, vereinsnummer, lvnummer, anzahl_spieler = \
        [line.split("=")[1] for line in general_data]
    general_data = GeneralData(name, spielklasse, liga, bezirk, spielfuehrer, betreuer,
                               vereinsnummer, lvnummer, int(anzahl_spieler), "", "")
    for index, row in spieler_csv.iterrows():
        players.append(PlayerData.create_player_from_csv(row))
    if len(players) < num_min_players:
        for i in range(1, num_min_players - len(players) + 1):
            players.append(PlayerData.create_platzhalter(i))
    mannschaft = MannschaftData(get_final_name_for_mannschaften_file(vereins_name, mannschaft_name), players=players,
                                general_data=general_data)
    write_mannschaft_file_from_mannschaft_data(mannschaft.file_name, mannschaft)


def import_new_mannschaften(num_min_players: int = 10, min_placeholder: int = 0, encoding="windows-1252") -> None:
    """
    Use this function to import all Mannschaften from the csv files. The csv files must be in the same folder as this
    script and must be named "Mannschaften.csv" and "Spieler.csv".
    :param encoding: encoding of the csv files. Default is windows-1252
    :type encoding: str
    :param min_placeholder: Minimum number of Platzhalter players. Default is 0
    :type min_placeholder: int
    :param num_min_players: Minimum number of players. If the number of players in the csv file is less than
    this number, Platzhalter players will be added. Default is 10
    :type num_min_players: int
    """
    spieler_csv = load_spieler_csv()
    mannschaften_csv = load_mannschaften_csv()
    vereine: list[VereinsData] = list()
    vereins_map: dict[str, dict[str, tuple[GeneralData, [list[PlayerData]]]]] = dict()

    for index, s_row in spieler_csv.iterrows():
        verein = s_row["Verein"]
        spieler_mannschaft = s_row["Mannschaft"] if not pd.isna(s_row["Mannschaft"]) else ""
        for m_index, m_row in mannschaften_csv.iterrows():
            mannschaft = m_row["Mannschaft"] if not pd.isna(m_row["Mannschaft"]) else ""
            if m_row["Verein"] == verein and mannschaft == spieler_mannschaft:
                if verein not in vereins_map:
                    vereins_map[verein] = dict()
                if mannschaft not in vereins_map[verein]:
                    general_data = GeneralData(
                        "" if pd.isna(mannschaft) else mannschaft,
                        "" if pd.isna(m_row["Spielklasse"]) else m_row["Spielklasse"],
                        "" if pd.isna(m_row["Liga"]) else m_row["Liga"],
                        "" if pd.isna(m_row["Bezirk"]) else m_row["Bezirk"],
                        "" if pd.isna(m_row["Spielführer"]) else m_row["Spielführer"],
                        "" if pd.isna(m_row["Betreuer"]) else m_row["Betreuer"],
                        "" if pd.isna(m_row["Vereinsnummer"]) else m_row["Vereinsnummer"],
                        "" if pd.isna(m_row["LV-Nummer"]) else m_row["LV-Nummer"],
                        -1,
                        "" if pd.isna(m_row["Verein"]) else m_row["Verein"],
                        "" if pd.isna(m_row["Verein Kurz"]) else m_row["Verein Kurz"],
                    )
                    vereins_map[verein][mannschaft] = (general_data, list())
                try:
                    vereins_map[verein][mannschaft][1].append(PlayerData.create_player_from_csv(s_row))
                except ValueError as _:
                    logging.warning(f"Spieler in {mannschaft} nicht verarbeitbar. War in Zeile {index}", )
                    continue
                break
    # create internal data structure
    map_to_internal_representation(vereine, vereins_map, min_placeholder, num_min_players)
    # write files
    for verein in vereine:
        for mannschaft in verein.mannschaften:
            write_mannschaft_file_from_mannschaft_data(mannschaft.file_name, mannschaft, encoding=encoding)


def map_to_internal_representation(vereine: list[VereinsData],
                                   vereins_map: dict[str, dict[str, tuple[GeneralData, [list[PlayerData]]]]],
                                   min_placeholder: int, num_min_players: int):
    """
    Map the data from the csv files to the internal data structure
    :param vereine: list of VereinsData objects
    :type vereine: list[VereinsData]
    :param vereins_map: dictionary with the VereinsData objects
    :type vereins_map: dict[str, dict[str, tuple[GeneralData, [list[PlayerData]]]]]
    :param min_placeholder: Minimum number of Platzhalter players. Default is 0
    :type min_placeholder: int
    :param num_min_players: Minimum number of players. If the number of players in the csv file is less than
    this number, Platzhalter players will be added. Default is 10
    :type num_min_players: int
    :return: None
    """
    for vereins_name, vereine_raw in vereins_map.items():
        mannschaften_list = list()
        for mannschaft_name, mannschaften_raw in vereine_raw.items():
            gen_data, players = mannschaften_raw
            correct_name = get_final_name_for_mannschaften_file(vereins_name, mannschaft_name)
            general_data = gen_data
            general_data.anzahl_spieler = max(len(players), num_min_players)
            num_platzhalter = 0
            if len(players) < num_min_players:
                num_platzhalter = 0
                for i in range(1, num_min_players - len(players) + 1):
                    players.append(PlayerData.create_platzhalter(i))
                    num_platzhalter += 1
            if num_platzhalter < min_placeholder:
                for i in range(num_platzhalter + 1, min_placeholder + 1):
                    players.append(PlayerData.create_platzhalter(i))
            general_data.name = correct_name
            mannschaften_list.append(MannschaftData(correct_name, general_data, players))
        vereinsdata = VereinsData(vereins_name, mannschaften_list)
        vereine.append(vereinsdata)


def print_options(with_input: bool = False) -> str:
    print(f"""    1 - Neue Mannschaft erstellen (als Input mit Spieler.csv)
    2 - Mannschaft neu einlesen und korrigieren
    3 - Mannschaften aus CSV einlesen (mit Platzhaltern)
    4 - Alle Mannschaften korrigieren (mit Platzhaltern)
    - {RED}Export{ENDC} -
    5 - Exportiere eine Mannschaft als CSV
    6 - Exportiere alle Mannschaften als CSV
    
    end - Programm beenden""")
    if with_input:
        return input("Wahl: ")
    return ""


def export_single_mannschaft(file_name: str = None):
    if file_name is None:
        file_name = input("Name der Mannschaft: ")
        if file_name.endswith(".ini"):
            file_name = file_name[:-4]
    directory = Path(DEFAULT_DATA_PATH)
    if not directory.joinpath("name").exists():
        logging.error(f"File {file_name}.ini does not exist")
        return
    export_name = input("Name der Exportdatei: ")
    if export_name in ["", " ", "\n", "\t", ":", "/"]:
        export_name = file_name
    data = read_finished_mannschaften(directory.joinpath(file_name))
    write_csv_from_mannschaft_data(data, export_name)


def export_all_mannschaften():
    try:
        mannschaften = read_folder_mannschaften(DEFAULT_DATA_PATH, False)
        write_csv_with_all_mannschaften(mannschaften)
    except FileNotFoundError:
        logging.error("Abbruch. Keine Mannschaften gefunden.")


def correct_all_mannschaften_in_dir():
    while (name_after_team := input("Datei soll wie Mannschaft heißen? (default=Y): ")) not in ["", "Y", "n"]:
        logging.warning("Ungültige Eingabe. Bitte y(es) oder n(o) eingeben.")
    name_after_team = name_after_team[0].lower()
    name_after_team = name_after_team == "" or name_after_team == "y"
    path = input(r"""Path to folder with Mannschaften files:
            Default is C:\Control Center Kegeln\Einstellungen\Mannschaften
            Path:""")
    path = path if path != "" else DEFAULT_DATA_PATH
    mannschaften = read_folder_mannschaften(path, True)
    for mannschaft in mannschaften:
        if name_after_team:
            mannschaft.file_name = mannschaft.general_data.name
        write_mannschaft_file_from_mannschaft_data(mannschaft.file_name, mannschaft)
    import_new_mannschaften(min_placeholder=3)


def import_mannschaft_from_csv():
    while (placeholder := input("Minimale Anzahl Platzhalter (default=3): ")).isdigit() and int(placeholder) < 0:
        logging.warning("Ungültige Eingabe. Bitte Zahl eingeben.")
    placeholder = int(placeholder) if placeholder != "" else 3
    import_new_mannschaften(min_placeholder=placeholder)


def cli_handle():
    print(f"""Mannschaften-KorrekturSystem ({BLUE}MKS{ENDC})
{GREEN}===================================={ENDC}""")
    while True:
        while (wahl := print_options(True)) not in ["1", "2", "3", "4", "5", "6", "end"]:
            logging.warning("Ungültige Eingabe. Bitte Zahl eingeben.")
        match wahl:
            case "1":
                create_new_mannschaft()
            case "2":
                rewrite_mannschaft()
            case "3":
                import_mannschaft_from_csv()
            case "4":
                correct_all_mannschaften_in_dir()
            case "5":
                export_single_mannschaft()
            case "6":
                export_all_mannschaften()
            case "end":
                print(f"""Beende Programm. 
    {GREEN}Gut Holz!{ENDC}""")
                exit(0)


if __name__ == '__main__':
    cli_handle()
