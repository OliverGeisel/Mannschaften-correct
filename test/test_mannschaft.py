import datetime
from unittest import TestCase

from mannschaft import PlayerData


class TestPlayerData(TestCase):

    def test_create_player_data(self):
        new_player = PlayerData("Spielmacher", "Jens", "", "Platz-Ziffer", "Spielernr.", datetime.date(2023, 1, 20),
                                "Altersklasse", "D123456", "Rangliste", "Super Verein")
        self.assertEqual(new_player.name, "Spielmacher")
        self.assertEqual(new_player.vorname, "Jens")
        self.assertEqual(new_player.letztes_spiel, "")
        self.assertEqual(new_player.platz_ziffer, "Platz-Ziffer")
        self.assertEqual(new_player.spielernr, "Spielernr.")
        self.assertEqual(new_player.geburtsjahr, datetime.date(2023, 1, 20))
        self.assertEqual(new_player.altersklasse, "Altersklasse")
        self.assertEqual(new_player.passnummer, "D123456")
        self.assertEqual(new_player.rangliste, "Rangliste")
        self.assertEqual(new_player.verein, "Super Verein")

    def test_valid_player(self):
        new_player = PlayerData("Spielmacher", "Jens", "", "Platz-Ziffer", "Spielernr.", datetime.date(2023, 1, 20),
                                "Altersklasse", "D123456", "Rangliste", "Super Verein")
        self.assertTrue(new_player.valid)

    def test_invalid_player_name(self):
        player = PlayerData("", "Jens", "", "Platz-Ziffer", "Spielernr.", datetime.date(2023, 1, 20),
                            "Altersklasse", "D123456", "Rangliste", "Super Verein")
        self.assertFalse(player.valid)

    def test_invalid_player_vorname(self):
        player = PlayerData("Spielmacher", "", "", "Platz-Ziffer", "Spielernr.", datetime.date(2023, 1, 20),
                            "Altersklasse", "D123456", "Rangliste", "Super Verein")
        self.assertFalse(player.valid)

    def test_invalid_player_geb_date(self):
        player = PlayerData("Spielmacher", "Jens", "", "Platz-Ziffer", "Spielernr.", datetime.date(2023, 1, 20),
                            "Altersklasse", "D123456", "Rangliste", "Super Verein")
        player.geburtsjahr = "2023-01-20"
        self.assertFalse(player.valid)


class TestGeneralData(TestCase):

    def test_get_general_data(self):
        pass
