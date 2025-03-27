"""
Author: Joseph Ishola
Email:joseph.k.ishola@gmail.com
Date: 2021-04-10
Description: module for Movie Recommendation System
"""
# Importing the required libraries
import pandas as pd
import numpy as np
import ast
from sklearn.preprocessing import MultiLabelBinarizer, StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD
from scipy.sparse import csr_matrix, hstack
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import seaborn as sns
import os
sns.set()

class MovieRecommendationSystem:
    """
    A class implementing a content-based movie recommendation system using TF-IDF and cosine similarity.
    Follows a modular pipeline architecture with distinct components.
    """
    
    def __init__(self):
        """Initialize the recommendation system components."""
        self.movies_df = None
        self.tfidf_matrix = None
        self.genres_sparse = None
        self.numerical_sparse = None
        self.collection_sparse = None
        self.reduced_features = None
        self.cosine_sim = None
        
    def data_ingestion(self, filepath):
        """
        Data Ingestion Module: Handles reading and initial parsing of the movie metadata CSV.
        
        Parameters:
        -----------
        filepath : str
            Path to the movie metadata CSV file
            
        Returns:
        --------
        pandas.DataFrame
            The loaded movies dataframe
        """
        print("Loading movie data...")
        self.movies_df = pd.read_csv(filepath, low_memory=False)
        print(f"Loaded {len(self.movies_df)} movies.")
        return self.movies_df
    
    def preprocessing_pipeline(self):
        """
        Preprocessing Pipeline: Manages data cleaning, type conversion, and feature extraction.
        
        This method handles:
        - Genre extraction and encoding
        - Collection information extraction
        - Text processing for movie overviews
        - Numerical feature normalization
        
        Returns:
        --------
        tuple
            A tuple containing the processed features: (genres_sparse, tfidf_matrix, numerical_sparse, collection_sparse)
        """
        print("Starting preprocessing pipeline...")
        
        # 1. Process Genres
        print("Processing genres...")
        # Convert genres from string to list of dictionaries
        self.movies_df['genres'] = self.movies_df['genres'].apply(
            lambda x: ast.literal_eval(x) if isinstance(x, str) else []
        )
        
        # Extract genre names
        self.movies_df['genre_names'] = self.movies_df['genres'].apply(
            lambda x: [genre['name'] for genre in x]
        )
        
        # Create binary genre features
        mlb = MultiLabelBinarizer()
        genres_matrix = mlb.fit_transform(self.movies_df['genre_names'])
        genres_df = pd.DataFrame(genres_matrix, columns=mlb.classes_)
        
        # Convert to sparse matrix for efficiency
        self.genres_sparse = csr_matrix(genres_df.values)
        
        # 2. Process Collection Information
        print("Processing collection information...")
        # Extract collection names
        def extract_collection_name(x):
            if pd.isna(x) or x == "" or x == "NaN":
                return ""
            try:
                data = ast.literal_eval(x)
                return data.get("name", "")
            except Exception:
                return ""
        
        # Apply the function to extract collection names
        self.movies_df['collection_name'] = self.movies_df['belongs_to_collection'].apply(extract_collection_name)
        
        # Create dummy variables for collection names
        collection_dummies = pd.get_dummies(self.movies_df['collection_name'], prefix='collection')
        
        # Convert to sparse matrix and apply weighting (collections are important signals)
        self.collection_sparse = csr_matrix(collection_dummies.values) * 2  # Applying weight multiplier
        
        # 3. Process Textual Features (Overview)
        print("Processing textual features...")
        # Fill NaN values in 'overview' column with an empty string
        self.movies_df['overview'] = self.movies_df['overview'].fillna("")
        
        # Initialize TF-IDF vectorizer and transform overviews
        tfidf = TfidfVectorizer(stop_words='english')
        self.tfidf_matrix = tfidf.fit_transform(self.movies_df['overview'])
        
        # 4. Process Numerical Features
        print("Processing numerical features...")
        # Select numerical features
        numerical_features = ['budget', 'revenue', 'runtime']
        numerical_df = self.movies_df[numerical_features].apply(pd.to_numeric, errors='coerce')
        
        # Replace 0s with the median to avoid zero-impact
        numerical_df = numerical_df.replace(0, numerical_df.median())
        
        # Fill any remaining NaN values with the median
        numerical_df = numerical_df.fillna(numerical_df.median())
        
        # Normalize numerical features
        scaler = StandardScaler()
        normalized_numerical_df = pd.DataFrame(
            scaler.fit_transform(numerical_df),
            columns=numerical_df.columns
        )
        
        # Convert to sparse matrix
        self.numerical_sparse = csr_matrix(normalized_numerical_df.values)
        
        # Store the processed features in the dataframe
        self.movies_df = pd.concat([self.movies_df, genres_df, normalized_numerical_df], axis=1)
        
        # Create genre_features field for evaluation
        self.movies_df['genre_features'] = self.movies_df['genre_names'].apply(
            lambda genres: ' '.join(genres) if isinstance(genres, list) else ''
        )
        
        print("Preprocessing complete.")
        return (self.genres_sparse, self.tfidf_matrix, self.numerical_sparse, self.collection_sparse)
    
    def similarity_engine(self, n_components=2000):
        """
        Similarity Engine: Computes and manages the similarity matrix.
        
        This method combines all features, performs dimensionality reduction, 
        and calculates the similarity matrix.
        
        Parameters:
        -----------
        n_components : int, default=2000
            Number of components to keep in dimensionality reduction
            
        Returns:
        --------
        numpy.ndarray
            The computed cosine similarity matrix
        """
        print("Building similarity engine...")
        
        # Ensure features are processed
        if any(x is None for x in [self.genres_sparse, self.tfidf_matrix, 
                                 self.numerical_sparse, self.collection_sparse]):
            print("Features not processed. Running preprocessing pipeline...")
            self.preprocessing_pipeline()
        
        # Combine all features
        print("Combining features...")
        combined_features_sparse = hstack([
            self.genres_sparse, 
            self.tfidf_matrix,
            self.numerical_sparse, 
            self.collection_sparse
        ])
        
        # Dimensionality reduction
        print(f"Performing dimensionality reduction to {n_components} components...")
        svd = TruncatedSVD(n_components=n_components, random_state=42)
        self.reduced_features = svd.fit_transform(combined_features_sparse)
        print(f"Explained variance ratio: {svd.explained_variance_ratio_.sum():.2f}")
        
        # Compute similarity matrix
        print("Computing similarity matrix...")
        self.cosine_sim = cosine_similarity(self.reduced_features, self.reduced_features)
        print("Similarity matrix computed.")
        
        return self.cosine_sim
    
    def recommendation_service(self, title, top_n=5):
        """
        Recommendation Service: Provides the interface for retrieving and rendering recommendations.
        
        Parameters:
        -----------
        title : str
            The title of the movie to get recommendations for
        top_n : int, default=5
            Number of recommendations to return
            
        Returns:
        --------
        tuple
            A tuple containing (input_movie_index, recommendations_dataframe)
        """
        # Ensure similarity matrix is computed
        if self.cosine_sim is None:
            print("Similarity matrix not found. Computing...")
            self.similarity_engine()
        
        title = title.lower()
        
        # Find the index of the movie that matches the title
        indices = pd.Series(self.movies_df.index, index=self.movies_df['title'].str.lower())
        
        # Handle titles not found exactly
        if title not in indices:
            closest_titles = self.movies_df[self.movies_df['title'].str.contains(title, case=False, na=False)]
            if len(closest_titles) > 0:
                title = closest_titles.iloc[0]['title'].lower()
                print(f"Title not found exactly. Using closest match: '{closest_titles.iloc[0]['title']}'")
            else:
                print(f"No title containing '{title}' found.")
                return None, pd.DataFrame()
        
        idx = indices[title]
        
        # Handle multiple movies with the same title
        if isinstance(idx, pd.Series):
            print(f"Multiple movies found for '{title}':")
            for i, index in enumerate(idx):
                movie_info = self.movies_df.loc[index, ['title', 'release_date']]
                print(f"{i+1}. {movie_info['title']} ({movie_info['release_date']})")
            
            choice = int(input("Enter the number of the movie you meant: ")) - 1
            idx = idx.iloc[choice]
        
        # Get the pairwise similarity scores for all movies with the target movie
        sim_scores = list(enumerate(self.cosine_sim[idx]))
        
        # Sort the movies based on the similarity scores
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        
        # Get the top N most similar movies (excluding the input movie)
        sim_scores = sim_scores[1:top_n+1]
        
        # Get the movie indices
        movie_indices = [i[0] for i in sim_scores]
        
        # Create a dataframe with the recommended movies and their similarity scores
        recommendations = self.movies_df.iloc[movie_indices].copy()
        
        # Add similarity scores to the dataframe
        recommendations['similarity_score'] = [i[1] for i in sim_scores]
        
        # Return recommended movies with relevant information
        return idx, recommendations[['title', 'genre_names', 'vote_average', 
                                   'release_date', 'similarity_score', 'overview']]
    
    def evaluation_framework(self, recommendations, input_idx):
        """
        Evaluation Framework: Calculates and reports performance metrics.
        
        Parameters:
        -----------
        recommendations : pandas.DataFrame
            The dataframe of recommended movies
        input_idx : int
            The index of the input movie
            
        Returns:
        --------
        dict
            A dictionary of evaluation metrics
        """
        # Get the genres of the input movie
        input_genres = self.movies_df.loc[input_idx, 'genre_names']
        
        # Calculate genre overlap
        genre_matches = []
        for _, row in recommendations.iterrows():
            rec_genres = row['genre_names']
            overlap = len(set(input_genres) & set(rec_genres)) / len(set(input_genres) | set(rec_genres)) if set(input_genres) | set(rec_genres) else 0
            genre_matches.append(overlap)
        
        avg_genre_overlap = sum(genre_matches) / len(genre_matches) if genre_matches else 0
        avg_genre_overlap = avg_genre_overlap * 100  # Convert to percentage
        
        # Calculate rating similarity
        input_rating = self.movies_df.loc[input_idx, 'vote_average']
        rating_diffs = []
        for _, row in recommendations.iterrows():
            rec_rating = row['vote_average']
            if pd.notna(rec_rating) and pd.notna(input_rating):
                diff = abs(float(rec_rating) - float(input_rating))
                rating_diffs.append(diff)
        
        avg_rating_diff = sum(rating_diffs) / len(rating_diffs) if rating_diffs else 0
        
        # Compute Content Relevance using TF-IDF + Cosine Similarity based on genres
        tfidf = TfidfVectorizer(stop_words='english')
        
        # Create genre features text if not already created
        if 'genre_features' not in self.movies_df.columns:
            self.movies_df['genre_features'] = self.movies_df['genre_names'].apply(
                lambda genres: ' '.join(genres) if isinstance(genres, list) else ''
            )
        
        tfidf_matrix = tfidf.fit_transform(self.movies_df['genre_features'])
        
        input_vector = tfidf_matrix[input_idx]
        content_similarities = []
        
        for _, row in recommendations.iterrows():
            rec_idx = self.movies_df[
                (self.movies_df['title'] == row['title']) & 
                (self.movies_df['release_date'] == row['release_date'])
            ].index[0]
            
            rec_vector = tfidf_matrix[rec_idx]
            similarity = cosine_similarity(input_vector, rec_vector)[0][0]
            content_similarities.append(similarity)
        
        avg_content_relevance = sum(content_similarities) / len(content_similarities) if content_similarities else 0
        avg_content_relevance = avg_content_relevance * 100  # Convert to percentage
        
        # Return evaluation metrics
        return {
            'average_genre_overlap': avg_genre_overlap,
            'average_rating_difference': avg_rating_diff,
            'average_content_relevance': avg_content_relevance
        }
    
    def visualize_recommendations(self, recommendations, title, output_path=None):
        """
        Visualization utility to create a bar chart of similarity scores.
        
        Parameters:
        -----------
        recommendations : pandas.DataFrame
            The dataframe of recommended movies
        title : str
            The title of the input movie
        output_path : str, optional
            Custom path to save the visualization. If None, uses default location.
            
        Returns:
        --------
        matplotlib.figure.Figure
            The figure object containing the visualization
        """
        # Format the title to be filename-friendly
        formatted_title = title.lower().replace(' ', '_').replace(':', '').replace('/', '_')

        # Set the default output path
        if output_path is None:
            output_path = f'pictures/{formatted_title}_similarity_chart.png'

        # Ensure the directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Create a new figure
        plt.figure(figsize=(12, 8))
        
        # Create a bar chart of similarity scores
        plt.barh(recommendations['title'], recommendations['similarity_score'], color='skyblue')
        plt.xlabel('Similarity Score')
        plt.ylabel('Movie Title')
        plt.title(f'Movies Similar to "{title}"')
        plt.gca().invert_yaxis()  # Invert y-axis to have the highest similarity at the top
        
        # Save the figure
        plt.tight_layout()
        plt.savefig(output_path)
        #print(f"Visualization saved to {output_path}")
        
        # Close the figure to prevent display in non-interactive environments
        plt.close()

        #return output_path
    
    def generate_wordcloud(self, recommendations, title, output_path=None):
        """
        Visualization utility to create a word cloud from movie overviews.
        
        Parameters:
        -----------
        recommendations : pandas.DataFrame
            The dataframe of recommended movies
        title : str
            The title of the input movie
        output_path : str, optional
            Custom path to save the visualization. If None, uses default location.
            
        Returns:
        --------
        wordcloud.WordCloud
            The generated word cloud object
        """
        # Format the title to be filename-friendly
        formatted_title = title.lower().replace(' ', '_').replace(':', '').replace('/', '_')

        if output_path is None:
            output_path = f'pictures/{formatted_title}_wordcloud.png'
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Combine all overviews
        combined_overview = ' '.join(recommendations['overview'].tolist())
        
        # Generate word cloud
        wordcloud = WordCloud(
            width=800, 
            height=500, 
            background_color='white',
            max_words=200, 
            contour_width=3, 
            contour_color='steelblue'
        )
        wordcloud.generate(combined_overview)
        
        # Create a new figure for the wordcloud
        plt.figure(figsize=(10, 7))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        
        # Save the figure
        plt.savefig(output_path)
        print(f"Word cloud saved to {output_path}")
        
        # Close the figure to prevent display in non-interactive environments
        plt.close()

        #return output_path


# if __name__ == "__main__":