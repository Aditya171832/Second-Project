from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Cart, CartItem

class Command(BaseCommand):
    help = 'Fix duplicate carts for users'
    
    def handle(self, *args, **options):
        # Get all users
        users = User.objects.all()
        
        for user in users:
            # Get all carts for this user
            user_carts = Cart.objects.filter(user=user)
            
            if user_carts.count() > 1:
                self.stdout.write(f"Fixing duplicate carts for user: {user.username}")
                
                # Keep the first cart and merge others into it
                main_cart = user_carts.first()
                duplicate_carts = user_carts.exclude(id=main_cart.id)
                
                # Move all items from duplicate carts to main cart
                for duplicate_cart in duplicate_carts:
                    duplicate_items = CartItem.objects.filter(cart=duplicate_cart)
                    
                    for item in duplicate_items:
                        # Check if same product already exists in main cart
                        existing_item = CartItem.objects.filter(
                            cart=main_cart, 
                            product=item.product
                        ).first()
                        
                        if existing_item:
                            # Merge quantities
                            existing_item.quantity += item.quantity
                            existing_item.save()
                            item.delete()
                        else:
                            # Move item to main cart
                            item.cart = main_cart
                            item.save()
                    
                    # Delete the duplicate cart
                    duplicate_cart.delete()
                
                self.stdout.write(f"✓ Fixed {user.username}: merged {duplicate_carts.count()} duplicate carts")
        
        self.stdout.write(self.style.SUCCESS('✅ All duplicate carts fixed!'))