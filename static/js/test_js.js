import kmeans from './kmeans.js';

let data = [[1,1,1],
            [1,2,1],
            [-1, -1, -1],
            [-1, -1, -1.5],
            [-1, -1, -1.5]];

let result = kmeans(data, 2)
console.log(result);