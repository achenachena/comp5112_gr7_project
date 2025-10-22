#!/usr/bin/env python3
"""
Fresh Social Media Scraper - Focus on new subreddits
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from real_social_media_scraper import RealSocialMediaScraper, ScrapingConfig

def main():
    print("🌐 Fresh Social Media Data Collection")
    print("="*50)
    print("Focusing on diverse subreddits for fresh content...")
    
    # Create config with diverse subreddits
    config = ScrapingConfig(
        max_posts_per_platform={'reddit': 10000, 'twitter': 0},  # Focus on Reddit
        rate_limit_respect=True,
        delay_range=(2, 5)
    )
    
    # Create scraper with diverse subreddits
    scraper = RealSocialMediaScraper(config)
    
    # Subreddits are loaded from config/subreddits.json
    # No need to override - the scraper loads them automatically
    
    print(f"📊 Target: {config.max_posts_per_platform['reddit']} posts")
    print(f"📊 Subreddits: {len(scraper.subreddits)}")
    print(f"📊 Posts per subreddit: ~{config.max_posts_per_platform['reddit'] // len(scraper.subreddits)}")
    
    try:
        scraper.scrape_all_platforms()
        print("\n✅ Fresh data collection completed!")
    except KeyboardInterrupt:
        print("\n⏹️ Collection stopped by user")
    except Exception as e:
        print(f"\n❌ Error during collection: {e}")

if __name__ == "__main__":
    main()
