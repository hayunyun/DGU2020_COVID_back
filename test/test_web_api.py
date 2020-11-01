import os
import json
import unittest
import requests

import webapi.konst as cst


API_ENDPOINT = "http://localhost:8000/api/"
DB_DATA_PATH = "./../extern/DGU2020_covid_database/database"


def _send_post_req(url, data):
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    r = requests.post(url=url, json=data, headers=headers)
    return json.loads(r.text)


class TestWebAPI(unittest.TestCase):
    def test_get_similar_seq_ids(self):
        expected_result = {
            'acc_id_list': {
                'EPI_ISL_426879': {'simil_identity': 100.0, 'simil_bit_score': 51926},
                'EPI_ISL_468579': {'simil_identity': 99.86518129567871, 'simil_bit_score': 51915},
                'EPI_ISL_454326': {'simil_identity': 99.86518129567871, 'simil_bit_score': 51915},
                'EPI_ISL_454625': {'simil_identity': 99.86518129567871, 'simil_bit_score': 51915},
                'EPI_ISL_454631': {'simil_identity': 99.86518129567871, 'simil_bit_score': 51915},
                'EPI_ISL_454334': {'simil_identity': 99.86518129567871, 'simil_bit_score': 51915},
                'EPI_ISL_454335': {'simil_identity': 99.86518129567871, 'simil_bit_score': 51915},
                'EPI_ISL_468948': {'simil_identity': 99.86518129567871, 'simil_bit_score': 51915},
                'EPI_ISL_420993': {'simil_identity': 99.86518129567871, 'simil_bit_score': 51915},
                'EPI_ISL_468921': {'simil_identity': 99.86518129567871, 'simil_bit_score': 51915}
            },
            'error_code': 0
        }

        with open(os.path.join(DB_DATA_PATH, "first_test_data.fasta"), "r") as file:
            fasta_str = file.read()

        response_data = _send_post_req(API_ENDPOINT + "get_similar_seq_ids/", {
            cst.KEY_SEQUENCE: fasta_str,
            cst.KEY_HOW_MANY: 10,
        })

        self.assertEqual(response_data[cst.KEY_ERROR_CODE], 0)
        self.assertEqual(len(response_data[cst.KEY_ACC_ID_LIST]), 10)
        for x in response_data[cst.KEY_ACC_ID_LIST].keys():
            self.assertTrue(x in expected_result[cst.KEY_ACC_ID_LIST].keys())

    def test_get_metadata_of_seq(self):
        acc_id = "EPI_ISL_426879"
        params = {
            cst.KEY_ACC_ID: acc_id,
            cst.KEY_COLUMN_LIST: [],
        }

        response_data = _send_post_req(API_ENDPOINT + "get_metadata_of_seq/", params)

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


if __name__ == '__main__':
    unittest.main()
