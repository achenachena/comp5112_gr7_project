#!/usr/bin/env python3
"""
Collect More Social Media Data - Fixed Import Issues
"""

import sys
import os
import time
import random
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

# Import required modules
from src.ecommerce_search.database.db_manager import get_db_manager
from src.ecommerce_search.database.models import SocialMediaProduct
import praw
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class MoreDataCollector:
    def __init__(self):
        self.db_manager = get_db_manager()
        
        # Reddit API credentials
        self.reddit_apis = []
        for i in range(1, 4):  # 3 Reddit apps
            client_id = os.getenv(f'REDDIT_CLIENT_ID_{i}')
            client_secret = os.getenv(f'REDDIT_CLIENT_SECRET_{i}')
            if client_id and client_secret:
                reddit = praw.Reddit(
                    client_id=client_id,
                    client_secret=client_secret,
                    user_agent=os.getenv('REDDIT_USER_AGENT', 'EcommerceSearchBot/1.0')
                )
                self.reddit_apis.append(reddit)
                print(f"✅ Reddit API {i} initialized")
        
        if not self.reddit_apis:
            print("❌ No Reddit API credentials found!")
            return
   
        # Diverse subreddits for fresh content
        self.subreddits = [
            # High-volume subreddits
            'AskReddit', 'gaming', 'technology', 'BuyItForLife', 'ProductPorn',
            'deals', 'consumerism', 'gadgets', 'fashion', 'malefashionadvice',
            'homeimprovement', 'DIY', 'cooking', 'skincareaddiction', 'fitness',
            # Additional diverse subreddits
            'cars', 'photography', 'books', 'movies', 'music', 'travel',
            'outdoorgear', 'coffee', 'tea', 'beer', 'wine', 'supplements',
            'keto', 'vegan', 'parenting', 'programming', 'woodworking',
            'gardening', 'camping', 'hiking', 'minimalism', 'frugal',
            'cleaning', 'sewing', 'painting', 'antiques', 'vintage',
            # More niche subreddits
            'headphones', 'mechanicalkeyboards', 'buildapc', 'pcmasterrace',
            'battlestations', 'audiophile', 'vinyl', 'coffee', 'tea',
            'cooking', 'baking', 'grilling', 'bbq', 'smoking', 'fermentation',
            'gardening', 'houseplants', 'succulents', 'bonsai', 'landscaping',
            'woodworking', 'carpentry', 'furniture', 'upholstery', 'restoration',
            'sewing', 'quilting', 'knitting', 'crochet', 'embroidery',
            'painting', 'drawing', 'sculpture', 'pottery', 'ceramics',
            'photography', 'videography', 'filmmaking', 'editing',
            'travel', 'backpacking', 'hiking', 'camping', 'climbing',
            'skiing', 'snowboarding', 'surfing', 'diving', 'fishing',
            'hunting', 'archery', 'shooting', 'guns', 'knives',
            'cars', 'motorcycles', 'bicycles', 'electricvehicles',
            'fitness', 'bodybuilding', 'yoga', 'pilates', 'running',
            'cycling', 'swimming', 'tennis', 'golf', 'basketball',
            'soccer', 'football', 'baseball', 'hockey', 'cricket',
            'gaming', 'pcgaming', 'nintendoswitch', 'playstation',
            'xbox', 'nintendo', 'retrogaming', 'emulation',
            'boardgames', 'tabletop', 'dnd', 'rpg', 'warhammer',
            'books', 'reading', 'literature', 'poetry', 'writing',
            'movies', 'television', 'netflix', 'hulu', 'disney',
            'music', 'listentothis', 'hiphopheads', 'popheads',
            'electronicmusic', 'jazz', 'classicalmusic', 'metal',
            'politics', 'worldnews', 'news', 'economics', 'finance',
            'investing', 'stocks', 'cryptocurrency', 'bitcoin',
            'ethereum', 'blockchain', 'defi', 'nft', 'web3',
            'programming', 'webdev', 'machinelearning', 'datascience',
            'artificial', 'robotics', '3Dprinting', 'arduino',
            'raspberry_pi', 'homelab', 'selfhosted', 'privacy',
            'security', 'hacking', 'cybersecurity', 'networking',
            'sysadmin', 'devops', 'cloudcomputing', 'aws',
            'azure', 'gcp', 'kubernetes', 'docker', 'linux',
            'macos', 'windows', 'android', 'ios', 'react',
            'vue', 'angular', 'nodejs', 'python', 'javascript',
            'typescript', 'java', 'csharp', 'cpp', 'rust',
            'go', 'swift', 'kotlin', 'php', 'ruby', 'scala',
            'clojure', 'haskell', 'erlang', 'elixir', 'ocaml',
            'fsharp', 'dart', 'flutter', 'xamarin', 'cordova',
            'ionic', 'reactnative', 'expo', 'unity', 'unreal',
            'blender', 'maya', 'cinema4d', 'aftereffects',
            'premiere', 'davinci', 'finalcut', 'logic', 'ableton',
            'flstudio', 'cubase', 'protools', 'reaper', 'audacity',
            'photoshop', 'illustrator', 'indesign', 'figma',
            'sketch', 'canva', 'gimp', 'inkscape', 'krita',
            'blender', 'maya', 'cinema4d', 'houdini', 'nuke',
            'aftereffects', 'premiere', 'davinci', 'finalcut',
            'logic', 'ableton', 'flstudio', 'cubase', 'protools',
            'reaper', 'audacity', 'photoshop', 'illustrator',
            'indesign', 'figma', 'sketch', 'canva', 'gimp',
            'inkscape', 'krita', 'blender', 'maya', 'cinema4d'
        ]
        
        print(f"📊 Target subreddits: {len(self.subreddits)}")
        print(f"📊 Reddit APIs available: {len(self.reddit_apis)}")

    def collect_from_subreddit(self, subreddit_name, max_posts=100):
        """Collect posts from a specific subreddit"""
        posts = []
        reddit_api = random.choice(self.reddit_apis)  # Random API selection

        try:
            subreddit = reddit_api.subreddit(subreddit_name)
            
            # Try different endpoints for variety
            endpoints = ['hot', 'new', 'top']
            posts_per_endpoint = max_posts // len(endpoints)
            
            for endpoint in endpoints:
                try:
                    if endpoint == 'hot':
                        submissions = subreddit.hot(limit=posts_per_endpoint)
                    elif endpoint == 'new':
                        submissions = subreddit.new(limit=posts_per_endpoint)
                    elif endpoint == 'top':
                        submissions = subreddit.top(limit=posts_per_endpoint, time_filter='week')
                    
                    for post in submissions:
                        try:
                            post_data = {
                                'post_id': f'reddit_{post.id}',
                                'platform': 'reddit',
                                'subreddit': subreddit_name,
                                'title': post.title,
                                'content': post.selftext,
                                'author': str(post.author),
                                'post_date': datetime.fromtimestamp(post.created_utc),
                                'upvotes': post.score,
                                'comments_count': post.num_comments,
                                'url': f"https://reddit.com{post.permalink}",
                                'created_at': datetime.now()
                            }
                            posts.append(post_data)
                            
                        except Exception as e:
                            print(f"⚠️ Error processing post: {e}")
                            continue
                            
                except Exception as e:
                    print(f"⚠️ Error with {endpoint} endpoint for r/{subreddit_name}: {e}")
                    continue
                    
        except Exception as e:
            print(f"❌ Error accessing r/{subreddit_name}: {e}")
            
        return posts

    def save_posts(self, posts, platform='reddit'):
        """Save posts to database"""
        if not posts:
            return 0
            
        try:
            with self.db_manager.get_session() as session:
                saved_count = 0
                for post_data in posts:
                    try:
                        # Check if post already exists
                        existing = session.query(SocialMediaProduct).filter_by(
                            post_id=post_data['post_id']
                        ).first()
                        
                        if existing:
                            continue  # Skip duplicates
                            
                        product = SocialMediaProduct(
                            post_id=post_data['post_id'],
                            platform=post_data['platform'],
                            subreddit=post_data.get('subreddit'),
                            title=post_data['title'],
                            content=post_data['content'],
                            author=post_data['author'],
                            post_date=post_data['post_date'],
                            upvotes=post_data['upvotes'],
                            comments_count=post_data['comments_count'],
                            url=post_data.get('url'),
                            created_at=post_data['created_at']
                        )
                        
                        session.add(product)
                        saved_count += 1
                        
                    except Exception as e:
                        print(f"⚠️ Error saving post {post_data.get('post_id', 'unknown')}: {e}")
                        continue
                
                session.commit()
                return saved_count
                
        except Exception as e:
            print(f"❌ Error saving posts: {e}")
            return 0

    def collect_more_data(self, target_posts=5000):
        """Collect more data from diverse subreddits"""
        print(f"🌐 Collecting {target_posts} more social media posts...")
        print("="*60)
        
        total_collected = 0
        posts_per_subreddit = max(10, target_posts // len(self.subreddits))
        
        for i, subreddit in enumerate(self.subreddits):
            print(f"📊 [{i+1}/{len(self.subreddits)}] Collecting from r/{subreddit}...")
            
            posts = self.collect_from_subreddit(subreddit, posts_per_subreddit)
            saved_count = self.save_posts(posts)
            
            total_collected += saved_count
            print(f"✅ Saved {saved_count}/{len(posts)} posts from r/{subreddit}")
            print(f"📈 Total collected: {total_collected}/{target_posts}")
            
            # Rate limiting
            time.sleep(random.uniform(2, 5))
            
            if total_collected >= target_posts:
                print(f"🎯 Target reached: {total_collected} posts")
                break
        
        print(f"\n🎉 Collection completed!")
        print(f"📊 Total new posts: {total_collected}")
        
        # Show final database stats
        with self.db_manager.get_session() as session:
            total_posts = session.query(SocialMediaProduct).count()
            print(f"📊 Total posts in database: {total_posts:,}")

def main():
    print("🌐 More Social Media Data Collection")
    print("="*50)
    
    collector = MoreDataCollector()
    if not collector.reddit_apis:
        print("❌ Cannot proceed without Reddit API credentials")
        return
    
    try:
        collector.collect_more_data(target_posts=5000)
    except KeyboardInterrupt:
        print("\n⏹️ Collection stopped by user")
    except Exception as e:
        print(f"\n❌ Error during collection: {e}")

if __name__ == "__main__":
    main()
