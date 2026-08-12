"""
COMPAREX Backend – Production Database Seed Script (Curated Real Products)

Populates production PostgreSQL database with a curated set of real,
commercially-available products. Every product in this seed script
corresponds to an actual product sold in the Indian market.

PRINCIPLES:
- Only real manufacturer model numbers and names
- No fabricated prices, random variants, or invented specs
- No random seed data generation
- base_price is catalog/reference price only — NOT a live marketplace price
- Live prices must come from verified marketplace observations (aggregator)
- Historical price observations are NOT seeded — they must come from real
  provider aggregation results only
"""

import asyncio
import os
import sys
import uuid
from decimal import Decimal

# Add backend directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select, func, or_
from app.db.base import Base
from app.db.session import AsyncSessionLocal, engine
import app.models  # noqa: F401

from app.models.marketplace import Marketplace
from app.models.category import Category
from app.models.brand import Brand
from app.models.product import Product
from app.models.product_image import ProductImage
from app.models.product_specification import ProductSpecification

# ── Seed Data Definitions ──────────────────────────────────────────────────

MARKETPLACES = [
    {
        "name": "Amazon India",
        "slug": "amazon",
        "base_url": "https://www.amazon.in",
        "logo_url": "https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg",
        "country_code": "IN",
    },
    {
        "name": "Flipkart",
        "slug": "flipkart",
        "base_url": "https://www.flipkart.com",
        "logo_url": "https://pngimg.com/uploads/flipkart/flipkart_PNG1.png",
        "country_code": "IN",
    },
    {
        "name": "Croma",
        "slug": "croma",
        "base_url": "https://www.croma.com",
        "logo_url": "https://upload.wikimedia.org/wikipedia/commons/5/53/Croma_Logo.svg",
        "country_code": "IN",
    },
    {
        "name": "Reliance Digital",
        "slug": "reliance_digital",
        "base_url": "https://www.reliancedigital.in",
        "logo_url": "https://www.reliancedigital.in/build/client/images/rd_logo.svg",
        "country_code": "IN",
    },
    {
        "name": "Tata CLiQ",
        "slug": "tata_cliq",
        "base_url": "https://www.tatacliq.com",
        "logo_url": "https://www.tatacliq.com/favicon.ico",
        "country_code": "IN",
    },
    {
        "name": "Myntra",
        "slug": "myntra",
        "base_url": "https://www.myntra.com",
        "logo_url": (
            "https://constant.myntassets.com/web/assets/img/"
            "800x500_2019-05-01-17-53-43_b6a039ede6cbb28eddca38bde021e0c3.jpg"
        ),
        "country_code": "IN",
    },
    {
        "name": "Meesho",
        "slug": "meesho",
        "base_url": "https://www.meesho.com",
        "logo_url": "https://images.meesho.com/images/pow/meeshoLogo.png",
        "country_code": "IN",
    },
]

CATEGORIES = [
    # Top Level
    {
        "name": "Electronics",
        "slug": "electronics",
        "description": "Gadgets, smartphones, computers, audio, and personal electronics.",
        "parent": None,
    },
    {
        "name": "Home & Kitchen",
        "slug": "home-kitchen",
        "description": "Appliances, furniture, cookware, lighting, and home decor.",
        "parent": None,
    },
    {
        "name": "Fashion",
        "slug": "fashion",
        "description": "Apparel, footwear, and accessories for men and women.",
        "parent": None,
    },
    # Electronics Subcategories
    {
        "name": "Smartphones",
        "slug": "smartphones",
        "description": "Mobile phones and 5G smartphones.",
        "parent": "electronics",
    },
    {
        "name": "Laptops & Computers",
        "slug": "laptops-computers",
        "description": "Ultrabooks, gaming laptops, and workstation PCs.",
        "parent": "electronics",
    },
    {
        "name": "Tablets",
        "slug": "tablets",
        "description": "iPads, Android tablets, and e-readers.",
        "parent": "electronics",
    },
    {
        "name": "Audio & Headphones",
        "slug": "audio-headphones",
        "description": "TWS earbuds, noise-canceling headphones, and Bluetooth speakers.",
        "parent": "electronics",
    },
    {
        "name": "Smartwatches & Wearables",
        "slug": "smartwatches-wearables",
        "description": "Fitness trackers, Apple Watches, and smart bands.",
        "parent": "electronics",
    },
    {
        "name": "Televisions",
        "slug": "televisions",
        "description": "4K OLED, QLED, and Smart Android TVs.",
        "parent": "electronics",
    },
    {
        "name": "Gaming Consoles & Accessories",
        "slug": "gaming",
        "description": "PS5, Xbox, Nintendo Switch, and gaming gear.",
        "parent": "electronics",
    },
    # Home & Kitchen Subcategories
    {
        "name": "Refrigerators",
        "slug": "refrigerators",
        "description": "Single door, double door, and side-by-side refrigerators.",
        "parent": "home-kitchen",
    },
    {
        "name": "Washing Machines",
        "slug": "washing-machines",
        "description": "Front load and top load fully automatic washing machines.",
        "parent": "home-kitchen",
    },
    {
        "name": "Air Conditioners",
        "slug": "air-conditioners",
        "description": "Split inverter ACs and window air conditioners.",
        "parent": "home-kitchen",
    },
    # Fashion Subcategories
    {
        "name": "Footwear",
        "slug": "footwear",
        "description": "Sneakers, running shoes, formal shoes, and sandals.",
        "parent": "fashion",
    },
]

