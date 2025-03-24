# Content-Based Movie Recommendation System
Read More: https://joseph-ishola.github.io/Movie-Recommendation-Algo/

![Movie Recommendation](https://img.shields.io/badge/Machine%20Learning-Recommendation%20System-blue)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![TF-IDF](https://img.shields.io/badge/NLP-TF--IDF-green)
![Scikit-learn](https://img.shields.io/badge/Framework-Scikit--learn-orange)

A sophisticated content-based filtering system that recommends similar movies based on features such as genres, descriptions, and other metadata. This project demonstrates advanced NLP techniques, dimensionality reduction, and similarity calculations to provide accurate movie recommendations without requiring user interaction data.

## Table of Contents
- [Overview](#overview)
- [Key Features](#key-features)
- [System Architecture](#system-architecture)
- [Installation](#installation)
- [Usage](#usage)
- [Data Processing](#data-processing)
- [Methodology](#methodology)
- [Evaluation](#evaluation)
- [Example Results](#example-results)
- [Future Improvements](#future-improvements)
- [License](#license)

## Overview

This project implements a content-based movie recommendation system that analyzes movie metadata to find similarities between films. Unlike collaborative filtering which requires user rating data, this approach solves the "cold start" problem by exclusively using movie properties to identify similar content.

The system leverages natural language processing and machine learning techniques to extract meaningful features from movie descriptions, genres, collections, and other metadata. Through dimensionality reduction and cosine similarity calculations, the model can efficiently recommend movies that share thematic, stylistic, and categorical elements with a specified input film.

## Key Features

- **Pure Content-Based Filtering**: Recommends movies based solely on content features, requiring no user rating data
- **Multi-Feature Analysis**: Combines text features (overview), categorical features (genres), and numerical features (runtime, budget, revenue)
- **Special Collection Weighting**: Enhanced recommendations for movie series by applying higher weights to collection membership
- **Memory-Efficient Processing**: Uses sparse matrices and dimensionality reduction to handle large datasets
- **Comprehensive Evaluation Metrics**: Evaluates recommendations on genre overlap, rating similarity, and content relevance
- **Interactive Interface**: Provides a user-friendly command-line interface for exploring recommendations
- **Custom Visualizations**: Generates similarity visualizations and word clouds for recommended movies with film-specific filenames

## System Architecture

The system follows a modular pipeline architecture with five core components:

1. **Data Ingestion Module**: Handles reading and parsing the movie metadata CSV
2. **Preprocessing Pipeline**: Manages data cleaning, feature extraction, and encoding
3. **Similarity Engine**: Computes and manages the similarity matrix using dimensionality reduction
4. **Recommendation Service**: Provides the interface for retrieving and rendering recommendations
5. **Evaluation Framework**: Calculates and reports performance metrics

This architecture enables independent optimization of each component and facilitates future extensions.

## Installation

```bash
# Clone the repository
git clone https://github.com/joseph-ishola/Movie-Recommendation-Algo.git
cd Movie-Recommendation-Algo

# Create and activate a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required packages
pip install -r requirements.txt
```

### Requirements
- Python 3.8+
- pandas
- numpy
- scikit-learn
- scipy
- matplotlib
- seaborn
- wordcloud

## Usage

### Using the Interactive Interface

The simplest way to use the system is through the interactive command-line interface:

```bash
python interactive_movie_recommender.py
```

This will load the movie data, process features, and prompt you to enter movie titles for recommendations.

### Using the MovieRecommendationSystem Class

For programmatic use or integration into other applications:

```python
from movie_recommendation_system import MovieRecommendationSystem

# Initialize the system
recommender = MovieRecommendationSystem()

# Load and process the data
recommender.data_ingestion('movies_metadata.csv')
recommender.preprocessing_pipeline()
recommender.similarity_engine()

# Get recommendations for a specific movie
movie_title = "The Avengers"
input_idx, recommendations = recommender.recommendation_service(movie_title)

# Display recommendations
print(recommendations)

# Visualize the recommendations
recommender.visualize_recommendations(recommendations, movie_title)
recommender.generate_wordcloud(recommendations, movie_title)

# Evaluate recommendation quality
eval_metrics = recommender.evaluation_framework(recommendations, input_idx)
print(eval_metrics)
```

## Data Processing

The system processes a variety of feature types:

### Genre Processing
- Extracts genre information from nested JSON structures
- Converts to a multi-label binary encoding using MultiLabelBinarizer
- Creates a sparse matrix for efficient processing

### Collection Analysis
- Identifies movies belonging to the same series (e.g., "Star Wars Collection")
- Applies weight multipliers (2x) to emphasize collection relationships
- Significantly improves recommendations for franchise films

### Text Processing
- Applies TF-IDF vectorization to movie overviews
- Removes common stopwords to focus on meaningful content
- Creates high-dimensional sparse vectors representing thematic elements

### Numerical Feature Normalization
- Standardizes budget, revenue, and runtime features
- Replaces missing or zero values with median values
- Ensures all features contribute proportionally to similarity

## Methodology

### Feature Engineering

The system combines multiple feature types into a unified representation:
1. **Binary genre vectors**: Representing genre membership
2. **TF-IDF text vectors**: Capturing thematic content from overviews
3. **Normalized numerical features**: Including runtime, budget, and revenue
4. **Collection membership**: With enhanced weighting for series relationships

### Dimensionality Reduction

To manage the high dimensionality of the combined feature space (primarily from TF-IDF):
- Uses TruncatedSVD to reduce dimensions from ~77,000 to 2,000
- Preserves approximately 85% of variance while dramatically reducing memory usage
- Enables efficient similarity calculations that would be prohibitive in the original space

### Similarity Calculation

Recommendations are generated using:
- **Cosine similarity**: Measures the cosine of the angle between feature vectors
- **Precomputed similarity matrix**: Enables sub-second recommendation retrieval
- **Top-N filtering**: Returns the most similar movies excluding the input film

## Evaluation

The system includes comprehensive evaluation metrics to assess recommendation quality:

### Genre Overlap (0-100%)
- Measures the Jaccard similarity between the genres of the input movie and recommendations
- Higher values indicate better genre matching
- Typical values range from 70-95% for good recommendations

### Rating Difference (0-10)
- Calculates the absolute difference between the input movie's rating and the recommendations
- Lower values indicate more consistent quality
- Typical values under 1.0 indicate strong rating similarity

### Content Relevance (0-100%)
- Evaluates semantic similarity between the input movie and recommendations
- Based on TF-IDF and cosine similarity of feature representations
- Values above 80% indicate strong thematic relevance

## Example Results

### Star Trek (2009)

Recommendations:
1. **Star Trek Into Darkness** (2013) - Similarity: 0.997
2. **Star Trek Beyond** (2016) - Similarity: 0.988
3. **Pacific Rim** (2013) - Similarity: 0.977
4. **Interstellar** (2014) - Similarity: 0.966
5. **Guardians of the Galaxy** (2014) - Similarity: 0.962

Evaluation Metrics:
- Average Genre Overlap: 90.00%
- Average Rating Difference: 0.72
- Average Content Relevance: 95.95%

### The Avengers (2012)

Recommendations:
1. **Star Wars: The Force Awakens** (2015) - Similarity: 0.992
2. **Furious 7** (2015) - Similarity: 0.991
3. **Iron Man 3** (2013) - Similarity: 0.991
4. **Avengers: Age of Ultron** (2015) - Similarity: 0.989
5. **Transformers: Dark of the Moon** (2011) - Similarity: 0.989

Evaluation Metrics:
- Average Genre Overlap: 81.67%
- Average Rating Difference: 0.44
- Average Content Relevance: 85.77%

## Future Improvements

Potential enhancements to the system include:

- **Hybrid Approach**: Combine content-based and collaborative filtering for improved recommendations
- **Deep Learning Integration**: Use neural networks to learn latent features from movie data
- **User Preferences**: Add personalization by allowing users to weight features based on their preferences
- **Web Application**: Deploy the system as an interactive web app accessible to movie enthusiasts
- **Additional Features**: Incorporate more features like cast, crew, keywords, and production companies
- **Diversity Mechanisms**: Implement techniques to ensure diverse recommendations beyond obvious similarities

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

Developed by Joseph Ishola | [Read More](https://joseph-ishola.github.io/Movie-Recommendation-Algo/) | [LinkedIn](https://linkedin.com/in/joseph-ishola)