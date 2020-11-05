import os
import json
import unittest
import requests

import webapi.konst as cst


API_ENDPOINT = "http://localhost:8000/api/"
DB_DATA_PATH = "C:\\Users\\woos8\\Documents\\GitHub\\DGU2020_covid_database\\database"

REQUEST_HEADER = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

TEST_SEQ_FILE_NAMES = (
    "wuhan.fasta",
    "versus.fasta",
    "first_test_data.fasta",
    "second_test_data.fasta",
)

def _send_post_req(url, data):
    r = requests.post(url=url, json=data, headers=REQUEST_HEADER)
    return json.loads(r.text)

def _send_get_req(url, data=None):
    r = requests.get(url=url, json=data, headers=REQUEST_HEADER)
    return json.loads(r.text)


class TestWebAPI(unittest.TestCase):
    def test_get_similar_seq_ids(self):
        # It failes with 'second_test_data.fasta'

        for file_name in TEST_SEQ_FILE_NAMES:
            print(file_name)
            with open(os.path.join(DB_DATA_PATH, file_name), "r") as file:
                fasta_str = file.read()

            response_data = _send_post_req(API_ENDPOINT + "get_similar_seq_ids/", {
                cst.KEY_SEQUENCE: fasta_str,
                cst.KEY_HOW_MANY: 10,
            })
            print(response_data)

            self.assertEqual(response_data[cst.KEY_ERROR_CODE], 0)
            self.assertEqual(len(response_data[cst.KEY_ACC_ID_LIST]), 10)

    def test_get_metadata_of_seq(self):
        acc_id = "EPI_ISL_426879"
        params = {
            cst.KEY_ACC_ID: acc_id,
            cst.KEY_COLUMN_LIST: [],
        }

        response_data = _send_post_req(API_ENDPOINT + "get_metadata_of_seq/", params)
        print(response_data[cst.KEY_METADATA])

        self.assertEqual(response_data[cst.KEY_ERROR_CODE], 0)
        self.assertEqual(response_data[cst.KEY_METADATA]["acc_id"], acc_id)

    def test_calc_similarity_of_two_seq(self):
        with open(os.path.join(DB_DATA_PATH, "wuhan.fasta"), "r") as file:
            seq_1 = file.read()
        with open(os.path.join(DB_DATA_PATH, "versus.fasta"), "r") as file:
            seq_2 = file.read()

        response_data = _send_post_req(API_ENDPOINT + "calc_similarity_of_two_seq/", {
            cst.KEY_SEQUENCE_LIST: [seq_1, seq_2]
        })

        self.assertEqual(response_data[cst.KEY_ERROR_CODE], 0)
        self.assertEqual(int(response_data[cst.KEY_SIMILARITY_IDENTITY]), 99)
        self.assertEqual(int(response_data[cst.KEY_SIMILARITY_BIT_SCORE]), 55231)

    def test_get_all_acc_ids(self):
        response_data = _send_get_req(API_ENDPOINT + "get_all_acc_ids/")
        acc_id_list = response_data[cst.KEY_ACC_ID_LIST]

        self.assertEqual(response_data[cst.KEY_ERROR_CODE], 0)
        print(acc_id_list)
        self.assertTrue(len(acc_id_list) > 1000)

    def test_find_mutations(self):
        for i in range(len(TEST_SEQ_FILE_NAMES)):
            for j in range(i + 1, len(TEST_SEQ_FILE_NAMES)):
                name_1 = TEST_SEQ_FILE_NAMES[i]
                name_2 = TEST_SEQ_FILE_NAMES[j]
                print("'{}' vs '{}'".format(name_1, name_2))

                with open(os.path.join(DB_DATA_PATH, name_1), "r") as file:
                    seq_1 = file.read()
                with open(os.path.join(DB_DATA_PATH, name_2), "r") as file:
                    seq_2 = file.read()

                response_data = _send_get_req(API_ENDPOINT + "find_mutations/", {
                    cst.KEY_SEQUENCE_LIST: [seq_1, seq_2],
                })

                self.assertEqual(response_data[cst.KEY_ERROR_CODE], 0)
                print(response_data)


if __name__ == '__main__':
    unittest.main()
