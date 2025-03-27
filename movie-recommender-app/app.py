# app.py
from flask import Flask, request, render_template, jsonify
from movie_recommendation_system import MovieRecommendationSystem
import os
import time

app = Flask(__name__)

# Initialize the recommendation system
movie_recommender = MovieRecommendationSystem()
model_ready = False

@app.route('/')
def home():
    return render_template('index.html', model_ready=model_ready)

@app.route('/initialize', methods=['GET'])
def initialize_model():
    global model_ready
    
    if not model_ready:
        try:
            # Initialize the model in the background
            app.logger.info("Initializing recommendation system...")
            
            # Load data and prepare the model
            movie_recommender.data_ingestion('movies_metadata.csv')
            movie_recommender.preprocessing_pipeline()
            movie_recommender.similarity_engine()
            
            model_ready = True
            app.logger.info("Recommendation system initialized!")
            
            return jsonify({'status': 'success', 'message': 'Model initialized successfully'})
        except Exception as e:
            app.logger.error(f"Error initializing model: {str(e)}")
            return jsonify({'status': 'error', 'message': f'Error initializing model: {str(e)}'})
    else:
        return jsonify({'status': 'success', 'message': 'Model already initialized'})

@app.route('/recommend', methods=['POST'])
def recommend():
    global model_ready
    
    if not model_ready:
        return jsonify({'status': 'error', 'message': 'Model not initialized yet'})
    
    movie_title = request.form['movie_title']
    
    try:
        # Get recommendations
        input_idx, recommendations = movie_recommender.recommendation_service(movie_title)
        
        if recommendations.empty:
            return jsonify({'status': 'error', 'message': 'No recommendations found'})
            
        # Convert recommendations to a list of dictionaries
        recommendations_list = []
        for _, row in recommendations.iterrows():
            recommendations_list.append({
                'title': row['title'],
                'genre_names': row['genre_names'],
                'vote_average': float(row['vote_average']),
                'release_date': row['release_date'],
                'similarity_score': float(row['similarity_score']),
                'overview': row['overview']
            })
        
        # Create directory for visualizations if it doesn't exist
        os.makedirs('static/visualizations', exist_ok=True)
        
        # Format the movie title for filenames
        formatted_title = movie_title.lower().replace(' ', '_').replace(':', '').replace('/', '_')
        
        # Define paths for where the files should be saved initially
        temp_chart_path = f"pictures/{formatted_title}_similarity_chart.png"
        temp_wordcloud_path = f"pictures/{formatted_title}_wordcloud.png"
        
        # Define paths for where the files should be moved to (for web access)
        final_chart_path = f"static/visualizations/{formatted_title}_similarity_chart.png"
        final_wordcloud_path = f"static/visualizations/{formatted_title}_wordcloud.png"
        
        # Make sure the pictures directory exists
        os.makedirs('pictures', exist_ok=True)
        
        # Generate visualizations (these will save to the 'pictures' directory)
        movie_recommender.visualize_recommendations(recommendations, movie_title)
        movie_recommender.generate_wordcloud(recommendations, movie_title)
        
        # Move files to the static/visualizations directory
        import shutil
        if os.path.exists(temp_chart_path):
            shutil.copy2(temp_chart_path, final_chart_path)
        else:
            return jsonify({'status': 'error', 'message': f'Visualization file not generated: {temp_chart_path}'})
            
        if os.path.exists(temp_wordcloud_path):
            shutil.copy2(temp_wordcloud_path, final_wordcloud_path)
        else:
            return jsonify({'status': 'error', 'message': f'Wordcloud file not generated: {temp_wordcloud_path}'})
        
        # Get evaluation metrics
        eval_metrics = movie_recommender.evaluation_framework(recommendations, input_idx)
        
        return jsonify({
            'status': 'success',
            'recommendations': recommendations_list,
            'chart_path': f"/static/visualizations/{formatted_title}_similarity_chart.png",
            'wordcloud_path': f"/static/visualizations/{formatted_title}_wordcloud.png",
            'metrics': eval_metrics
        })
    
    except Exception as e:
        app.logger.error(f"Error generating recommendations: {str(e)}")
        return jsonify({'status': 'error', 'message': f'Error: {str(e)}'})

if __name__ == '__main__':
    # Create visualizations directory if it doesn't exist
    os.makedirs('static/visualizations', exist_ok=True)
    
    # Get port from environment variable or use 5000 as default
    port = int(os.environ.get('PORT', 80))
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=port, debug=True)