from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

history = []


# =========================
# HALAMAN
# =========================

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/caesar")
def caesar():
    return render_template("caesar.html")


@app.route("/vigenere")
def vigenere():
    return render_template("vigenere.html")


@app.route("/affine")
def affine():
    return render_template("affine.html")

@app.route("/affine/process", methods=["POST"])
def process_affine():

    data = request.get_json()

    text = data["text"]
    a = int(data["a"])
    b = int(data["b"])
    mode = data["mode"]

    result = ""
    steps = []

    # validasi a
    valid_a = [1,3,5,7,9,11,15,17,19,21,23,25]

    if a not in valid_a:
        return jsonify({
            "result": "Nilai a tidak valid!",
            "steps": ["Nilai a harus relatif prima dengan 26"]
        })

    for char in text:

        if char.isalpha():

            start = ord('A') if char.isupper() else ord('a')

            x = ord(char) - start

            if mode == "encrypt":

                y = (a * x + b) % 26

                result_char = chr(y + start)

                steps.append(
                    f"{char} → ({a} × {x} + {b}) mod 26 = {y} → {result_char}"
                )

            else:

                # inverse a
                a_inv = 0

                for i in range(26):
                    if (a * i) % 26 == 1:
                        a_inv = i
                        break

                y = (a_inv * (x - b)) % 26

                result_char = chr(y + start)

                steps.append(
                    f"{char} → {a_inv} × ({x} - {b}) mod 26 = {y} → {result_char}"
                )

            result += result_char

        else:
            result += char

    return jsonify({
        "result": result,
        "steps": steps
    })


@app.route("/hill")
def hill():
    return render_template("hill.html")

# =========================
# HILL PROCESS
# =========================

@app.route("/hill/process", methods=["POST"])
def process_hill():

    data = request.get_json()

    text = data["text"].upper().replace(" ", "")
    matrix = data["matrix"]
    mode = data["mode"]

    size = len(matrix)

    result = ""
    steps = []

    # padding jika kurang
    while len(text) % size != 0:
        text += "X"

    # proses per blok
    for i in range(0, len(text), size):

        block = text[i:i+size]

        vector = []

        for char in block:
            vector.append(ord(char) - 65)

        # matrix multiplication
        result_vector = []

        for row in matrix:

            total = 0
            calc = ""

            for j in range(size):

                total += row[j] * vector[j]

                calc += f"({row[j]}×{vector[j]})"

                if j < size - 1:
                    calc += " + "

            mod_result = total % 26

            result_vector.append(mod_result)

            steps.append(
                f"{calc} mod 26 = {mod_result}"
            )

        # convert hasil ke huruf
        for num in result_vector:

            result += chr(num + 65)

    return jsonify({
        "result": result,
        "steps": steps
    })


@app.route("/playfair")
def playfair():
    return render_template("playfair.html")


# =========================
# PLAYFAIR PROCESS
# =========================

