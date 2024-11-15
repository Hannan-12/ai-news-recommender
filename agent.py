# agent.py
from newsapi import NewsApiClient
from groq import Groq
import os
from datetime import datetime, timedelta
from collections import Counter
from Prompt import SUMMARIZATION_PROMPT, CATEGORIZATION_PROMPT
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class NewsAgent:
    def __init__(self):
        # Get API keys from environment variables
        groq_api_key = os.getenv('GROQ_API_KEY')
        news_api_key = os.getenv('NEWS_API_KEY')
        
        if not groq_api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        if not news_api_key:
            raise ValueError("NEWS_API_KEY not found in environment variables")
            
        self.groq_client = Groq(api_key=groq_api_key)
        self.newsapi = NewsApiClient(api_key=news_api_key)
        
    def fetch_news(self, category, num_articles=5):
        """Fetch real-time news articles from NewsAPI."""
        try:
            # Get top headlines for the specified category
            response = self.newsapi.get_top_headlines(
                category=category,
                language='en',
                page_size=num_articles
            )
            
            if response['status'] == 'ok':
                articles = response['articles']
                # Filter out articles with missing fields
                valid_articles = []
                for article in articles:
                    if all(key in article and article[key] for key in ['title', 'description', 'url', 'publishedAt']):
                        valid_articles.append({
                            'title': article['title'],
                            'description': article['description'],
                            'url': article['url'],
                            'publishedAt': article['publishedAt'],
                            'source': article.get('source', {}).get('name', 'Unknown Source')
                        })
                return valid_articles
            else:
                print(f"Error fetching news: {response.get('message', 'Unknown error')}")
                return []
                
        except Exception as e:
            print(f"Error fetching news: {str(e)}")
            return []

    def summarize_article(self, text):
        """Summarize article using Groq API."""
        if not text:
            return "No content available to summarize."
            
        prompt = SUMMARIZATION_PROMPT.format(article_text=text)
        
        try:
            response = self.groq_client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=100,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error generating summary: {str(e)}"

    def categorize_article(self, title, description):
        """Categorize article using Groq API."""
        prompt = CATEGORIZATION_PROMPT.format(
            title=title,
            description=description
        )
        
        try:
            response = self.groq_client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=50,
            )
            return response.choices[0].message.content.strip().lower()
        except Exception as e:
            return "general"

    def get_recommendations(self, user_preferences):
        """Generate personalized news recommendations."""
        recent_history = [
            h for h in user_preferences['reading_history']
            if datetime.fromisoformat(h['timestamp']) > datetime.now() - timedelta(days=7)
        ]
        
        if not recent_history:
            # Default categories if no history
            categories = ['technology', 'business', 'science']
        else:
            category_counts = Counter(h['category'] for h in recent_history)
            categories = [category for category, _ in category_counts.most_common(3)]
        
        recommendations = []
        for category in categories:
            articles = self.fetch_news(category, num_articles=2)
            for article in articles:
                summary = self.summarize_article(article['description'])
                recommendations.append({
                    'title': article['title'],
                    'summary': summary,
                    'category': category,
                    'url': article['url'],
                    'source': article['source'],
                    'published_at': article['publishedAt'],
                    'reason': f"Based on your interest in {category} articles"
                })
                
        return recommendations

    def search_news(self, query, num_articles=5):
        """Search for news articles based on a query."""
        try:
            response = self.newsapi.get_everything(
                q=query,
                language='en',
                sort_by='relevancy',
                page_size=num_articles
            )
            
            if response['status'] == 'ok':
                articles = response['articles']
                valid_articles = []
                for article in articles:
                    if all(key in article and article[key] for key in ['title', 'description', 'url', 'publishedAt']):
                        valid_articles.append({
                            'title': article['title'],
                            'description': article['description'],
                            'url': article['url'],
                            'publishedAt': article['publishedAt'],
                            'source': article.get('source', {}).get('name', 'Unknown Source')
                        })
                return valid_articles
            else:
                print(f"Error searching news: {response.get('message', 'Unknown error')}")
                return []
                
        except Exception as e:
            print(f"Error searching news: {str(e)}")
            return []