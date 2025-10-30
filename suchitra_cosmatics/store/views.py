from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Product, Category
from decimal import Decimal, InvalidOperation

def search_results(request):
    """
    Handles product search functionality.
    """
    query = request.GET.get('q')
    products = Product.objects.none() # Return no products if query is empty

    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        )

    # Pagination
    paginator = Paginator(products, 12) # Show 12 products per page
    page_number = request.GET.get('page')
    products_page = paginator.get_page(page_number)

    # Preserve other query params in pagination links
    query_params = request.GET.copy()
    if 'page' in query_params:
        del query_params['page']

    context = {
        'query': query,
        'products': products_page,
        'query_params': query_params.urlencode(),
    }
    return render(request, 'store/search_results.html', context)

def product_detail(request, slug):
    """
    Displays a single product detail page.
    """
    product = get_object_or_404(Product, slug=slug, is_available=True)
    context = {
        'product': product
    }
    return render(request, 'store/product_detail.html', context)

def home(request):
    """
    Displays the homepage.
    """
    featured_products = Product.objects.filter(is_featured=True, is_available=True)[:6]
    categories = Category.objects.all()
    context = {
        'featured_products': featured_products,
        'categories': categories,
    }
    return render(request, 'store/home.html', context)

def product_list_by_category(request, category_slug):
    """
    Displays a list of products filtered by a specific category.
    """
    category = get_object_or_404(Category, slug=category_slug)
    products = Product.objects.filter(category=category, is_available=True)

    # Get available brands within the current category before filtering
    available_brands = products.order_by('brand').values_list('brand', flat=True).distinct()
    available_brands = [brand for brand in available_brands if brand] # Remove empty strings

    # Filtering logic
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    if min_price:
        try:
            products = products.filter(price__gte=Decimal(min_price))
        except (ValueError, InvalidOperation):
            min_price = None  # Ignore invalid input

    if max_price:
        try:
            products = products.filter(price__lte=Decimal(max_price))
        except (ValueError, InvalidOperation):
            max_price = None  # Ignore invalid input

    selected_brands = request.GET.getlist('brand')
    if selected_brands:
        products = products.filter(brand__in=selected_brands)

    # Pagination
    paginator = Paginator(products, 12) # Show 12 products per page
    page_number = request.GET.get('page')
    products_page = paginator.get_page(page_number)

    # Preserve other query params in pagination links
    query_params = request.GET.copy()
    if 'page' in query_params:
        del query_params['page']
    
    context = {
        'category': category,
        'products': products_page, # Pass the paginated page object
        'min_price': min_price,
        'max_price': max_price,
        'available_brands': available_brands,
        'selected_brands': selected_brands,
        'query_params': query_params.urlencode(),
    }
    return render(request, 'store/product_list.html', context)

def product_list(request):
    """
    Displays a list of all available products.
    """
    products = Product.objects.filter(is_available=True)

    # Get available brands for all products
    available_brands = products.order_by('brand').values_list('brand', flat=True).distinct()
    available_brands = [brand for brand in available_brands if brand] # Remove empty strings

    # Filtering logic
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    if min_price:
        try:
            products = products.filter(price__gte=Decimal(min_price))
        except (ValueError, InvalidOperation):
            min_price = None

    if max_price:
        try:
            products = products.filter(price__lte=Decimal(max_price))
        except (ValueError, InvalidOperation):
            max_price = None

    selected_brands = request.GET.getlist('brand')
    if selected_brands:
        products = products.filter(brand__in=selected_brands)

    # Pagination
    paginator = Paginator(products, 12) # Show 12 products per page
    page_number = request.GET.get('page')
    products_page = paginator.get_page(page_number)

    # Preserve other query params in pagination links
    query_params = request.GET.copy()
    if 'page' in query_params:
        del query_params['page']
    
    context = {
        'products': products_page,
        'min_price': min_price,
        'max_price': max_price,
        'available_brands': available_brands,
        'selected_brands': selected_brands,
        'query_params': query_params.urlencode(),
    }
    return render(request, 'store/product_list.html', context)