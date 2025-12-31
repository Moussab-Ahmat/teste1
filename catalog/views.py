from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .cache import get_cached_products, set_cached_products
from .models import Category, Product
from .serializers import CategorySerializer, ProductDetailSerializer, ProductListSerializer


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductListView(generics.ListAPIView):
    serializer_class = ProductListSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return Product.objects.select_related('category').prefetch_related('images')

    def list(self, request, *args, **kwargs):
        cache_params = {
            'page': request.query_params.get('page', 1),
            'page_size': request.query_params.get('page_size', self.pagination_class.page_size),
        }
        cached = get_cached_products(cache_params)
        if cached is not None:
            return Response(cached)

        response = super().list(request, *args, **kwargs)
        set_cached_products(cache_params, response.data)
        return response


class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.select_related('category').prefetch_related('images')
    serializer_class = ProductDetailSerializer
    lookup_field = 'id'