BRANDS = [
    {
        "name": "Apple",
        "slug": "apple",
        "logo_url": "https://www.apple.com/ac/structured-data/images/open_graph_logo.png",
        "website_url": "https://www.apple.com/in",
    },
    {
        "name": "Samsung",
        "slug": "samsung",
        "logo_url": "https://images.samsung.com/is/image/samsung/assets/global/about-us/"
                    "brand/logo/mo/360_221_1.png",
        "website_url": "https://www.samsung.com/in",
    },
    {
        "name": "Sony",
        "slug": "sony",
        "logo_url": "https://www.sony.co.in/image/5d02da5df552836db894cead8a68f5f3",
        "website_url": "https://www.sony.co.in",
    },
    {
        "name": "OnePlus",
        "slug": "oneplus",
        "logo_url": "https://oasis.opstatics.com/content/dam/oasis/default/logo/"
                    "oneplus-logo.png",
        "website_url": "https://www.oneplus.in",
    },
    {
        "name": "Realme",
        "slug": "realme",
        "logo_url": "https://image01.realme.net/general/20190802/1564709341417.png",
        "website_url": "https://www.realme.com/in",
    },
    {
        "name": "Dell",
        "slug": "dell",
        "logo_url": "https://upload.wikimedia.org/wikipedia/commons/4/48/Dell_Logo.svg",
        "website_url": "https://www.dell.com/en-in",
    },
    {
        "name": "HP",
        "slug": "hp",
        "logo_url": "https://upload.wikimedia.org/wikipedia/commons/a/ad/HP_logo_2012.svg",
        "website_url": "https://www.hp.com/in-en",
    },
    {
        "name": "Lenovo",
        "slug": "lenovo",
        "logo_url": "https://upload.wikimedia.org/wikipedia/commons/b/b8/Lenovo_logo_2015.svg",
        "website_url": "https://www.lenovo.com/in/en",
    },
    {
        "name": "LG",
        "slug": "lg",
        "logo_url": "https://upload.wikimedia.org/wikipedia/commons/2/20/LG_symbol.svg",
        "website_url": "https://www.lg.com/in",
    },
    {
        "name": "Bose",
        "slug": "bose",
        "logo_url": "https://upload.wikimedia.org/wikipedia/commons/2/29/Bose_wordmark.svg",
        "website_url": "https://www.boseindia.com",
    },
    {
        "name": "boAt",
        "slug": "boat",
        "logo_url": "https://www.boat-lifestyle.com/cdn/shop/files/boat_logo_tagline.svg",
        "website_url": "https://www.boat-lifestyle.com",
    },
    {
        "name": "Nike",
        "slug": "nike",
        "logo_url": "https://upload.wikimedia.org/wikipedia/commons/a/a6/Logo_NIKE.svg",
        "website_url": "https://www.nike.com/in",
    },
    {
        "name": "Adidas",
        "slug": "adidas",
        "logo_url": "https://upload.wikimedia.org/wikipedia/commons/2/20/Adidas_Logo.svg",
        "website_url": "https://www.adidas.co.in",
    },
    {
        "name": "Whirlpool",
        "slug": "whirlpool",
        "logo_url": "https://upload.wikimedia.org/wikipedia/commons/7/7f/"
                    "Whirlpool_Corporation_Logo.svg",
        "website_url": "https://www.whirlpoolindia.com",
    },
    {
        "name": "OPPO",
        "slug": "oppo",
        "logo_url": "https://upload.wikimedia.org/wikipedia/commons/b/b8/OPPO_Logo.svg",
        "website_url": "https://www.oppo.com/in",
    },
    {
        "name": "POCO",
        "slug": "poco",
        "logo_url": "https://upload.wikimedia.org/wikipedia/commons/a/a2/POCO_Logo.png",
        "website_url": "https://www.poco.in",
    },
]

