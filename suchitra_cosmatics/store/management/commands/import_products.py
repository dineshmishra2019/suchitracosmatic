import csv
import os
from decimal import Decimal, InvalidOperation
from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify
from django.core.files import File
from store.models import Product, Category, ProductImage

class Command(BaseCommand):
    help = 'Imports products from a specified CSV file, with optional image import.'

    def add_arguments(self, parser):
        parser.add_argument('csv_file_path', type=str, help='The full path to the CSV file to be imported.')
        parser.add_argument('--image_dir', type=str, help='The directory containing product images. Image filenames should match product slugs (e.g., my-product.jpg).')

    def handle(self, *args, **options):
        file_path = options['csv_file_path']
        image_dir = options.get('image_dir')
        self.stdout.write(self.style.SUCCESS(f'Starting product import from: {file_path}'))

        try:
            with open(file_path, mode='r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                # Define expected headers. The slug is used as the unique identifier.
                expected_headers = ['Label', 'Brand', 'Name', 'Price', 'Ingredients']
                if not all(header in reader.fieldnames for header in expected_headers):
                    missing = set(expected_headers) - set(reader.fieldnames)
                    raise CommandError(f"CSV file is missing required headers: {', '.join(missing)}")

                for row_num, row in enumerate(reader, 1):
                    product_name = row.get('Name')
                    if not product_name:
                        self.stdout.write(self.style.WARNING(f'Skipping row {row_num}: "Name" column is missing or empty.'))
                        continue

                    # Get or create the category from the 'Label' column
                    category_name = row.get('Label').strip()
                    category, created = Category.objects.get_or_create(
                        name=category_name,
                        defaults={'slug': slugify(category_name)}
                    )
                    if created:
                        self.stdout.write(f'Created new category: {category.name}')

                    # Prepare product data
                    try:
                        product_data = {
                            'name': f"{row.get('Brand')} {product_name}".strip(),
                            'category': category,
                            'price': Decimal(row['price']),
                            'ingredients': row.get('Ingredients', ''),
                            'is_available': True, # Default to available
                        }

                        # Generate a unique slug
                        base_slug = slugify(product_data['name'])
                        slug = base_slug
                        counter = 1
                        while Product.objects.filter(slug=slug).exists():
                            slug = f'{base_slug}-{counter}'
                            counter += 1

                        # Use update_or_create to either update an existing product or create a new one
                        product, created = Product.objects.update_or_create(
                            slug=slug,
                            defaults=product_data
                        )

                        status = "Created" if created else "Updated"
                        self.stdout.write(self.style.SUCCESS(f'{status} product: {product.name} (Slug: {slug})'))

                        # --- Image Import Logic ---
                        if image_dir and not product.images.exists():
                            image_found = False
                            for ext in ['.jpg', '.jpeg', '.png']:
                                image_path = os.path.join(image_dir, f"{slug}{ext}")
                                if os.path.exists(image_path):
                                    with open(image_path, 'rb') as f:
                                        product_image = ProductImage(product=product, is_main_image=True)
                                        product_image.image.save(os.path.basename(image_path), File(f), save=True)
                                        self.stdout.write(self.style.SUCCESS(f'  └─ Attached image: {os.path.basename(image_path)}'))
                                    image_found = True
                                    break # Stop after finding the first matching image
                            if not image_found:
                                self.stdout.write(self.style.WARNING(f'  └─ No image found for slug: {slug}'))

                    except (InvalidOperation, ValueError):
                        self.stdout.write(self.style.ERROR(f'Skipping row {row_num} for "{product_name}": Invalid price "{row.get("price")}".'))
        except FileNotFoundError:
            raise CommandError(f'File not found at: {file_path}')