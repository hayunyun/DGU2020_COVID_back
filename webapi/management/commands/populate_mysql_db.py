import os

from django.core.management.base import BaseCommand, CommandError

import dgucovidb.db_interface as bst
import dgucovidb.sql_interface as sql


class Command(BaseCommand):
    help = 'Build BLAST database using a fasta file'

    __ARG_SQL_USERNAME = "sql_username"
    __ARG_SQL_PASSWD = "sql_passwd"
    __ARG_SETTING_PATH = "setting_path"
    __ARG_FASTA_PATH = "fasta_path"
    __ARG_METADATA_PATH = "metadata_path"

    def add_arguments(self, parser):
        parser.add_argument(self.__ARG_SQL_USERNAME, type=str)
        parser.add_argument(self.__ARG_SQL_PASSWD, type=str)
        parser.add_argument(self.__ARG_SETTING_PATH, type=str)
        parser.add_argument(self.__ARG_FASTA_PATH, type=str)
        parser.add_argument(self.__ARG_METADATA_PATH, type=str)

    def handle(self, *args, **options):
        blast = bst.InterfBLAST("./database/blast")
        if not blast.does_db_exists():
            raise CommandError("blast db has not been set up. run 'gen_blast_db' first")

        username = str(options[self.__ARG_SQL_USERNAME])
        password = str(options[self.__ARG_SQL_PASSWD])
        setting_path = str(options[self.__ARG_SETTING_PATH])
        fasta_path = str(options[self.__ARG_FASTA_PATH])
        metadata_path = str(options[self.__ARG_METADATA_PATH])

        for p in (setting_path, fasta_path, metadata_path):
            if not os.path.isfile(p):
                raise CommandError("file not found: '{}'".format(p))

        mysql = sql.InterfMySQL(username, password)
        mysql.populate(setting_path, fasta_path, metadata_path)