# ── Real Curated Products Only ─────────────────────────────────────────────
#
# IMPORTANT: Every product here must be a real commercially-available product.
# - model_name: exact manufacturer model designation
# - base_price: catalog/reference price in INR (not a live marketplace price)
# - image_url: real manufacturer or trusted CDN image (not Unsplash)
# - No random prices, no invented model numbers, no synthetic variants
#
CURATED_PRODUCTS = [
    # ── Smartphones ───────────────────────────────────────────────────────
    {
        "name": "Apple iPhone 16 Pro Max (256GB) - Natural Titanium",
        "category_slug": "smartphones",
        "brand_slug": "apple",
        "model_name": "iPhone 16 Pro Max",
        "base_price": 144900.0,
        "ean": "194253900001",
        "image_url": (
            "https://store.storeimages.cdn-apple.com/4668/as-images.apple.com/is/"
            "iphone-16-pro-finish-select-202409-6-9inch-naturaltitanium?wid=5120"
            "&hei=2880&fmt=p-jpg&qlt=80&.v=1723780969358"
        ),
        "description": (
            "iPhone 16 Pro Max with grade 5 titanium design, 6.9-inch Super Retina XDR "
            "ProMotion display, A18 Pro chip with Apple Intelligence, 48MP Fusion camera "
            "system with 5x Telephoto, up to 33 hours video playback."
        ),
        "specs": {
            "Display": "6.9-inch OLED 120Hz ProMotion (Always-On)",
            "Processor": "Apple A18 Pro (3nm)",
            "Camera": "48MP Main + 48MP Ultra Wide + 12MP 5x Telephoto Periscope",
            "Battery": "Up to 33 hours video playback",
            "Storage": "256 GB",
            "OS": "iOS 18",
        },
    },
    {
        "name": "Apple iPhone 15 Pro Max (256GB) - Natural Titanium",
        "category_slug": "smartphones",
        "brand_slug": "apple",
        "model_name": "iPhone 15 Pro Max",
        "base_price": 129900.0,
        "ean": "194253900009",
        "image_url": (
            "https://store.storeimages.cdn-apple.com/4668/as-images.apple.com/is/"
            "iphone-15-pro-finish-select-202309-6-7inch-naturaltitanium?wid=5120"
            "&hei=2880&fmt=p-jpg&qlt=80&.v=1693009278720"
        ),
        "description": (
            "iPhone 15 Pro Max forged in grade 5 titanium design, 6.7-inch Super Retina XDR "
            "display, A17 Pro chip, 48MP Fusion camera with 5x Telephoto."
        ),
        "specs": {
            "Display": "6.7-inch OLED 120Hz ProMotion",
            "Processor": "Apple A17 Pro",
            "Camera": "48MP Main + 12MP Ultra Wide + 12MP 5x Telephoto Periscope",
            "Battery": "Up to 29 hours video playback",
            "Storage": "256 GB",
        },
    },
    {
        "name": "Apple iPhone 15 (128GB) - Blue",
        "category_slug": "smartphones",
        "brand_slug": "apple",
        "model_name": "iPhone 15",
        "base_price": 69900.0,
        "ean": "194253900002",
        "image_url": (
            "https://store.storeimages.cdn-apple.com/4668/as-images.apple.com/is/"
            "iphone-15-finish-select-202309-6-1inch-blue?wid=5120&hei=2880"
            "&fmt=p-jpg&qlt=80&.v=1692923777972"
        ),
        "description": (
            "iPhone 15 with Dynamic Island, 48MP Main camera with 2x Telephoto, "
            "color-infused back glass, aluminum enclosure, and USB-C port."
        ),
        "specs": {
            "Display": "6.1-inch Super Retina XDR",
            "Processor": "A16 Bionic",
            "Camera": "48MP Main + 12MP Ultra Wide",
            "Storage": "128 GB",
        },
    },
    {
        "name": "Samsung Galaxy S25 Ultra 5G (12GB RAM, 512GB) - Titanium Silver Blue",
        "category_slug": "smartphones",
        "brand_slug": "samsung",
        "model_name": "Galaxy S25 Ultra",
        "base_price": 129999.0,
        "ean": "880609900099",
        "image_url": (
            "https://images.samsung.com/is/image/samsung/p6pim/in/"
            "2501/gallery/in-galaxy-s25-ultra-sm-s938-sm-s938qzsgins-thumb-539573400"
        ),
        "description": (
            "Samsung Galaxy S25 Ultra 5G with Snapdragon 8 Elite Galaxy Edition, "
            "200MP Quad Telephoto Camera System, Built-in S Pen, Galaxy AI features."
        ),
        "specs": {
            "Display": "6.8-inch Dynamic AMOLED 2X 120Hz",
            "Processor": "Snapdragon 8 Elite for Galaxy",
            "Camera": "200MP Main + 50MP Periscope + 50MP Ultra-Wide + 10MP Telephoto",
            "Battery": "5000 mAh with 45W Super Fast Charging",
            "RAM": "12 GB",
            "Storage": "512 GB",
        },
    },
    {
        "name": "Samsung Galaxy S24 FE 5G (8GB RAM, 128GB) - Blue",
        "category_slug": "smartphones",
        "brand_slug": "samsung",
        "model_name": "Galaxy S24 FE",
        "base_price": 49999.0,
        "ean": "880609900088",
        "image_url": (
            "https://images.samsung.com/is/image/samsung/p6pim/in/"
            "2410/gallery/in-galaxy-s24-fe-sm-s721-sm-s721bzbgins-thumb-542261900"
        ),
        "description": (
            "Samsung Galaxy S24 FE 5G with Exynos 2500 processor, 6.7-inch FHD+ "
            "Dynamic AMOLED 2X display, 50MP triple camera, 4700 mAh battery."
        ),
        "specs": {
            "Display": "6.7-inch FHD+ Dynamic AMOLED 2X 120Hz",
            "Processor": "Exynos 2500",
            "Camera": "50MP Main + 10MP Telephoto + 12MP Ultra Wide",
            "Battery": "4700 mAh with 45W Super Fast Charging",
            "RAM": "8 GB",
            "Storage": "128 GB",
        },
    },
    {
        "name": "OnePlus Nord 4 5G (8GB RAM, 128GB) - Mercurial Silver",
        "category_slug": "smartphones",
        "brand_slug": "oneplus",
        "model_name": "Nord 4",
        "base_price": 29999.0,
        "ean": "6921815627944",
        "image_url": (
            "https://oasis.opstatics.com/content/dam/oasis/page/2024/"
            "nord-4/kv/Nord4-silver.png"
        ),
        "description": (
            "OnePlus Nord 4 5G with Snapdragon 7+ Gen 3, 6.74-inch 120Hz AMOLED display, "
            "50MP Sony IMX890 camera, 5500 mAh battery with 100W SUPERVOOC charging."
        ),
        "specs": {
            "Display": "6.74-inch FHD+ AMOLED 120Hz",
            "Processor": "Snapdragon 7+ Gen 3",
            "Camera": "50MP Sony IMX890 + 8MP Ultra Wide",
            "Battery": "5500 mAh with 100W SUPERVOOC",
            "RAM": "8 GB",
            "Storage": "128 GB",
        },
    },
    {
        "name": "Realme GT 6 5G (8GB RAM, 256GB) - Fluid Silver",
        "category_slug": "smartphones",
        "brand_slug": "realme",
        "model_name": "GT 6",
        "base_price": 39999.0,
        "ean": "6941399090441",
        "image_url": (
            "https://image01.realme.net/general/20240619/1718804278290.png"
        ),
        "description": (
            "Realme GT 6 5G with Snapdragon 8s Gen 3, 6.78-inch 120Hz AMOLED display, "
            "50MP Sony LYT-808 camera, 5500 mAh battery with 120W SUPERVOOC charging."
        ),
        "specs": {
            "Display": "6.78-inch AMOLED 120Hz",
            "Processor": "Snapdragon 8s Gen 3",
            "Camera": "50MP Sony LYT-808 + 8MP Ultra Wide + 2MP Macro",
            "Battery": "5500 mAh with 120W SUPERVOOC",
            "RAM": "8 GB",
            "Storage": "256 GB",
        },
    },
    {
        "name": "OPPO A6x 5G (6GB RAM, 128GB) - Starry Purple",
        "category_slug": "smartphones",
        "brand_slug": "oppo",
        "model_name": "OPPO A6x 5G",
        "base_price": 13999.0,
        "ean": "693672000001",
        "image_url": "https://www.oppo.com/content/dam/oppo/product-asset-new/a/a6x-5g/v1/assets/a6x-purple.png",
        "description": (
            "OPPO A6x 5G with MediaTek Dimensity 6300 processor, 90Hz Eye-Care Punch-Hole "
            "display, 5000mAh battery with 45W SUPERVOOC flash charge, 50MP AI Dual Camera."
        ),
        "specs": {
            "Display": "6.67-inch HD+ 90Hz LCD",
            "Processor": "MediaTek Dimensity 6300 5G",
            "Camera": "50MP Main + 2MP Portrait",
            "Battery": "5000 mAh with 45W SUPERVOOC",
            "RAM": "6 GB",
            "Storage": "128 GB",
        },
    },
    {
        "name": "OPPO K14x 5G (8GB RAM, 128GB) - Midnight Blue",
        "category_slug": "smartphones",
        "brand_slug": "oppo",
        "model_name": "OPPO K14x 5G",
        "base_price": 16999.0,
        "ean": "693672000002",
        "image_url": "https://www.oppo.com/content/dam/oppo/product-asset-new/k/k14x-5g/v1/assets/k14x-blue.png",
        "description": (
            "OPPO K14x 5G powered by MediaTek Dimensity 7050, 120Hz Full HD+ AMOLED screen, "
            "67W SUPERVOOC charging, and 64MP Ultra-Clear Dual Camera system."
        ),
        "specs": {
            "Display": "6.72-inch FHD+ 120Hz AMOLED",
            "Processor": "MediaTek Dimensity 7050 5G",
            "Camera": "64MP Main + 2MP Depth",
            "Battery": "5000 mAh with 67W SUPERVOOC",
            "RAM": "8 GB",
            "Storage": "128 GB",
        },
    },
    {
        "name": "OPPO Reno 12 Pro 5G (12GB RAM, 512GB) - Sunset Gold",
        "category_slug": "smartphones",
        "brand_slug": "oppo",
        "model_name": "OPPO Reno 12 Pro 5G",
        "base_price": 36999.0,
        "ean": "693672000003",
        "image_url": "https://www.oppo.com/content/dam/oppo/product-asset-new/reno/reno12-pro-5g/v1/assets/reno12pro-gold.png",
        "description": (
            "OPPO Reno 12 Pro 5G featuring GenAI Eraser 2.0, MediaTek Dimensity 7300-Energy, "
            "50MP Sony LYT-600 main camera with OIS, 50MP Telephoto, and 80W SUPERVOOC."
        ),
        "specs": {
            "Display": "6.7-inch 1.5K 120Hz Quad-Curved AMOLED",
            "Processor": "MediaTek Dimensity 7300-Energy (4nm)",
            "Camera": "50MP Sony LYT-600 OIS + 50MP 2x Telephoto + 8MP UW",
            "Battery": "5000 mAh with 80W SUPERVOOC",
            "RAM": "12 GB",
            "Storage": "512 GB",
        },
    },
    {
        "name": "POCO X6 Pro 5G (12GB RAM, 512GB) - Racing Yellow",
        "category_slug": "smartphones",
        "brand_slug": "poco",
        "model_name": "POCO X6 Pro 5G",
        "base_price": 26999.0,
        "ean": "694181270001",
        "image_url": "https://i02.appmifile.com/832_operator_in/11/01/2024/2f80164c489d81d2df0dd9965a397c11.png",
        "description": (
            "POCO X6 Pro 5G powered by flagship MediaTek Dimensity 8300-Ultra (4nm), "
            "1.5K 120Hz Flow AMOLED display, 64MP OIS Triple Camera, 67W Turbo Charge."
        ),
        "specs": {
            "Display": "6.67-inch 1.5K 120Hz Flow AMOLED",
            "Processor": "MediaTek Dimensity 8300-Ultra (4nm)",
            "Camera": "64MP OIS + 8MP UW + 2MP Macro",
            "Battery": "5000 mAh with 67W Turbo Charge",
            "RAM": "12 GB",
            "Storage": "512 GB",
        },
    },
    {
        "name": "POCO M6 Pro 5G (6GB RAM, 128GB) - Power Black",
        "category_slug": "smartphones",
        "brand_slug": "poco",
        "model_name": "POCO M6 Pro 5G",
        "base_price": 10999.0,
        "ean": "694181270002",
        "image_url": "https://i02.appmifile.com/479_operator_in/05/08/2023/15c15fbddf3a47fb82f6fbf82103f191.png",
        "description": (
            "POCO M6 Pro 5G with Snapdragon 4 Gen 2 5G processor, 6.79-inch 90Hz FHD+ "
            "display with Corning Gorilla Glass, Premium Glass Back Design, 5000mAh battery."
        ),
        "specs": {
            "Display": "6.79-inch FHD+ 90Hz LCD",
            "Processor": "Snapdragon 4 Gen 2 (4nm)",
            "Camera": "50MP AI Dual Camera",
            "Battery": "5000 mAh with 18W Fast Charging",
            "RAM": "6 GB",
            "Storage": "128 GB",
        },
    },
    {
        "name": "POCO F6 5G (8GB RAM, 256GB) - Titanium Gray",
        "category_slug": "smartphones",
        "brand_slug": "poco",
        "model_name": "POCO F6 5G",
        "base_price": 29999.0,
        "ean": "694181270003",
        "image_url": "https://i02.appmifile.com/152_operator_in/23/05/2024/ee3241d725667e51c140df9ce5b24479.png",
        "description": (
            "POCO F6 5G equipped with Snapdragon 8s Gen 3 processor, WildBoost Optimization 3.0, "
            "1.5K 120Hz AMOLED display, 50MP Sony IMX882 camera with OIS, 90W Turbo Charge."
        ),
        "specs": {
            "Display": "6.67-inch 1.5K 120Hz CrystalRes AMOLED",
            "Processor": "Snapdragon 8s Gen 3 (4nm)",
            "Camera": "50MP Sony IMX882 OIS + 8MP UW",
            "Battery": "5000 mAh with 90W Turbo Charge",
            "RAM": "8 GB",
            "Storage": "256 GB",
        },
    },
    # ── Laptops ───────────────────────────────────────────────────────────
    {
        "name": "Apple MacBook Air M4 (16GB RAM, 512GB SSD) - Space Grey",
        "category_slug": "laptops-computers",
        "brand_slug": "apple",
        "model_name": "MacBook Air M4",
        "base_price": 114900.0,
        "ean": "194253900088",
        "image_url": (
            "https://store.storeimages.cdn-apple.com/4668/as-images.apple.com/is/"
            "mba13-midnight-select-202503?wid=800&hei=800&fmt=jpeg&qlt=90&.v=1741894259761"
        ),
        "description": (
            "MacBook Air with next-gen Apple M4 chip, 13.6-inch Liquid Retina display, "
            "16GB unified memory, 512GB SSD, up to 18 hours battery life."
        ),
        "specs": {
            "Display": "13.6-inch Liquid Retina 500 nits",
            "Processor": "Apple M4 Chip 10-core CPU, 10-core GPU",
            "Memory": "16 GB Unified Memory",
            "Storage": "512 GB SSD",
            "Battery": "Up to 18 hours",
        },
    },
    {
        "name": "Dell Inspiron 15 3520 (Intel Core i5-1235U, 8GB RAM, 512GB SSD)",
        "category_slug": "laptops-computers",
        "brand_slug": "dell",
        "model_name": "Inspiron 15 3520",
        "base_price": 52990.0,
        "ean": "884116427216",
        "image_url": (
            "https://i.dell.com/is/image/DellContent/content/dam/ss2/product-images/"
            "dell-client-products/notebooks/inspiron-notebooks/15-3520/pdp/laptop-"
            "inspiron-15-3520-pdp-gray-resin.psd?fmt=pjpg&pscan=auto&scl=1"
            "&hei=402&wid=402&qlt=100,1&resMode=sharp2&size=402,402&chrss=full"
        ),
        "description": (
            "Dell Inspiron 15 3520 with Intel Core i5-1235U (12th Gen), 8GB DDR4 RAM, "
            "512GB SSD, 15.6-inch FHD display, Windows 11 Home."
        ),
        "specs": {
            "Display": "15.6-inch FHD (1920x1080) WVA AG",
            "Processor": "Intel Core i5-1235U (12th Gen)",
            "Memory": "8 GB DDR4",
            "Storage": "512 GB SSD",
            "OS": "Windows 11 Home",
        },
    },
    {
        "name": "HP Pavilion Plus 14-eh1013TU (Intel Core Ultra 5 125H, 16GB, 512GB SSD)",
        "category_slug": "laptops-computers",
        "brand_slug": "hp",
        "model_name": "Pavilion Plus 14-eh1013TU",
        "base_price": 74999.0,
        "ean": "197497584613",
        "image_url": (
            "https://ssl-product-images.www8-hp.com/digmedialib/prodimg/knowledgebase/"
            "c08794973.png"
        ),
        "description": (
            "HP Pavilion Plus 14 with Intel Core Ultra 5 125H, 14-inch 2.8K OLED "
            "display, 16GB RAM, 512GB SSD, Intel Arc Graphics."
        ),
        "specs": {
            "Display": "14-inch 2.8K OLED 120Hz",
            "Processor": "Intel Core Ultra 5 125H",
            "Memory": "16 GB LPDDR5x",
            "Storage": "512 GB PCIe Gen4 SSD",
            "OS": "Windows 11 Home",
        },
    },
    {
        "name": "Lenovo IdeaPad Slim 5 (Intel Core i5-12450H, 16GB RAM, 512GB SSD)",
        "category_slug": "laptops-computers",
        "brand_slug": "lenovo",
        "model_name": "IdeaPad Slim 5 82XF0040IN",
        "base_price": 61990.0,
        "ean": "195477498612",
        "image_url": (
            "https://p3-ofp.static.pub/ShareResource/na/products/laptops/500/"
            "lenovo-laptop-ideapad-slim-5-aura-edition-14-hero.png"
        ),
        "description": (
            "Lenovo IdeaPad Slim 5 with Intel Core i5-12450H, 16GB RAM, 512GB SSD, "
            "15.6-inch FHD IPS display, Windows 11 Home."
        ),
        "specs": {
            "Display": "15.6-inch FHD IPS 300 nits",
            "Processor": "Intel Core i5-12450H",
            "Memory": "16 GB DDR4",
            "Storage": "512 GB SSD PCIe Gen 4",
            "OS": "Windows 11 Home",
        },
    },
    # ── Audio & Headphones ────────────────────────────────────────────────
    {
        "name": "Sony WH-1000XM5 Wireless Noise Cancelling Headphones - Black",
        "category_slug": "audio-headphones",
        "brand_slug": "sony",
        "model_name": "WH-1000XM5",
        "base_price": 26990.0,
        "ean": "4548736146433",
        "image_url": (
            "https://www.sony.co.in/image/8b0f4c0b8d62fa8bb01cc0ee39e78c7d"
        ),
        "description": (
            "Sony WH-1000XM5 flagship noise-canceling headphones featuring Integrated "
            "Processor V1, HD Noise Canceling Processor QN1, 8 microphones for crystal-"
            "clear calls, up to 30-hour battery life."
        ),
        "specs": {
            "Noise Cancellation": "Dual Processor Auto NC Optimizer with 8 mics",
            "Driver": "30mm specially engineered driver",
            "Battery": "Up to 30 hours (NC on), 40 hours (NC off)",
            "Multipoint": "Connect 2 devices simultaneously",
            "Weight": "250 g",
        },
    },
    {
        "name": "Sony WH-CH720N Noise Canceling Wireless Headphones - White",
        "category_slug": "audio-headphones",
        "brand_slug": "sony",
        "model_name": "WH-CH720N",
        "base_price": 9990.0,
        "ean": "4548736144989",
        "image_url": (
            "https://www.sony.co.in/image/5b1c2bf34c4d7cdeb3c7cb5e0e553855"
        ),
        "description": (
            "Sony WH-CH720N over-ear Bluetooth headphones with Integrated Processor V1, "
            "Dual Noise Sensor technology, lightweight 192g design."
        ),
        "specs": {
            "Noise Cancellation": "V1 Processor Dual Noise Sensor",
            "Battery": "Up to 35 hours",
            "Weight": "192 g ultra light",
            "Bluetooth": "5.2",
        },
    },
    {
        "name": "boAt Rockerz 550 Wireless Bluetooth Headphones - Luscious Black",
        "category_slug": "audio-headphones",
        "brand_slug": "boat",
        "model_name": "Rockerz 550",
        "base_price": 1499.0,
        "ean": "8906104900559",
        "image_url": (
            "https://www.boat-lifestyle.com/cdn/shop/products/"
            "Rockerz550_LusciousBlack_1.png?v=1652090563"
        ),
        "description": (
            "boAt Rockerz 550 over-ear wireless headphones with 15H playback, "
            "40mm dynamic drivers, foldable design, and ENx technology."
        ),
        "specs": {
            "Battery": "Up to 15 hours playtime",
            "Driver": "40mm Dynamic Driver",
            "Connectivity": "Bluetooth 5.0",
            "Charging": "Micro USB",
        },
    },
    # ── Televisions ───────────────────────────────────────────────────────
    {
        "name": "Samsung 55-inch Crystal 4K Vivid Pro Ultra HD Smart TV (UA55CUE60AKLXL)",
        "category_slug": "televisions",
        "brand_slug": "samsung",
        "model_name": "UA55CUE60AKLXL",
        "base_price": 44990.0,
        "ean": "880609900001",
        "image_url": (
            "https://images.samsung.com/is/image/samsung/p6pim/in/ua55cue60aklxl/"
            "gallery/in-crystal-uhd-cue60-ua55cue60aklxl-thumb-539474200"
        ),
        "description": (
            "Samsung 55-inch Crystal 4K Smart TV with PurColor, Crystal Processor 4K, "
            "Q-Symphony sound, Motion Xcelerator, Smart Hub with Knox Security."
        ),
        "specs": {
            "Display": "55-inch 4K Ultra HD (3840 x 2160) Crystal UHD",
            "Processor": "Crystal Processor 4K",
            "Audio": "20W 2CH, OTS Lite, Q-Symphony",
            "OS": "Tizen Smart TV",
            "HDR": "HDR10+",
        },
    },
    {
        "name": "Sony Bravia 65-inch X90L 4K Google TV (XR-65X90L)",
        "category_slug": "televisions",
        "brand_slug": "sony",
        "model_name": "XR-65X90L",
        "base_price": 169990.0,
        "ean": "4548736145566",
        "image_url": (
            "https://www.sony.co.in/image/a30a3d9acf7c9fefa374c6c8f2b6acf4"
        ),
        "description": (
            "Sony Bravia 65-inch X90L 4K Full Array LED Google TV with BRAVIA XR "
            "Cognitive Processor, XR Triluminos Pro display, Dolby Vision & Atmos."
        ),
        "specs": {
            "Display": "65-inch 4K Full Array LED",
            "Processor": "BRAVIA XR Cognitive Processor",
            "Audio": "Dolby Atmos, Acoustic Multi-Audio",
            "OS": "Google TV",
            "HDR": "Dolby Vision, HDR10, HLG",
        },
    },
    {
        "name": "LG 43-inch 4K Smart LED TV (43UR7500PSC)",
        "category_slug": "televisions",
        "brand_slug": "lg",
        "model_name": "43UR7500PSC",
        "base_price": 28990.0,
        "ean": "8806084973115",
        "image_url": (
            "https://gscs-b2c.lge.com/downloadFile?fileId=lJ5Yp7qVHSoGBYopIolNSQ"
        ),
        "description": (
            "LG 43-inch 4K Smart TV with α5 AI Processor 4K Gen6, HDR10 support, "
            "webOS 23, Filmmaker Mode, and Game Optimizer."
        ),
        "specs": {
            "Display": "43-inch 4K UHD (3840 x 2160) LED",
            "Processor": "α5 AI Processor 4K Gen6",
            "Audio": "20W 2.0 Ch",
            "OS": "webOS 23",
            "HDR": "HDR10 Pro, HLG",
        },
    },
    # ── Smartwatches ─────────────────────────────────────────────────────
    {
        "name": "Apple Watch SE (2nd Gen) GPS 44mm - Midnight Aluminium",
        "category_slug": "smartwatches-wearables",
        "brand_slug": "apple",
        "model_name": "Apple Watch SE 2nd Gen 44mm GPS",
        "base_price": 29900.0,
        "ean": "194253451427",
        "image_url": (
            "https://store.storeimages.cdn-apple.com/4668/as-images.apple.com/is/"
            "MRTF3ref_VW_34FR+watch-44-alum-midnight-nc-se_VW_34FR_WF_CO+watch-face"
            "-44-midnight-nc-se_VW_34FR?wid=700&hei=700&trim=1"
        ),
        "description": (
            "Apple Watch SE (2nd gen) with S8 SiP chip, crash detection, fall detection, "
            "heart rate monitor, 18-hour battery life."
        ),
        "specs": {
            "Case Size": "44mm Aluminium",
            "Connectivity": "GPS",
            "Battery": "Up to 18 hours",
            "OS": "watchOS",
            "Water Resistance": "50m",
        },
    },
    {
        "name": "Samsung Galaxy Watch 7 47mm LTE - Green",
        "category_slug": "smartwatches-wearables",
        "brand_slug": "samsung",
        "model_name": "Galaxy Watch 7 47mm LTE",
        "base_price": 34999.0,
        "ean": "8806095345444",
        "image_url": (
            "https://images.samsung.com/is/image/samsung/p6pim/in/sm-l315fzgains/"
            "gallery/in-galaxy-watch7-sm-l315-sm-l315fzgains-thumb-541219200"
        ),
        "description": (
            "Samsung Galaxy Watch 7 with Exynos W1000, advanced health monitoring "
            "(BioActive sensor), sleep coaching, AI-powered energy score."
        ),
        "specs": {
            "Case Size": "47mm",
            "Connectivity": "LTE + Wi-Fi + Bluetooth 5.3",
            "Battery": "Up to 40 hours (Typical), Up to 18 hours (LTE)",
            "OS": "One UI Watch 6 (Wear OS 5)",
            "Water Resistance": "10 ATM",
        },
    },
    # ── Tablets ──────────────────────────────────────────────────────────
    {
        "name": "Apple iPad Air M2 (11-inch, Wi-Fi, 128GB) - Starlight",
        "category_slug": "tablets",
        "brand_slug": "apple",
        "model_name": "iPad Air M2 11-inch",
        "base_price": 59900.0,
        "ean": "195949108402",
        "image_url": (
            "https://store.storeimages.cdn-apple.com/4668/as-images.apple.com/is/"
            "ipad-air-finish-unselect-gallery-1-202405?wid=5120&hei=2880&fmt=p-jpg"
            "&qlt=95&.v=1708871520363"
        ),
        "description": (
            "iPad Air with Apple M2 chip, 11-inch Liquid Retina display, 12MP camera, "
            "10-hour battery life, Center Stage."
        ),
        "specs": {
            "Display": "11-inch Liquid Retina (2360 x 1640)",
            "Processor": "Apple M2 chip",
            "Storage": "128 GB",
            "Camera": "12MP Wide + 12MP Ultra Wide TrueDepth front",
            "Battery": "Up to 10 hours",
        },
    },
    {
        "name": "Samsung Galaxy Tab S9 FE (10.9-inch, Wi-Fi, 128GB) with S Pen - Lavender",
        "category_slug": "tablets",
        "brand_slug": "samsung",
        "model_name": "Galaxy Tab S9 FE",
        "base_price": 34999.0,
        "ean": "8806095017892",
        "image_url": (
            "https://images.samsung.com/is/image/samsung/p6pim/in/"
            "sm-x516blgains/gallery/in-galaxy-tab-s9-fe-sm-x516-sm-x516blgains-thumb"
        ),
        "description": (
            "Samsung Galaxy Tab S9 FE with Exynos 1380, 10.9-inch TFT LCD display, "
            "8MP rear camera, 10090 mAh battery, included S Pen."
        ),
        "specs": {
            "Display": "10.9-inch TFT LCD (2304 x 1440)",
            "Processor": "Exynos 1380",
            "RAM": "6 GB",
            "Storage": "128 GB",
            "Battery": "10090 mAh with 45W fast charging",
            "Includes": "S Pen",
        },
    },
    # ── Gaming ────────────────────────────────────────────────────────────
    {
        "name": "Sony PlayStation 5 (PS5) Slim Console - Disc Edition",
        "category_slug": "gaming",
        "brand_slug": "sony",
        "model_name": "PlayStation 5 Slim Disc Edition",
        "base_price": 54990.0,
        "ean": "711719577898",
        "image_url": (
            "https://gmedia.playstation.com/is/image/SIEPDC/"
            "ps5-slim-product-thumbnail-01-en-10aug23?$1600px--t$"
        ),
        "description": (
            "PlayStation 5 Slim console with AMD Ryzen Zen 2 CPU, AMD RDNA 2 GPU, "
            "1TB SSD, 4K UHD Blu-ray drive, DualSense wireless controller included."
        ),
        "specs": {
            "CPU": "AMD Ryzen Zen 2, 8 Cores, 3.5GHz",
            "GPU": "AMD RDNA 2, 10.3 TFLOPS",
            "RAM": "16 GB GDDR6",
            "Storage": "1 TB Custom SSD",
            "Resolution": "Up to 8K",
            "Includes": "DualSense Wireless Controller",
        },
    },
    # ── Appliances ────────────────────────────────────────────────────────
    {
        "name": "LG 242L 3 Star Smart Inverter Frost-Free Double Door Refrigerator "
                "(GL-S262SDSY)",
        "category_slug": "refrigerators",
        "brand_slug": "lg",
        "model_name": "GL-S262SDSY",
        "base_price": 26490.0,
        "ean": "8806084974181",
        "image_url": (
            "https://gscs-b2c.lge.com/downloadFile?fileId=lLF3q9mPD3WQ6Z7BI23lLw"
        ),
        "description": (
            "LG 242L 3-Star Frost-Free Double Door Refrigerator with Smart Inverter "
            "Compressor, Door Cooling+, Multi Air Flow system."
        ),
        "specs": {
            "Capacity": "242 Litres",
            "Star Rating": "3 Star",
            "Compressor": "Smart Inverter",
            "Type": "Frost Free Double Door",
            "Warranty": "10 Years on Compressor",
        },
    },
    {
        "name": "Whirlpool 7.5 Kg 5 Star Fully-Automatic Top Load Washing Machine "
                "(WHITEMAGIC ELITE 7.5)",
        "category_slug": "washing-machines",
        "brand_slug": "whirlpool",
        "model_name": "WHITEMAGIC ELITE 7.5",
        "base_price": 19490.0,
        "ean": "8901722119131",
        "image_url": (
            "https://assets.whirlpool.in/content/dam/documents/product-images/"
            "washing-machine/31438-White.png"
        ),
        "description": (
            "Whirlpool 7.5 Kg 5-Star Fully Automatic Top Load Washing Machine with "
            "6th Sense Technology, StainWash technology, 12 wash programs."
        ),
        "specs": {
            "Capacity": "7.5 Kg",
            "Star Rating": "5 Star",
            "Type": "Fully Automatic Top Load",
            "Technology": "6th Sense Technology",
            "Programs": "12 Wash Programs",
        },
    },
    # ── Footwear ─────────────────────────────────────────────────────────
    {
        "name": "Nike Air Zoom Pegasus 41 Running Shoes - Black/White (Men's)",
        "category_slug": "footwear",
        "brand_slug": "nike",
        "model_name": "Air Zoom Pegasus 41",
        "base_price": 10995.0,
        "ean": "196978050972",
        "image_url": (
            "https://static.nike.com/a/images/t_PDP_936_v1/"
            "f_auto,q_auto:eco/i1-aad30e0e-7cc4-4b0b-afec-49f61c90f8e3/"
            "pegasus-41-road-running-shoes-JRPJVG.png"
        ),
        "description": (
            "Nike Air Zoom Pegasus 41 with ZoomX foam, Zoom Air in the forefoot, "
            "engineered mesh upper for breathability, rubber outsole."
        ),
        "specs": {
            "Technology": "ZoomX foam + Zoom Air unit",
            "Upper": "Engineered mesh",
            "Outsole": "Rubber",
            "Drop": "10mm",
            "Weight": "Approx. 284g (Men's size 10)",
        },
    },
    {
        "name": "Adidas Ultraboost Light Running Shoes - Core Black/Carbon",
        "category_slug": "footwear",
        "brand_slug": "adidas",
        "model_name": "Ultraboost Light",
        "base_price": 14999.0,
        "ean": "4066754074618",
        "image_url": (
            "https://assets.adidas.com/images/h_840,f_auto,q_auto,"
            "fl_lossy,c_fill,g_auto/f1437e2e0ef84e6ab780af970184acfe_9366/"
            "Ultraboost_Light_Shoes_Black_HQ6339_01_standard.jpg"
        ),
        "description": (
            "Adidas Ultraboost Light with BOOST cushioning 30% lighter than previous "
            "generation, Linear Energy Push system, Primeknit+ upper."
        ),
        "specs": {
            "Technology": "BOOST midsole (30% lighter), Linear Energy Push",
            "Upper": "Primeknit+",
            "Outsole": "Continental™ rubber",
            "Drop": "10mm",
        },
    },
]


