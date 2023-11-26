import logging
from pathlib import Path

import pandas as pd

from exceptions import FileIncompleteError
from ini_files import get_general_info_str_from_input, get_player_str, platzhalter_player_str, \
    read_finished_mannschaften, write_mannschaft_file_from_mannschaft_data
from mannschaft import MannschaftData, PlayerData, VereinsData, GeneralData


def read_csv(name: str = "Mannschaften", sep: str = ";") -> pd.DataFrame:
    """
    Read a csv file with the given name and return a pandas DataFrame
    :param sep: separator of the csv file. Default is ";"
    :type sep: str
    :param name: name of the csv file without the .csv ending
    :type name: str
    :return: pandas DataFrame with the data from the csv file
    :rtype: pd.DataFrame
    """
    df = pd.read_csv(f'{name}.csv', sep=sep, encoding='utf-8', header=0)
    return df


def load_mannschaften_csv(sep=";") -> pd.DataFrame:
    return read_csv(sep=sep)


def load_spieler_csv(sep=";") -> pd.DataFrame:
    return read_csv("Spieler", sep=sep)


def write_csv(players: list[dict], name: str = "Mannschaften") -> None:
    """
    Write a csv file with the given name and the given data
    :param players: players to write to the csv file
    :type players:  list[dict]
    :param name: name of the csv file without the .csv ending
    :type name: str
    :return: None
    :rtype: None
    """
    df = pd.DataFrame(players)
    if not Path("out").exists():
        Path("out").mkdir()
    df.to_csv(f'out/{name}.csv', sep=';', encoding='utf-8', index=False)


def write_csv_from_mannschaft_data(mannschaft: MannschaftData, name: str = "Mannschaften") -> None:
    data = [{"Nachname": player.name, "Vorname": player.vorname, "Geburtsdatum": player.get_geburtsjahr_str(),
             "Passnummer": player.passnummer, "Altersklasse": player.altersklasse, "Verein": player.verein}
            for player in mannschaft.players]
    write_csv(data, name)


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
    """
    folder = Path(folder_name)
    files = [file for file in folder.iterdir() if file.suffix == ".ini"]
    mannschaften_list = []
    for file in files:
        try:
            mannschaften_list.append(read_finished_mannschaften(file))
        except FileIncompleteError or ValueError:
            continue
    if print_teams:
        for mannschaft in mannschaften_list:
            print(mannschaft)
    return mannschaften_list


def write_mannschaft_file_input(file_name: str, csv_name: str = "Mannschaften", anzahl_spieler: int = 10,
                                sort: bool = True, encoding="utf-8") -> None:
    if file_name.endswith(".ini"):
        file_name = file_name[:-4]
    if not Path(f"out").exists():
        Path(f"out").mkdir()
    if Path(f"out/{file_name}.ini").exists():
        logging.warning(f"File {file_name}.ini already exists. Overwriting.")
    with open(f"out/{file_name}.ini", "w", encoding=encoding) as f:
        f.write(get_general_info_str_from_input(file_name))
        i = 0
        players = []
        for index, row in read_csv(csv_name).iterrows():
            if i >= anzahl_spieler:
                break
            if pd.isna(row).max():
                continue
            try:
                players.append(PlayerData.create_player_from_csv(row))
            except ValueError:
                continue
            i += 1
        # sort and complete with platzhalter players
        if sort:
            players = sorted(players, key=lambda x: x.name)
        for j, player in enumerate(players):
            try:
                f.write(get_player_str(j, player))
            except ValueError:
                logging.warning(
                    f"Could not write player {player.name} {player.vorname} {player.geburtsjahr}. Date format "
                    f"is unknown \nSkipping player.")
                continue
        if i < anzahl_spieler:
            for j in range(i, anzahl_spieler):
                f.write(platzhalter_player_str(j))


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
    mannschaft = read_finished_mannschaften(Path(f"{name}.ini"))
    new_name = name if new_name is None else new_name
    write_mannschaft_file_from_mannschaft_data(new_name, mannschaft, encoding="windows-1252")


def create_new_mannschaft():
    name = input("Name der Mannschaft: ")
    write_mannschaft_file_input(name, encoding="windows-1252")


def rewrite_mannschaft():
    name = input("Name der Mannschaft: ")
    new_name = input("Neuer Name: ")
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


def import_new_mannschaften(num_min_players: int = 10, min_placeholder: int = 0, encoding="windows-1252"):
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
    :return: None
    :rtype:  None
    """
    spieler_csv = load_spieler_csv()
    mannschaften_csv = load_mannschaften_csv()
    vereine: list[VereinsData] = list()
    vereins_map: dict[str, dict[str, tuple[GeneralData, [list[PlayerData]]]]] = dict()

    for index, row in spieler_csv.iterrows():
        verein = row["Verein"]
        spieler_mannschaft = row["Mannschaft"]
        for m_index, m_row in mannschaften_csv.iterrows():
            mannschaft = m_row["Mannschaft"]
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
                    vereins_map[verein][mannschaft][1].append(PlayerData.create_player_from_csv(row))
                except ValueError as e:
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


if __name__ == '__main__':
    # create_new_mannschaft()
    # rewrite_mannschaft()
    import_new_mannschaften(min_placeholder=3)
    # mannschaften = read_folder_mannschaften("C:\\Control Center Kegeln\\Einstellungen\\Mannschaften - Kopie", True)
