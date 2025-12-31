from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from django_redis import get_redis_connection

from catalog.models import Category, Product
from catalog.cache import _build_cache_key


class CatalogAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.category = Category.objects.create(name='Electronics', slug='electronics')
        products = [
            Product(category=self.category, name=f'Product {i}', price='9.99')
            for i in range(1, 16)
        ]
        Product.objects.bulk_create(products)
        self.redis = get_redis_connection()
        self.redis.flushall()

    def test_product_list_paginates(self):
        response = self.client.get(reverse('product-list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 10)
        self.assertIn('next', response.data)

    def test_product_list_cache_miss_then_hit(self):
        cache_key = _build_cache_key({'page': 1, 'page_size': 10})
        self.assertIsNone(self.redis.get(cache_key))

        with self.assertNumQueries(3):
            first_response = self.client.get(reverse('product-list'))
        self.assertEqual(first_response.status_code, 200)
        self.assertIsNotNone(self.redis.get(cache_key))

        with self.assertNumQueries(0):
            second_response = self.client.get(reverse('product-list'))
        self.assertEqual(second_response.status_code, 200)
        self.assertEqual(first_response.data, second_response.data)

    def test_product_list_has_no_n_plus_one_queries(self):
        response = self.client.get(reverse('product-list'))
        self.assertEqual(response.status_code, 200)
        self.redis.flushall()

        with self.assertNumQueries(3):
            response = self.client.get(reverse('product-list'))
            self.assertEqual(len(response.data['results']), 10)

    def test_product_detail_includes_images_and_category(self):
        product = Product.objects.first()
        url = reverse('product-detail', kwargs={'id': product.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], product.id)
        self.assertIn('category', response.data)
        self.assertIn('images', response.data)

    def test_cache_invalidation_on_product_save(self):
        self.client.get(reverse('product-list'))
        cache_key = _build_cache_key({'page': 1, 'page_size': 10})
        self.assertIsNotNone(self.redis.get(cache_key))
        product = Product.objects.first()
        product.name = 'Updated Name'
        product.save()
        self.assertIsNone(self.redis.get(cache_key))
