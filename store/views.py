from django.views.generic import TemplateView

class Catalog(TemplateView):
    template_name = 'store/catalog.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Example product data (replace with database query or logic)
        all_products = [
            {'id': 1, 'name': 'Product 1', 'category': 'electronics', 'price': 50, 'rating': 4},
            {'id': 2, 'name': 'Product 2', 'category': 'books', 'price': 15, 'rating': 1},
            {'id': 3, 'name': 'Product 3', 'category': 'electronics', 'price': 75, 'rating': 3},
            {'id': 4, 'name': 'Product 4', 'category': 'books', 'price': 20, 'rating': 2},
            {'id': 5, 'name': 'Product 5', 'category': 'test', 'price': 23, 'rating': 5},
        ]

        # Filters from request
        category = self.request.GET.get('category')
        price_min = self.request.GET.get('price_min')
        price_max = self.request.GET.get('price_max')
        min_rating = self.request.GET.get('rating')

        # Apply filters
        filtered_products = all_products
        if category:
            filtered_products = [p for p in filtered_products if p['category'] == category]
        if price_min:
            filtered_products = [p for p in filtered_products if p['price'] >= int(price_min)]
        if price_max:
            filtered_products = [p for p in filtered_products if p['price'] <= int(price_max)]
        if min_rating:
            filtered_products = [p for p in filtered_products if p['rating'] >= int(min_rating)]

        # Apply sorting
        sort_by = self.request.GET.get('sort_by')
        if sort_by == 'price_asc':
            all_products.sort(key=lambda x: x['price'])
        elif sort_by == 'price_desc':
            all_products.sort(key=lambda x: x['price'], reverse=True)
        elif sort_by == 'name_asc':
            all_products.sort(key=lambda x: x['name'])
        elif sort_by == 'name_desc':
            all_products.sort(key=lambda x: x['name'], reverse=True)
        elif sort_by == 'rating_asc':
            all_products.sort(key=lambda x: x['rating'])
        elif sort_by == 'rating_desc':
            all_products.sort(key=lambda x: x['rating'], reverse=True)

        context['products'] = filtered_products
        context['categories'] = ['electronics', 'books', 'test']  # Example categories
        context['total_review'] = range(0, 6)  # Star ratings 0 to 5
        return context
