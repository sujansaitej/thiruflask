from flask import Flask, render_template, request
import numpy as np

app = Flask(__name__)

# Letter ↔ Number mappings
char_map = {chr(i+64): i for i in range(1, 27)}
char_map[' '] = 0
num_map = {v: k for k, v in char_map.items()}

def text_to_numbers(text):
    return [char_map.get(char.upper(), 0) for char in text]

def numbers_to_text(numbers):
    return ''.join(num_map[num % 27] for num in numbers)

def encrypt_message(matrix, message, size):
    nums = text_to_numbers(message)
    while len(nums) % size != 0:
        nums.append(0)
    encrypted = []
    for i in range(0, len(nums), size):
        block = np.array(nums[i:i+size])
        result = np.dot(block, matrix) % 27
        encrypted.extend(result.astype(int))
    return numbers_to_text(encrypted)

def decrypt_message(matrix, message, size):
    try:
        inv_matrix = np.linalg.inv(matrix)
    except np.linalg.LinAlgError:
        return "Matrix not invertible!"
    
    nums = text_to_numbers(message)
    while len(nums) % size != 0:
        nums.append(0)
    decrypted = []
    for i in range(0, len(nums), size):
        block = np.array(nums[i:i+size])
        result = np.dot(block, inv_matrix) % 27
        rounded = np.round(result).astype(int)
        decrypted.extend(rounded)
    return numbers_to_text(decrypted)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', output=None)

@app.route('/process', methods=['POST'])
def process():
    size = int(request.form['matrixSize'])
    matrix = []
    for i in range(size):
        row = []
        for j in range(size):
            key = f'm{i}{j}'
            row.append(int(request.form[key]))
        matrix.append(row)
    matrix = np.array(matrix)
    message = request.form['message']
    operation = request.form['operation']

    if operation == 'encrypt':
        result_msg = encrypt_message(matrix, message, size)
        label = "Encrypted"
    else:
        result_msg = decrypt_message(matrix, message, size)
        label = "Decrypted"
    return render_template('index.html', output=result_msg, label=label)

if __name__ == '__main__':
    app.run(debug=True)
