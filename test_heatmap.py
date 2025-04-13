from flask import Flask, jsonify, render_template
import serial
import threading
import numpy as np
import time

app = Flask(__name__)

# Serial Configuration
SERIAL_PORT = "/dev/ttyACM0"
BAUD_RATE = 115200
START_READING_COMMAND = "start_reading"
VERIFICATION_WIDTH = 4
ROW_WIDTH = 28
MAT_SIZE = 1568
VERIFICATION_SEQUENCE = [255, 254, 254, 255]

ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)

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

# # Read Serial Data in Background
# def read_serial():
#     global data_buffer, count

#     # file_name = 'C:\\Users\\ROG\\Documents\\pressure_mat\\data_saver\\calibrated_3.csv'
#     # matrix_data = load_csv(file_name)

#     while True:
#         # Generate new data in real-time
#         # if count == 850:
#         #     count = 0
#         # else:
#         #     count += 1
#         X = np.squeeze(matrix_data[count,:,:])
#         X[(X < 190)] = 0
#         X = get_sparse(X)
#         data_buffer = X.tolist()
#         # print(len(data_buffer))
#         time.sleep(0.05)


def mat_list_to_array_subsize(mat_as_list: list, width: int, height: int):
    """
    Converts a 1d python list (presumably the mat) to a 2D numpy array
    """

    array = np.empty((width, height), dtype=np.uint8)
    
    for i in range(height):
        array[i, :] = mat_as_list[i*ROW_WIDTH : i*ROW_WIDTH+width]

    return array


def read_serial():
    global data_buffer
    # with serial.Serial(port=SERIAL_PORT, baudrate=BAUD_RATE, timeout=10) as ser:
    # ser.set_buffer_size(rx_size = 1700, tx_size = 1700)
    
    # send the message to start reading the mat
    ser.write((START_READING_COMMAND + '\n').encode('utf-8'))
    polling = True

    # prev_sample_time_ns = time.time_ns()

    # continually poll serial for new mat data
    while polling:
        # mat data is transmitted as raw bytes
        bytes = ser.read(VERIFICATION_WIDTH + MAT_SIZE)
        if bytes == b'':
            print("Serial timed out!")
            continue
        
        flat_mat = [x for x in bytes]
        # print(flat_mat)

        # if VERIFICATION_SEQUENCE is not flat_mat[-4:]:
        #     ser.read(1)

        # ensure that the verifiation message was aligned
        for ver, val in zip(VERIFICATION_SEQUENCE, flat_mat[-4:]):
            if not (ver == val):
                # transmission_errors += 1
                print("====TRANSMISSION ERROR OCCURED! FIXING!!!====")
                # a verification error has occured, probably because the fifo filled up
                # to resolve it, simply wipe the fifo and read until the next verification sequence
                ser.reset_input_buffer()
                hist = np.zeros(VERIFICATION_WIDTH, dtype=np.uint8)

                # wait for verification sequence to be found, proving data stream is still intact
                while(not np.array_equal(hist, np.asarray(VERIFICATION_SEQUENCE, dtype=np.uint8))):
                    hist = np.roll(hist, -1)
                    hist[-1] = int.from_bytes(ser.read(1), "big")

                break   # do not false positive another error

        # prettyprint_mat(flat_mat)

        # process the collected data
        # data_array = mat_list_to_array(flat_mat)
        subarray = mat_list_to_array_subsize(flat_mat, 9, 9)
        for i in range(9):
            for j in range(9):
                subarray[i][j] -= min(subarray[i][j], 30)
        X = get_sparse(subarray)
        # print(subarray)
        data_buffer = X.tolist()
        # print(data_buffer)
        # time.sleep(0.05)


# Start Serial Thread
# ser.write((START_READING_COMMAND + '\n').encode('utf-8'))
threading.Thread(target=read_serial, daemon=True).start()

# API to Serve Matrix Data
@app.route('/data')
def data():
    global data_buffer
    # print(data_buffer)
    
    return jsonify(data_buffer) 

@app.route('/')
def index():
    # return render_template('index_heatmap.html')
    return render_template('index_heatmap_ave.html')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)
    # app.run(host='0.0.0.0', port=5000, debug=False)
