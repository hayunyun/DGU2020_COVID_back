import os
import time
import json

import dgucovidb.db_interface as bst
import dgucovidb.sql_interface as sql

import webapi.konst as cst


BLAST_INTERF = bst.InterfBLAST(cst.BLAST_DB_PATH)
MYSQL_INTERF = sql.InterfMySQL(cst.MYSQL_USERNAME, cst.MYSQL_PASSWORD)
CACHE_FOL_PATH = "./../../../database/cache"


def generate_cases_per_places(folder_path: str):
    start_time = time.time()

    division_types = ("region", "country", "division")
    result_dict = {divi_type: {} for divi_type in division_types}

    conn, cursor = MYSQL_INTERF.create_connection_cursor()

    strain_list = MYSQL_INTERF.get_all_strains()
    for i, strain in enumerate(strain_list):
        if i % 1000 == 0:
            elapsed_time = time.time() - start_time
            duration_per_one = elapsed_time / max(i, 1)
            remaining_ones = len(strain_list) - i
            remaining_time = remaining_ones * duration_per_one
            print("{} / {} ({:.2%}) {:.2f} sec remaining".format(
                i, len(strain_list), i / len(strain_list), remaining_time
            ))

        cursor.execute(
            f"SELECT m.*, s.sequence from meta_data as m, "
            f"sequences as s where m.strain = s.strain and m.strain = '{strain}';"
        )
        metadata = cursor.fetchone()
        if metadata is None:
            continue

        for divi_type in division_types:
            try:
                value = metadata[divi_type]
            except KeyError:
                pass
            else:
                value = str(value).strip().lower()
                divi_dict = result_dict[divi_type]
                if value in divi_dict.keys():
                    divi_dict[value] += 1
                else:
                    divi_dict[value] = 1

    cursor.close()
    conn.close()

    for divi_type in division_types:
        file_path = os.path.join(folder_path, "cases_per_{}.json".format(divi_type))
        print(result_dict[divi_type])
        with open(file_path, "w") as file:
            json.dump(result_dict[divi_type], file, indent=4)
        print("Saved:", file_path)


def main():
    if not os.path.isdir(CACHE_FOL_PATH):
        os.mkdir(CACHE_FOL_PATH)

    generate_cases_per_places(CACHE_FOL_PATH)


if __name__ == '__main__':
    main()