@app.route("/playfair/process", methods=["POST"])
def process_playfair():

    data = request.get_json()

    text = data["text"].upper()
    key = data["key"].upper()
    mode = data["mode"]

    # =========================
    # HAPUS SPASI & GANTI J → I
    # =========================

    text = text.replace(" ", "").replace("J", "I")
    key = key.replace(" ", "").replace("J", "I")

    # =========================
    # BUAT TABEL 5x5
    # =========================

    alphabet = "ABCDEFGHIKLMNOPQRSTUVWXYZ"

    matrix_string = ""

    for char in key:
        if char not in matrix_string and char in alphabet:
            matrix_string += char

    for char in alphabet:
        if char not in matrix_string:
            matrix_string += char

    table = []

    index = 0

    for i in range(5):

        row = []

        for j in range(5):

            row.append(matrix_string[index])
            index += 1

        table.append(row)

    # =========================
    # PAIRING HURUF
    # =========================

    pairs = []

    i = 0

    while i < len(text):

        a = text[i]

        if i + 1 < len(text):
            b = text[i + 1]
        else:
            b = "X"

        if a == b:
            pairs.append(a + "X")
            i += 1
        else:
            pairs.append(a + b)
            i += 2

    # padding
    if len(pairs[-1]) == 1:
        pairs[-1] += "X"

    # =========================
    # CARI POSISI HURUF
    # =========================

    def find_position(char):

        for r in range(5):
            for c in range(5):

                if table[r][c] == char:
                    return r, c

    # =========================
    # ENCRYPT / DECRYPT
    # =========================

    result = ""
    steps = []

    for pair in pairs:

        a, b = pair[0], pair[1]

        r1, c1 = find_position(a)
        r2, c2 = find_position(b)

        # SATU BARIS
        if r1 == r2:

            if mode == "encrypt":
                new_a = table[r1][(c1 + 1) % 5]
                new_b = table[r2][(c2 + 1) % 5]
            else:
                new_a = table[r1][(c1 - 1) % 5]
                new_b = table[r2][(c2 - 1) % 5]

            rule = "Satu Baris"

        # SATU KOLOM
        elif c1 == c2:

            if mode == "encrypt":
                new_a = table[(r1 + 1) % 5][c1]
                new_b = table[(r2 + 1) % 5][c2]
            else:
                new_a = table[(r1 - 1) % 5][c1]
                new_b = table[(r2 - 1) % 5][c2]

            rule = "Satu Kolom"

        # PERSEGI
        else:

            new_a = table[r1][c2]
            new_b = table[r2][c1]

            rule = "Persegi"

        encrypted_pair = new_a + new_b

        result += encrypted_pair

        steps.append(
            f"{pair} → {encrypted_pair} ({rule})"
        )

    # =========================
    # RESPONSE
    # =========================

    return jsonify({
        "result": result,
        "table": table,
        "pairs": pairs,
        "steps": steps
    })

# =========================
# HISTORY
# =========================

@app.route("/history")
def show_history():
    return jsonify(history)


# =========================
# CAESAR PROCESS
# =========================

@app.route("/caesar/process", methods=["POST"])
def process_caesar():

    data = request.get_json()

    text = data["text"]
    shift = int(data["shift"])
    mode = data["mode"]

    if mode == "decrypt":
        shift = -shift

    result = ""
    steps = []

    for char in text:

        if char.isalpha():

            start = ord('A') if char.isupper() else ord('a')

            old = ord(char) - start
            new = (old + shift) % 26

            encrypted = chr(new + start)

            result += encrypted

            steps.append(
                f"{char} → ({old} + {shift}) mod 26 = {new} → {encrypted}"
            )

        else:
            result += char

    history.append({
        "cipher": "Caesar",
        "text": text,
        "result": result
    })

    return jsonify({
        "result": result,
        "steps": steps,
        "formula": "E(x) = (x + k) mod 26"
    })


# =========================
# VIGENERE PROCESS
# =========================

@app.route("/vigenere/process", methods=["POST"])
def process_vigenere():

    data = request.get_json()

    text = data["text"]
    key = data["key"]
    mode = data["mode"]

    result = ""
    steps = []

    key = key.upper()
    key_index = 0

    for char in text:

        if char.isalpha():

            shift = ord(key[key_index % len(key)]) - 65

            if mode == "decrypt":
                shift = -shift

            start = ord('A') if char.isupper() else ord('a')

            old = ord(char) - start
            new = (old + shift) % 26

            encrypted = chr(new + start)

            result += encrypted

            steps.append(
                f"{char} + {key[key_index % len(key)]} = {encrypted}"
            )

            key_index += 1

        else:
            result += char

    return jsonify({
        "result": result,
        "steps": steps,
        "formula": "Ci = (Pi + Ki) mod 26"
    })


# =========================
# RUN
# =========================

if __name__ == "__main__":
    app.run(debug=True)