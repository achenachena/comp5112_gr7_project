// Utility functions
function showStatus(elementId, message, type) {
    const element = document.getElementById(elementId);
    element.innerHTML = message;
    element.className = 'status ' + type;
}

function showLoading(elementId) {
    showStatus(elementId, '<span class="loading-spinner"></span>Loading...', 'loading');
}

// Data loading
async function loadData() {
    const limit = document.getElementById('limit').value;
    const dataset = document.getElementById('datasetSelect').value;
    showLoading('dataStatus');
    
    try {
        const response = await fetch('/api/load_data', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                limit: limit ? parseInt(limit) : null,
                dataset: dataset
            })
        });
        
        const result = await response.json();
        if (result.success) {
            const datasetName = dataset === 'api' ? 'API' : 'Social Media';
            showStatus('dataStatus', `Successfully loaded ${result.count} products from ${datasetName} dataset`, 'success');
            document.getElementById('dataInfo').innerHTML = `
                <p><strong>Dataset:</strong> ${datasetName}</p>
                <p><strong>Products loaded:</strong> ${result.count.toLocaleString()}</p>
                <p><strong>Database:</strong> ${result.db_info.database_type}</p>
            `;
        } else {
            showStatus('dataStatus', `Error: ${result.error}`, 'error');
        }
    } catch (error) {
        showStatus('dataStatus', `Error: ${error.message}`, 'error');
    }
}

// Comparison
async function runComparison() {
    showLoading('comparisonStatus');
    document.getElementById('compareBtn').disabled = true;
    
    try {
        const response = await fetch('/api/run_comparison', { method: 'POST' });
        const result = await response.json();
        
        if (result.success) {
            showStatus('comparisonStatus', `Comparison completed in ${result.time.toFixed(2)}s`, 'success');
            displayResults(result.results);
        } else {
            showStatus('comparisonStatus', `Error: ${result.error}`, 'error');
        }
    } catch (error) {
        showStatus('comparisonStatus', `Error: ${error.message}`, 'error');
    } finally {
        document.getElementById('compareBtn').disabled = false;
    }
}

// Search
async function search() {
    const query = document.getElementById('searchQuery').value.trim();
    if (!query) return;
    
    showStatus('searchResults', '<span class="loading-spinner"></span>Searching...', 'loading');
    
    try {
        const response = await fetch('/api/search', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: query })
        });
        
        const result = await response.json();
        if (result.success) {
            displaySearchResults(result.results, query);
        } else {
            showStatus('searchResults', `Error: ${result.error}`, 'error');
        }
    } catch (error) {
        showStatus('searchResults', `Error: ${error.message}`, 'error');
    }
}

// Display search results
function displaySearchResults(results, query) {
    const html = `
        <div class="results">
            <h4>Search Results for "${query}"</h4>
            <div class="metrics">
                ${Object.entries(results).map(([algorithm, data]) => `
                    <div class="metric-card">
                        <h5>${algorithm.replace('_', ' ').toUpperCase()}</h5>
                        <p><strong>Results:</strong> ${data.results.length}</p>
                        <p><strong>Time:</strong> ${data.search_time.toFixed(4)}s</p>
                        ${data.results.slice(0, 3).map(item => `
                            <p style="margin: 5px 0; font-size: 0.9em;">
                                <strong>${item.title}</strong><br>
                                <small>${item.description || 'No description'}</small>
                            </p>
                        `).join('')}
                    </div>
                `).join('')}
            </div>
        </div>
    `;
    document.getElementById('searchResults').innerHTML = html;
}

