import os

from django.core.management.base import BaseCommand, CommandError

import dgucovidb.db_interface as bst
import dgucovidb.sql_interface as sql


MYSQL_USERNAME = 'dgucovid'
MYSQL_PASSWORD = 'COVID@dgu2020'


class Command(BaseCommand):
    help = 'Build BLAST database using a fasta file'

    __ARG_DB_SRC_PATH = "db_src_folder_path"

    def add_arguments(self, parser):
        parser.add_argument(self.__ARG_DB_SRC_PATH, type=str)

    def handle(self, *args, **options):
        blast = bst.InterfBLAST("./database/blast")
        if not blast.does_db_exists():
            raise CommandError("blast db has not been set up. run 'gen_blast_db' first")

        db_src_fol_path = str(options[self.__ARG_DB_SRC_PATH])

        setting_path = os.path.join(db_src_fol_path, "setting.sql")
        fasta_path = os.path.join(db_src_fol_path, "sequences.fasta")
        metadata_path = os.path.join(db_src_fol_path, "metadata.tsv")
        ref_fasta_path = os.path.join(db_src_fol_path, "wuhan.fasta")
        cft_path = os.path.join(db_src_fol_path, "statistic_for_covid_of_the_world.csv")

        for p in (setting_path, fasta_path, metadata_path, ref_fasta_path, cft_path):
            if not os.path.isfile(p):
                raise CommandError("file not found: '{}'".format(p))

        mysql = sql.InterfMySQL(MYSQL_USERNAME, MYSQL_PASSWORD)

        print("Start init MySQL db")
        mysql.init_mysql(setting_path)
        print("Done init")
        mysql.populate_sequence(fasta_path, ref_fasta_path)
        print("Done populating sequences")
        mysql.populate_meta(metadata_path, cft_path)
        print("Done populating metadata")
