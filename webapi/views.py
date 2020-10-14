from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request


class TestList(APIView):
    def get(self, request, format_arg=None):
        return Response([1, 2, 3])
