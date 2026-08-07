"""
COMPAREX Backend - High-Scale Idempotent Catalog Seeding Pipeline (>100,000 Products)

Populates product catalog with >=100,000 products (scalable to millions) across 15 categories:
Mobiles, Laptops, Tablets, Smart Watches, Headphones, TVs, Home Appliances,
Fashion, Beauty, Furniture, Groceries, Books, Toys, Sports, Automotive.

Each product includes:
- Canonical Name & EAN
- Brand & Category linking
- Base Price & Multiple Price Ranges
- Detailed Key-Value Specifications
- 5-10 HD Gallery Image URLs
- Rich Descriptions
- Ratings, Reviews, Popularity Scores
- Search Keywords & AI Tags
- Cross-Marketplace Listings (Amazon, Flipkart, Croma, Reliance Digital)
"""

import argparse
import asyncio
import os
import random
import sys
import uuid
from decimal import Decimal

# Ensure backend path is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import select, func
from app.db.session import AsyncSessionLocal
from app.models.brand import Brand
from app.models.category import Category
from app.models.marketplace import Marketplace
from app.models.product import Product
from app.models.product_image import ProductImage
from app.models.product_listing import ProductListing
from app.models.product_specification import ProductSpecification

# 15 Required Categories & Rich Spec Generation Metadata
CATEGORIES_DATA = {
    "Mobiles": {
        "slug": "mobiles",
        "brands": ["Apple", "Samsung", "POCO", "Xiaomi", "OnePlus", "Google", "Realme", "iQOO", "Vivo", "Motorola", "Nothing", "Honor"],
        "price_range": (8999, 159900),
        "keywords": ["5g", "smartphone", "camera", "oled", "fast charging", "gaming", "amoled", "snapdragon", "bionic"],
        "specs": [
            ("Processor", ["Snapdragon 8 Gen 3", "Apple A17 Pro", "Dimensity 9300", "Snapdragon 7+ Gen 3", "Exynos 2400"]),
            ("Display", ["6.7-inch Super AMOLED 120Hz", "6.1-inch Super Retina XDR", "6.78-inch LTPO OLED", "6.67-inch FHD+ 144Hz"]),
            ("Camera", ["200MP + 50MP + 12MP Triple", "48MP Main + 12MP UltraWide", "50MP Sony LYT-900 OIS", "108MP Quad Camera"]),
            ("Battery", ["5000 mAh 120W HyperCharge", "4422 mAh MagSafe", "5500 mAh 100W SUPERVOOC", "4800 mAh 67W Turbo"]),
            ("RAM & Storage", ["8GB / 128GB", "12GB / 256GB", "16GB / 512GB", "16GB / 1TB"]),
            ("OS", ["Android 14 / Funtouch 14", "iOS 17", "OxygenOS 14", "One UI 6.1", "HyperOS"]),
        ],
        "templates": [
            "{brand} Galaxy S{num} Ultra 5G", "{brand} iPhone {num} Pro Max ({ram}GB)",
            "{brand} Phone {num} Pro 5G", "{brand} Note {num} Pro Plus", "{brand} Edge {num} Ultra",
            "{brand} Neo {num} 5G", "{brand} Nord CE {num}", "{brand} GT {num} Pro",
            "{brand} Pixel {num} Pro 5G", "{brand} Z Flip {num}", "{brand} Magic {num} Pro"
        ],
        "images": [
            "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=800&q=80",
            "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=800&q=80",
            "https://images.unsplash.com/photo-1565849904461-04a58ad377e0?w=800&q=80",
            "https://images.unsplash.com/photo-1574944985070-8f30c4397e3c?w=800&q=80",
            "https://images.unsplash.com/photo-1592899677977-9c10ca588bbd?w=800&q=80",
            "https://images.unsplash.com/photo-1580910051074-3eb694886505?w=800&q=80",
            "https://images.unsplash.com/photo-1533228876829-65c94e7b5025?w=800&q=80",
            "https://images.unsplash.com/photo-1601784551446-20c9e07cdbdb?w=800&q=80",
        ]
    },
    "Laptops": {
        "slug": "laptops",
        "brands": ["Apple", "Dell", "ASUS", "HP", "Lenovo", "Acer", "MSI", "Samsung", "Razer", "Gigabyte"],
        "price_range": (29990, 329900),
        "keywords": ["laptop", "notebook", "macbook", "gaming", "intel i9", "ryzen 9", "rtx 4090", "thin and light", "oled"],
        "specs": [
            ("Processor", ["Intel Core i9-14900HX", "Apple M3 Max", "AMD Ryzen 9 7945HX", "Intel Core Ultra 7", "Apple M3 Pro"]),
            ("Graphics", ["NVIDIA RTX 4090 16GB", "Apple 38-core GPU", "NVIDIA RTX 4070 8GB", "NVIDIA RTX 4060 8GB", "Intel Arc"]),
            ("RAM", ["16GB LPDDR5X", "32GB DDR5 5600MHz", "64GB DDR5", "128GB Unified"]),
            ("Storage", ["512GB PCIe 4.0 NVMe SSD", "1TB Gen4 SSD", "2TB NVMe M.2 SSD", "4TB SSD"]),
            ("Display", ["16-inch 3.2K 165Hz Mini-LED", "14.2-inch Liquid Retina XDR", "15.6-inch QHD 240Hz", "13.6-inch Retina"]),
        ],
        "templates": [
            "{brand} MacBook Air M{num} ({ram}GB, {storage}GB)", "{brand} XPS {num} OLED Laptop",
            "{brand} ROG Zephyrus G{num}", "{brand} ThinkPad X1 Carbon Gen {num}",
            "{brand} Pavilion x360 14", "{brand} Predator Helios {num}", "{brand} ZenBook 14 OLED",
            "{brand} Legion Pro {num} Gaming Laptop", "{brand} Galaxy Book {num} Pro 360", "{brand} Vivobook S{num}"
        ],
        "images": [
            "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=800&q=80",
            "https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=800&q=80",
            "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=800&q=80",
            "https://images.unsplash.com/photo-1525547719571-a2d4ac8945e2?w=800&q=80",
            "https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=800&q=80",
            "https://images.unsplash.com/photo-1541807084-5c52b6b3adef?w=800&q=80",
        ]
    },
    "Tablets": {
        "slug": "tablets",
        "brands": ["Apple", "Samsung", "Lenovo", "Xiaomi", "OnePlus", "Realme", "Honor"],
        "price_range": (11999, 139900),
        "keywords": ["tablet", "ipad", "stylus", "drawing", "amoled", "4k", "keyboard", "portable"],
        "specs": [
            ("Screen", ["13-inch Ultra Retina Tandem OLED", "12.4-inch Dynamic AMOLED 2X", "11-inch 2.5K 144Hz", "10.9-inch Liquid Retina"]),
            ("Chipset", ["Apple M4", "Snapdragon 8 Gen 2", "MediaTek Dimensity 9000", "Apple M2"]),
            ("Battery", ["10090 mAh 45W", "8820 mAh 67W", "7600 mAh 33W"]),
        ],
        "templates": [
            "{brand} iPad Air M{num} Wi-Fi", "{brand} Galaxy Tab S{num} Ultra",
            "{brand} Pad {num} Pro Tablet", "{brand} Tab P{num} Pro 11-inch",
            "{brand} iPad Pro 12.9-inch M{num}", "{brand} Pad Go LTE", "{brand} Galaxy Tab A{num}"
        ],
        "images": [
            "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=800&q=80",
            "https://images.unsplash.com/photo-1561154464-82e9adf32764?w=800&q=80",
            "https://images.unsplash.com/photo-1585790050230-5dd28404ccb9?w=800&q=80",
            "https://images.unsplash.com/photo-1589739900243-4b52cd9b104e?w=800&q=80",
        ]
    },
    "Smart Watches": {
        "slug": "smart-watches",
        "brands": ["Apple", "Samsung", "Garmin", "boAt", "Noise", "Amazfit", "Fire-Boltt", "Fitbit", "Fossil"],
        "price_range": (1299, 69990),
        "keywords": ["smartwatch", "fitness tracker", "heart rate", "gps", "amoled", "ecg", "calling", "sports"],
        "specs": [
            ("Display", ["1.96-inch HD AMOLED 600 nits", "1.4-inch Sapphire Crystal", "1.39-inch Circular Retina"]),
            ("Sensors", ["ECG + Heart Rate + SpO2 + Temperature", "BioTracker 4.0 PPG", "Multi-GNSS Dual-Band GPS"]),
            ("Battery Life", ["Up to 14 Days", "Up to 36 Hours Normal Use", "Up to 7 Days Heavy Use"]),
        ],
        "templates": [
            "{brand} Watch Series {num} GPS", "{brand} Galaxy Watch {num} Classic",
            "{brand} Fenix {num} Pro Multisport", "{brand} Wave Call {num} Smartwatch",
            "{brand} ColorFit Pro {num}", "{brand} GTR {num} AMOLED Watch", "{brand} Ninja Call Pro"
        ],
        "images": [
            "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800&q=80",
            "https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?w=800&q=80",
            "https://images.unsplash.com/photo-1434493789847-2f02dc6ca35d?w=800&q=80",
            "https://images.unsplash.com/photo-1579586337278-3befd40fd17a?w=800&q=80",
        ]
    },
    "Headphones": {
        "slug": "headphones",
        "brands": ["Sony", "Bose", "Sennheiser", "boAt", "JBL", "Realme", "OnePlus", "Apple", "Marshall", "Anker"],
        "price_range": (999, 49900),
        "keywords": ["headphones", "earbuds", "wireless", "bluetooth", "noise cancellation", "anc", "bass", "audio"],
        "specs": [
            ("Driver", ["40mm Neodymium Driver", "11mm Dynamic Driver + 6mm Planar", "30mm Precision Engineered"]),
            ("Active Noise Cancellation", ["Industry-leading HD Noise Cancelling Processor QN1", "Customizable Active ANC 45dB", "Spatial Audio with Dynamic Head Tracking"]),
            ("Battery Life", ["30 Hours Playtime with Fast Charge", "40 Hours Playback", "24 Hours Total with Charging Case"]),
        ],
        "templates": [
            "{brand} WH-1000XM{num} Wireless ANC", "{brand} QuietComfort {num} Headphones",
            "{brand} Momentum {num} Wireless", "{brand} Rockerz {num} Over Ear",
            "{brand} Tune {num} BT Headset", "{brand} Buds Air {num} TWS", "{brand} AirPods Pro Gen {num}"
        ],
        "images": [
            "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&q=80",
            "https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=800&q=80",
            "https://images.unsplash.com/photo-1484704849700-f032a568e944?w=800&q=80",
            "https://images.unsplash.com/photo-1583394838336-acd977736f90?w=800&q=80",
        ]
    },
    "TVs": {
        "slug": "tvs",
        "brands": ["LG", "Samsung", "Sony", "TCL", "Xiaomi", "Hisense", "OnePlus", "VU", "Acer"],
        "price_range": (11990, 249900),
        "keywords": ["tv", "television", "smart tv", "4k", "oled", "qled", "hdr10+", "dolby vision", "google tv"],
        "specs": [
            ("Display Panel", ["4K Ultra HD OLED EVO Panel 120Hz", "Neo QLED 4K Quantum Matrix", "4K HDR Dolby Vision Atmos"]),
            ("Audio", ["60W 4.2 Channel Dolby Atmos", "40W Sound by Onkyo", "20W Stereo Speakers DTS Virtual:X"]),
            ("Smart OS", ["Google TV", "webOS 24", "Tizen OS", "Fire TV Edition"]),
        ],
        "templates": [
            "{brand} C{num} {size}-inch 4K OLED Smart TV", "{brand} Neo QLED {size}-inch 4K TV",
            "{brand} Bravia XR {size}-inch Google TV", "{brand} QLED {size}-inch 4K Android TV",
            "{brand} Smart TV X{num} {size}-inch Ultra HD"
        ],
        "images": [
            "https://images.unsplash.com/photo-1593784991095-a205069470b6?w=800&q=80",
            "https://images.unsplash.com/photo-1461151304267-38535e780c79?w=800&q=80",
            "https://images.unsplash.com/photo-1577979749830-f1d742b96791?w=800&q=80",
        ]
    },
    "Home Appliances": {
        "slug": "home-appliances",
        "brands": ["Dyson", "Philips", "Bosch", "IFB", "LG", "Whirlpool", "Samsung", "Haier", "Voltas", "Panasonic"],
        "price_range": (2999, 119900),
        "keywords": ["appliance", "washing machine", "refrigerator", "air conditioner", "ac", "vacuum", "air fryer"],
        "specs": [
            ("Energy Rating", ["5 Star BEE Certified", "4 Star Inverter Efficiency", "3 Star Energy Saver"]),
            ("Capacity", ["8.0 kg Front Load", "550 Litres Side-by-Side", "1.5 Ton Inverter Dual Split", "7.2 Litres XXL"]),
            ("Technology", ["AI Direct Drive Motor", "Digital Inverter Compressor", "HEPA H13 Air Filtration"]),
        ],
        "templates": [
            "{brand} V{num} Detect Cordless Vacuum", "{brand} Air Fryer XXL 7.{num}L",
            "{brand} Front Load Washing Machine {size}kg", "{brand} Frost Free Double Door Refrigerator",
            "{brand} Inverter Split AC 1.5 Ton 5 Star", "{brand} Dishwasher {num} Place Settings"
        ],
        "images": [
            "https://images.unsplash.com/photo-1584622650111-993a426fbf0a?w=800&q=80",
            "https://images.unsplash.com/photo-1556911220-e15b29be8c8f?w=800&q=80",
            "https://images.unsplash.com/photo-1626806787461-102c1bfaaea1?w=800&q=80",
        ]
    },
    "Fashion": {
        "slug": "fashion",
        "brands": ["Nike", "Adidas", "Puma", "Levi's", "Zara", "H&M", "Tommy Hilfiger", "Calvin Klein", "Under Armour"],
        "price_range": (699, 19999),
        "keywords": ["fashion", "clothing", "sneakers", "shoes", "hoodie", "jeans", "apparel", "wearable"],
        "specs": [
            ("Material", ["100% Organic Cotton", "Breathable Mesh + Cushion Poly", "Stretch Denim"]),
            ("Fit Type", ["Regular Fit", "Slim Fit", "Athletic Active Fit"]),
        ],
        "templates": [
            "{brand} Air Force {num} '07 Sneakers", "{brand} Trefoil Cotton Hoodie",
            "{brand} Slim Fit Stretch Jeans", "{brand} Running Shoes Pro {num}",
            "{brand} Essential Casual Shirt", "{brand} Sportswear Track Pant"
        ],
        "images": [
            "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800&q=80",
            "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=800&q=80",
            "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=800&q=80",
            "https://images.unsplash.com/photo-1434389677669-e08b4cac3105?w=800&q=80",
        ]
    },
    "Beauty": {
        "slug": "beauty",
        "brands": ["Estée Lauder", "L'Oréal", "Maybelline", "Nivea", "The Body Shop", "Neutrogena", "MAC", "Clinique"],
        "price_range": (299, 12900),
        "keywords": ["beauty", "skincare", "makeup", "serum", "foundation", "moisturizer", "dermatologist approved"],
        "specs": [
            ("Skin Type", ["All Skin Types", "Sensitive & Dry Skin", "Oily & Combination Skin"]),
            ("Volume", ["50ml", "100ml", "30ml Bottle"]),
        ],
        "templates": [
            "{brand} Advanced Night Repair Serum {size}ml", "{brand} Revitalift Hyaluronic Acid Cream",
            "{brand} Fit Me Matte Foundation", "{brand} Soft Light Moisture Cream",
            "{brand} Tea Tree Skin Clearing Facial Wash"
        ],
        "images": [
            "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=800&q=80",
            "https://images.unsplash.com/photo-1571781926291-c477ebfd024b?w=800&q=80",
            "https://images.unsplash.com/photo-1598440947619-2c35fc9aa908?w=800&q=80",
        ]
    },
    "Furniture": {
        "slug": "furniture",
        "brands": ["Featherlite", "IKEA", "Wakefit", "Godrej Interio", "Nilkamal", "Durian", "Pepperfry"],
        "price_range": (1999, 79990),
        "keywords": ["furniture", "chair", "bed", "sofa", "table", "desk", "home decor", "wood"],
        "specs": [
            ("Primary Material", ["Solid Sheesham Wood", "High-Grade Engineered Wood + Metal Frame", "Breathable Mesh + Memory Foam"]),
            ("Warranty", ["3 Years Manufacturer Warranty", "5 Years Structural Guarantee"]),
        ],
        "templates": [
            "{brand} Ergonomic Mesh Office Chair", "{brand} Solid Wood Queen Bed",
            "{brand} 3-Seater Fabric Sofa", "{brand} Study Table with Storage",
            "{brand} Recliner Armchair Comfort"
        ],
        "images": [
            "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=800&q=80",
            "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=800&q=80",
            "https://images.unsplash.com/photo-1540574163026-643ea20ade25?w=800&q=80",
        ]
    },
    "Groceries": {
        "slug": "groceries",
        "brands": ["Borges", "Tata Sampann", "Fortune", "Nestlé", "Amul", "Kellogg's", "Dabur", "Organic India"],
        "price_range": (99, 1999),
        "keywords": ["groceries", "food", "olive oil", "dal", "pulses", "organic", "health", "staples"],
        "specs": [
            ("Pack Size", ["1 Kg", "5 Kg", "1 Litre Bottle", "Pack of 3"]),
            ("Shelf Life", ["12 Months", "18 Months", "6 Months"]),
        ],
        "templates": [
            "{brand} Extra Virgin Olive Oil 1L", "{brand} Organic Unpolished Arhar Dal 1kg",
            "{brand} Sunlite Refined Sunflower Oil 5L", "{brand} Everyday Dairy Whitener",
            "{brand} Real Fruit Juice Pack of {num}"
        ],
        "images": [
            "https://images.unsplash.com/photo-1542838132-92c53300491e?w=800&q=80",
            "https://images.unsplash.com/photo-1588964895597-cfccd6e2dbf9?w=800&q=80",
        ]
    },
    "Books": {
        "slug": "books",
        "brands": ["Penguin", "HarperCollins", "Rupa", "Bloomsbury", "Oxford", "Simon & Schuster"],
        "price_range": (199, 1999),
        "keywords": ["books", "novel", "bestseller", "reading", "paperback", "hardcover", "education", "literature"],
        "specs": [
            ("Format", ["Paperback", "Hardcover Collector Edition"]),
            ("Language", ["English"]),
        ],
        "templates": [
            "Atomic Habits by James Clear Vol {num}", "The Psychology of Money Edition {num}",
            "Rich Dad Poor Dad Guide {num}", "Sapiens Masterpiece Vol {num}",
            "Deep Work Principles Vol {num}", "Thinking Fast and Slow Ed {num}"
        ],
        "images": [
            "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=800&q=80",
            "https://images.unsplash.com/photo-1512820790803-83ca734da794?w=800&q=80",
        ]
    },
    "Toys": {
        "slug": "toys",
        "brands": ["LEGO", "Hot Wheels", "Barbie", "Nerf", "Fisher-Price", "Hamleys", "Hasbro"],
        "price_range": (399, 49999),
        "keywords": ["toys", "kids", "games", "lego", "building blocks", "dolls", "action figures"],
        "specs": [
            ("Age Range", ["8+ Years", "3-6 Years", "10+ Years"]),
            ("Safety", ["Non-Toxic BPA Free Plastic"]),
        ],
        "templates": [
            "{brand} Technic Bugatti Chiron Set {num}", "{brand} Die-Cast Track Builder Set {num}",
            "{brand} Dreamhouse Dollhouse Edition {num}", "{brand} Elite Blaster Gun V{num}", "{brand} Learning Activity Table"
        ],
        "images": [
            "https://images.unsplash.com/photo-1566576912321-d58ddd7a6088?w=800&q=80",
            "https://images.unsplash.com/photo-1587654780291-39c9404d746b?w=800&q=80",
        ]
    },
    "Sports": {
        "slug": "sports",
        "brands": ["Yonex", "Decathlon", "Cosco", "Nivia", "Vector X", "Puma Sports", "Under Armour"],
        "price_range": (399, 24990),
        "keywords": ["sports", "fitness", "gym", "racket", "football", "cricket", "yoga", "workout"],
        "specs": [
            ("Sport Type", ["Badminton", "Fitness & Gym", "Football", "Cricket"]),
        ],
        "templates": [
            "{brand} Astrox {num} Pro Badminton Racket", "{brand} Seamless Fitness Yoga Mat {num}mm",
            "{brand} Country Football Size {num}", "{brand} Cricket Bat English Willow {num}",
            "{brand} Adjustable Dumbbell Set {size}kg"
        ],
        "images": [
            "https://images.unsplash.com/photo-1517649763962-0c623266010b?w=800&q=80",
            "https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=800&q=80",
        ]
    },
    "Automotive": {
        "slug": "automotive",
        "brands": ["70mai", "Bosch", "Michelin", "Philips Automotive", "CEAT", "Apollo Tyres"],
        "price_range": (799, 29990),
        "keywords": ["automotive", "car accessories", "dashcam", "tyres", "car washer", "led bulbs", "inflator"],
        "specs": [
            ("Vehicle Type", ["Car & SUV", "Universal Fit"]),
        ],
        "templates": [
            "{brand} Dash Cam Pro Plus A{num}", "{brand} High Pressure Car Washer V{num}",
            "{brand} Tubeless Car Tyre 195/55 R16 Gen {num}", "{brand} LED Headlight Bulb Pair {num}W",
            "{brand} Digital Tyre Inflator Pump V{num}"
        ],
        "images": [
            "https://images.unsplash.com/photo-1511919884226-fd3cad34687c?w=800&q=80",
            "https://images.unsplash.com/photo-1489824904134-891ab64532f1?w=800&q=80",
        ]
    }
}

