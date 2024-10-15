from flask import Flask, request, jsonify, render_template
import os
import re

app = Flask(__name__)

# 定义目录
UPLOAD_FOLDER = 'D:/Documents/uploads'  # 最终文件目录
TEMP_FOLDER = 'D:/Documents/uploads/temp'  # 临时文件目录

# 创建目录
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TEMP_FOLDER, exist_ok=True)

print(os.listdir(TEMP_FOLDER))


@app.route("/")
def index():
    return render_template('index.html')


# 上传分块接口
@app.route('/upload', methods=['POST'])
def upload_chunk():
    chunk = request.files['chunk']
    file_name = request.form['fileName']
    chunk_index = request.form['chunkIndex']

    # 生成临时分块文件名，确保按顺序存储到临时目录
    chunk_filename = f"{file_name}_part_{chunk_index}"
    chunk.save(os.path.join(TEMP_FOLDER, chunk_filename))

    return jsonify({"status": "Chunk uploaded", "chunkIndex": chunk_index})


# 检查已上传分块接口
@app.route('/checkChunks', methods=['GET'])
def check_chunks():
    file_name = request.args.get('fileName')
    uploaded_chunks = []

    # 查找临时目录中已上传的分块文件
    for filename in os.listdir(TEMP_FOLDER):
        if file_name in filename:
            match = re.search(r'_part_(\d+)', filename)
            if match:
                uploaded_chunks.append(match.group(1))  # 提取分块编号
    uploaded_chunks.sort(key=lambda x: int(x))
    return jsonify(uploaded_chunks)


# 合并文件接口
@app.route('/merge', methods=['POST'])
def merge_file():
    data = request.json
    file_name = data['fileName']

    # 获取临时目录中的所有分块文件，并按顺序合并
    chunk_files = sorted(
        [f for f in os.listdir(TEMP_FOLDER) if file_name in f],
        key=lambda x: int(re.search(r'_part_(\d+)', x).group(1))
    )

    # 合并分块到最终目录
    final_file_path = os.path.join(UPLOAD_FOLDER, file_name)
    with open(final_file_path, 'wb') as final_file:
        for chunk_file in chunk_files:
            chunk_path = os.path.join(TEMP_FOLDER, chunk_file)
            with open(chunk_path, 'rb') as f:
                final_file.write(f.read())

            # 合并后删除临时分块文件
            os.remove(chunk_path)

    return jsonify({"status": "File merged", "fileName": file_name})


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
