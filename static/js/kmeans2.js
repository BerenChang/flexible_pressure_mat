function kmeans(data, k, maxIterations = 100) {
    // Initialize centroids randomly from data points
    let centroids = [];
    for (let i = 0; i < k; i++) {
        const randomIndex = Math.floor(Math.random() * data.length);
        centroids.push([...data[randomIndex]]);
    }

    let clusters = [];
    let prevCentroids = new Array(k).fill(null);
    let iterations = 0;

    // Loop until convergence or maxIterations
    while (iterations < maxIterations) {
        clusters = new Array(k).fill().map(() => []);

        // Step 1: Assign each data point to the nearest centroid
        for (const point of data) {
            let distances = centroids.map(centroid => {
                return Math.sqrt(centroid.reduce((sum, value, idx) => sum + Math.pow(value - point[idx], 2), 0));
            });
            const closestCentroidIndex = distances.indexOf(Math.min(...distances));
            clusters[closestCentroidIndex].push(point);
        }

        // Step 2: Update centroids
        prevCentroids = JSON.parse(JSON.stringify(centroids));
        centroids = centroids.map((centroid, idx) => {
            if (clusters[idx].length === 0) return centroid; // Skip if no points in cluster
            const newCentroid = centroid.map((_, i) => {
                return clusters[idx].reduce((sum, point) => sum + point[i], 0) / clusters[idx].length;
            });
            return newCentroid;
        });

        // Step 3: Check for convergence (if centroids have stopped changing)
        if (JSON.stringify(centroids) === JSON.stringify(prevCentroids)) break;

        iterations++;
    }

    return { centroids, clusters };
}

// // Example data points (2D coordinates)
// const data = [
//     [1, 2], [1, 3], [2, 3], [6, 6], [7, 8], [8, 7]
// ];

// // Number of clusters (k)
// const k = 2;

// // Run K-means algorithm
// const result = kMeans(data, k);

// // Output the results
// console.log('Centroids:', result.centroids);
// console.log('Clusters:', result.clusters);
