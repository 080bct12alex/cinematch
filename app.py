import pickle
import streamlit as st
import requests
import pandas as pd
from streamlit_javascript import st_javascript
import lzma

# Set page configuration for better layout
st.set_page_config(
    page_title="CineMatch: Movie Recommendation System",
    page_icon="🎬",
    layout="wide"
)

# Custom CSS for responsive design and visual improvements
st.markdown("""<style>
    .movie-card {
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
        background-color: rgba(49, 51, 63, 0.7);
        transition: transform 0.3s ease;
    }
    .movie-card:hover {
        transform: scale(1.02);
    }
    .movie-title {
        font-weight: bold;
        margin-top: 0.5rem;
        margin-bottom: 0.2rem;
    }
    .movie-meta {
        font-size: 0.9rem;
        color: #9e9e9e;
    }
    .stButton>button {
        width: 100%;
        background-color: #FF4B4B;
        color: white;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #FF2B2B;
    }
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        margin-bottom: 1rem;
    }
</style>""", unsafe_allow_html=True)

# API configuration
API_KEY = "8265bd1679663a7ea12ac168da84d2e8"

# Function to get screen width using streamlit-javascript
def get_screen_width():
    try:
        width = st_javascript("window.innerWidth")
        return width if width is not None else 1200  # Default fallback
    except Exception as e:
        st.warning(f"Screen width detection error: {str(e)}")
        return 1200  # Default fallback if component fails

# Function to determine number of columns based on screen width
def get_column_count(width):
    if width < 576:
        return 1  # Mobile
    elif width < 992:
        return 2  # Tablet
    elif width < 1400:
        return 3  # Small desktop
    else:
        return 5  # Large desktop

# Cache data fetching functions
@st.cache_data
def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}"
        response = requests.get(url, timeout=10)
        data = response.json()
        if data.get('poster_path'):
            return f"https://image.tmdb.org/t/p/w500/{data['poster_path']}"
        return "https://via.placeholder.com/500x750?text=Poster+Not+Available"
    except Exception as e:
        st.error(f"Error fetching poster: {str(e)}")
        return "https://via.placeholder.com/500x750?text=Error+Loading+Poster"

@st.cache_data
def get_movie_details(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}"
        response = requests.get(url, timeout=10)
        data = response.json()
        return {
            'rating': round(data.get('vote_average', 0), 1),
            'year': data.get('release_date', '')[:4] if data.get('release_date') else 'N/A',
            'overview': data.get('overview', 'No description available'),
            'genres': ', '.join([g['name'] for g in data.get('genres', [])]) or 'N/A',
            'runtime': f"{data.get('runtime', 0)} min" if data.get('runtime') else 'N/A'
        }
    except Exception as e:
        st.error(f"Error fetching movie details: {str(e)}")
        return {
            'rating': 'N/A',
            'year': 'N/A',
            'overview': 'Error loading details',
            'genres': 'N/A',
            'runtime': 'N/A'
        }

