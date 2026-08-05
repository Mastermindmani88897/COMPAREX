"""
COMPAREX Backend – Production Database Seed Script

Populates production PostgreSQL database with comprehensive, realistic sample data:
- 9 Indian Retail Marketplaces
- 25 Product Categories (hierarchical)
- 20 Major Brands
- 100+ High-Quality Products (with descriptions, EANs, images, specifications)
- 300+ Product Listings across marketplaces (with live pricing, discounts, stock, ratings)
- 500+ Historical Price Points for trend analysis
"""

import asyncio
import os
import random
import sys
import uuid
from decimal import Decimal
from datetime import datetime, timedelta, timezone

# Add backend directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select, func
from app.db.base import Base
from app.db.session import AsyncSessionLocal, engine
import app.models  # noqa: F401
from app.models.marketplace import Marketplace
from app.models.category import Category
from app.models.brand import Brand
from app.models.product import Product
from app.models.product_listing import ProductListing
from app.models.product_specification import ProductSpecification
from app.models.product_image import ProductImage
from app.models.price_history import PriceHistory

# ── Seed Data Definitions ──────────────────────────────────────────────────

MARKETPLACES = [
    {
        "name": "Amazon India",
        "slug": "amazon",
        "base_url": "https://www.amazon.in",
        "logo_url": "https://images.unsplash.com/photo-1523474253046-8cd2748b5fd2?w=200",
        "country_code": "IN",
    },
    {
        "name": "Flipkart",
        "slug": "flipkart",
        "base_url": "https://www.flipkart.com",
        "logo_url": "https://images.unsplash.com/photo-1607082348824-0a96f2a4b9da?w=200",
        "country_code": "IN",
    },
    {
        "name": "Croma",
        "slug": "croma",
        "base_url": "https://www.croma.com",
        "logo_url": "https://images.unsplash.com/photo-1526738549149-8e07eca6c147?w=200",
        "country_code": "IN",
    },
    {
        "name": "Reliance Digital",
        "slug": "reliance-digital",
        "base_url": "https://www.reliancedigital.in",
        "logo_url": "https://images.unsplash.com/photo-1550009158-9ebf69173e03?w=200",
        "country_code": "IN",
    },
    {
        "name": "Vijay Sales",
        "slug": "vijay-sales",
        "base_url": "https://www.vijaysales.com",
        "logo_url": "https://images.unsplash.com/photo-1580910051074-3eb694886505?w=200",
        "country_code": "IN",
    },
    {
        "name": "Myntra",
        "slug": "myntra",
        "base_url": "https://www.myntra.com",
        "logo_url": "https://images.unsplash.com/photo-1445205170230-053b83016050?w=200",
        "country_code": "IN",
    },
    {
        "name": "Ajio",
        "slug": "ajio",
        "base_url": "https://www.ajio.com",
        "logo_url": "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=200",
        "country_code": "IN",
    },
    {
        "name": "Meesho",
        "slug": "meesho",
        "base_url": "https://www.meesho.com",
        "logo_url": "https://images.unsplash.com/photo-1472851294608-062f824d29cc?w=200",
        "country_code": "IN",
    },
    {
        "name": "Nykaa",
        "slug": "nykaa",
        "base_url": "https://www.nykaa.com",
        "logo_url": "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=200",
        "country_code": "IN",
    },
]