// Display comparison results
function displayResults(results) {
    const html = `
        <div class="results">
            <h4>Performance Summary</h4>
            <p><strong>Queries:</strong> ${results.total_queries} | <strong>Products:</strong> ${results.total_products.toLocaleString()} | <strong>Time:</strong> ${results.total_time.toFixed(2)}s</p>
            
            <div class="metrics">
                ${Object.entries(results.algorithms).map(([name, data]) => `
                    <div class="metric-card">
                        <h5>${name.replace('_', ' ').toUpperCase()}</h5>
                        <p><strong>MAP:</strong> ${data.metrics.map.toFixed(4)}</p>
                        <p><strong>F1@5:</strong> ${data.metrics['f1@5'].toFixed(4)}</p>
                        <p><strong>NDCG@10:</strong> ${data.metrics['ndcg@10'].toFixed(4)}</p>
                        <p><strong>Avg Time:</strong> ${data.avg_search_time.toFixed(4)}s</p>
                    </div>
                `).join('')}
            </div>
            
            <h4>Performance Charts</h4>
            <div class="charts-container">
                <div class="chart-card">
                    <div class="chart-title">F1-Score Trends (K=1 to 10)</div>
                    <div class="chart-container" id="f1Chart"></div>
                </div>
                <div class="chart-card">
                    <div class="chart-title">Precision Trends (K=1 to 10)</div>
                    <div class="chart-container" id="precisionChart"></div>
                </div>
                <div class="chart-card">
                    <div class="chart-title">Recall Trends (K=1 to 10)</div>
                    <div class="chart-container" id="recallChart"></div>
                </div>
                <div class="chart-card">
                    <div class="chart-title">NDCG Trends (K=1 to 10)</div>
                    <div class="chart-container" id="ndcgChart"></div>
                </div>
            </div>
            
            <div class="detailed-metrics">
                <h4>Detailed Metrics Table</h4>
                <table class="metrics-table">
                    <thead>
                        <tr>
                            <th>Algorithm</th>
                            <th>MAP</th>
                            <th>MRR</th>
                            <th>Precision@1</th>
                            <th>Recall@1</th>
                            <th>F1@1</th>
                            <th>Precision@3</th>
                            <th>Recall@3</th>
                            <th>F1@3</th>
                            <th>Precision@5</th>
                            <th>Recall@5</th>
                            <th>F1@5</th>
                            <th>NDCG@10</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${Object.entries(results.algorithms).map(([name, data]) => `
                            <tr>
                                <td><strong>${name.replace('_', ' ').toUpperCase()}</strong></td>
                                <td>${data.metrics.map.toFixed(4)}</td>
                                <td>${data.metrics.mrr.toFixed(4)}</td>
                                <td>${(data.metrics['precision@1'] || 0).toFixed(4)}</td>
                                <td>${(data.metrics['recall@1'] || 0).toFixed(4)}</td>
                                <td>${(data.metrics['f1@1'] || 0).toFixed(4)}</td>
                                <td>${(data.metrics['precision@3'] || 0).toFixed(4)}</td>
                                <td>${(data.metrics['recall@3'] || 0).toFixed(4)}</td>
                                <td>${(data.metrics['f1@3'] || 0).toFixed(4)}</td>
                                <td>${(data.metrics['precision@5'] || 0).toFixed(4)}</td>
                                <td>${(data.metrics['recall@5'] || 0).toFixed(4)}</td>
                                <td>${(data.metrics['f1@5'] || 0).toFixed(4)}</td>
                                <td>${(data.metrics['ndcg@10'] || 0).toFixed(4)}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
            
            <h4>Best Performing Algorithms</h4>
            <ul>
                ${Object.entries(results.summary.best_algorithms).map(([metric, info]) => `
                    <li><strong>${metric.toUpperCase()}:</strong> ${info.algorithm} (${info.score.toFixed(4)})</li>
                `).join('')}
            </ul>
        </div>
    `;
    document.getElementById('comparisonResults').innerHTML = html;
    
    // Generate charts after DOM is updated
    setTimeout(() => generateLineCharts(results), 100);
}

// Generate beautiful line charts
function generateLineCharts(results) {
    const algorithms = Object.keys(results.algorithms);
    const colors = ['#667eea', '#f093fb', '#4facfe', '#43e97b'];
    
    // F1-Score Chart
    generateLineChart('f1Chart', 'F1-Score Trends', algorithms, 
        algorithms.map(name => {
            const data = [];
            for (let k = 1; k <= 10; k++) {
                data.push(results.algorithms[name].metrics[`f1@${k}`] || 0);
            }
            return data;
        }), colors, 'F1-Score');
    
    // Precision Chart
    generateLineChart('precisionChart', 'Precision Trends', algorithms, 
        algorithms.map(name => {
            const data = [];
            for (let k = 1; k <= 10; k++) {
                data.push(results.algorithms[name].metrics[`precision@${k}`] || 0);
            }
            return data;
        }), colors, 'Precision');
    
    // Recall Chart
    generateLineChart('recallChart', 'Recall Trends', algorithms, 
        algorithms.map(name => {
            const data = [];
            for (let k = 1; k <= 10; k++) {
                data.push(results.algorithms[name].metrics[`recall@${k}`] || 0);
            }
            return data;
        }), colors, 'Recall');
    
    // NDCG Chart
    generateLineChart('ndcgChart', 'NDCG Trends', algorithms, 
        algorithms.map(name => {
            const data = [];
            for (let k = 1; k <= 10; k++) {
                data.push(results.algorithms[name].metrics[`ndcg@${k}`] || 0);
            }
            return data;
        }), colors, 'NDCG');
}

// Create beautiful line chart
function generateLineChart(containerId, title, labels, dataSeries, colors, yAxisLabel) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    const width = container.offsetWidth - 40;
    const height = 300;
    const margin = { top: 20, right: 60, bottom: 40, left: 60 };
    
    const xScale = (width - margin.left - margin.right) / 9; // K values 1-10
    const maxValue = Math.max(...dataSeries.flat());
    const yScale = (height - margin.top - margin.bottom) / (maxValue || 1);
    
    let svg = d3.select(container)
        .append('svg')
        .attr('width', width)
        .attr('height', height)
        .attr('class', 'chart-svg');
    
    // Add grid lines
    svg.selectAll('.grid-h')
        .data(d3.range(0, maxValue + 0.1, maxValue / 5))
        .enter().append('line')
        .attr('class', 'chart-grid')
        .attr('x1', margin.left)
        .attr('x2', width - margin.right)
        .attr('y1', d => height - margin.bottom - (d * yScale))
        .attr('y2', d => height - margin.bottom - (d * yScale));
    
    // Add grid lines for K values
    svg.selectAll('.grid-v')
        .data(d3.range(1, 11))
        .enter().append('line')
        .attr('class', 'chart-grid')
        .attr('x1', d => margin.left + (d - 1) * xScale)
        .attr('x2', d => margin.left + (d - 1) * xScale)
        .attr('y1', margin.top)
        .attr('y2', height - margin.bottom);
    
    // Create line generator
    const line = d3.line()
        .x((d, i) => margin.left + i * xScale)
        .y(d => height - margin.bottom - (d * yScale))
        .curve(d3.curveMonotoneX);
    
    // Add lines for each algorithm
    dataSeries.forEach((data, index) => {
        const path = svg.append('path')
            .datum(data)
            .attr('class', 'chart-line')
            .attr('d', line)
            .attr('stroke', colors[index % colors.length])
            .attr('stroke-width', 3)
            .attr('fill', 'none');
        
        // Add animated drawing effect
        const totalLength = path.node().getTotalLength();
        path
            .attr('stroke-dasharray', totalLength + ' ' + totalLength)
            .attr('stroke-dashoffset', totalLength)
            .transition()
            .duration(1500)
            .ease(d3.easeLinear)
            .attr('stroke-dashoffset', 0);
        
        // Add points
        svg.selectAll(`.point-${index}`)
            .data(data)
            .enter().append('circle')
            .attr('class', 'chart-point')
            .attr('cx', (d, i) => margin.left + i * xScale)
            .attr('cy', d => height - margin.bottom - (d * yScale))
            .attr('r', 0)
            .attr('fill', colors[index % colors.length])
            .transition()
            .delay(1500)
            .duration(500)
            .attr('r', 4);
        
        // Add tooltips
        svg.selectAll(`.point-${index}`)
            .append('title')
            .text((d, i) => `${labels[index]}: K=${i+1}, ${yAxisLabel}=${d.toFixed(4)}`);
    });
    
    // Add axes
    svg.append('line')
        .attr('class', 'chart-axis')
        .attr('x1', margin.left)
        .attr('x2', width - margin.right)
        .attr('y1', height - margin.bottom)
        .attr('y2', height - margin.bottom);
    
    svg.append('line')
        .attr('class', 'chart-axis')
        .attr('x1', margin.left)
        .attr('x2', margin.left)
        .attr('y1', margin.top)
        .attr('y2', height - margin.bottom);
    
    // Add axis labels
    svg.selectAll('.x-label')
        .data(d3.range(1, 11))
        .enter().append('text')
        .attr('class', 'chart-label')
        .attr('x', d => margin.left + (d - 1) * xScale)
        .attr('y', height - margin.bottom + 20)
        .text(d => d);
    
    svg.selectAll('.y-label')
        .data(d3.range(0, maxValue + 0.1, maxValue / 5))
        .enter().append('text')
        .attr('class', 'chart-label')
        .attr('x', margin.left - 10)
        .attr('y', d => height - margin.bottom - (d * yScale) + 5)
        .text(d => d.toFixed(2));
    
    // Add axis titles
    svg.append('text')
        .attr('class', 'chart-title-text')
        .attr('x', width / 2)
        .attr('y', height - 10)
        .text('K Values');
    
    svg.append('text')
        .attr('class', 'chart-title-text')
        .attr('transform', 'rotate(-90)')
        .attr('x', -height / 2)
        .attr('y', 15)
        .text(yAxisLabel);
    
    // Add legend
    const legend = svg.append('g')
        .attr('transform', `translate(${width - margin.right + 10}, ${margin.top})`);
    
    labels.forEach((label, index) => {
        const legendItem = legend.append('g')
            .attr('transform', `translate(0, ${index * 20})`);
        
        legendItem.append('line')
            .attr('x1', 0)
            .attr('x2', 15)
            .attr('y1', 0)
            .attr('y2', 0)
            .attr('stroke', colors[index % colors.length])
            .attr('stroke-width', 3);
        
        legendItem.append('text')
            .attr('class', 'chart-legend')
            .attr('x', 20)
            .attr('y', 5)
            .text(label.replace('_', ' ').toUpperCase());
    });
}

// Initialize page
window.onload = function() {
    loadData();
};
