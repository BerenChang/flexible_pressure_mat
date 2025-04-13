from flask import Flask, jsonify, render_template
# import serial
import threading
import numpy as np
import time

app = Flask(__name__)

# Serial Configuration
# SERIAL_PORT = "/dev/ttyUSB0"
# BAUD_RATE = 9600

# ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)

# Data Buffer: 9x9 Matrix (initially all zeros)
data_buffer = [255, 254, 254, 255]
count = 0

def load_csv(file_name):
    """
    load the test csv files
    """
    raw_data = np.genfromtxt(file_name, delimiter=',')
    matrix_data = np.empty([len(raw_data)-1,9,9])

    for i in range(len(raw_data)-1):
        matrix_data[i,:,:] = raw_data[i+1].reshape([9,9])
    
    return matrix_data

def get_sparse(matrix: np.array):
    """
    Input: matrix: 2d numpy array
    Output: numpy array of [x, y, value], where value = matrix[x, y]
    """
    # Get indices of nonzero elements
    x, y = np.nonzero(matrix)

    # Get corresponding values
    values = matrix[x, y]

    # Stack into [x, y, value] format
    return np.column_stack((x, y, values))

# Read Serial Data in Background
def read_serial():
    global data_buffer, count

    file_name = 'C:\\Users\\ROG\\Documents\\pressure_mat\\data_saver\\calibrated_3.csv'
    matrix_data = load_csv(file_name)

    while True:
        # Generate new data in real-time
        if count == 850:
            count = 0
        else:
            count += 1
        X = np.squeeze(matrix_data[count,:,:])
        X[(X < 190)] = 0
        X = get_sparse(X)
        data_buffer = X.tolist()
        time.sleep(0.05)
        

# Start Serial Thread
threading.Thread(target=read_serial, daemon=True).start()

# API to Serve Matrix Data
@app.route('/data')
def data():
    # global data_buffer
    return jsonify(data_buffer) 

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
