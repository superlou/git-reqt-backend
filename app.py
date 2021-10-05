
from flask import Flask, request, Response
from flask_cors import CORS, cross_origin
from pathlib import Path
from git import Repo
import json
from project import Project


app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['PROJECT_DIR'] = '../example'


def build_block_response(block_id, doc_id):
    project = Project(app.config['PROJECT_DIR'])
    block_path = project.build_block_path(block_id, doc_id)

    with open(block_path) as block_file:
        content = block_file.read()

    return {
        'data': {
            'type': 'block',
            'id': block_id,
            'attributes': {
                'content': content
            },
            'relationships': {
                'doc': {
                    'type': 'doc',
                    'id': doc_id
                }
            }
        }
    }


@app.route('/api/v1/blocks/<block_id>', methods=['PATCH'])
@cross_origin()
def update_block(block_id):
    r = request.get_json()
    doc_id = r['data']['relationships']['doc']['data']['id']
    content = r['data']['attributes']['content']

    project = Project(app.config['PROJECT_DIR'])
    project.update_block(block_id, doc_id, content)

    return build_block_response(block_id, doc_id)


@ app.route('/api/v1/blocks/<block_id>', methods=['DELETE'])
@ cross_origin()
def delete_block(block_id):
    project = Project(app.config['PROJECT_DIR'])
    project.delete_block(block_id)
    return Response({}, status=200)


@ app.route('/api/v1/blocks', methods=['POST'])
@ cross_origin()
def create_block():
    r = request.get_json()
    doc_id = r['data']['relationships']['doc']['data']['id']
    content = r['data']['attributes']['content']

    project = Project(app.config['PROJECT_DIR'])
    block_id = project.create_block(doc_id, content)

    return build_block_response(block_id, doc_id)


@ app.route('/api/v1/docs')
@ cross_origin()
def docs():
    path = Path(app.config['PROJECT_DIR'])
    indices = [(json.loads(open(x / 'index.json').read()), x.name)
               for x in path.iterdir()
               if x.is_dir() and not x.name.startswith('.')]

    data = [{
        'type': 'doc',
        'id': index[1],
        'attributes': {
            'title': index[0]['title']
        }
    } for index in indices]

    return {
        'data': data
    }


@app.route('/api/v1/docs/<id>', methods=['PATCH'])
def update_doc(id):
    r = request.get_json()

    project = Project(app.config['PROJECT_DIR'])
    title = r['data']['attributes']['title']
    block_ids = [block['id']
                 for block in r['data']['relationships']['blocks']['data']]
    project.update_doc(id, title, block_ids)

    return build_doc_response(id)


def build_doc_response(doc_id):
    project = Project(app.config['PROJECT_DIR'])
    index = project.load_doc_index(doc_id)

    blocks = [(block_id, project.read_block_content(block_id, doc_id))
              for block_id in index['blocks']]

    included_blocks = [{
        'type': 'block',
        'id': block[0],
        'attributes': {
            'content': block[1]
        }
    } for block in blocks]

    return {
        'data': {
            'type': 'doc',
            'id': doc_id,
            'attributes': {
                'title': index['title']
            },
            'relationships': {
                'blocks': {
                    'data': [{'type': 'block', 'id': block_id}
                             for block_id in index['blocks']]
                }
            }
        },
        'included': included_blocks
    }


@app.route('/api/v1/docs/<id>')
def doc(id):
    return build_doc_response(id)


@ app.route('/')
def index():
    return '<p>Index</p>'

    # if __name__ == '__main__':
    #     repo = Repo('./project')
    #     master = repo.heads.master
    #     tree = master.commit.tree
    #
    #     index = master.commit.tree / 'index.json'
    #     index = json.loads(index.data_stream.read())
    #
    #     for item in index['items']:
    #         blob = master.commit.tree / f'{item}.md'
    #         print(blob.data_stream.read().decode())
    #         print(blob.data_stream.read().decode())
    #         print(blob.data_stream.read().decode())
