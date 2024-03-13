import numpy
import json
import base64

from flask import Flask, send_file

app = Flask("I cook methamphetamine") 

coords = [
    (0, 0), (1, 0), (2, 0),
    (0, 1), (1, 1), (2, 1),
    (0, 2), (1, 2), (2, 2)
]
total_coords = len(coords)
matrix = numpy.matrix([
    [0.0 for j in range(total_coords)] for i in range(total_coords)])

def getIndex(position):
    return coords.index(position)

def processData():
    entries = json.load(open("play_data.json"))["entries"]
    for entry in entries:
        start = 1 # if hyuman win, learn from human
        if didComputerWin(len(entry)): start = 0 # if computer win, learn from computer

        for i in range(start, len(entry) - 1, 2):
            tuple_cur = tuple(entry[i])
            tuple_next = tuple(entry[1])

            m_coord = (getIndex(tuple_cur), getIndex(tuple_next))
            # print(m_coord)

            matrix.itemset(m_coord, matrix.item(m_coord) + 1.0)\

    for i in range(total_coords):
        sum_row = 0
        for j in range(total_coords):
            sum_row += matrix.item((i, j))
        if sum_row == 0: continue # to prevent division by zero

        for j in range(total_coords):
            matrix.itemset((i, j), matrix.item((i, j)) / sum_row)

def didComputerWin(length):
    return length % 2 == 0

processData()

print(matrix)
print("Processed!")

@app.route("/")
def index():
    return send_file("index.html")

@app.route("/move/<board_raw>/<x>/<y>", methods=["POST"])
def move(board_raw, x, y):
    print('hi')
    # turn board_raw into array
    board = []
    for i in range(3):
        board.append([])
        for j in range(3):
            board[i].append(board_raw[i * 3 + j])
    human_play = (int(x), int(y))
    row_matrix = matrix[getIndex(human_play), :]
    row_probabilities = []
    for i in range(total_coords):
        row_probabilities.append({
            "probability": row_matrix.item(0, i),
            "item": coords[i]
        })

    # sort for ranking
    for i in range(total_coords):
        for j in range(total_coords - 1):
            cur = row_probabilities[j]["probability"]
            _next = row_probabilities[j + 1]["probability"]
            if _next > cur:
                row_probabilities[j], row_probabilities[j + 1] = row_probabilities[j + 1], row_probabilities[j]
    for datum in row_probabilities:
        coord = datum["item"]
        if board[coord[1]][coord[0]] == "N":
            return list(coord)
    return "fuck"

@app.route("/win/<moves_encoded>", methods=["POST"])
def win(moves_encoded):
    raw_json = base64.b64decode(moves_encoded).decode()
    print(f"HHAHAHAHAHAHHAHAHAHAHHAHA {raw_json}")
    moves = json.loads("{\"entry\":" + raw_json + "}")["entry"]

    data_json = json.load(open("play_data.json"))
    data_json["entries"].append(moves)

    open("play_data.json", "w").write(json.dumps(data_json))
    return "Hi lol"
    

if __name__ == '__main__':
#    app.run(debug = True)
    from waitress import serve
    serve(app, host="0.0.0.0", port=8000)