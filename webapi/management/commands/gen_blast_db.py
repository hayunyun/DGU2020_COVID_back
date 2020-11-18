import os

from django.core.management.base import BaseCommand, CommandError

import dgucovidb.db_interface as bst


class Command(BaseCommand):
    help = 'Build BLAST database using a fasta file'

    __ARG_DB_SRC_PATH = "db_src_folder_path"

    def add_arguments(self, parser):
        parser.add_argument(self.__ARG_DB_SRC_PATH, type=str)

    def handle(self, *args, **options):
        db_src_fol_path = str(options[self.__ARG_DB_SRC_PATH])
        if not os.path.isdir(db_src_fol_path):
            raise CommandError("'{}' is not a valid folder".format(db_src_fol_path))

        blast = bst.InterfBLAST("./database/blast")

        try:
            blast.create_db(os.path.join(db_src_fol_path, "sequences.fasta"))
        except FileExistsError:
            self.stdout.write("blast db aleady exists")
        else:
            self.stdout.write(self.style.SUCCESS("generated blast db successfully"))
