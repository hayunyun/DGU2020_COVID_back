import os

from django.core.management.base import BaseCommand, CommandError

import dgucovidb.db_interface as bst


class Command(BaseCommand):
    help = 'Build BLAST database using a fasta file'

    __ARG_SRG_FASTA = "src_fasta"

    def add_arguments(self, parser):
        parser.add_argument(self.__ARG_SRG_FASTA, type=str)

    def handle(self, *args, **options):
        fasta_path = str(options[self.__ARG_SRG_FASTA])
        if not os.path.isfile(fasta_path):
            raise CommandError("'{}' is not a file".format(fasta_path))

        blast = bst.InterfBLAST("./database/blast")

        try:
            blast.create_db(fasta_path)
        except FileExistsError:
            self.stdout.write("blast db aleady exists")
        else:
            self.stdout.write(self.style.SUCCESS("generated blast db successfully"))
