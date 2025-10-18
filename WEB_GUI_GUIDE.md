# 🌐 Web-based GUI Guide

## Overview

The web-based GUI provides a modern, browser-based interface for the E-commerce Search Algorithm Comparison project. It completely avoids tkinter and GIL issues by using Flask and a web interface.

## 🚀 Quick Start

### 1. Start the Web GUI

```bash
python web_gui.py
```

### 2. Open Your Browser

Navigate to: **http://localhost:5000**

### 3. Use the Interface

- **Load Database Data**: Click to load products from your database
- **Run Comparison**: Compare algorithms across multiple test queries
- **Interactive Search**: Test individual search queries

## ✨ Features

### 📊 Data Management
- Load products from SQLite database
- Set custom limits (or load all products)
- Real-time data status and information

### 🚀 Algorithm Comparison
- Compare Keyword Matching vs TF-IDF algorithms
- 20 comprehensive test queries
- Real-time progress and completion status
- Performance metrics display (MAP, F1@5, NDCG@10)
- Best algorithm rankings

### 🔍 Interactive Search
- Test individual search queries
- Compare results from both algorithms
- See top results from each algorithm
- Performance timing for each search

## 🎯 Key Advantages

- ✅ **No GIL Issues**: Avoids Python 3.14 + tkinter problems
- ✅ **Modern Interface**: Clean, responsive web design
- ✅ **Real-time Updates**: Live progress and status updates
- ✅ **Cross-platform**: Works on any system with a web browser
- ✅ **Mobile Friendly**: Responsive design works on tablets/phones
- ✅ **No Installation Issues**: Just run `python web_gui.py`

## 🔧 Technical Details

### Architecture
- **Backend**: Flask (Python web framework)
- **Frontend**: HTML5 + CSS3 + JavaScript (no frameworks)
- **Data**: Direct database integration
- **Algorithms**: Same ultra-simple comparison engine

### Performance
- **Fast Loading**: Loads 1,000 products in seconds
- **Quick Comparison**: 20 queries across 1,000 products in ~0.1s
- **Responsive**: Real-time UI updates
- **Stable**: No threading or GIL issues

## 🛠️ Troubleshooting

### Port Already in Use
If you get a "port already in use" error:
```bash
# Kill existing processes
pkill -f "python web_gui.py"

# Or use a different port
python -c "
from web_gui import app
app.run(port=5001)
"
```

### Database Issues
Make sure your database is initialized:
```bash
python init_database.py
```

### Missing Dependencies
Install Flask if not already installed:
```bash
pip install flask
```

## 📱 Browser Compatibility

- ✅ Chrome/Chromium
- ✅ Firefox
- ✅ Safari
- ✅ Edge
- ✅ Mobile browsers

## 🎉 Usage Tips

1. **Start with Data Loading**: Always load data first before running comparisons
2. **Use Reasonable Limits**: Start with 1,000 products for testing
3. **Check Status Messages**: The interface provides clear feedback
4. **Try Interactive Search**: Test individual queries to understand algorithm behavior
5. **Compare Results**: Look at the performance metrics to see algorithm differences

## 🔄 Why Web GUI?

The web-based GUI was created to replace the previous tkinter GUI due to:

1. **Python 3.14 Compatibility**: tkinter had GIL (Global Interpreter Lock) issues with Python 3.14
2. **Better Stability**: No more crashes or hanging during comparisons
3. **Modern Interface**: Clean, responsive design that works on any device
4. **Cross-platform**: Works on any system with a web browser
5. **No Dependencies**: No need to install tkinter or deal with GUI library issues

The web GUI provides all the same functionality with better stability and modern interface design!
