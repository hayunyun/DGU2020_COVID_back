import os

import dgucovidb.db_interface as dgu
import dgucovidb.sql_interface as sql


DB_PATH = "./../database/blast"


def open_fasta(file_path: str) -> str:
    result = ""
    with open(file_path, "r") as f:
        while True:
            line = f.readline()

            if len(line) == 0:
                break

            if ">" in line:
                continue

            result += line

    return result


def main():
    blast = dgu.InterfBLAST(DB_PATH)
    sqldb = sql.InterfMySQL("dgucovid", "COVID@dgu2020")

    try:
        blast.create_db("./../extern/DGU2020_covid_database/database/gisaid_hcov-19_2020_06_29_03.fasta")
    except FileExistsError:
        print("the db already exists")

    test_data = open_fasta("./../extern/DGU2020_covid_database/database/second_test_data.fasta")
    if not os.path.isfile("result.tmp"):
        print("start query")
        blast.gen_query_result(test_data, "result.tmp")

    print("start fetch")
    result1 = blast.find_ids_of_the_similars("result.tmp", 10)
    print(result1)
    result2 = sqldb.get_metadata_of(result1[0])
    print(result2)


if __name__ == '__main__':
    main()
