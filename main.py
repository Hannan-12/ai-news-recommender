# main.py
import gradio as gr
from agent import NewsAgent
from datetime import datetime
import json
import os
from html import escape

def load_user_preferences(user_id='default'):
    try:
        with open(f'user_prefs_{user_id}.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            'preferred_categories': ['technology', 'business', 'health'],
            'reading_history': []
        }

def save_user_preferences(prefs, user_id='default'):
    with open(f'user_prefs_{user_id}.json', 'w') as f:
        json.dump(prefs, f)

def fetch_and_process_news(category, num_articles=5):
    agent = NewsAgent()
    articles = agent.fetch_news(category, num_articles)
    processed_articles = []
    
    for article in articles:
        summary = agent.summarize_article(article['description'])
        suggested_category = agent.categorize_article(article['title'], article['description'])
        processed_articles.append({
            'title': article['title'],
            'summary': summary,
            'category': suggested_category,
            'url': article['url'],
            'published_at': article['publishedAt']
        })
    
    return processed_articles

def create_article_html(articles):
    if not articles:
        return "<div style='padding: 20px;'>No articles found. Check your API key or try again later.</div>"
    html = "<div style='padding: 20px;'>"
    for i, article in enumerate(articles, 1):
        html += f"""
        <div style='margin-bottom: 20px; padding: 15px; border: 1px solid #ddd; border-radius: 5px;'>
            <h3 style='color: #2a9fd6;'>{i}. {escape(str(article['title']))}</h3>
            <p><strong>Category:</strong> {escape(str(article['category']))}</p>
            <p><strong>Summary:</strong> {escape(str(article['summary']))}</p>
            <p><strong>Published:</strong> {escape(str(article['published_at']))}</p>
            <a href='{escape(str(article['url']), quote=True)}' target='_blank' rel='noopener noreferrer' style='
                display: inline-block;
                padding: 8px 16px;
                background-color: #2a9fd6;
                color: white;
                text-decoration: none;
                border-radius: 4px;
                margin-top: 10px;
            '>Read More</a>
        </div>
        """
    html += "</div>"
    return html

def create_recommendations_html(recommendations):
    if not recommendations:
        return "<div style='padding: 20px;'>No recommendations available yet. Fetch news to build your reading history.</div>"
    html = "<div style='padding: 20px;'>"
    html += "<h2>Recommended Articles</h2>"
    for i, rec in enumerate(recommendations, 1):
        html += f"""
        <div style='margin-bottom: 20px; padding: 15px; border: 1px solid #ddd; border-radius: 5px;'>
            <h3 style='color: #2a9fd6;'>{i}. {escape(str(rec['title']))}</h3>
            <p><strong>Category:</strong> {escape(str(rec['category']))}</p>
            <p><strong>Summary:</strong> {escape(str(rec['summary']))}</p>
            <p><strong>Why:</strong> {escape(str(rec['reason']))}</p>
            <a href='{escape(str(rec['url']), quote=True)}' target='_blank' rel='noopener noreferrer' style='
                display: inline-block;
                padding: 8px 16px;
                background-color: #2a9fd6;
                color: white;
                text-decoration: none;
                border-radius: 4px;
                margin-top: 10px;
            '>Read More</a>
        </div>
        """
    html += "</div>"
    return html

def update_user_preferences(article_data, user_id='default'):
    prefs = load_user_preferences(user_id)
    prefs['reading_history'].append({
        'category': article_data['category'],
        'timestamp': datetime.now().isoformat()
    })
    save_user_preferences(prefs, user_id)

def get_recommendations(user_id='default'):
    agent = NewsAgent()
    prefs = load_user_preferences(user_id)
    return agent.get_recommendations(prefs)

def create_interface():
    with gr.Blocks(title="AI News Recommender", theme=gr.themes.Base()) as interface:
        gr.HTML("""
            <div style='text-align: center; padding: 20px;'>
                <h1 style='color: #2a9fd6;'>📰 AI News Recommender</h1>
            </div>
        """)
        
        with gr.Row():
            with gr.Column(scale=1):
                category_input = gr.Dropdown(
                    choices=["technology", "business", "health", "science", "entertainment"],
                    label="Select Category",
                    value="technology"
                )
                num_articles = gr.Slider(
                    minimum=1, 
                    maximum=10, 
                    value=5, 
                    step=1, 
                    label="Number of Articles"
                )
                fetch_button = gr.Button("🔍 Fetch News", variant="primary")
                recommend_button = gr.Button("🎯 Get Personalized Recommendations", variant="secondary")

            with gr.Column(scale=2):
                # Changed from Markdown to HTML for better styling and clickable links
                news_output = gr.HTML(label="News Articles")
                recommendations_output = gr.HTML(label="Recommended Articles")

        def fetch_news(category, num):
            try:
                articles = fetch_and_process_news(category, num)
                return create_article_html(articles)
            except Exception as exc:
                return f"<div style='padding: 20px;'>Unable to fetch news ({escape(type(exc).__name__)}). Check configuration and try again.</div>"

        def get_personal_recommendations():
            try:
                recommendations = get_recommendations()
                return create_recommendations_html(recommendations)
            except Exception as exc:
                return f"<div style='padding: 20px;'>Unable to load recommendations ({escape(type(exc).__name__)}). Check configuration and try again.</div>"

        fetch_button.click(
            fetch_news,
            inputs=[category_input, num_articles],
            outputs=[news_output]
        )
        
        recommend_button.click(
            get_personal_recommendations,
            outputs=[recommendations_output]
        )

        gr.HTML("""
        <div style='padding: 20px; margin-top: 20px; background-color: #f5f5f5; border-radius: 5px;'>
            <h3 style='color: #2a9fd6;'>📌 How to Use</h3>
            <ol style='margin-left: 20px;'>
                <li>Select a news category from the dropdown</li>
                <li>Choose how many articles you want to see</li>
                <li>Click "Fetch News" to get the latest articles</li>
                <li>Click "Get Personalized Recommendations" to see articles based on your reading history</li>
                <li>Use the "Read More" button to view the full article on the source website</li>
            </ol>
        </div>
        """)

    return interface

if __name__ == "__main__":
    interface = create_interface()
    interface.launch(
        server_name=os.getenv("HOST") or "0.0.0.0",
        server_port=int(os.getenv("PORT") or "7861"),
    )