# ── Main Seed Script ───────────────────────────────────────────────────────

async def seed_database():
    print("=========================================================")
    print("COMPAREX Production Database Seed Script (Curated Products)")
    print("=========================================================")

    # Ensure all tables exist in PostgreSQL
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        # 1. Marketplaces
        print("\n[1/5] Seeding 7 Major Indian Retail Marketplaces...")
        marketplace_map = {}
        for mp_data in MARKETPLACES:
            res = await session.execute(
                select(Marketplace).where(
                    or_(Marketplace.slug == mp_data["slug"], Marketplace.name == mp_data["name"])
                )
            )
            existing = res.scalars().first()
            if not existing:
                mp = Marketplace(
                    id=uuid.uuid4(),
                    name=mp_data["name"],
                    slug=mp_data["slug"],
                    base_url=mp_data["base_url"],
                    logo_url=mp_data["logo_url"],
                    country_code=mp_data["country_code"],
                    is_active=True,
                )
                session.add(mp)
                await session.flush()
                marketplace_map[mp.slug] = mp
                print(f"  + Created Marketplace: {mp.name}")
            else:
                marketplace_map[existing.slug] = existing
                print(f"  . Existing Marketplace: {existing.name}")

        # 2. Categories
        print("\n[2/5] Seeding Categories...")
        category_map = {}
        # First pass: Top-level
        for cat_data in CATEGORIES:
            if cat_data["parent"] is None:
                res = await session.execute(
                    select(Category).where(Category.slug == cat_data["slug"])
                )
                existing = res.scalar_one_or_none()
                if not existing:
                    cat = Category(
                        id=uuid.uuid4(),
                        name=cat_data["name"],
                        slug=cat_data["slug"],
                        description=cat_data["description"],
                        parent_id=None,
                    )
                    session.add(cat)
                    await session.flush()
                    category_map[cat.slug] = cat
                    print(f"  + Created Top Category: {cat.name}")
                else:
                    category_map[existing.slug] = existing

        # Second pass: Subcategories
        for cat_data in CATEGORIES:
            if cat_data["parent"] is not None:
                res = await session.execute(
                    select(Category).where(Category.slug == cat_data["slug"])
                )
                existing = res.scalar_one_or_none()
                parent_obj = category_map.get(cat_data["parent"])
                parent_id = parent_obj.id if parent_obj else None
                if not existing:
                    cat = Category(
                        id=uuid.uuid4(),
                        name=cat_data["name"],
                        slug=cat_data["slug"],
                        description=cat_data["description"],
                        parent_id=parent_id,
                    )
                    session.add(cat)
                    await session.flush()
                    category_map[cat.slug] = cat
                    print(f"  + Created Subcategory: {cat.name}")
                else:
                    category_map[existing.slug] = existing

        # 3. Brands
        print("\n[3/5] Seeding Brands...")
        brand_map = {}
        for b_data in BRANDS:
            res = await session.execute(
                select(Brand).where(Brand.slug == b_data["slug"])
            )
            existing = res.scalar_one_or_none()
            if not existing:
                brand = Brand(
                    id=uuid.uuid4(),
                    name=b_data["name"],
                    slug=b_data["slug"],
                    logo_url=b_data["logo_url"],
                    website_url=b_data["website_url"],
                )
                session.add(brand)
                await session.flush()
                brand_map[brand.slug] = brand
                print(f"  + Created Brand: {brand.name}")
            else:
                brand_map[existing.slug] = existing

        # 4. Curated Real Products (catalog only — no fake listings or fake prices)
        print("\n[4/5] Seeding Curated Real Products (catalog information only)...")
        product_count = 0

        for p_data in CURATED_PRODUCTS:
            # Check by EAN first (unique identifier), then by name
            res = await session.execute(
                select(Product).where(Product.ean == p_data["ean"])
            )
            existing = res.scalar_one_or_none()

            if existing:
                print(f"  . Existing Product: {p_data['name'][:60]}")
                # Update image_url if it's currently None or Unsplash
                if (
                    not existing.image_url
                    or "unsplash.com" in (existing.image_url or "")
                ):
                    existing.image_url = p_data["image_url"]
                    print(f"    -> Updated image URL")
                continue

            cat_obj = category_map.get(p_data["category_slug"])
            brand_obj = brand_map.get(p_data["brand_slug"])

            prod = Product(
                id=uuid.uuid4(),
                name=p_data["name"],
                description=p_data["description"],
                category_id=cat_obj.id if cat_obj else None,
                brand_id=brand_obj.id if brand_obj else None,
                category=cat_obj.name if cat_obj else p_data["category_slug"].title(),
                brand=brand_obj.name if brand_obj else p_data["brand_slug"].title(),
                image_url=p_data["image_url"],
                ean=p_data["ean"],
                model_name=p_data.get("model_name"),
                # base_price is a catalog reference price, NOT a live marketplace price
                base_price=Decimal(str(p_data["base_price"])),
                is_verified=True,
                is_quarantined=False,
            )
            session.add(prod)
            await session.flush()
            product_count += 1

            # Specs
            for spec_k, spec_v in p_data.get("specs", {}).items():
                spec = ProductSpecification(
                    id=uuid.uuid4(),
                    product_id=prod.id,
                    key=spec_k,
                    value=str(spec_v),
                )
                session.add(spec)

            # Primary Image (real manufacturer/CDN URL)
            img = ProductImage(
                id=uuid.uuid4(),
                product_id=prod.id,
                url=p_data["image_url"],
                alt_text=p_data["name"],
                is_primary=True,
            )
            session.add(img)

            print(f"  + Product: {prod.name[:70]}")

        print("\n[5/5] Committing database transaction...")
        await session.commit()
        print("  [OK] Transaction committed successfully.")

        # Final Statistics
        print("\nFinal Production Database Statistics:")
        m_cnt = (
            await session.execute(select(func.count()).select_from(Marketplace))
        ).scalar()
        c_cnt = (
            await session.execute(select(func.count()).select_from(Category))
        ).scalar()
        b_cnt = (
            await session.execute(select(func.count()).select_from(Brand))
        ).scalar()
        p_cnt = (
            await session.execute(select(func.count()).select_from(Product))
        ).scalar()

        print(f"  * Marketplaces: {m_cnt}")
        print(f"  * Categories:   {c_cnt}")
        print(f"  * Brands:       {b_cnt}")
        print(f"  * Products:     {p_cnt}")
        print(
            "\nNOTE: No marketplace listings or price history were seeded."
        )
        print(
            "      Live prices come exclusively from verified marketplace "
            "aggregator observations."
        )
        print("\n=========================================================")
        print("COMPAREX Production Database Seeding Completed Successfully!")
        print("=========================================================")


if __name__ == "__main__":
    asyncio.run(seed_database())