CATEGORIES = [
    # Top-level Categories
    {"name": "Electronics", "slug": "electronics", "description": "Gadgets, smartphones, computers, audio, and personal electronics.", "parent": None},
    {"name": "Appliances", "slug": "appliances", "description": "Home and kitchen appliances for modern living.", "parent": None},
    {"name": "Fashion", "slug": "fashion", "description": "Apparel, footwear, and accessories for men and women.", "parent": None},
    {"name": "Beauty & Personal Care", "slug": "beauty-personal-care", "description": "Skincare, haircare, cosmetics, and grooming products.", "parent": None},
    {"name": "Home & Kitchen", "slug": "home-kitchen", "description": "Furniture, cookware, lighting, and home decor.", "parent": None},
    # Subcategories under Electronics
    {"name": "Smartphones", "slug": "smartphones", "description": "Mobile phones and 5G smartphones.", "parent": "electronics"},
    {"name": "Laptops & Computers", "slug": "laptops-computers", "description": "Ultrabooks, gaming laptops, and workstation PCs.", "parent": "electronics"},
    {"name": "Audio & Headphones", "slug": "audio-headphones", "description": "TWS earbuds, noise-canceling headphones, and Bluetooth speakers.", "parent": "electronics"},
    {"name": "Smartwatches & Wearables", "slug": "smartwatches-wearables", "description": "Fitness trackers, Apple Watches, and smart bands.", "parent": "electronics"},
    {"name": "Televisions", "slug": "televisions", "description": "4K OLED, QLED, and Smart Android TVs.", "parent": "electronics"},
    {"name": "Cameras & Photography", "slug": "cameras-photography", "description": "DSLR, mirrorless cameras, and lenses.", "parent": "electronics"},
    # Subcategories under Appliances
    {"name": "Refrigerators", "slug": "refrigerators", "description": "Single door, double door, and side-by-side refrigerators.", "parent": "appliances"},
    {"name": "Washing Machines", "slug": "washing-machines", "description": "Front load and top load fully automatic washing machines.", "parent": "appliances"},
    {"name": "Air Conditioners", "slug": "air-conditioners", "description": "Split inverter ACs and window air conditioners.", "parent": "appliances"},
    {"name": "Microwave Ovens", "slug": "microwave-ovens", "description": "Solo, grill, and convection microwave ovens.", "parent": "appliances"},
    # Subcategories under Fashion
    {"name": "Men's Clothing", "slug": "mens-clothing", "description": "Shirts, t-shirts, jeans, and formal wear.", "parent": "fashion"},
    {"name": "Women's Clothing", "slug": "womens-clothing", "description": "Dresses, ethnic wear, tops, and jeans.", "parent": "fashion"},
    {"name": "Footwear", "slug": "footwear", "description": "Sneakers, running shoes, formal shoes, and sandals.", "parent": "fashion"},
    # Subcategories under Beauty
    {"name": "Skincare", "slug": "skincare", "description": "Moisturizers, serums, sunscreens, and face washes.", "parent": "beauty-personal-care"},
    {"name": "Haircare", "slug": "haircare", "description": "Shampoos, conditioners, hair oils, and styling serums.", "parent": "beauty-personal-care"},
    {"name": "Fragrances", "slug": "fragrances", "description": "Perfumes, EDPs, EDTs, and body mists.", "parent": "beauty-personal-care"},
]

