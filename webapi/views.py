import os
import traceback
from typing import Dict, Type, Optional

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.exceptions import ParseError

import dgucovidb.db_interface as bst
import dgucovidb.sql_interface as sql

from . import konst as cst


BLAST_INTERF = bst.InterfBLAST(cst.BLAST_DB_PATH)
MYSQL_INTERF = sql.InterfMySQL(cst.MYSQL_USERNAME, cst.MYSQL_PASSWORD)


class ErrorMap:
    def __init__(self):
        self.__map: Dict[int, str] = {}

        self.add_spec_dict({
            1: "Unkown error",
            2: "Invalid request payload",
            3: "Key '{}' not found",
            4: "Expected '{}' to be a '{}', got '{}' instead",  # Wrong type for a value
            5: "Failed to generate BLAST query result",
            6: "Invalid json syntax",
        })

    def __getitem__(self, err_code: int):
        return self.get_message(err_code)

    def add_spec(self, err_code: int, err_message: str):
        assert isinstance(err_code, int)
        assert isinstance(err_message, str)

        if err_code in self.__map.keys():
            raise RuntimeError("Tried to add a key which was already registered")

        self.__map[err_code] = err_message

    def add_spec_dict(self, specs: Dict[int, str]):
        for k, v in specs.items():
            self.add_spec(k, v)

    def get_message(self, err_code: int):
        return self.__map[err_code]


ERROR_MAP = ErrorMap()


# Returns None if the payload is valid
def _validate_request_payload(req: Request, criteria: Dict[str, Type]) -> Optional[dict]:
    try:
        payload = req.data
    except ParseError:
        return {
            cst.KEY_ERROR_CODE: 6,
            cst.KEY_ERROR_TEXT: ERROR_MAP[6]
        }

    if not isinstance(payload, dict):
        return {cst.KEY_ERROR_CODE: 2, cst.KEY_ERROR_TEXT: ERROR_MAP[2]}

    for key_name, value_type in criteria.items():
        if key_name not in payload.keys():
            return {
                cst.KEY_ERROR_CODE: 3,
                cst.KEY_ERROR_TEXT: ERROR_MAP[3].format(key_name)
            }

        maybe_value = payload[key_name]
        if not isinstance(maybe_value, value_type):
            return {
                cst.KEY_ERROR_CODE: 4,
                cst.KEY_ERROR_TEXT: ERROR_MAP[4].format(
                    cst.KEY_HOW_MANY, value_type.__name__, type(maybe_value).__name__
                )
            }

    return None


class Echo(APIView):
    @staticmethod
    def get(_: Request, __=None):
        return Response("No input")

    @staticmethod
    def post(request: Request, _=None):
        return Response(request.data)


class SimilarSeqIDs(APIView):
    @staticmethod
    def post(request: Request, _=None):
        if not isinstance(request.data, dict):
            return Response("invalid input")

        try:
            input_sequence = str(request.data["seq"])
            how_many = int(request.data["how_many"])
        except KeyError:
            return Response("no input found")
        except ValueError:
            return Response("invalid input")

        input_sequence = "".join(input_sequence.split('\n'))
        result_file_name = "result.tmp"

        print("[] started blast query")
        if not BLAST_INTERF.gen_query_result(input_sequence, result_file_name):
            return Response("failed to generate BLAST query result")

        print("[] started finding similar ids")
        ids = BLAST_INTERF.find_ids_of_the_similars(result_file_name, how_many)

        os.remove(result_file_name)

        result: Dict[str: Dict] = {}
        for acc_id in ids:
            result[acc_id] = MYSQL_INTERF.get_metadata_of(acc_id)

        return Response(result)


class GetSimilarSeqIDs(APIView):
    """
    Requst payload must have following fields
    * sequence: string -> A DNA sequence of covid19
    * how_many: number ->

    On success, it responds with following fields
    * acc_id_list: array[string] -> List of sequence IDs which represent sequences that are similar to input sequence
                                    by client
    * error_code: number -> It should be 0

    Meanwhile on failure, the reponse payload contains followings
    * error_code: number -> It can be any integer number but 0
    * error_text: string -> Refer to local variable "ERROR_MAP" for details
    """

    @staticmethod
    def post(request: Request, _=None):
        try:
            #### Validate client input ####

            validate_result = _validate_request_payload(request, {
                cst.KEY_SEQUENCE: str,
                cst.KEY_HOW_MANY: int,
            })
            if validate_result is not None:
                return Response(validate_result)

            seq = str(request.data[cst.KEY_SEQUENCE])
            how_many = int(request.data[cst.KEY_HOW_MANY])

            #### Work ####

            result_file_name = "result.tmp"
            print("[] started blast query")
            if not BLAST_INTERF.gen_query_result(seq, result_file_name):
                os.remove(result_file_name)
                return Response({cst.KEY_ERROR_CODE: 5, cst.KEY_ERROR_TEXT: ERROR_MAP[5]})
            print("[] finished blast query")

            ids = BLAST_INTERF.find_ids_of_the_similars(result_file_name, how_many)
            print("[] ids foind: {}".format(ids))
            os.remove(result_file_name)

            return Response({
                cst.KEY_ACC_ID_LIST: ids,
                cst.KEY_ERROR_CODE: 0,
            })

        except:
            traceback.print_exc()
            return Response({
                cst.KEY_ERROR_CODE: 1,
                cst.KEY_ERROR_TEXT: ERROR_MAP[1],
            })
