import logging
from pathlib import Path

import pandas as pd

from mannschaft import MannschaftData


def read_csv(name: str = "Mannschaften", sep: str = ";") -> pd.DataFrame:
    """
    Read a csv file with the given name and return a pandas DataFrame
    The encoding is set to utf-8 and the header is set to 0
    :param sep: separator of the csv file. Default is ";"
    :type sep: str
    :param name: name of the csv file without the .csv ending
    :type name: str
    :return: pandas DataFrame with the data from the csv file
    :rtype: pd.DataFrame
    """
    if not name.endswith(".csv"):
        name = f"{name}.csv"
    df = pd.read_csv(name, sep=sep, encoding='utf-8', header=0)
    return df


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
    if not name.endswith(".csv"):
        name = f"{name}.csv"
    if not Path("out").exists():
        Path("out").mkdir()
    df.to_csv(f'out/{name}', sep=';', encoding='utf-8', index=False)


def _create_mannschaft_csv(mannschaft: MannschaftData, name: str) -> None:
    """
    Create a csv file (Spieler.csv) with the given MannschaftData object
    :param mannschaft: MannschaftData
    :type mannschaft: MannschaftData
    """
    frame = mannschaft.players_as_dataframe()
    if not Path("out").exists():
        Path("out").mkdir()
    frame.to_csv(name, sep=";", encoding="utf-8", index=False)


def write_csv_from_mannschaft_data(mannschaft: MannschaftData, name: str = None) -> None:
    if name is None:
        name = mannschaft.file_name
    if not name.endswith(".csv"):
        name = f"{name}.csv"
    _create_mannschaft_csv(mannschaft, name)


def write_csv_with_all_mannschaften(mannschaften: list[MannschaftData]) -> None:
    """
    Write a csv file with all given MannschaftData
    :param mannschaften: list of MannschaftData
    :type mannschaften: list[MannschaftData]
    """
    if not Path("out").exists():
        Path("out").mkdir()
    complete_frame_spieler = pd.DataFrame()
    complete_frame_mannschaften = pd.DataFrame()
    for mannschaft in mannschaften:
        spieler_frame = mannschaft.players_as_dataframe()
        complete_frame_spieler = pd.concat([complete_frame_spieler, spieler_frame])
        mannschaft_frame = mannschaft.mannschaft_as_dataframe()
        complete_frame_mannschaften = pd.concat([complete_frame_mannschaften, mannschaft_frame])
    today = pd.Timestamp.today().strftime("%Y-%m-%d-%H-%M")
    logging.info(f"Writing to out/Spieler_{today}.csv")
    complete_frame_spieler.to_csv(f"out/Spieler_{today}.csv", sep=";", encoding="utf-8", index=False)
    logging.info(f"Writing to out/Mannschaften_{today}.csv")
    complete_frame_mannschaften.to_csv(f"out/Mannschaften_{today}.csv", sep=";", encoding="utf-8", index=False)
