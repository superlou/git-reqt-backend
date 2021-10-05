from pathlib import Path
import uuid
import json


def get_doc_paths(base_path):
    return [path for path in base_path.iterdir()
            if path.is_dir() and not path.name.startswith('.')]


class Project:
    def __init__(self, base_path):
        self.base = Path(base_path)

    def update_doc(self, doc_id, title, block_ids):
        index = self.load_doc_index(doc_id)
        index['title'] = title
        index['blocks'] = block_ids
        self.save_doc_index(doc_id, index)

    def update_block(self, block_id, doc_id, content):
        block_path = self.build_block_path(block_id, doc_id)

        with open(block_path, 'w') as block_file:
            block_file.write(content)

    def create_block(self, doc_id, content):
        block_id = str(uuid.uuid4())
        block_path = self.build_block_path(block_id, doc_id)

        with open(block_path, 'w') as block_file:
            block_file.write(content)

        index = self.load_doc_index(doc_id)
        index['blocks'].append(block_id)
        self.save_doc_index(doc_id, index)

        return block_id

    def read_block_content(self, block_id, doc_id):
        return open(self.build_block_path(block_id, doc_id)).read()

    def delete_block(self, block_id):
        doc_id = self.find_block_doc(block_id)
        block_path = self.build_block_path(block_id, doc_id)
        block_path.unlink(missing_ok=True)

        index = self.load_doc_index(doc_id)
        index['blocks'] = [id for id in index['blocks'] if id != block_id]
        self.save_doc_index(doc_id, index)

    def find_block_doc(self, block_id):
        for doc_id in self.doc_ids:
            block_path = self.base / doc_id / f'{block_id}.md'
            if block_path.exists():
                return doc_id

        return None

    def build_index_path(self, doc_id):
        return self.base / doc_id / 'index.json'

    def build_block_path(self, block_id, doc_id):
        return self.base / doc_id / f'{block_id}.md'

    def load_doc_index(self, doc_id):
        index_path = self.build_index_path(doc_id)
        return json.loads(open(index_path).read())

    def save_doc_index(self, doc_id, data):
        index_path = self.build_index_path(doc_id)
        json.dump(data, open(index_path, 'w'), indent=4)

    @property
    def doc_ids(self):
        return [path.name for path in self.base.iterdir()
                if path.is_dir() and not path.name.startswith('.')]