MARKETPLACES_SEED = [
    {"name": "Amazon India", "slug": "amazon", "base_url": "https://www.amazon.in"},
    {"name": "Flipkart", "slug": "flipkart", "base_url": "https://www.flipkart.com"},
    {"name": "Croma", "slug": "croma", "base_url": "https://www.croma.com"},
    {"name": "Reliance Digital", "slug": "reliance-digital", "base_url": "https://www.reliancedigital.in"},
]


async def seed_scalable_catalog(target_count: int = 100000, batch_size: int = 5000):
    """Seed target_count products across 15 categories with batch transactions."""
    print("==================================================================")
    print(f"COMPAREX Scalable Catalog Generator (Target: {target_count:,} Products)")
    print("==================================================================")

    async with AsyncSessionLocal() as session:
        # 1. Seed/Fetch Marketplaces
        marketplaces: list[Marketplace] = []
        for m_data in MARKETPLACES_SEED:
            stmt = select(Marketplace).where(Marketplace.slug == m_data["slug"])
            res = await session.execute(stmt)
            m = res.scalars().first()
            if not m:
                m = Marketplace(
                    id=uuid.uuid4(),
                    name=m_data["name"],
                    slug=m_data["slug"],
                    base_url=m_data["base_url"],
                    country_code="IN",
                    is_active=True,
                )
                session.add(m)
                await session.flush()
            marketplaces.append(m)
        await session.commit()

        # 2. Seed/Fetch Categories & Brands
        category_map: dict[str, Category] = {}
        brand_map: dict[str, Brand] = {}

        for cat_name, data in CATEGORIES_DATA.items():
            cat_slug = data["slug"]
            stmt = select(Category).where(Category.slug == cat_slug)
            res = await session.execute(stmt)
            cat_obj = res.scalars().first()
            if not cat_obj:
                cat_obj = Category(
                    id=uuid.uuid4(),
                    name=cat_name,
                    slug=cat_slug,
                    description=f"{cat_name} product catalog on COMPAREX",
                )
                session.add(cat_obj)
                await session.flush()
            category_map[cat_name] = cat_obj

            for brand_name in data["brands"]:
                brand_slug = brand_name.lower().replace(" ", "-").replace("'", "")
                if brand_name not in brand_map:
                    stmt = select(Brand).where(Brand.slug == brand_slug)
                    res = await session.execute(stmt)
                    b_obj = res.scalars().first()
                    if not b_obj:
                        b_obj = Brand(
                            id=uuid.uuid4(),
                            name=brand_name,
                            slug=brand_slug,
                        )
                        session.add(b_obj)
                        await session.flush()
                    brand_map[brand_name] = b_obj

        await session.commit()

        # Check existing count
        count_stmt = select(func.count()).select_from(Product)
        current_count = (await session.execute(count_stmt)).scalar() or 0
        print(f"Current catalog size in DB: {current_count:,} products.")

        if current_count >= target_count:
            print(f"Catalog already has {current_count:,} products (>= target {target_count:,}). No action needed.")
            return

        needed = target_count - current_count
        print(f"Generating {needed:,} products in batches of {batch_size:,}...")

        cat_keys = list(CATEGORIES_DATA.keys())
        total_created = 0

        # Batch generator loop
        while total_created < needed:
            chunk_products = []
            chunk_images = []
            chunk_specs = []
            chunk_listings = []

            chunk_target = min(batch_size, needed - total_created)

            for idx in range(chunk_target):
                global_idx = current_count + total_created + idx + 1
                cat_name = cat_keys[global_idx % len(cat_keys)]
                c_data = CATEGORIES_DATA[cat_name]

                brand = c_data["brands"][global_idx % len(c_data["brands"])]
                brand_obj = brand_map.get(brand)
                cat_obj = category_map[cat_name]

                template = c_data["templates"][global_idx % len(c_data["templates"])]
                prod_name = template.format(
                    brand=brand,
                    num=global_idx,
                    ram=random.choice([8, 12, 16, 32]),
                    storage=random.choice([128, 256, 512, 1024]),
                    size=random.choice([14, 15, 43, 55, 65, 75, 8, 10]),
                )

                ean_code = f"890{(global_idx % 90)+10:02d}{(global_idx % 99999):05d}{(global_idx % 999):03d}"
                min_p, max_p = c_data["price_range"]
                base_price = Decimal(str(random.randint(min_p, max_p)))
                img_pool = c_data["images"]
                primary_img = img_pool[global_idx % len(img_pool)]

                rating = round(random.uniform(3.5, 5.0), 1)
                reviews = random.randint(15, 12500)
                pop_score = round(random.uniform(50.0, 99.9), 1)
                keywords = f"{cat_name.lower()}, {brand.lower()}, " + ", ".join(c_data.get("keywords", []))

                prod_id = uuid.uuid4()
                p = Product(
                    id=prod_id,
                    name=prod_name,
                    description=f"Authentic {cat_name} product by {brand}. Features top performance, official brand warranty, and price comparison across major marketplaces.",
                    category_id=cat_obj.id,
                    brand_id=brand_obj.id if brand_obj else None,
                    category=cat_name,
                    brand=brand,
                    image_url=primary_img,
                    ean=ean_code,
                    base_price=base_price,
                    rating=rating,
                    review_count=reviews,
                    popularity_score=pop_score,
                    search_keywords=keywords,
                    stock_status="in_stock",
                    discount_percentage=round(random.uniform(5.0, 40.0), 1),
                )
                chunk_products.append(p)

                # 5 gallery images per product
                for img_i in range(5):
                    sub_img = img_pool[(global_idx + img_i) % len(img_pool)]
                    chunk_images.append(
                        ProductImage(
                            id=uuid.uuid4(),
                            product_id=prod_id,
                            url=sub_img,
                            alt_text=f"{prod_name} view {img_i+1}",
                            is_primary=(img_i == 0),
                        )
                    )

                # Specifications
                chunk_specs.append(ProductSpecification(id=uuid.uuid4(), product_id=prod_id, key="Brand", value=brand))
                chunk_specs.append(ProductSpecification(id=uuid.uuid4(), product_id=prod_id, key="Category", value=cat_name))
                for spec_k, spec_vals in c_data.get("specs", []):
                    val = random.choice(spec_vals)
                    chunk_specs.append(ProductSpecification(id=uuid.uuid4(), product_id=prod_id, key=spec_k, value=val))

                # Marketplace Listings
                for mp_idx, mp in enumerate(marketplaces):
                    var_factor = Decimal(str(round(1.0 + (mp_idx * 0.02) - 0.01, 2)))
                    m_price = round(base_price * var_factor, 2)
                    orig_price = round(m_price * Decimal("1.25"), 2)

                    chunk_listings.append(
                        ProductListing(
                            id=uuid.uuid4(),
                            product_id=prod_id,
                            marketplace_id=mp.id,
                            marketplace_product_id=f"MP-{mp.slug[:3]}-{global_idx}",
                            price=m_price,
                            original_price=orig_price,
                            discount_percent=Decimal("20.00"),
                            currency="INR",
                            listing_url=f"{mp.base_url}/dp/B0{global_idx:07d}",
                            seller_name=f"{brand} Authorized Store",
                            is_available=True,
                            is_prime=True,
                            stock_status="IN_STOCK",
                            delivery_estimate="Express Delivery Available",
                            rating=Decimal(str(rating)),
                            review_count=reviews,
                        )
                    )

            # Insert batch
            async with AsyncSessionLocal() as batch_session:
                batch_session.add_all(chunk_products)
                batch_session.add_all(chunk_images)
                batch_session.add_all(chunk_specs)
                batch_session.add_all(chunk_listings)
                await batch_session.commit()

            total_created += chunk_target
            print(f"  -> Successfully seeded batch of {chunk_target:,} products. Total seeded: {total_created:,} / {needed:,}")

        final_count = (await session.execute(select(func.count()).select_from(Product))).scalar() or 0
        print("==================================================================")
        print(f"Seeding process finished! Final catalog size: {final_count:,} products.")
        print("==================================================================")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="COMPAREX Catalog Seeding Pipeline")
    parser.add_argument("--count", type=int, default=100000, help="Target number of products to seed")
    parser.add_argument("--batch", type=int, default=5000, help="Batch size for DB commits")
    args = parser.parse_args()

    asyncio.run(seed_scalable_catalog(target_count=args.count, batch_size=args.batch))
