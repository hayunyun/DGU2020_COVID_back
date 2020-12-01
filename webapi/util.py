import csv
from typing import List


class LatLngFinder:
    __ALTERNATIVE_NAME = {
        "republic of the congo": (
            "Congo [Republic]",
        ),
        "democratic republic of the congo": (
            "Congo [DRC]",
        ),
        "usa": (
            "United States",
        ),
        "myanmar": (
            "Myanmar [Burma]",
        ),
        "north macedonia": (
            "Macedonia [FYROM]",
        ),
        "palestine": (
            "Palestinian Territories",
        ),
    }

    def __init__(self, csv_file_path: str):
        self.__data = self.__load_data(csv_file_path)

    def find_by_country(self, country_name: str):
        country_name = country_name.lower()
        if country_name in self.__data.keys():
            return self.__data[country_name]

        return None

    def find_by_name_candidates(self, country_name_candidates: List[str]):
        for x in country_name_candidates:
            x = x.lower()
            if x in self.__data.keys():
                return self.__data[x]

        return None

    def find_with_alternatives(self, country_name: str):
        name_candidates = [country_name]
        if country_name in self.__ALTERNATIVE_NAME.keys():
            name_candidates += self.__ALTERNATIVE_NAME[country_name]

        return self.find_by_name_candidates(name_candidates)

    @staticmethod
    def __load_data(csv_file_path: str):
        result = {}

        with open(csv_file_path, "r", newline="", encoding="utf8") as file:
            spamreader = csv.reader(file, delimiter=",", quotechar='|')
            for row in spamreader:
                try:
                    lat = float(row[1])
                    lng = float(row[2])
                    country = str(row[3]).lower()
                except ValueError:
                    pass
                else:
                    result[country] = (lat, lng)

        return result
