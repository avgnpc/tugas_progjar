import os
import json
import base64
from glob import glob

class FileInterface:
    def __init__(self):
        self.files_dir = os.path.join(os.path.dirname(__file__), 'files')
        os.makedirs(self.files_dir, exist_ok=True)

    def _get_path(self, filename):
        return os.path.join(self.files_dir, os.path.basename(filename))

    def list(self, params=[]):
        try:
            filelist = [os.path.basename(f) for f in glob(os.path.join(self.files_dir, '*.*'))]
            return dict(status='OK', data=filelist)
        except Exception as e:
            return dict(status='ERROR', data=str(e))

    def get(self, params=[]):
        try:
            filename = params[0]
            path = self._get_path(filename)
            with open(path, 'rb') as f:
                encoded = base64.b64encode(f.read()).decode()
            return dict(status='OK', data_namafile=filename, data_file=encoded)
        except Exception as e:
            return dict(status='ERROR', data=str(e))

    def upload(self, params=[]):
        try:
            filename, filedata = params
            path = self._get_path(filename)
            with open(path, 'wb') as f:
                f.write(base64.b64decode(filedata))
            return dict(status='OK', data=f'{filename} berhasil diupload')
        except Exception as e:
            return dict(status='ERROR', data=str(e))

    def delete(self, params=[]):
        try:
            filename = params[0]
            path = self._get_path(filename)
            if os.path.exists(path):
                os.remove(path)
                return dict(status='OK', data=f'{filename} berhasil dihapus')
            else:
                return dict(status='ERROR', data='File tidak ditemukan')
        except Exception as e:
            return dict(status='ERROR', data=str(e))


if __name__ == '__main__':
    f = FileInterface()
    print(f.list())
    print(f.get(['pokijan.jpg']))

