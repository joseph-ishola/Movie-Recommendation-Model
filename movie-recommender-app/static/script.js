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
    const errorMessage = document.getElementById('errorMessage');

    // Initialize model button click handler
    if (initializeButton) {
        initializeButton.addEventListener('click', function() {
            // Show progress indicators
            initializeButton.disabled = true;
            initProgress.style.display = 'block';
            
            // Simulate progress updates
            let progress = 0;
            const progressInterval = setInterval(function() {
                progress += Math.random() * 3;
                if (progress > 95) {
                    clearInterval(progressInterval);
                    progress = 98;
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
                
                // Check if we got multiple matches
                if (data.status === 'multiple_matches') {
                    // Show multiple matches selection UI
                    showMultipleMatchesUI(data.matches, movieTitle);
                    return;
                }

                // Check if no matching movie was found
                if (data.status === 'no_match') {
                    showNoMatchUI(data.message, data.similar_titles, movieTitle);
                    return;
                }
                
                // Display recommendations
                displayRecommendations(data);
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

    // Function to display multiple matches selection UI
    function showMultipleMatchesUI(matches, movieTitle) {
        // Create HTML for movie selection
        const matchesHTML = `
            <div class="card shadow-sm mb-4">
                <div class="card-header bg-primary text-white">
                    <h3 class="card-title mb-0">Multiple Matches Found</h3>
                </div>
                <div class="card-body">
                    <p>We found multiple movies with the title "${movieTitle}". Please select which one you meant:</p>
                    <div class="list-group mb-3">
                        ${matches.map(match => `
                            <button type="button" class="list-group-item list-group-item-action movie-choice"
                                    data-index="${match.index}" data-title="${match.title}">
                                ${match.title} (${match.release_date})
                            </button>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;
        
        // Display the matches UI
        recommendationsContainer.innerHTML = matchesHTML;
        recommendationsContainer.style.display = 'block';
        
        // Add event listeners to the movie choices
        document.querySelectorAll('.movie-choice').forEach(button => {
            button.addEventListener('click', function() {
                const choiceIndex = this.getAttribute('data-index');
                const movieTitle = this.getAttribute('data-title');
                
                // Show loading again
                recommendationsContainer.style.display = 'none';
                loadingIndicator.style.display = 'block';
                
                // Create form data with the chosen index
                const formData = new FormData();
                formData.append('movie_title', movieTitle);
                formData.append('choice_index', choiceIndex);
                
                // Send request with the chosen movie
                fetch('/recommend', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    loadingIndicator.style.display = 'none';
                    
                    if (data.status === 'error') {
                        errorMessage.textContent = data.message;
                        errorMessage.style.display = 'block';
                        return;
                    }
                    
                    // Display recommendations
                    displayRecommendations(data);
                })
                .catch(error => {
                    loadingIndicator.style.display = 'none';
                    errorMessage.textContent = 'An error occurred while connecting to the server.';
                    errorMessage.style.display = 'block';
                    console.error('Error:', error);
                });
            });
        });
    }

    // Function to display a UI when no match is found
    function showNoMatchUI(message, similarTitles, searchedTitle) {
        let similarTitlesHTML = '';
        
        if (similarTitles && similarTitles.length > 0) {
            similarTitlesHTML = `
                <p class="mb-3">Did you mean one of these?</p>
                <div class="list-group mb-4">
                    ${similarTitles.map(movie => `
                        <button type="button" class="list-group-item list-group-item-action similar-title d-flex justify-content-between align-items-center"
                                data-title="${movie.title}">
                            <span><i class="bi bi-film me-2"></i>${movie.title} (${movie.release_date})</span>
                            <i class="bi bi-chevron-right"></i>
                        </button>
                    `).join('')}
                </div>
            `;
        } else {
            similarTitlesHTML = `<p class="mb-4">No similar titles were found in our database.</p>`;
        }
        
        const noMatchHTML = `
            <div class="card shadow-sm mb-4 fade-in">
                <div class="card-header bg-warning text-dark">
                    <div class="d-flex align-items-center">
                        <i class="bi bi-exclamation-triangle-fill me-2"></i>
                        <h3 class="card-title mb-0">Movie Not Found</h3>
                    </div>
                </div>
                <div class="card-body">
                    <div class="text-center my-4">
                        <i class="bi bi-film-slash" style="font-size: 4rem; color: #ccc;"></i>
                    </div>
                    <p class="text-center">${message}</p>
                    ${similarTitlesHTML}
                    <div class="text-center">
                        <button class="btn btn-primary" id="newSearchBtn">
                            <i class="bi bi-search me-2"></i>Try Another Search
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        recommendationsContainer.innerHTML = noMatchHTML;
        recommendationsContainer.style.display = 'block';
        
        // Add event listeners to the similar title buttons
        document.querySelectorAll('.similar-title').forEach(button => {
            button.addEventListener('click', function() {
                const movieTitle = this.getAttribute('data-title');
                document.getElementById('movieTitle').value = movieTitle;
                document.getElementById('recommendForm').dispatchEvent(new Event('submit'));
            });
        });
        
        // Add event listener to the new search button
        document.getElementById('newSearchBtn').addEventListener('click', function() {
            document.getElementById('movieTitle').value = '';
            document.getElementById('movieTitle').focus();
            resultsDiv.style.display = 'none';
        });
    }

    // Function to display recommendations
    function displayRecommendations(data) {
        console.log("Displaying recommendations:", data);
        
        // Format the recommendations table rows
        const tableRows = data.recommendations.map(rec => {
            // Format genres as a comma-separated list
            const genres = Array.isArray(rec.genre_names) ? rec.genre_names.join(', ') : rec.genre_names;
            
            // Format similarity as percentage
            const similarity = (rec.similarity_score * 100).toFixed(1) + '%';
            
            return `
            <tr>
                <td><strong>${rec.title}</strong></td>
                <td>${genres}</td>
                <td>
                    <div class="d-flex align-items-center">
                        <div class="text-warning me-2"><i class="bi bi-star-fill"></i></div>
                        <div>${rec.vote_average.toFixed(1)}</div>
                    </div>
                </td>
                <td>${rec.release_date}</td>
                <td>
                    <div class="progress" style="height: 8px;">
                        <div class="progress-bar" role="progressbar" style="width: ${similarity};" 
                             aria-valuenow="${rec.similarity_score * 100}" aria-valuemin="0" aria-valuemax="100"></div>
                    </div>
                    <small class="text-muted">${similarity}</small>
                </td>
            </tr>
            `;
        }).join('');
        
        // Create the full HTML structure for recommendations
        const recommendationsHTML = `
            <div class="card shadow-sm mb-4 fade-in">
                <div class="card-header bg-primary text-white">
                    <div class="d-flex align-items-center">
                        <i class="bi bi-list-stars me-2"></i>
                        <h3 class="card-title mb-0">Recommended Movies</h3>
                    </div>
                </div>
                <div class="card-body">
                    <div class="table-responsive">
                        <table class="table table-hover">
                            <thead>
                                <tr>
                                    <th>Title</th>
                                    <th>Genres</th>
                                    <th>Rating</th>
                                    <th>Release Date</th>
                                    <th>Similarity</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${tableRows}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
    
            <div class="row">
                <div class="col-md-6 mb-4">
                    <div class="card shadow-sm fade-in">
                        <div class="card-header bg-primary text-white">
                            <div class="d-flex align-items-center">
                                <i class="bi bi-bar-chart-fill me-2"></i>
                                <h3 class="card-title mb-0">Similarity Chart</h3>
                            </div>
                        </div>
                        <div class="card-body text-center">
                            <img src="${data.chart_path}?t=${new Date().getTime()}" class="img-fluid rounded" alt="Similarity chart">
                        </div>
                    </div>
                </div>
                <div class="col-md-6 mb-4">
                    <div class="card shadow-sm fade-in">
                        <div class="card-header bg-primary text-white">
                            <div class="d-flex align-items-center">
                                <i class="bi bi-cloud-fill me-2"></i>
                                <h3 class="card-title mb-0">Themes & Topics</h3>
                            </div>
                        </div>
                        <div class="card-body text-center">
                            <img src="${data.wordcloud_path}?t=${new Date().getTime()}" class="img-fluid rounded" alt="Word cloud">
                        </div>
                    </div>
                </div>
            </div>
    
            <div class="card shadow-sm fade-in">
                <div class="card-header bg-primary text-white">
                    <div class="d-flex align-items-center">
                        <i class="bi bi-graph-up me-2"></i>
                        <h3 class="card-title mb-0">Evaluation Metrics</h3>
                    </div>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-4">
                            <div class="card text-center mb-3 mb-md-0">
                                <div class="card-body">
                                    <i class="bi bi-intersect text-primary mb-3" style="font-size: 2rem;"></i>
                                    <h5 class="card-title">Genre Overlap</h5>
                                    <h2 class="display-4">${data.metrics.average_genre_overlap.toFixed(1)}%</h2>
                                    <p class="text-muted">Shared genres between movies</p>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="card text-center mb-3 mb-md-0">
                                <div class="card-body">
                                    <i class="bi bi-star-half text-primary mb-3" style="font-size: 2rem;"></i>
                                    <h5 class="card-title">Rating Similarity</h5>
                                    <h2 class="display-4">${data.metrics.average_rating_difference.toFixed(2)}</h2>
                                    <p class="text-muted">Avg. rating difference (lower is better)</p>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="card text-center">
                                <div class="card-body">
                                    <i class="bi bi-shuffle text-primary mb-3" style="font-size: 2rem;"></i>
                                    <h5 class="card-title">Content Relevance</h5>
                                    <h2 class="display-4">${data.metrics.average_content_relevance.toFixed(1)}%</h2>
                                    <p class="text-muted">Thematic similarity</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Update the recommendations container with the generated HTML
        recommendationsContainer.innerHTML = recommendationsHTML;
        recommendationsContainer.style.display = 'block';
    }

    // Add event listener for the back to search button
    // This button is shown when no match is found or multiple matches are found
    if (document.getElementById('backToSearch')) {
        document.getElementById('backToSearch').addEventListener('click', function() {
            resultsDiv.style.display = 'none';
            document.getElementById('movieTitle').value = '';
        });
    }
});