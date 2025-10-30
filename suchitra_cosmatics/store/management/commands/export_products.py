import csv
from django.core.management.base import BaseCommand
from store.models import Product

class Command(BaseCommand):
    help = 'Exports all products and their main image URL to a CSV file.'

    def add_arguments(self, parser):
        parser.add_argument('csv_file_path', type=str, help='The full path for the output CSV file.')

    def handle(self, *args, **options):
        file_path = options['csv_file_path']
        self.stdout.write(self.style.SUCCESS(f'Starting product export to: {file_path}'))

        # Define the headers for your CSV file
        headers = [
            'slug', 
            'name', 
            'category', 
            'price', 
            'description', 
            'ingredients', 
            'how_to_use', 
            'is_available', 
            'is_featured', 
            'image_url'
        ]

        try:
            with open(file_path, mode='w', encoding='utf-8', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers)

                # Optimize the query to fetch related category and images efficiently
                products = Product.objects.all().select_related('category').prefetch_related('images')

                for product in products:
                    # Get the URL of the first image, if it exists
                    image_url = ''
                    first_image = product.images.filter(is_main_image=True).first() or product.images.first()
                    if first_image and first_image.image:
                        # We need to build the full URL
                        image_url = options.get('request').build_absolute_uri(first_image.image.url) if options.get('request') else first_image.image.url

                    writer.writerow([
                        product.slug, product.name, product.category.name, product.price,
                        product.description, product.ingredients, product.how_to_use,
                        product.is_available, product.is_featured, image_url
                    ])
            
            self.stdout.write(self.style.SUCCESS(f'Successfully exported {products.count()} products to {file_path}'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An error occurred: {e}'))