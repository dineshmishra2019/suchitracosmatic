import csv
from decimal import Decimal, InvalidOperation
from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify
from store.models import Product, Category

class Command(BaseCommand):
    help = 'Imports products from the cosmetics.csv file.'

    def add_arguments(self, parser):
        parser.add_argument('csv_file_path', type=str, help='The full path to the CSV file to be imported.')

    def handle(self, *args, **options):
        file_path = options['csv_file_path']
        self.stdout.write(self.style.SUCCESS(f'Starting product import from: {file_path} ...'))

        try:
            with open(file_path, mode='r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                # Define expected headers from cosmetics.csv
                expected_headers = ['Label', 'Brand', 'Name', 'Price', 'Ingredients']
                if not all(header in reader.fieldnames for header in expected_headers):
                    missing = set(expected_headers) - set(reader.fieldnames)
                    raise CommandError(f"CSV file is missing required headers: {', '.join(missing)}")

                for row_num, row in enumerate(reader, 1):
                    product_name = row.get('Name')
                    if not product_name:
                        self.stdout.write(self.style.WARNING(f'Skipping row {row_num}: "Name" column is missing or empty.'))
                        continue

                    # Get or create the category
                    category_name = row.get('Label').strip()
                    category, created = Category.objects.get_or_create(
                        name=category_name,
                        defaults={'slug': slugify(category_name)}
                    )
                    if created:
                        self.stdout.write(f'-- Created new category: {category.name}')

                    # Prepare product data
                    try:
                        full_name = f"{row.get('Brand')} {product_name}".strip()
                        
                        # Generate a unique slug
                        base_slug = slugify(full_name)
                        slug = base_slug
                        counter = 1
                        while Product.objects.filter(slug=slug).exists():
                            slug = f'{base_slug}-{counter}'
                            counter += 1

                        product_data = {
                            'name': full_name,
                            'category': category,
                            'price': Decimal(row['price']),
                            'ingredients': row.get('Ingredients', ''),
                            'is_available': True, # Default to available
                        }

                        # Since slugs are newly generated, we use create. This avoids overwriting.
                        product = Product.objects.create(slug=slug, **product_data)
                        self.stdout.write(self.style.SUCCESS(f'Successfully created product: {product.name}'))

                    except (InvalidOperation, ValueError):
                        self.stdout.write(self.style.ERROR(f'Skipping row {row_num} for "{product_name}": Invalid price "{row.get("price")}".'))
        except FileNotFoundError:
            raise CommandError(f'File not found at: {file_path}')