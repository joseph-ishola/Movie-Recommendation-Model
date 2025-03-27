// static/script.js
document.addEventListener('DOMContentLoaded', function() {
    // Elements for model initialization
    const initializationSection = document.getElementById('initializationSection');
    const initializeButton = document.getElementById('initializeButton');
    const initProgress = document.getElementById('initProgress');
    const progressBar = document.getElementById('progressBar');
    const initStatus = document.getElementById('initStatus');
    const searchSection = document.getElementById('searchSection');
    
    // Elements for recommendations
    const recommendForm = document.getElementById('recommendForm');
    const resultsDiv = document.getElementById('results');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const recommendationsContainer = document.getElementById('recommendationsContainer');
    const recommendationsTable = document.getElementById('recommendationsTable');
    const errorMessage = document.getElementById('errorMessage');
    const similarityChart = document.getElementById('similarityChart');
    const wordcloud = document.getElementById('wordcloud');
    const metricsContainer = document.getElementById('metricsContainer');

    // Initialize model button click handler
    if (initializeButton) {
        initializeButton.addEventListener('click', function() {
            // Show progress indicators
            initializeButton.disabled = true;
            initProgress.style.display = 'block';
            
            // Simulate progress updates (since we can't get real-time updates easily)
            let progress = 0;
            const progressInterval = setInterval(function() {
                progress += Math.random() * 5;
                if (progress > 95) {
                    clearInterval(progressInterval);
                    progress = 95; // Cap at 95% until we get server confirmation
                }
                progressBar.style.width = progress + '%';
                initStatus.textContent = 'Initializing model components... ' + Math.floor(progress) + '%';
            }, 1000);
            
            // Call the initialization endpoint
            fetch('/initialize')
                .then(response => response.json())
                .then(data => {
                    clearInterval(progressInterval);
                    
                    if (data.status === 'success') {
                        // Complete the progress bar
                        progressBar.style.width = '100%';
                        initStatus.textContent = 'Initialization complete!';
                        
                        // After a short delay, show the search section
                        setTimeout(function() {
                            initializationSection.style.display = 'none';
                            searchSection.style.display = 'block';
                        }, 1500);
                    } else {
                        // Show error
                        initStatus.textContent = 'Error: ' + data.message;
                        initStatus.classList.add('text-danger');
                        initializeButton.disabled = false;
                    }
                })
                .catch(error => {
                    clearInterval(progressInterval);
                    initStatus.textContent = 'Error connecting to server. Please try again.';
                    initStatus.classList.add('text-danger');
                    initializeButton.disabled = false;
                    console.error('Error:', error);
                });
        });
    }

    // Recommendation form submit handler
    if (recommendForm) {
        recommendForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Show results section with loading indicator
            resultsDiv.style.display = 'block';
            loadingIndicator.style.display = 'block';
            recommendationsContainer.style.display = 'none';
            errorMessage.style.display = 'none';
            
            // Get the movie title
            const movieTitle = document.getElementById('movieTitle').value;
            
            // Create form data
            const formData = new FormData();
            formData.append('movie_title', movieTitle);
            
            // Send request to the server
            fetch('/recommend', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                // Hide loading indicator
                loadingIndicator.style.display = 'none';
                
                // Check if there was an error
                if (data.status === 'error') {
                    errorMessage.textContent = data.message;
                    errorMessage.style.display = 'block';
                    return;
                }
                
                // Display recommendations
                recommendationsContainer.style.display = 'block';
                
                // Set images with cache-busting parameter
                const timestamp = new Date().getTime();
                similarityChart.src = data.chart_path + '?t=' + timestamp;
                wordcloud.src = data.wordcloud_path + '?t=' + timestamp;
                
                // Clear previous recommendations
                recommendationsTable.innerHTML = '';
                
                // Add recommendations to table
                data.recommendations.forEach(rec => {
                    const row = document.createElement('tr');
                    
                    // Format genres as a comma-separated list
                    const genres = Array.isArray(rec.genre_names) ? rec.genre_names.join(', ') : rec.genre_names;
                    
                    // Format similarity as percentage
                    const similarity = (rec.similarity_score * 100).toFixed(1) + '%';
                    
                    // Format the row content
                    row.innerHTML = `
                        <td>${rec.title}</td>
                        <td>${genres}</td>
                        <td>${rec.vote_average.toFixed(1)}</td>
                        <td>${rec.release_date}</td>
                        <td>${similarity}</td>
                    `;
                    
                    recommendationsTable.appendChild(row);
                });
                
                // Display metrics
                metricsContainer.innerHTML = `
                    <div class="col-md-4">
                        <div class="card text-center mb-3 mb-md-0">
                            <div class="card-body">
                                <h5 class="card-title">Genre Overlap</h5>
                                <h2 class="display-4">${data.metrics.average_genre_overlap.toFixed(1)}%</h2>
                                <p class="text-muted">Shared genres between movies</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card text-center mb-3 mb-md-0">
                            <div class="card-body">
                                <h5 class="card-title">Rating Similarity</h5>
                                <h2 class="display-4">${data.metrics.average_rating_difference.toFixed(2)}</h2>
                                <p class="text-muted">Avg. rating difference (lower is better)</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card text-center">
                            <div class="card-body">
                                <h5 class="card-title">Content Relevance</h5>
                                <h2 class="display-4">${data.metrics.average_content_relevance.toFixed(1)}%</h2>
                                <p class="text-muted">Thematic similarity</p>
                            </div>
                        </div>
                    </div>
                `;
            })
            .catch(error => {
                // Hide loading indicator and show error
                loadingIndicator.style.display = 'none';
                errorMessage.textContent = 'An error occurred while connecting to the server. Please try again.';
                errorMessage.style.display = 'block';
                console.error('Error:', error);
            });
        });
    }
});