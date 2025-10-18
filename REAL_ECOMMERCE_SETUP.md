# Real E-commerce API Data Collection

## 🎯 Goal: Collect REAL product data from genuine e-commerce APIs

This guide helps you collect authentic e-commerce data from real marketplace APIs, **not** fake or test APIs.

---

## 🛒 Available Real E-commerce APIs

### **1. Best Buy API (RECOMMENDED)**
- **URL**: https://developer.bestbuy.com/
- **Products**: Electronics, appliances, computers, gaming
- **Rate Limit**: 5,000 requests/day (free)
- **Setup**: Easy - just register and get API key
- **Data Quality**: Excellent - real prices, inventory, descriptions

### **2. Target API**
- **URL**: https://developer.target.com/
- **Products**: General merchandise, home goods, electronics
- **Rate Limit**: Varies by endpoint
- **Setup**: Medium complexity
- **Data Quality**: Good - real retail products

### **3. Newegg API**
- **URL**: https://developer.newegg.com/
- **Products**: Tech products, gaming, electronics
- **Rate Limit**: Limited free tier
- **Setup**: Medium complexity
- **Data Quality**: Excellent for tech products

### **4. Shopify Store APIs**
- **URL**: Public store endpoints
- **Products**: Various categories (depends on store)
- **Rate Limit**: No limits (public data)
- **Setup**: Easy - no API key needed
- **Data Quality**: Good - real store products

---

## 🚀 Quick Start Guide

### **Step 1: Get Best Buy API Key (Easiest)**

1. **Go to**: https://developer.bestbuy.com/
2. **Sign up** for a free account
3. **Create an application** (takes 2 minutes)
4. **Copy your API key**

### **Step 2: Configure Environment**

Create a `.env` file in your project root:
```bash
BESTBUY_API_KEY=your_api_key_here
TARGET_API_KEY=your_target_key_here  # Optional
NEWEGG_API_KEY=your_newegg_key_here  # Optional
```

### **Step 3: Collect Data**

```bash
python collect_real_ecommerce.py
```

---

## 📊 What You'll Get

### **Real Product Data:**
- **Actual prices** from Best Buy, Target, etc.
- **Real product descriptions** and specifications
- **Genuine inventory** and availability
- **Authentic categories** and classifications
- **Real brand names** and model numbers

### **Sample Products:**
- iPhone 15 Pro Max - $999.99 (Best Buy)
- Samsung Galaxy S24 Ultra - $1,199.99 (Best Buy)
- MacBook Pro 16-inch - $2,499.99 (Best Buy)
- Gaming Mouse Logitech G502 - $79.99 (Best Buy)
- Wireless Charging Pad - $29.99 (Best Buy)

---

## 🔧 API Setup Details

### **Best Buy API (Recommended)**

**Why Best Buy API:**
- ✅ **100% Real Data** - Actual Best Buy products and prices
- ✅ **Free** - No cost, just registration
- ✅ **High Rate Limit** - 5,000 requests/day
- ✅ **Good Documentation** - Easy to implement
- ✅ **Electronics Focus** - Perfect for your research

**Setup Process:**
1. Visit https://developer.bestbuy.com/
2. Click "Get Started"
3. Create account with email
4. Create new application
5. Copy API key
6. Add to `.env` file

**API Endpoints:**
- Search: `https://api.bestbuy.com/v1/products(search=query)`
- Product Details: `https://api.bestbuy.com/v1/products/sku.json`
- Categories: `https://api.bestbuy.com/v1/categories`

### **Target API**

**Setup Process:**
1. Visit https://developer.target.com/
2. Register for developer account
3. Create application
4. Get API key
5. Add to `.env` file

**Note**: Target API is more complex and requires product IDs for some endpoints.

### **Newegg API**

**Setup Process:**
1. Visit https://developer.newegg.com/
2. Register for developer account
3. Create application
4. Get API key
5. Add to `.env` file

**Note**: Newegg API has limited free tier but excellent tech product data.

---

## 🎯 Search Queries

The script searches for these product categories:

### **Electronics:**
- iPhone, Samsung Galaxy, laptop, tablet, headphones

### **Gaming:**
- gaming mouse, mechanical keyboard, gaming headset, gaming controller

### **Home & Kitchen:**
- smart speaker, wireless charger, bluetooth speaker, smart home

### **Computers:**
- graphics card, computer monitor, webcam, external hard drive

---

## 📁 Output Files

After running the collection script:

1. **`data/real_ecommerce_products.json`** - Your real API dataset
2. **`data/real_ecommerce_summary.txt`** - Statistics and summary
3. **`results/comparison_results.json`** - Algorithm comparison results

---

## 🚀 Using Your Real Data

### **Test with Algorithms:**
```bash
python prototype/cli.py --mode compare --data data/real_ecommerce_products.json
```

### **Use in GUI:**
```bash
python web_gui.py
# Then load: data/real_ecommerce_products.json
```

---

## ⚠️ Important Notes

### **API Rate Limits:**
- **Best Buy**: 5,000 requests/day
- **Target**: Varies by endpoint
- **Newegg**: Limited free tier
- **Shopify**: No limits (public data)

### **Data Authenticity:**
- ✅ **Real prices** from actual stores
- ✅ **Real inventory** and availability
- ✅ **Authentic product descriptions**
- ✅ **Genuine categories** and classifications
- ❌ **No fake/test data**

### **Network Considerations:**
- APIs may be slow during peak hours
- Some APIs have geographic restrictions
- Rate limiting may require delays between requests

---

## 🎉 Success Criteria

You'll know you have real e-commerce data when:

1. **Products have real prices** from actual stores
2. **Product descriptions** are detailed and authentic
3. **Categories** match real e-commerce classifications
4. **Brand names** are genuine (Apple, Samsung, etc.)
5. **Product URLs** point to real store pages

---

## 🔧 Troubleshooting

### **"No API keys found"**
- Get API key from Best Buy Developer Portal
- Add to `.env` file in project root
- Restart the script

### **"Rate limit exceeded"**
- Wait before making more requests
- Best Buy allows 5,000 requests/day
- Consider upgrading to paid tier

### **"No products collected"**
- Check your internet connection
- Verify API key is correct
- Try different search queries

### **"API error"**
- Check API documentation
- Verify endpoint URLs
- Contact API provider support

---

## 🏆 Expected Results

After successful collection, you should have:

- **50-200 real products** from genuine e-commerce APIs
- **Authentic pricing** and product information
- **Diverse categories** (electronics, gaming, home, etc.)
- **Working search algorithms** with real data
- **Measurable performance differences** between algorithms

**Your research will use 100% authentic e-commerce data!** 🎊
