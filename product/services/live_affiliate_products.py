"""
filepath: /product/services/live_affiliate_products.py

Production-ready affiliate network integration
Replace your mock data with real API calls
"""

import logging
from typing import List, Dict, Optional
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

# =============================
# Affiliate API Wrappers
# =============================

class AmazonProductAPI:
    def __init__(self):
        self.api_key = getattr(settings, 'AMAZON_API_KEY', None)
        self.api_secret = getattr(settings, 'AMAZON_API_SECRET', None)
        self.affiliate_tag = getattr(settings, 'AMAZON_AFFILIATE_TAG', None)
        self.region = getattr(settings, 'AMAZON_REGION', 'US')

    def is_configured(self):
        return all([self.api_key, self.api_secret, self.affiliate_tag])

    def search_products(self, query: str, limit: int = 10) -> List[Dict]:
        if not self.is_configured():
            logger.warning("Amazon API not configured")
            return []
        cache_key = f"amazon_search_{query}_{limit}"
        cached = cache.get(cache_key)
        if cached:
            return cached
        try:
            from amazon.paapi import AmazonAPI
            amazon = AmazonAPI(
                key=self.api_key,
                secret=self.api_secret,
                tag=self.affiliate_tag,
                country=self.region
            )
            items = amazon.search_items(
                keywords=query,
                item_count=limit,
                resources=[
                    'ItemInfo.Title',
                    'ItemInfo.ByLineInfo',
                    'ItemInfo.Features',
                    'Images.Primary.Large',
                    'Offers.Listings.Price'
                ]
            )
            products = []
            for item in items.items:
                price = float(item.offers.listings[0].price.amount) if item.offers and item.offers.listings else 0
                description = " ".join(item.item_info.features.display_values[:2]) if item.item_info.features else ""
                brand = item.item_info.by_line_info.brand.display_value if item.item_info.by_line_info and item.item_info.by_line_info.brand else "Unknown"
                products.append({
                    "name": item.item_info.title.display_value,
                    "brand": brand,
                    "description": description,
                    "price": price,
                    "image_url": item.images.primary.large.url if item.images else "",
                    "affiliate_url": item.detail_page_url,
                    "store": "Amazon",
                    "asin": item.asin
                })
            cache.set(cache_key, products, 3600)
            return products
        except ImportError:
            logger.error("python-amazon-paapi not installed. Run: pip install python-amazon-paapi")
            return []
        except Exception as e:
            logger.error(f"Amazon API error: {str(e)}")
            return []

class WalmartProductAPI:
    def __init__(self):
        self.api_key = getattr(settings, 'WALMART_API_KEY', None)
        self.affiliate_id = getattr(settings, 'WALMART_AFFILIATE_ID', None)
        self.base_url = "https://developer.api.walmart.com/api-proxy/service/affil/product/v2"

    def is_configured(self):
        return bool(self.api_key and self.affiliate_id)

    def search_products(self, query: str, limit: int = 10) -> List[Dict]:
        if not self.is_configured():
            logger.warning("Walmart API not configured")
            return []
        cache_key = f"walmart_search_{query}_{limit}"
        cached = cache.get(cache_key)
        if cached:
            return cached
        try:
            import requests
            url = f"{self.base_url}/search"
            params = {
                'apiKey': self.api_key,
                'query': query,
                'numItems': limit,
                'format': 'json'
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            products = []
            for item in data.get('items', []):
                product_url = item.get('productTrackingUrl', item.get('productUrl', ''))
                affiliate_url = f"{product_url}?affcamid={self.affiliate_id}" if product_url else ""
                products.append({
                    "name": item.get('name', 'Unknown Product'),
                    "brand": item.get('brandName', 'Unknown'),
                    "description": item.get('shortDescription', ''),
                    "price": float(item.get('salePrice', 0)),
                    "image_url": item.get('largeImage', item.get('mediumImage', '')),
                    "affiliate_url": affiliate_url,
                    "store": "Walmart",
                    "item_id": item.get('itemId')
                })
            cache.set(cache_key, products, 3600)
            return products
        except Exception as e:
            logger.error(f"Walmart API error: {str(e)}")
            return []

# =============================
# Tag Detection
# =============================

def _detect_product_tag(product: Dict) -> str:
    text = f"{product.get('name', '').lower()} {product.get('brand', '').lower()} {product.get('description', '').lower()}"
    am_keywords = ['made in usa', 'american made', 'manufactured in usa', 'usa made', 'proudly made in usa']
    tf_keywords = ['tariff free', 'no tariff', 'duty free', 'tariff exempt', 'zero tariff']
    aust_keywords = ['assembled in usa', 'usa assembly', 'american assembly']
    has_am = any(k in text for k in am_keywords)
    has_tf = any(k in text for k in tf_keywords)
    has_aust = any(k in text for k in aust_keywords)
    if has_am and has_tf:
        return "Both"
    elif has_am:
        return "AM"
    elif has_tf:
        return "TF"
    elif has_aust:
        return "AUS-T"
    return "None"

# =============================
# Main Aggregator
# =============================

def fetch_live_affiliate_products(query: Optional[str] = None, tag_filter: Optional[str] = None, store_filter: Optional[str] = None, limit_per_store: int = 10) -> List[Dict]:
    all_products = []
    amazon = AmazonProductAPI()
    walmart = WalmartProductAPI()
    stores_to_query = []
    if not store_filter or store_filter.lower() == 'amazon':
        if amazon.is_configured():
            stores_to_query.append(('Amazon', amazon))
    if not store_filter or store_filter.lower() == 'walmart':
        if walmart.is_configured():
            stores_to_query.append(('Walmart', walmart))
    if not stores_to_query:
        logger.warning("No affiliate networks configured. Using mock data.")
        return []
    for store_name, api in stores_to_query:
        try:
            products = api.search_products(query or '', limit_per_store)
            for product in products:
                product['tag'] = _detect_product_tag(product)
            all_products.extend(products)
            logger.info(f"Fetched {len(products)} products from {store_name}")
        except Exception as e:
            logger.error(f"Error fetching from {store_name}: {str(e)}")
    if tag_filter:
        all_products = [p for p in all_products if p.get('tag') == tag_filter]
    if query:
        query_lower = query.lower()
        all_products = [p for p in all_products if query_lower in p.get('name', '').lower() or query_lower in p.get('description', '').lower()]
    return all_products
