import os
import traceback
from typing import Dict

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request

import dgucovidb.db_interface as bst
import dgucovidb.sql_interface as sql


# This path is relative to the repo root path where manage.py is located
BLAST_INTERF = bst.InterfBLAST("./database/blast")
MYSQL_INTERF = sql.InterfMySQL("dgucovid", "COVID@dgu2020")

KEY_SEQ = "seq"
KEY_SEQ_ID = "seq_id"
KEY_SEQ_ID_LIST = "seq_id_list"

KEY_HOW_MANY = "how_many"

KEY_ERROR_CODE = "error_code"
KEY_ERROR_TEXT = "error_text"


class TestList(APIView):
    def get(self, request, format_arg=None):
        print("BLAST:", BLAST_INTERF.does_db_exists())
        return Response([1, 2, 3])


class Echo(APIView):
    def get(self, request: Request, format_arg=None):
        return Response("No input")

    def post(self, request: Request, format_arg=None):
        return Response(request.data)


class SimilarSeqIDs(APIView):
    def post(self, request: Request, format_arg=None):
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
    * seq: string -> A DNA sequence of covid19
    * how_many: number ->

    On success, it responds with following fields
    * seq_id_list: array[string] -> List of sequence IDs which represent sequences that are similar to input sequence by client
    * error_code: number -> It should be 0

    Meanwhile on failure, the reponse payload contains followings
    * error_code: number -> It can be any integer number but 0
    * error_text: string -> Refer to local variable "ERROR_MAP" for details
    """
    def post(self, request: Request, format_arg=None):
        ERROR_MAP = {
            1: "Unkown error",
            2: "Invalid request payload",
            3: "Key '{}' not found",
            4: "Expected '{}' to be a '{}', got '{}' instead",  # Wrong type for a value
            5: "Failed to generate BLAST query result",
        }

        try:
            #### Validate client input ####

            if not isinstance(request.data, dict):
                return Response({KEY_ERROR_CODE: 2, KEY_ERROR_TEXT: ERROR_MAP[2]})

            payload: dict = request.data
            if KEY_SEQ not in payload.keys():
                return Response({
                    KEY_ERROR_CODE: 3,
                    KEY_ERROR_TEXT: ERROR_MAP[3].format(KEY_SEQ)
                })
            if KEY_HOW_MANY not in payload.keys():
                return Response({
                    KEY_ERROR_CODE: 3,
                    KEY_ERROR_TEXT: ERROR_MAP[3].format(KEY_HOW_MANY)
                })

            maybe_seq = payload[KEY_SEQ]
            try:
                seq = str(maybe_seq)
            except:
                return Response({
                    KEY_ERROR_CODE: 4,
                    KEY_ERROR_TEXT: ERROR_MAP[4].format(KEY_SEQ, "str", type(maybe_seq))
                })

            maybe_how_many = payload[KEY_HOW_MANY]
            try:
                how_many = int(maybe_how_many)
            except:
                return Response({
                    KEY_ERROR_CODE: 4,
                    KEY_ERROR_TEXT: ERROR_MAP[4].format(KEY_HOW_MANY, "int", type(maybe_how_many))
                })

            #### Work ####

            result_file_name = "result.tmp"
            print("[] started blast query")
            if not BLAST_INTERF.gen_query_result(seq, result_file_name):
                os.remove(result_file_name)
                return Response({KEY_ERROR_CODE: 5, KEY_ERROR_TEXT: ERROR_MAP[5]})
            print("[] finished blast query")

            ids = BLAST_INTERF.find_ids_of_the_similars(result_file_name, how_many)
            print("[] ids foind: {}".format(ids))
            os.remove(result_file_name)

            return Response({
                KEY_SEQ_ID_LIST: ids,
                KEY_ERROR_CODE: 0,
            })

        except:
            traceback.print_exc()
            return Response({
                KEY_ERROR_CODE: 1,
                KEY_ERROR_TEXT: ERROR_MAP[1],
            })
