"""
Author: Joseph Ishola
Email:joseph.k.ishola@gmail.com
Date: 2021-04-10
Description: Interactive Movie Recommendation System   


This script provides an interactive command-line interface to the MovieRecommendationSystem.
Run this after setting up the recommendation system to quickly test recommendations for
different movies.
"""

# Import the movie recommendation system
from movie_recommendation_system import MovieRecommendationSystem

def run_interactive_mode(csv_path='movies_metadata.csv'):
    """
    Run an interactive session for testing movie recommendations.
    
    Parameters:
    -----------
    csv_path : str, default='movies_metadata.csv'
        Path to the movie metadata CSV file
    """
    print("Initializing Movie Recommendation System...")
    
    # Create and initialize the recommendation system
    recommender = MovieRecommendationSystem()
    
    # Load and process the data
    recommender.data_ingestion(csv_path)
    recommender.preprocessing_pipeline()
    recommender.similarity_engine()
    
    print("\nMovie Recommendation System is ready!")
    print("----------------------------------------")
    
    while True:
        # Get user input
        user_input = input("\nEnter a movie title for recommendations (or 'quit' to exit): ")
        
        # Check if user wants to quit
        if user_input.lower() == 'quit':
            print("Thank you for using the Movie Recommendation System. Goodbye!")
            break
        
        try:
            # Get recommendations
            input_idx, recommendations = recommender.recommendation_service(user_input)
            
            # Display and visualize recommendations if found
            if not recommendations.empty:
                print("\nRecommendations:")
                print(recommendations)
                
                # Generate visualizations
                recommender.visualize_recommendations(recommendations, user_input)
                recommender.generate_wordcloud(recommendations, user_input)
                
                # Calculate and display evaluation metrics
                eval_metrics = recommender.evaluation_framework(recommendations, input_idx)
                print(f"\nEvaluation Metrics for '{user_input}':")
                for metric, value in eval_metrics.items():
                    print(f"{metric}: {value:.2f}")
            
        except Exception as e:
            print(f"Error: {e}")
            print("Please try another movie title.")


if __name__ == "__main__":
    # You can change the path to your CSV file if needed
    run_interactive_mode()