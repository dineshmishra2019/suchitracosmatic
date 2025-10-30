import csv
from decimal import Decimal, InvalidOperation
from django.core.management.base import BaseCommand, CommandError
from store.models import Product, Category

class Command(BaseCommand):
    help = 'Imports or updates products from a specified CSV file.'

    def add_arguments(self, parser):
        parser.add_argument('csv_file_path', type=str, help='The full path to the CSV file to be imported.')

    def handle(self, *args, **options):
        file_path = options['csv_file_path']
        self.stdout.write(self.style.SUCCESS(f'Starting product import from: {file_path}'))

        try:
            with open(file_path, mode='r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                # Define expected headers. The slug is used as the unique identifier.
                expected_headers = ['slug', 'name', 'category_name', 'price', 'description', 'is_available', 'is_featured']
                if not all(header in reader.fieldnames for header in expected_headers):
                    missing = set(expected_headers) - set(reader.fieldnames)
                    raise CommandError(f"CSV file is missing required headers: {', '.join(missing)}")

                for row_num, row in enumerate(reader, 1):
                    slug = row.get('slug')
                    if not slug:
                        self.stdout.write(self.style.WARNING(f'Skipping row {row_num}: slug is missing.'))
                        continue

                    # Get or create the category
                    category, created = Category.objects.get_or_create(
                        name=row['category_name'],
                        defaults={'slug': row['category_name'].lower().replace(' ', '-')}
                    )
                    if created:
                        self.stdout.write(f'Created new category: {category.name}')

                    # Prepare product data
                    try:
                        product_data = {
                            'name': row['name'],
                            'category': category,
                            'price': Decimal(row['price']),
                            'description': row.get('description', ''),
                            'is_available': row['is_available'].strip().lower() in ['true', '1', 'yes'],
                            'is_featured': row.get('is_featured', 'false').strip().lower() in ['true', '1', 'yes'],
                        }

                        # Use update_or_create to either update an existing product or create a new one
                        product, created = Product.objects.update_or_create(
                            slug=slug,
                            defaults=product_data
                        )

                        status = "Created" if created else "Updated"
                        self.stdout.write(self.style.SUCCESS(f'{status} product: {product.name} (Slug: {slug})'))

                    except InvalidOperation:
                        self.stdout.write(self.style.ERROR(f'Skipping row {row_num} for slug {slug}: Invalid price "{row["price"]}".'))
        except FileNotFoundError:
            raise CommandError(f'File not found at: {file_path}')