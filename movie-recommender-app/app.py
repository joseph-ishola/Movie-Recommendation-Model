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

import matplotlib
matplotlib.use('Agg')  # Set non-interactive backend at application startup

@app.route('/recommend', methods=['POST'])
def recommend():
    global model_ready
    
    if not model_ready:
        return jsonify({'status': 'error', 'message': 'Model not initialized yet'})
    
    movie_title = request.form['movie_title']
    choice_index = request.form.get('choice_index')  # Get choice_index if provided
    
    try:
        # Get recommendations
        if choice_index is not None:
            choice_index = int(choice_index)
        result = movie_recommender.recommendation_service(movie_title, choice_index=choice_index)
        
        # Check if we got multiple matches
        if isinstance(result, dict) and 'multiple_matches' in result:
            return jsonify({
                'status': 'multiple_matches',
                'matches': result['multiple_matches']
            })
        
        input_idx, recommendations = result
        
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
        
        # Set up paths for saving visualizations directly to static folder
        static_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
        chart_save_path = os.path.join(static_folder, f"visualizations/{formatted_title}_similarity_chart.png")
        wordcloud_save_path = os.path.join(static_folder, f"visualizations/{formatted_title}_wordcloud.png")
        
        # For web display, use these paths
        chart_path = f"/static/visualizations/{formatted_title}_similarity_chart.png"
        wordcloud_path = f"/static/visualizations/{formatted_title}_wordcloud.png"
        
        # Generate visualizations directly to the static folder
        movie_recommender.visualize_recommendations(recommendations, movie_title, output_path=chart_save_path)
        movie_recommender.generate_wordcloud(recommendations, movie_title, output_path=wordcloud_save_path)
        
        # Get evaluation metrics
        eval_metrics = movie_recommender.evaluation_framework(recommendations, input_idx)
        
        import matplotlib.pyplot as plt
        plt.close('all')  # Close all open figures to free up memory

        return jsonify({
            'status': 'success',
            'recommendations': recommendations_list,
            'chart_path': chart_path,
            'wordcloud_path': wordcloud_path,
            'metrics': eval_metrics
        })
    
    except Exception as e:
        import matplotlib.pyplot as plt
        plt.close('all')  # Make sure to close all plot windows
        app.logger.error(f"Error generating recommendations: {str(e)}")
        return jsonify({'status': 'error', 'message': f'Error: {str(e)}'})



if __name__ == '__main__':
    # Create visualizations directory if it doesn't exist
    os.makedirs('static/visualizations', exist_ok=True)
    
    # Get port from environment variable or use 5000 as default
    #port = int(os.environ.get('PORT', 80))
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=80, debug=True)