import os
import time
import shutil
import traceback
from typing import Dict, Type, Optional

import pymysql
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.exceptions import ParseError

import dgucovidb.db_interface as bst
import dgucovidb.sql_interface as sql
import dgucovidb.fasta_tool as fat
import dgucovidb.tmpCreator_interface as tmpFile
import dgucovidb.mutation_interface as mut

from . import konst as cst


BLAST_INTERF = bst.InterfBLAST(cst.BLAST_DB_PATH)
MYSQL_INTERF = sql.InterfMySQL(cst.MYSQL_USERNAME, cst.MYSQL_PASSWORD)


def _convert_to_seq_if_fasta(maybe_seq) -> Optional[str]:
    if isinstance(maybe_seq, str):
        if fat.is_str_dna_seq(maybe_seq):
            return maybe_seq

        fasta_data = fat.parse_fasta_str(maybe_seq)
        if 1 != len(fasta_data):
            return None

        if fat.is_str_dna_seq(fasta_data[0].sequence):
            return fasta_data[0].sequence

    return None


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
            7: "Data not found for '{}'",
            8: "List length does not match: user input size '{}' != expected size '{}'",
            9: "MySQL operation error: {}",
            10: "Your input '{}' is not a DNA sequence",
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
                    key_name, value_type.__name__, type(maybe_value).__name__
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
    """
    This class has been deprecated.
    Please don't use it or try to improve it.
    """
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
    * acc_id_list: dcit{ acc_id: {
                        "simil_identity": number,
                        "simil_bit_score": number,
                    }} -> List of sequence IDs which represent sequences that are similar to input sequence by client
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

            how_many = int(request.data[cst.KEY_HOW_MANY])

            maybe_valid_seq = _convert_to_seq_if_fasta(request.data[cst.KEY_SEQUENCE])
            if maybe_valid_seq is None:
                return Response({
                    cst.KEY_ERROR_CODE: 10,
                    cst.KEY_ERROR_TEXT: ERROR_MAP[10].format(cst.KEY_SEQUENCE)
                })
            seq: str = maybe_valid_seq

            #### Work ####

            result_file_name = tmpFile.TmpFileName("result-{}.txt".format(time.time()))
            print("[] started blast query")
            if not BLAST_INTERF.gen_query_result(seq, result_file_name.name):
                return Response({cst.KEY_ERROR_CODE: 5, cst.KEY_ERROR_TEXT: ERROR_MAP[5]})
            print("[] finished blast query")

            ids = BLAST_INTERF.find_similarity_of_the_similars(result_file_name.name, how_many)
            print("[] ids found: {}".format(ids.keys()))

            result_dict = {}
            for x, y in ids.items():
                result_dict[x] = {
                    cst.KEY_SIMILARITY_IDENTITY: y.identity,
                    cst.KEY_SIMILARITY_BIT_SCORE: y.bit_score,
                }

            return Response({
                cst.KEY_ACC_ID_LIST: result_dict,
                cst.KEY_ERROR_CODE: 0,
            })

        except:
            traceback.print_exc()
            return Response({
                cst.KEY_ERROR_CODE: 1,
                cst.KEY_ERROR_TEXT: ERROR_MAP[1],
            })


class GetMetadataOfSeq(APIView):
    """
    Requst payload must have following fields
    * acc_id: string
    * column_list: array[string] -> Column names that the user is interested in
                                    Returns all columns if the array is empty

    On success, it responds with following fields
    * error_code: number -> It should be 0
    * metadata: dict[string, optional[string]] -> Map where columns are keys
                                                  If client provided with invalid column, the value would be null

    Meanwhile on failure, the reponse payload contains followings
    * error_code: number -> It can be any integer number but 0
    * error_text: string -> Refer to local variable "ERROR_MAP" for details
    """

    @staticmethod
    def post(request: Request, _=None):
        try:
            #### Validate client input ####

            validate_result = _validate_request_payload(request, {
                cst.KEY_ACC_ID: str,
                cst.KEY_COLUMN_LIST: list,
            })
            if validate_result is not None:
                return Response(validate_result)

            acc_id: str = request.data[cst.KEY_ACC_ID]
            column_list: list = request.data[cst.KEY_COLUMN_LIST]

            #### Work ####

            try:
                metadata = MYSQL_INTERF.get_metadata_of(acc_id)
            except pymysql.err.OperationalError as e:
                return Response({
                    cst.KEY_ERROR_CODE: 9,
                    cst.KEY_ERROR_TEXT: ERROR_MAP[9].format(str(e))
                })

            if metadata is None:
                return Response({
                    cst.KEY_ERROR_CODE: 7,
                    cst.KEY_ERROR_TEXT: ERROR_MAP[7].format(acc_id)
                })

            if 0 == len(column_list):
                result_metadata = metadata
            else:
                result_metadata = {}

                for requested_column in column_list:
                    try:
                        result_metadata[requested_column] = metadata[requested_column]
                    except KeyError:
                        result_metadata[requested_column] = None

            return Response({
                cst.KEY_ERROR_CODE: 0,
                cst.KEY_METADATA: result_metadata,
            })

        except:
            traceback.print_exc()
            return Response({
                cst.KEY_ERROR_CODE: 1,
                cst.KEY_ERROR_TEXT: ERROR_MAP[1],
            })


