"""
Management command to ingest data from Excel files.
"""
from django.core.management.base import BaseCommand
from customers.tasks import ingest_all_data


class Command(BaseCommand):
    help = 'Ingest customer and loan data from Excel files'

    def handle(self, *args, **options):
        self.stdout.write('Starting data ingestion...')
        
        # Run ingestion task
        result = ingest_all_data()
        
        self.stdout.write(self.style.SUCCESS(result))
