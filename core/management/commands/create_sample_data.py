from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Category, Product, Profile

class Command(BaseCommand):
    help = 'Create sample data for the application'
    
    def handle(self, *args, **options):
        # Create categories
        categories_data = [
            {'name': 'Nitrogen Fertilizers', 'description': 'Fertilizers rich in nitrogen content'},
            {'name': 'Phosphatic Fertilizers', 'description': 'Fertilizers rich in phosphorus content'},
            {'name': 'Potassic Fertilizers', 'description': 'Fertilizers rich in potassium content'},
            {'name': 'NPK Complex', 'description': 'Complex fertilizers with balanced nutrients'},
            {'name': 'Organic Fertilizers', 'description': 'Natural and organic fertilizers'},
        ]
        
        for cat_data in categories_data:
            Category.objects.get_or_create(**cat_data)
        
        self.stdout.write(self.style.SUCCESS('Sample categories created!'))
        
        # Create a sample dealer
        dealer, created = User.objects.get_or_create(
            username='sample_dealer',
            defaults={
                'email': 'dealer@agrigrow.com',
                'first_name': 'Sample',
                'last_name': 'Dealer'
            }
        )
        if created:
            dealer.set_password('password123')
            dealer.save()
            Profile.objects.create(
                user=dealer,
                user_type='dealer',
                phone='9876543210',
                address='123 Business Street',
                city='Farm City',
                state='Agriculture State',
                pincode='123456',
                company_name='AgriSupply Co.',
                business_address='123 Business District',
                gst_number='GST123456789'
            )
        
        # Create sample products
        products_data = [
            {
                'name': 'Urea Fertilizer',
                'description': 'High-quality urea fertilizer for nitrogen supplementation',
                'category': Category.objects.get(name='Nitrogen Fertilizers'),
                'price': 500.00,
                'stock_quantity': 100,
                'nitrogen_content': 46.0,
                'phosphorus_content': 0.0,
                'potassium_content': 0.0,
                'suitable_crops': 'Wheat, Rice, Corn, Vegetables',
                'usage_instructions': 'Apply during vegetative growth stage'
            },
            {
                'name': 'DAP Fertilizer',
                'description': 'Diammonium phosphate for phosphorus and nitrogen',
                'category': Category.objects.get(name='Phosphatic Fertilizers'),
                'price': 1200.00,
                'stock_quantity': 75,
                'nitrogen_content': 18.0,
                'phosphorus_content': 46.0,
                'potassium_content': 0.0,
                'suitable_crops': 'All crops requiring phosphorus',
                'usage_instructions': 'Apply at planting or during early growth'
            },
            {
                'name': 'NPK 19:19:19',
                'description': 'Balanced NPK fertilizer for overall plant growth',
                'category': Category.objects.get(name='NPK Complex'),
                'price': 800.00,
                'stock_quantity': 50,
                'nitrogen_content': 19.0,
                'phosphorus_content': 19.0,
                'potassium_content': 19.0,
                'suitable_crops': 'All field and horticultural crops',
                'usage_instructions': 'Can be used as basal dose or top dressing'
            },
        ]
        
        for product_data in products_data:
            Product.objects.get_or_create(
                name=product_data['name'],
                defaults={
                    'dealer': dealer,
                    **product_data
                }
            )
        
        self.stdout.write(self.style.SUCCESS('Sample products created!'))