class CalcSimilarityOfTwoSeq(APIView):
    @staticmethod
    def post(request: Request, _=None):
        try:
            #### Validate client input ####

            validate_result = _validate_request_payload(request, {
                cst.KEY_SEQUENCE_LIST: list,
            })
            if validate_result is not None:
                return Response(validate_result)

            seq_list: list = request.data[cst.KEY_SEQUENCE_LIST]

            if 2 != len(seq_list):
                return Response({
                    cst.KEY_ERROR_CODE: 8,
                    cst.KEY_ERROR_TEXT: ERROR_MAP[8].format(len(seq_list), 2)
                })

            for i in range(2):
                if not isinstance(seq_list[i], str):
                    return Response({
                        cst.KEY_ERROR_CODE: 4,
                        cst.KEY_ERROR_TEXT: ERROR_MAP[4].format(
                            "{}[{}]".format(cst.KEY_SEQUENCE_LIST, i), str.__name__, type(seq_list[i]).__name__)
                    })

            valid_seq_list = []
            for i in range(2):
                maybe_valid_seq = _convert_to_seq_if_fasta(seq_list[i])
                if maybe_valid_seq is None:
                    return Response({
                        cst.KEY_ERROR_CODE: 10,
                        cst.KEY_ERROR_TEXT: ERROR_MAP[10].format("{}[{}]".format(cst.KEY_SEQUENCE_LIST, i))
                    })
                else:
                    valid_seq_list.append(maybe_valid_seq)

            seq_1 = valid_seq_list[0]
            seq_2 = valid_seq_list[1]

            #### Work ####

            simi = BLAST_INTERF.get_similarity_two_seq(seq_1, seq_2)

            return Response({
                cst.KEY_ERROR_CODE: 0,
                cst.KEY_SIMILARITY_IDENTITY: simi.identity,
                cst.KEY_SIMILARITY_BIT_SCORE: simi.bit_score,
            })

        except:
            traceback.print_exc()
            return Response({
                cst.KEY_ERROR_CODE: 1,
                cst.KEY_ERROR_TEXT: ERROR_MAP[1],
            })


class GetAllAccIDs(APIView):
    @staticmethod
    def get(request: Request, _=None):
        try:
            #### Work ####

            acc_id_list = MYSQL_INTERF.get_all_acc_ids()

            return Response({
                cst.KEY_ERROR_CODE: 0,
                cst.KEY_ACC_ID_LIST: acc_id_list,
            })

        except:
            traceback.print_exc()
            return Response({
                cst.KEY_ERROR_CODE: 1,
                cst.KEY_ERROR_TEXT: ERROR_MAP[1],
            })


class FindMutations(APIView):
    @staticmethod
    def get(request: Request, _=None):
        try:
            #### Validate client input ####

            validate_result = _validate_request_payload(request, {
                cst.KEY_SEQUENCE_LIST: list,
            })
            if validate_result is not None:
                return Response(validate_result)

            seq_list: list = request.data[cst.KEY_SEQUENCE_LIST]

            if 2 != len(seq_list):
                return Response({
                    cst.KEY_ERROR_CODE: 8,
                    cst.KEY_ERROR_TEXT: ERROR_MAP[8].format(len(seq_list), 2)
                })

            for i in range(2):
                if not isinstance(seq_list[i], str):
                    return Response({
                        cst.KEY_ERROR_CODE: 4,
                        cst.KEY_ERROR_TEXT: ERROR_MAP[4].format(
                            "{}[{}]".format(cst.KEY_SEQUENCE_LIST, i), str.__name__, type(seq_list[i]).__name__)
                    })

            valid_seq_list = []
            for i in range(2):
                maybe_valid_seq = _convert_to_seq_if_fasta(seq_list[i])
                if maybe_valid_seq is None:
                    return Response({
                        cst.KEY_ERROR_CODE: 10,
                        cst.KEY_ERROR_TEXT: ERROR_MAP[10].format("{}[{}]".format(cst.KEY_SEQUENCE_LIST, i))
                    })
                else:
                    valid_seq_list.append(maybe_valid_seq)

            seq_list = [
                valid_seq_list[0],
                valid_seq_list[1],
            ]

            #### Work ####

            temp_file_names = [
                "./tmp/one-{}.tmp".format(time.time()),
                "./tmp/two-{}.tmp".format(time.time()),
            ]
            if not os.path.isdir("./tmp"):
                os.mkdir("./tmp")

            for i in range(2):
                seq_fasta = fat.parse_fasta_str(seq_list[i])
                assert 1 == len(seq_fasta)

                with open(temp_file_names[i], "w") as file:
                    file.write(seq_fasta[0].export_text())

            mut_func = mut.InterfMutation(".", "wuhan")
            result = mut_func.get_mutation(temp_file_names[0], temp_file_names[1])

            if os.path.isdir("./tmp"):
                shutil.rmtree("./tmp")

            return Response({
                cst.KEY_ERROR_CODE: 0,
                cst.KEY_RESULT: result,
            })

        except:
            traceback.print_exc()
            return Response({
                cst.KEY_ERROR_CODE: 1,
                cst.KEY_ERROR_TEXT: ERROR_MAP[1],
            })
