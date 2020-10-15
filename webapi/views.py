from typing import Dict

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request

import dgucovidb.db_interface as bst
import dgucovidb.sql_interface as sql


# This path is relative to the repo root path where manage.py is located
BLAST_INTERF = bst.InterfBLAST("./database/blast")
MYSQL_INTERF = sql.InterfMySQL("woos8899", "Finethensql22@")


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
        else:
            input_sequence = "".join(input_sequence.split('\n'))

            print("[] started blast query")
            if not BLAST_INTERF.gen_query_result(input_sequence, "result.tmp"):
                return Response("failed to generate BLAST query result")

            print("[] started finding similar ids")
            ids = BLAST_INTERF.find_ids_of_the_similars("result.tmp", how_many)

            result: Dict[str: Dict] = {}
            for acc_id in ids:
                result[acc_id] = MYSQL_INTERF.get_metadata_of(acc_id)

            return Response(result)
