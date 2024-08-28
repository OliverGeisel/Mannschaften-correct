from pathlib import Path


def run():
    input_response = "y"
    if Path("Mannschaften.csv").exists():
        print("Files already exist")
        input_response = input("Overwrite?[yes|NO]")[0].lower()
    if input_response == "y":
        # Create Mannschaften.csv file
        with (open("Mannschaften.csv", "w", encoding="utf-8") as file):
            columns = ["Verein", "Mannschaft", "Bezirk", "Ort", "Liga", "Spielklasse", "Spielführer", "Betreuer",
                       "Vereinsnummer", "LV-Nummer", "Land", "Verein Kurz"]
            file.write(";".join(columns))
    if Path("Spieler.csv").exists():
        print("Files already exist")
        input_response = input("Overwrite?[yes|NO]")[0].lower()
    if input_response == "y":
        with open("Spieler.csv", "w", encoding="utf-8") as file:
            columns = ["Vorname", "Name", "Geburtsdatum", "Geschlecht", "Altersklasse", "Passnummer", "Verein",
                       "Mannschaft", "Verein_angehörig"]
            file.write(";".join(columns))
    print("Files created")


run()
