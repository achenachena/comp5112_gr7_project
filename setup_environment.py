#!/usr/bin/env python3
"""
Environment Setup Script

This script helps you set up your environment variables for API keys
and configuration settings securely.
"""

import os
from pathlib import Path


def create_env_file():
    """Create .env file from template."""
    template_path = Path("env.template")
    env_path = Path(".env")
    
    if env_path.exists():
        print("✅ .env file already exists!")
        return
    
    if not template_path.exists():
        print("❌ env.template not found!")
        return
    
    # Copy template to .env
    with open(template_path, 'r', encoding='utf-8') as template:
        content = template.read()
    
    with open(env_path, 'w', encoding='utf-8') as env_file:
        env_file.write(content)
    
    print("✅ Created .env file from template!")
    print("📝 Please edit .env file and add your actual API keys")


def check_api_keys():
    """Check which API keys are configured."""
    from dotenv import load_dotenv
    load_dotenv()
    
    print("\n🔑 API Key Status:")
    print("-" * 40)
    
    apis = {
        'BESTBUY_API_KEY': 'Best Buy API',
        'TARGET_API_KEY': 'Target API', 
        'NEWEGG_API_KEY': 'Newegg API',
        'WALMART_API_KEY': 'Walmart API'
    }
    
    configured = 0
    for key, name in apis.items():
        value = os.getenv(key)
        if value and value != f'your_{key.lower().replace("_", "_")}_here':
            print(f"✅ {name}: Configured")
            configured += 1
        else:
            print(f"❌ {name}: Not configured")
    
    print(f"\n📊 Configured: {configured}/{len(apis)} APIs")
    
    if configured == 0:
        print("\n💡 To get API keys:")
        print("   • Best Buy: https://developer.bestbuy.com/")
        print("   • Target: https://developer.target.com/")
        print("   • Newegg: https://developer.newegg.com/")
        print("   • Walmart: https://developer.walmart.com/")


def show_config_info():
    """Show current configuration."""
    from dotenv import load_dotenv
    load_dotenv()
    
    print("\n⚙️ Current Configuration:")
    print("-" * 40)
    print(f"Database URL: {os.getenv('DATABASE_URL', 'sqlite:///data/ecommerce_research.db')}")
    print(f"API Delay: {os.getenv('API_DELAY', '1')} seconds")
    print(f"Max Products: {os.getenv('MAX_PRODUCTS_PER_SOURCE', '10000')}")


def main():
    """Main setup function."""
    print("🚀 E-commerce Research Project Setup")
    print("=" * 50)
    
    # Check if .env exists
    if not Path(".env").exists():
        print("\n📝 Setting up environment file...")
        create_env_file()
    else:
        print("\n✅ Environment file found!")
    
    # Check API keys
    check_api_keys()
    
    # Show configuration
    show_config_info()
    
    print("\n🎯 Next Steps:")
    print("1. Edit .env file with your API keys")
    print("2. Run: python collect_to_database.py")
    print("3. Run: python run_database_search.py")
    
    print("\n🔒 Security Note:")
    print("Your .env file is already in .gitignore")
    print("API keys will NOT be committed to GitHub!")


if __name__ == "__main__":
    main()