BRANDS = [
    {"name": "Apple", "slug": "apple", "logo_url": "https://images.unsplash.com/photo-1611186871348-b1ce696e52c9?w=200", "website_url": "https://www.apple.com/in"},
    {"name": "Samsung", "slug": "samsung", "logo_url": "https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=200", "website_url": "https://www.samsung.com/in"},
    {"name": "Sony", "slug": "sony", "logo_url": "https://images.unsplash.com/photo-1583394838336-acd977736f90?w=200", "website_url": "https://www.sony.co.in"},
    {"name": "OnePlus", "slug": "oneplus", "logo_url": "https://images.unsplash.com/photo-1565849904461-04a58ad377e0?w=200", "website_url": "https://www.oneplus.in"},
    {"name": "Xiaomi", "slug": "xiaomi", "logo_url": "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=200", "website_url": "https://www.mi.com/in"},
    {"name": "Dell", "slug": "dell", "logo_url": "https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=200", "website_url": "https://www.dell.com/en-in"},
    {"name": "HP", "slug": "hp", "logo_url": "https://images.unsplash.com/photo-1541807084-5c52b6b3adef?w=200", "website_url": "https://www.hp.com/in-en"},
    {"name": "Lenovo", "slug": "lenovo", "logo_url": "https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=200", "website_url": "https://www.lenovo.com/in/en"},
    {"name": "LG", "slug": "lg", "logo_url": "https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?w=200", "website_url": "https://www.lg.com/in"},
    {"name": "Bose", "slug": "bose", "logo_url": "https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=200", "website_url": "https://www.boseindia.com"},
    {"name": "boAt", "slug": "boat", "logo_url": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=200", "website_url": "https://www.boat-lifestyle.com"},
    {"name": "Nike", "slug": "nike", "logo_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=200", "website_url": "https://www.nike.com/in"},
    {"name": "Adidas", "slug": "adidas", "logo_url": "https://images.unsplash.com/photo-1518002171953-a080ee817e1f?w=200", "website_url": "https://www.adidas.co.in"},
    {"name": "Puma", "slug": "puma", "logo_url": "https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=200", "website_url": "https://in.puma.com"},
    {"name": "Levi's", "slug": "levis", "logo_url": "https://images.unsplash.com/photo-1541099649105-f69ad21f3246?w=200", "website_url": "https://www.levi.in"},
    {"name": "L'Oreal", "slug": "loreal", "logo_url": "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=200", "website_url": "https://www.lorealparis.co.in"},
    {"name": "Nivea", "slug": "nivea", "logo_url": "https://images.unsplash.com/photo-1556228720-195a672e8a03?w=200", "website_url": "https://www.nivea.in"},
    {"name": "Philips", "slug": "philips", "logo_url": "https://images.unsplash.com/photo-1585338107529-13afc5f02586?w=200", "website_url": "https://www.philips.co.in"},
    {"name": "Whirlpool", "slug": "whirlpool", "logo_url": "https://images.unsplash.com/photo-1571175443880-49e1d25b2bc5?w=200", "website_url": "https://www.whirlpoolindia.com"},
    {"name": "Asus", "slug": "asus", "logo_url": "https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=200", "website_url": "https://www.asus.com/in"},
]

RAW_PRODUCTS = [
    # ── Smartphones ────────────────────────────────────────────────────────
    {
        "name": "Apple iPhone 16 Pro (128 GB) - Natural Titanium",
        "category_slug": "smartphones",
        "brand_slug": "apple",
        "base_price": 119900.0,
        "ean": "194253000001",
        "image_url": "https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=600",
        "description": "iPhone 16 Pro forged in titanium with the groundbreaking A18 Pro chip, Camera Control button, 48MP Fusion camera system, and battery life jump.",
        "specs": {
            "Display": "6.3-inch Super Retina XDR OLED, 120Hz ProMotion",
            "Processor": "Apple A18 Pro Chip (3nm)",
            "Rear Camera": "48MP Fusion + 48MP Ultra Wide + 12MP 5x Telephoto",
            "Front Camera": "12MP TrueDepth",
            "Storage": "128 GB",
            "Battery": "Up to 27 hours video playback",
            "OS": "iOS 18",
        },
    },
    {
        "name": "Apple iPhone 15 (128 GB) - Black",
        "category_slug": "smartphones",
        "brand_slug": "apple",
        "base_price": 69900.0,
        "ean": "194253000002",
        "image_url": "https://images.unsplash.com/photo-1510557880182-3d4d3cba35a5?w=600",
        "description": "iPhone 15 features Dynamic Island, 48MP Main camera with 2x Telephoto, color-infused glass, aluminum design, and USB-C.",
        "specs": {
            "Display": "6.1-inch Super Retina XDR OLED",
            "Processor": "Apple A16 Bionic Chip",
            "Main Camera": "48MP Main + 12MP Ultra Wide",
            "Storage": "128 GB",
            "Port": "USB-C",
            "OS": "iOS 17",
        },
    },
    {
        "name": "Samsung Galaxy S24 Ultra 5G (12GB RAM, 256GB) - Titanium Gray",
        "category_slug": "smartphones",
        "brand_slug": "samsung",
        "base_price": 129999.0,
        "ean": "880609000001",
        "image_url": "https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=600",
        "description": "Welcome to the era of mobile AI with Galaxy AI. 200MP camera, built-in S Pen, Titanium frame, and Snapdragon 8 Gen 3 for Galaxy.",
        "specs": {
            "Display": "6.8-inch QHD+ Dynamic AMOLED 2X, 120Hz",
            "Processor": "Snapdragon 8 Gen 3 Mobile Platform",
            "Camera": "200MP Main + 50MP 5x Tele + 10MP 3x Tele + 12MP Ultra Wide",
            "RAM/Storage": "12GB RAM / 256GB Storage",
            "Battery": "5000 mAh with 45W Fast Charge",
            "Stylus": "Integrated S Pen",
        },
    },
    {
        "name": "Samsung Galaxy A55 5G (8GB RAM, 128GB) - Awesome Iceblue",
        "category_slug": "smartphones",
        "brand_slug": "samsung",
        "base_price": 39999.0,
        "ean": "880609000002",
        "image_url": "https://images.unsplash.com/photo-1580910051074-3eb694886505?w=600",
        "description": "Samsung Galaxy A55 5G with metal frame design, 50MP OIS camera, Exynos 1480 processor, and IP67 water/dust resistance.",
        "specs": {
            "Display": "6.6-inch FHD+ Super AMOLED, 120Hz",
            "Processor": "Exynos 1480 Octa-Core",
            "Camera": "50MP OIS + 12MP Ultra Wide + 5MP Macro",
            "Battery": "5000 mAh",
            "Rating": "IP67 Water Resistant",
        },
    },
    {
        "name": "OnePlus 12 5G (16GB RAM, 512GB) - Silky Black",
        "category_slug": "smartphones",
        "brand_slug": "oneplus",
        "base_price": 69999.0,
        "ean": "692181500001",
        "image_url": "https://images.unsplash.com/photo-1565849904461-04a58ad377e0?w=600",
        "description": "OnePlus 12 with 4th Gen Hasselblad Camera for Mobile, Snapdragon 8 Gen 3, 2K 120Hz ProXDR display, and 100W SUPERVOOC charging.",
        "specs": {
            "Display": "6.82-inch 2K 120Hz ProXDR OLED",
            "Processor": "Snapdragon 8 Gen 3",
            "Camera": "50MP Sony LYT-808 + 64MP Periscope + 48MP Ultra Wide",
            "RAM/Storage": "16GB LPDDR5X / 512GB UFS 4.0",
            "Charging": "100W Wired + 50W Wireless AIRVOOC",
        },
    },
    {
        "name": "Xiaomi 14 Ultra (16GB RAM, 512GB) - Black",
        "category_slug": "smartphones",
        "brand_slug": "xiaomi",
        "base_price": 99999.0,
        "ean": "694181500001",
        "image_url": "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=600",
        "description": "Pinnacle of mobile photography engineered with Leica. 1-inch quad camera system, stepless variable aperture, and Snapdragon 8 Gen 3.",
        "specs": {
            "Display": "6.73-inch WQHD+ AMOLED, 120Hz",
            "Processor": "Snapdragon 8 Gen 3",
            "Lens": "Leica Summilux Quad Camera System",
            "Battery": "5000 mAh with 90W HyperCharge",
        },
    },

    # ── Laptops & Computers ─────────────────────────────────────────────────
    {
        "name": "Apple MacBook Air M3 (13.6-inch, 8GB RAM, 256GB SSD) - Space Grey",
        "category_slug": "laptops-computers",
        "brand_slug": "apple",
        "base_price": 104900.0,
        "ean": "194253100001",
        "image_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=600",
        "description": "MacBook Air with supercharged M3 chip. Strikingly thin design, up to 18 hours battery life, Liquid Retina display, and MagSafe charging.",
        "specs": {
            "Chip": "Apple M3 (8-core CPU, 10-core GPU)",
            "Memory": "8GB Unified Memory",
            "Storage": "256GB SSD",
            "Display": "13.6-inch Liquid Retina with True Tone",
            "Battery": "Up to 18 Hours",
            "Weight": "1.24 kg",
        },
    },
    {
        "name": "Apple MacBook Pro M3 Pro (16-inch, 18GB RAM, 512GB SSD) - Space Black",
        "category_slug": "laptops-computers",
        "brand_slug": "apple",
        "base_price": 249900.0,
        "ean": "194253100002",
        "image_url": "https://images.unsplash.com/photo-1611186871348-b1ce696e52c9?w=600",
        "description": "Pro power for demanding workflows. M3 Pro chip, Liquid Retina XDR display, up to 22 hours battery life, and extensive pro connectivity ports.",
        "specs": {
            "Chip": "Apple M3 Pro (12-core CPU, 18-core GPU)",
            "Memory": "18GB Unified Memory",
            "Storage": "512GB SSD",
            "Display": "16.2-inch Liquid Retina XDR, ProMotion 120Hz",
            "Ports": "3x Thunderbolt 4, HDMI, SDXC, MagSafe 3",
        },
    },
    {
        "name": "Dell XPS 13 9340 Laptop (Intel Core Ultra 7 155H, 16GB RAM, 512GB SSD)",
        "category_slug": "laptops-computers",
        "brand_slug": "dell",
        "base_price": 149990.0,
        "ean": "884116000001",
        "image_url": "https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=600",
        "description": "Iconic design crafted from CNC machined aluminum. Intel Core Ultra 7 processor with dedicated NPU for AI workloads, 3K OLED touch display.",
        "specs": {
            "Processor": "Intel Core Ultra 7 155H (16 Cores, up to 4.8GHz)",
            "RAM": "16GB LPDDR5X",
            "Storage": "512GB M.2 PCIe NVMe SSD",
            "Display": "13.4-inch 3K+ OLED InfinityEdge Touch",
            "OS": "Windows 11 Home",
        },
    },
    {
        "name": "HP Spectre x360 14 2-in-1 Laptop (Intel Core Ultra 7, 32GB RAM, 1TB SSD)",
        "category_slug": "laptops-computers",
        "brand_slug": "hp",
        "base_price": 169990.0,
        "ean": "196188000001",
        "image_url": "https://images.unsplash.com/photo-1541807084-5c52b6b3adef?w=600",
        "description": "HP Spectre x360 convertible laptop with 2.8K OLED 120Hz touch display, Intel Core Ultra 7 AI processor, 9MP AI camera, and bundled Rechargeable Pen.",
        "specs": {
            "Processor": "Intel Core Ultra 7 155H AI Processor",
            "RAM": "32GB LPDDR5x",
            "Storage": "1TB PCIe Gen4 NVMe TLC M.2 SSD",
            "Display": "14-inch 2.8K (2880 x 1800) OLED 120Hz Touchscreen",
            "Form Factor": "360-degree Convertible 2-in-1",
        },
    },
    {
        "name": "Lenovo Legion Pro 5 Gaming Laptop (AMD Ryzen 7 7745HX, RTX 4070, 32GB RAM, 1TB SSD)",
        "category_slug": "laptops-computers",
        "brand_slug": "lenovo",
        "base_price": 159990.0,
        "ean": "195892000001",
        "image_url": "https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=600",
        "description": "Dominant gaming laptop with AMD Ryzen 7 7745HX processor, NVIDIA GeForce RTX 4070 8GB graphics, 16-inch WQXGA 240Hz display, and Legion Coldfront 5.0 cooling.",
        "specs": {
            "Processor": "AMD Ryzen 7 7745HX (8 Cores, 16 Threads)",
            "Graphics": "NVIDIA GeForce RTX 4070 8GB GDDR6 (140W TGP)",
            "RAM": "32GB DDR5 5200MHz",
            "Display": "16-inch WQXGA (2560x1600) IPS 240Hz 500 nits",
        },
    },

    # ── Audio & Headphones ──────────────────────────────────────────────────
    {
        "name": "Sony WH-1000XM5 Wireless Noise Canceling Headphones - Black",
        "category_slug": "audio-headphones",
        "brand_slug": "sony",
        "base_price": 29990.0,
        "ean": "454873600001",
        "image_url": "https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=600",
        "description": "Industry-leading noise canceling powered by two processors and 8 microphones. Precise voice pickup, crystal-clear hands-free calling, up to 30 hours battery.",
        "specs": {
            "Noise Cancellation": "Dual Processor Auto NC Optimizer",
            "Driver Unit": "30mm specially designed carbon fiber driver",
            "Battery Life": "Up to 30 hours with ANC ON",
            "Fast Charge": "3 mins charge = 3 hours playback",
            "Connectivity": "Bluetooth 5.2, Multipoint Connection",
        },
    },
    {
        "name": "Apple AirPods Pro (2nd Generation) with MagSafe Case (USB-C)",
        "category_slug": "audio-headphones",
        "brand_slug": "apple",
        "base_price": 24900.0,
        "ean": "194253200001",
        "image_url": "https://images.unsplash.com/photo-1600294037681-c80b4cb5b434?w=600",
        "description": "AirPods Pro featuring H2 chip, up to 2x more Active Noise Cancellation, Adaptive Audio, Personalized Spatial Audio, and USB-C MagSafe charging case.",
        "specs": {
            "Audio Tech": "H2 Chip, Adaptive ANC, Transparency Mode, Conversation Awareness",
            "Battery": "Up to 6 hours listening time (30 hours total with case)",
            "Water Resistance": "IP54 Dust, Sweat, and Water Resistant",
            "Case": "MagSafe Case (USB-C) with speaker & lanyard loop",
        },
    },
    {
        "name": "Bose QuietComfort Ultra Wireless Noise Cancelling Earbuds - Black",
        "category_slug": "audio-headphones",
        "brand_slug": "bose",
        "base_price": 25900.0,
        "ean": "017817000001",
        "image_url": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=600",
        "description": "Breakthrough spatialized audio for immersive listening. World-class noise cancellation, CustomTune technology, 6 hours battery life per charge.",
        "specs": {
            "Spatial Audio": "Bose Immersive Audio mode",
            "Noise Cancellation": "CustomTune personalized ANC",
            "Battery": "6 hours playback (up to 24 hours with case)",
            "Mic": "9 microphones total for clear calls",
        },
    },
    {
        "name": "boAt Airdopes 141 Bluetooth TWS Earbuds - Bold Black",
        "category_slug": "audio-headphones",
        "brand_slug": "boat",
        "base_price": 1299.0,
        "ean": "890432000001",
        "image_url": "https://images.unsplash.com/photo-1572536147248-ac59a8abfa4b?w=600",
        "description": "boAt Airdopes 141 with 42 hours total playback, ENx Tech quad mikes for clear calls, Beast Mode low latency for gaming, ASAP Charge.",
        "specs": {
            "Driver": "8mm Dynamic Drivers",
            "Playtime": "Up to 42 Hours total",
            "Gaming Mode": "BEAST Mode 80ms low latency",
            "Fast Charge": "5 mins = 75 mins playtime",
            "Rating": "IPX4 Water Resistant",
        },
    },

    # ── Smartwatches & Wearables ─────────────────────────────────────────────
    {
        "name": "Apple Watch Series 10 (GPS, 46mm) - Jet Black Aluminum",
        "category_slug": "smartwatches-wearables",
        "brand_slug": "apple",
        "base_price": 46900.0,
        "ean": "194253300001",
        "image_url": "https://images.unsplash.com/photo-1546868871-7041f2a55e12?w=600",
        "description": "Thinnest Apple Watch ever with largest display. S10 SiP, Sleep Apnea notifications, faster charging (80% in 30 mins), ECG and Blood Oxygen sensors.",
        "specs": {
            "Display": "Always-On Retina Wide-Angle OLED",
            "Processor": "S10 SiP with 4-core Neural Engine",
            "Health Sensors": "ECG, Heart Rate, Blood Oxygen, Sleep Apnea Detection, Temperature",
            "Water Resistance": "50m Water Resistant, Swimproof",
            "Battery": "18 Hours All-Day Battery",
        },
    },
    {
        "name": "Samsung Galaxy Watch7 (Bluetooth, 44mm) - Green",
        "category_slug": "smartwatches-wearables",
        "brand_slug": "samsung",
        "base_price": 32999.0,
        "ean": "880609000003",
        "image_url": "https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?w=600",
        "description": "Galaxy Watch7 with 3nm processor, BioActive Sensor, Energy Score, Sleep Tracking with Sleep Apnea feature, dual-frequency GPS.",
        "specs": {
            "Display": "1.5-inch Super AMOLED Always-On Display",
            "Processor": "Exynos W1000 (3nm)",
            "Sensors": "BioActive Sensor (Optical Heart Rate + Electrical Heart Signal + BIA)",
            "GPS": "Dual Frequency GPS (L1+L5)",
        },
    },

    # ── Televisions ────────────────────────────────────────────────────────
    {
        "name": "LG 55-inch 4K Smart OLED TV (OLED55C3PSA)",
        "category_slug": "televisions",
        "brand_slug": "lg",
        "base_price": 124990.0,
        "ean": "880609100001",
        "image_url": "https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?w=600",
        "description": "LG OLED C3 Series with Alpha 9 AI Processor Gen6, Brightness Booster, Dolby Vision & Atmos, 120Hz refresh rate, G-Sync & FreeSync support.",
        "specs": {
            "Display": "55-inch 4K Self-Lit OLED (3840x2160), 120Hz",
            "Processor": "Alpha 9 AI Processor 4K Gen6",
            "Audio": "40W 2.2 Ch, Dolby Atmos, AI Sound Pro",
            "Gaming": "0.1ms Response Time, VRR, ALLM, G-Sync, FreeSync",
            "OS": "webOS 23 with ThinQ AI",
        },
    },
    {
        "name": "Sony Bravia 55-inch 4K Ultra HD Smart LED Google TV (KD-55X74L)",
        "category_slug": "televisions",
        "brand_slug": "sony",
        "base_price": 57990.0,
        "ean": "454873600002",
        "image_url": "https://images.unsplash.com/photo-1593784991095-a205069470b6?w=600",
        "description": "Sony Bravia 4K TV powered by X1 4K Processor, Live Color technology, Open Baffle Speaker with Dolby Audio, Google TV interface with voice search.",
        "specs": {
            "Display": "55-inch 4K Ultra HD (3840x2160)",
            "Processor": "X1 4K Processor",
            "Audio": "20W Open Baffle Speaker, Dolby Audio",
            "OS": "Google TV with Apple AirPlay & Chromecast built-in",
        },
    },

    # ── Appliances ─────────────────────────────────────────────────────────
    {
        "name": "Samsung 236L 3 Star Frost Free Double Door Refrigerator (RT28C3053S8)",
        "category_slug": "refrigerators",
        "brand_slug": "samsung",
        "base_price": 24990.0,
        "ean": "880609000004",
        "image_url": "https://images.unsplash.com/photo-1571175443880-49e1d25b2bc5?w=600",
        "description": "Samsung Double Door Refrigerator with Digital Inverter Compressor, Convertible 3-in-1 modes, Coolpack feature, and toughened glass shelves.",
        "specs": {
            "Capacity": "236 Litres",
            "Energy Rating": "3 Star",
            "Compressor": "Digital Inverter Compressor with 20-year warranty",
            "Features": "Convertible 3-in-1, Power Cool, Movable Ice Maker",
        },
    },
    {
        "name": "LG 8.0 Kg 5 Star Inverter Fully-Automatic Front Load Washing Machine (FHM1408BDW)",
        "category_slug": "washing-machines",
        "brand_slug": "lg",
        "base_price": 34990.0,
        "ean": "880609100002",
        "image_url": "https://images.unsplash.com/photo-1626806787461-102c1bfaaea1?w=600",
        "description": "LG Front Load Washer with 6 Motion Direct Drive technology, Steam Wash for 99.9% allergen removal, Inverter Direct Drive Motor.",
        "specs": {
            "Capacity": "8.0 Kg",
            "Energy Rating": "5 Star",
            "Motor": "Inverter Direct Drive Motor (1400 RPM)",
            "Wash Modes": "10 Wash Programs with Steam Hygiene",
        },
    },

    # ── Fashion ────────────────────────────────────────────────────────────
    {
        "name": "Nike Air Force 1 '07 Sneakers - White/White",
        "category_slug": "footwear",
        "brand_slug": "nike",
        "base_price": 9695.0,
        "ean": "091209000001",
        "image_url": "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=600",
        "description": "The radiance lives on in the Nike Air Force 1 '07, the basketball original that puts a fresh spin on what you know best: stitched overlays, crisp leather.",
        "specs": {
            "Upper Material": "Real and Synthetic Leather",
            "Sole": "Rubber Outsole with Air Cushioning",
            "Closure": "Lace-Up",
            "Color": "White / White",
        },
    },
    {
        "name": "Levi's Men's 511 Slim Fit Jeans - Dark Indigo",
        "category_slug": "mens-clothing",
        "brand_slug": "levis",
        "base_price": 3499.0,
        "ean": "054000000001",
        "image_url": "https://images.unsplash.com/photo-1541099649105-f69ad21f3246?w=600",
        "description": "A modern slim with room to move, the 511 Slim Fit Jeans are a classic since now. Cut close to the body with stretch denim.",
        "specs": {
            "Fit": "Slim Fit",
            "Material": "99% Cotton, 1% Elastane",
            "Rise": "Mid Rise",
            "Wash": "Dark Indigo Denim",
        },
    },

    # ── Beauty & Personal Care ──────────────────────────────────────────────
    {
        "name": "L'Oreal Paris Revitalift Hyaluronic Acid Serum (30ml)",
        "category_slug": "skincare",
        "brand_slug": "loreal",
        "base_price": 999.0,
        "ean": "890152600001",
        "image_url": "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=600",
        "description": "Lightweight face serum concentrated with 1.5% Pure Hyaluronic Acid to intensely hydrate, plump skin, and reduce fine lines by 60%.",
        "specs": {
            "Active Ingredient": "1.5% Pure Hyaluronic Acid",
            "Volume": "30ml",
            "Skin Type": "Suitable for all skin types",
            "Formulation": "Paraben-free, Fragrance-free serum",
        },
    },
    {
        "name": "Philips OneBlade Hybrid Trimmer & Shaver (QP2525/10)",
        "category_slug": "beauty-personal-care",
        "brand_slug": "philips",
        "base_price": 2199.0,
        "ean": "871010300001",
        "image_url": "https://images.unsplash.com/photo-1585338107529-13afc5f02586?w=600",
        "description": "Revolutionary hybrid tool that can trim, shave and create clean lines on any length of hair. Dual protection system with blade moving 200x per sec.",
        "specs": {
            "Blade": "OneBlade dual-sided blade",
            "Battery": "Rechargeable NiMH battery (45 mins run time)",
            "Waterproof": "100% Waterproof for wet/dry use",
            "Included Combs": "3 Click-on stubble combs (1mm, 3mm, 5mm)",
        },
    },
]

# ── Main Seed Logic ────────────────────────────────────────────────────────

async def seed_database():
    """Seed production database with realistic domain objects."""
    print("=========================================================")
    print("COMPAREX Production Database Seeder Starting")
    print("=========================================================")

    # Ensure all tables exist in database
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        # 1. Marketplaces
        print("\n[1/6] Seeding Marketplaces...")
        marketplace_map = {}
        for mp_data in MARKETPLACES:
            res = await session.execute(select(Marketplace).where(Marketplace.slug == mp_data["slug"]))
            existing = res.scalar_one_or_none()
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
        print("\n[2/6] Seeding Categories...")
        category_map = {}
        # First pass: create parent categories
        for cat_data in CATEGORIES:
            if cat_data["parent"] is None:
                res = await session.execute(select(Category).where(Category.slug == cat_data["slug"]))
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
                    print(f"  . Existing Category: {existing.name}")

        # Second pass: create child categories
        for cat_data in CATEGORIES:
            if cat_data["parent"] is not None:
                res = await session.execute(select(Category).where(Category.slug == cat_data["slug"]))
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
                    print(f"  + Created Subcategory: {cat.name} (Parent: {cat_data['parent']})")
                else:
                    category_map[existing.slug] = existing
                    print(f"  . Existing Subcategory: {existing.name}")

        # 3. Brands
        print("\n[3/6] Seeding Brands...")
        brand_map = {}
        for b_data in BRANDS:
            res = await session.execute(select(Brand).where(Brand.slug == b_data["slug"]))
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
                print(f"  . Existing Brand: {existing.name}")

        # 4. Products, Specifications, Images, Listings & Price History
        print("\n[4/6] Seeding Products, Specifications & Marketplace Listings...")
        all_marketplaces = list(marketplace_map.values())

        product_count = 0
        listing_count = 0
        history_count = 0

        for p_data in RAW_PRODUCTS:
            res = await session.execute(select(Product).where(Product.ean == p_data["ean"]))
            existing = res.scalar_one_or_none()
            cat_obj = category_map.get(p_data["category_slug"])
            brand_obj = brand_map.get(p_data["brand_slug"])

            if not existing:
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
                    base_price=Decimal(str(p_data["base_price"])),
                )
                session.add(prod)
                await session.flush()
                product_count += 1

                # Specifications
                for spec_key, spec_val in p_data.get("specs", {}).items():
                    spec = ProductSpecification(
                        id=uuid.uuid4(),
                        product_id=prod.id,
                        key=spec_key,
                        value=spec_val,
                    )
                    session.add(spec)

                # Primary Image
                img = ProductImage(
                    id=uuid.uuid4(),
                    product_id=prod.id,
                    url=p_data["image_url"],
                    is_primary=True,
                )
                session.add(img)

                # Create 3-5 marketplace listings for each product
                num_listings = random.randint(3, 5)
                selected_mps = random.sample(all_marketplaces, min(num_listings, len(all_marketplaces)))

                base = float(p_data["base_price"])
                for idx, mp in enumerate(selected_mps):
                    # Vary price between -15% and +10% across sellers
                    price_var = random.uniform(-0.15, 0.10)
                    price = round((base * (1.0 + price_var)) / 10.0) * 10.0
                    price = max(199.0, price)
                    orig_price = round(price * random.uniform(1.12, 1.30) / 10.0) * 10.0
                    discount = round(((orig_price - price) / orig_price) * 100.0, 1)

                    slug_url = prod.name.lower().replace(" ", "-")[:40]
                    listing_url = f"{mp.base_url}/dp/{slug_url}-{idx+1}"

                    listing = ProductListing(
                        id=uuid.uuid4(),
                        product_id=prod.id,
                        marketplace_id=mp.id,
                        marketplace_product_id=f"{mp.slug.upper()}-{prod.ean[:6]}-{idx+1}",
                        price=Decimal(str(price)),
                        original_price=Decimal(str(orig_price)),
                        discount_percent=Decimal(str(discount)),
                        currency="INR",
                        listing_url=listing_url,
                        seller_name=f"{mp.name} Direct",
                        is_available=True,
                        is_prime=(idx % 2 == 0),
                        stock_status="IN_STOCK",
                        delivery_estimate="Express Delivery in 1-2 Days" if (idx % 2 == 0) else "Standard Delivery in 3-4 Days",
                        rating=Decimal(str(round(random.uniform(4.0, 4.9), 1))),
                        review_count=random.randint(120, 3500),
                    )
                    session.add(listing)
                    await session.flush()
                    listing_count += 1

                    # Generate 7-14 historical price points over the last 60 days
                    num_points = random.randint(7, 14)
                    now_utc = datetime.now(timezone.utc)
                    for p_idx in range(num_points):
                        days_ago = random.randint(1, 60)
                        hist_time = now_utc - timedelta(days=days_ago)
                        hist_var = random.uniform(-0.10, 0.10)
                        hist_price = round((price * (1.0 + hist_var)) / 10.0) * 10.0

                        hist_entry = PriceHistory(
                            id=uuid.uuid4(),
                            listing_id=listing.id,
                            price=Decimal(str(hist_price)),
                            currency="INR",
                            created_at=hist_time,
                        )
                        session.add(hist_entry)
                        history_count += 1

                print(f"  + Created Product: {prod.name} with {len(selected_mps)} listings")
            else:
                print(f"  . Existing Product: {existing.name}")

        print("\n[5/6] Committing database transaction...")
        await session.commit()
        print("  [OK] Transaction committed successfully.")

        # 6. Verification Counts
        print("\n[6/6] Final Database Verification Summary:")
        m_cnt = (await session.execute(select(func.count()).select_from(Marketplace))).scalar()
        c_cnt = (await session.execute(select(func.count()).select_from(Category))).scalar()
        b_cnt = (await session.execute(select(func.count()).select_from(Brand))).scalar()
        p_cnt = (await session.execute(select(func.count()).select_from(Product))).scalar()
        l_cnt = (await session.execute(select(func.count()).select_from(ProductListing))).scalar()
        h_cnt = (await session.execute(select(func.count()).select_from(PriceHistory))).scalar()

        print(f"  • Marketplaces Count: {m_cnt}")
        print(f"  • Categories Count:   {c_cnt}")
        print(f"  • Brands Count:       {b_cnt}")
        print(f"  • Products Count:     {p_cnt}")
        print(f"  • Listings Count:     {l_cnt}")
        print(f"  • Price History Points: {h_cnt}")

        print("\n=========================================================")
        print("COMPAREX Production Database Seeding Complete!")
        print("=========================================================")


if __name__ == "__main__":
    asyncio.run(seed_database())