@st.cache_data
def fetch_trailer(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={API_KEY}"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        # Get all YouTube trailers
        trailers = [v for v in data.get('results', []) 
                   if v.get('site') == 'YouTube' and v.get('type', '').lower() == 'trailer']
        
        # If trailers exist, return the first one
        if trailers:
            trailer_key = trailers[0].get('key')
            if trailer_key:
                return f"https://www.youtube.com/embed/{trailer_key}"
        return None
    except Exception as e:
        st.error(f"Error fetching trailer: {str(e)}")
        return None

@st.cache_data
def recommend(movie):
    try:
        index = movies[movies['title'] == movie].index[0]
        distances = sorted(enumerate(similarity[index]), reverse=True, key=lambda x: x[1])
        return [movies.iloc[i[0]] for i in distances[1:6]]
    except Exception as e:
        st.error(f"Recommendation error: {str(e)}")
        return []

@st.cache_data
def fetch_trending_movies():
    try:
        url = f"https://api.themoviedb.org/3/trending/movie/week?api_key={API_KEY}"
        response = requests.get(url, timeout=10)
        return response.json().get('results', [])[:5]
    except Exception as e:
        st.error(f"Error fetching trending movies: {str(e)}")
        return []

# Function to test API connection
def test_api_connection():
    try:
        response = requests.get(f"https://api.themoviedb.org/3/movie/550?api_key={API_KEY}", timeout=5)
        if response.status_code == 200:
            return True
        else:
            st.error(f"API connection failed: {response.status_code}")
            return False
    except Exception as e:
        st.error(f"API connection error: {str(e)}")
        return False

# Header section with branding
st.markdown('<h1 class="main-header">🎬 CineMatch: Movie Recommendation System</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Discover your next favorite movies based on your preferences</p>', unsafe_allow_html=True)

# Load data with error handling
try:
    # Attempt to load the movie list from a pickle file
    with open('movie_list.pkl', 'rb') as movie_file:
        movies = pickle.load(movie_file)

    # Load the compressed .xz file for similarity data
    with lzma.open('similarity.xz', 'rb') as similarity_file:
        similarity = pickle.load(similarity_file)

except FileNotFoundError:
    # Handle the case where the file is not found
    st.error("Critical Error: Data files not found!")
    st.stop()
except Exception as e:
    # Handle any other exceptions that may occur
    st.error(f"Error loading data: {str(e)}")
    st.stop()
# Test API connection
api_working = test_api_connection()
if not api_working:
    st.warning("API connection issues detected. Some features may not work correctly.")

# Create sidebar for filters and options
with st.sidebar:
    st.header("🔍 Search Options")
    
    # Year filter
    st.subheader("Filter by Year")
    min_year = 1950
    max_year = 2025  # Current year as of April 2025
    year_range = st.slider("Select Year Range", min_year, max_year, (min_year, max_year))
    
    # Genre filter
    st.subheader("Filter by Genre")
    genres = ["All Genres", "Action", "Adventure", "Animation", "Comedy", "Crime",
              "Documentary", "Drama", "Family", "Fantasy", "History", "Horror",
              "Music", "Mystery", "Romance", "Science Fiction", "Thriller", "War", "Western"]
    selected_genre = st.selectbox("Select Genre", genres)
    
    # Rating filter
    st.subheader("Filter by Rating")
    min_rating = st.slider("Minimum Rating", 0.0, 10.0, 0.0, 0.5)
    
    st.markdown("---")
    st.markdown("### About")
    st.markdown("CineMatch uses collaborative filtering to recommend movies based on similarity scores.")
    st.markdown("Data source: TMDB API")
    st.markdown("Last updated: April 21, 2025")

# Apply filters to movie list
filtered_movies = movies.copy()

# Apply year filter if data available
if 'year' in filtered_movies.columns:
    filtered_movies = filtered_movies[(
        filtered_movies['year'] >= year_range[0]) & 
        (filtered_movies['year'] <= year_range[1])]

# Apply genre filter if selected
if selected_genre != "All Genres" and 'genres' in filtered_movies.columns:
    filtered_movies = filtered_movies[
        filtered_movies['genres'].str.contains(selected_genre, case=False, na=False)]

# Apply rating filter if data available
if 'rating' in filtered_movies.columns:
    filtered_movies = filtered_movies[filtered_movies['rating'] >= min_rating]

# Main content area
col1, col2 = st.columns([3, 1])

with col1:
    # Movie selection
    if 'title' not in filtered_movies.columns or filtered_movies.empty:
        st.error("No movie titles available that match your filters!")
        selected_movie = None
    else:
        selected_movie = st.selectbox(
            "🔍 Search your favorite movie",
            filtered_movies['title'].values,
            key='movie_select',
            help="Type or select a movie title to get recommendations"
        )

with col2:
    # Recommendation button with callback to set session state
    recommend_btn = st.button(
        'Get Recommendations', 
        key='recommend_btn_trigger', 
        on_click=lambda: setattr(st.session_state, 'recommend_btn', True)
    )

# Progress indicator
progress_placeholder = st.empty()

# Recommendation section
if selected_movie and st.session_state.get('recommend_btn', False):
    with progress_placeholder.container():
        with st.spinner('🎥 Finding perfect matches...'):
            recommendations = recommend(selected_movie)
            
            if not recommendations:
                st.warning("No recommendations found. Please try another movie.")
            else:
                # Display selected movie with trailer
                st.subheader(f"You searched: {selected_movie}")
                
                try:
                    selected_id = movies[movies['title'] == selected_movie].movie_id.values[0]
                    selected_poster = fetch_poster(selected_id)
                    selected_details = get_movie_details(selected_id)
                    selected_trailer = fetch_trailer(selected_id)
                    
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        st.image(selected_poster, use_container_width=True)
                        st.markdown(f"⭐ **Rating:** {selected_details['rating']}/10")
                        st.markdown(f"📅 **Year:** {selected_details['year']}")
                        st.markdown(f"🎭 **Genres:** {selected_details['genres']}")
                        st.markdown(f"⏱️ **Runtime:** {selected_details['runtime']}")
                    
                    with col2:
                        st.markdown("### Overview")
                        st.markdown(selected_details['overview'])
                        
                        if selected_trailer:
                            st.markdown("### Trailer")
                            st.markdown(f'<iframe width="100%" height="315" src="{selected_trailer}" '
                                       f'frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; '
                                       f'gyroscope; picture-in-picture" allowfullscreen></iframe>', 
                                       unsafe_allow_html=True)
                        else:
                            st.info("Trailer not available for this movie")
                
                except Exception as e:
                    st.error(f"Error loading movie details: {str(e)}")
                
                # Display recommendations
                st.markdown("---")
                st.subheader("🎬 Recommended Movies")
                
                # Get screen width and determine column count
                screen_width = get_screen_width()
                num_cols = get_column_count(screen_width)
                
                # Create dynamic columns based on screen size
                cols = st.columns(num_cols)
                
                for i, movie in enumerate(recommendations):
                    col_index = i % num_cols
                    
                    with cols[col_index]:
                        with st.container():
                            st.markdown('<div class="movie-card">', unsafe_allow_html=True)
                            
                            # Fetch movie details
                            movie_id = movie.movie_id
                            poster = fetch_poster(movie_id)
                            details = get_movie_details(movie_id)
                            trailer = fetch_trailer(movie_id)
                            
                            # Display poster
                            st.image(poster, use_container_width=True)
                            
                            # Display title and metadata
                            st.markdown(f'<p class="movie-title">{movie.title}</p>', unsafe_allow_html=True)
                            st.markdown(f'<p class="movie-meta">⭐ {details["rating"]} | 📅 {details["year"]}</p>', unsafe_allow_html=True)
                            
                            # Overview in expander
                            with st.expander("Overview"):
                                st.markdown(details['overview'])
                            
                            # Trailer in expander if available
                            if trailer:
                                with st.expander("Watch Trailer"):
                                    st.markdown(f'<iframe width="100%" height="215" src="{trailer}" '
                                               f'frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; '
                                               f'gyroscope; picture-in-picture" allowfullscreen></iframe>', 
                                               unsafe_allow_html=True)
                            
                            st.markdown('</div>', unsafe_allow_html=True)
else:
    # Display trending movies when no search is performed
    trending = fetch_trending_movies()
    
    if trending:
        st.subheader("📈 Trending This Week")
        
        # Get screen width and determine column count
        screen_width = get_screen_width()
        num_cols = get_column_count(screen_width)
        
        # Create dynamic columns based on screen size
        cols = st.columns(num_cols)
        
        for i, movie in enumerate(trending):
            col_index = i % num_cols
            
            with cols[col_index]:
                with st.container():
                    st.markdown('<div class="movie-card">', unsafe_allow_html=True)
                    
                    # Display poster
                    poster_path = movie.get('poster_path')
                    if poster_path:
                        poster_url = f"https://image.tmdb.org/t/p/w500/{poster_path}"
                    else:
                        poster_url = "https://via.placeholder.com/500x750?text=Poster+Not+Available"
                    
                    st.image(poster_url, use_container_width=True)
                    
                    # Display title and metadata
                    title = movie.get('title', 'Unknown Title')
                    release_date = movie.get('release_date', '')
                    year = release_date[:4] if release_date else 'N/A'
                    rating = movie.get('vote_average', 'N/A')
                    
                    st.markdown(f'<p class="movie-title">{title}</p>', unsafe_allow_html=True)
                    st.markdown(f'<p class="movie-meta">⭐ {rating} | 📅 {year}</p>', unsafe_allow_html=True)
                    
                    # Overview in expander
                    with st.expander("Overview"):
                        overview = movie.get('overview', 'No overview available')
                        st.markdown(overview)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("👋 Welcome to CineMatch! Search for a movie above to get personalized recommendations.")
        
        st.markdown("""<div style="margin: 2rem 0;">
            ### How to use CineMatch:
            1. Search for a movie you like in the search box
            2. Click "Get Recommendations" to see similar movies
            3. Explore movie details, trailers, and overviews
            4. Use sidebar filters to refine your search
        </div>""")

# Footer section
st.markdown("""<div style="text-align: center; margin-top: 2rem; padding: 1rem; background-color: rgba(49, 51, 63, 0.7); border-radius: 10px;">
    <p>🎬 CineMatch: Movie Recommendation System | Powered by TMDB API | Made with Streamlit</p>
    <p>© 2025 | Last updated: April 22, 2025</p>
</div>""", unsafe_allow_html=True)