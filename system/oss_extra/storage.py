# -*- coding: utf-8 -*-
import os, time, random 
from django.core.files.base import File
from django.core.files.storage import Storage
from django.conf import settings 
from django.core.files import File
import oss.oss_api
import oss.oss_util

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
from memory import settings

class AliyunStorage(Storage):
    
    def __init__(self, location="zhuyuanprj"): 
        self.prefix = location
        self.client = oss.oss_api.OssAPI(settings.OSS_HOST,settings.OSS_ACCESS_KEY_ID,settings.OSS_SECRET_ACCESS_KEY)

    def _put_file(self, name, content):
        name = name.replace('\\', '/')
        content_type = oss.oss_util.get_content_type_by_filename(name)
        input_content = content
        res = self.client.put_object_with_data(self.prefix, name, input_content,content_type)
        if (res.status / 100) == 2:
            print "put_object_from_string OK"
        else:
            print "put_object_from_string ERROR"
        

    def _read(self, name):
        memory_file = StringIO()
        try:
            memory_file = self.client.get_object(self.prefix, name).read()
        except:
            pass
        return memory_file

    def _open(self, name, mode="rb"):
        return AliyunStorageFile(name, self, mode=mode)

    def _save(self, name, content): 
        if hasattr(content, 'chunks'):
            content_str = ''.join(chunk for chunk in content.chunks())
        else:
            content_str = content.read()
        #for fake tempfile
        if not content_str and hasattr(content, "file"):
            try:
                content_str = content.file.getvalue()
            except:
                pass
        self._put_file(name, content_str)
        return name

    def delete(self, name):
        self.client.delete(self.prefix, name)

    def exists(self, name):
        try:
            o = self.client.get_object(self.prefix, name).status
            if o == 200:
                return True
        except:
            pass
        return False

    def listdir(self):
        files = self.client.list_objects(self.prefix)
        return files
        
    def size(self, name):
        try:
            stat = self.client.get_object(self.prefix, name)
        except:
            return 0
        return stat.length

    def url(self, name):
        url = self.client.sign_url("GET",self.prefix, name,60)
        url = url.split("?")
        return str(url[0])
        
        
    def isdir(self, name):
        return False if name else True

    def isfile(self, name):
        return self.exists(name) if name else False
        
    def modified_time(self, name):
        from datetime import datetime
        return datetime.now()
        
    def path(self,name):
    	return name
        
class AliyunStorageFile(File):
    """docstring for AliyunStorageFile"""
    def __init__(self, name, storage, mode):
        self._name = name
        self._storage = storage
        self._mode = mode
        self._is_dirty = False
        self.file = StringIO()
        self._is_read = False

    @property
    def size(self):
        if not hasattr(self, '_size'):
            self._size = self._storage.size(self._name)
        return self._size

    def read(self, num_bytes=None):
        if not self._is_read:
            self.file = self._storage._read(self._name)
            self.file = StringIO(self._storage.client.get_object(self._storage.prefix, self._name).read())
            self._is_read = True
        if num_bytes:
            return self.file.read(num_bytes)
        else:
            return self.file.read()
            
    def write(self, content):
        if 'w' not in self._mode:
            raise AttributeError("File was opened for read-only access.")
        self.file = StringIO(content)
        self._is_dirty = True
        self._is_read = True

    def close(self):
        if self._is_dirty:
            self._storage._put_file(self._name, self._storage.client.get_object(self._storage.prefix, self._name).read())
        self.file.close()
        