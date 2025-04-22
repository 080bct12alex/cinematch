# CineMatch: Movie Recommendation System

A personalized movie recommendation system built with Streamlit that helps users discover new movies based on their preferences. The system uses collaborative filtering and integrates with TMDB API for movie data.


### Weblink: [Live Website](https://cinematch3.onrender.com)



## Overview

CineMatch is a web-based application designed to recommend movies based on user preferences. It features a responsive design, movie trailers, detailed movie information, and filtering options. The system leverages precomputed similarity scores for efficient recommendations.

## Features

- **Personalized Recommendations**: Get movie suggestions based on your favorite films
- **Movie Details**: View ratings, genres, runtime, and overview for each movie
- **Trailers**: Watch movie trailers directly in the app
- **Filters**: Narrow down movies by year, genre, and rating
- **Responsive Design**: Works well on both desktop and mobile devices
- **Trending Movies**: Display of currently trending movies
- **Interactive UI**: Clean and user-friendly interface with expandable sections

## Installation

1. Clone the repository:
 -  git clone https://github.com/080bct12alex/cinematch.git

2. Install required dependencies:
  -   pip install streamlit requests pandas streamlit-javascript python-lzma

3. Run the application:
  -  streamlit run app.py

Usage
- Search for Movies: Use the search box to find your favorite movies
- Get Recommendations: Click the "Get Recommendations" button to see similar movies
- View Details: Expand sections to view movie overviews and trailers
- Filter Results: Use sidebar filters to refine movie selections by year, genre, and rating



Data Sources
- TMDB API: For movie details, posters, and trailers
- Precomputed Data: Movie list and similarity scores stored in movie_list.pkl and similarity.xz
- Streamlit: For enabling the creation of a powerful web interface
- Python Libraries: Including requests, pandas, and lzma for data handling
- API Key :  To use this application, you need a TMDB API key. You can obtain one for free by signing up at TMDB.

