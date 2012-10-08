# -*- coding: utf-8 -*-

import os
#import re
import shutil
import magic

from .volumedriver import VolumeDriver
from .. import exceptions as exc

class Driver(VolumeDriver):
    """
    elFinder driver for local filesystem.
    """
    
    DRIVER_ID = 'l'
    
    def __init__(self, finder):
        super().__init__(finder)
        self._root_realpath = None
        self._options['alias']    = '' #alias to replace root dir_ name
        self._options['dirMode']  = 0o755 #new dirs mode
        self._options['fileMode'] = 0o644 #new files mode

    def _before_mount(self):
        self._root_realpath = os.path.realpath(self._root_path)
        # TODO Init quarantine dir (where archives are extracted to)
        #      and thumbnails

    #*********************************************************************#
    #*                               FS API                              *#
    #*********************************************************************#
    
    def _dirname(self, path):
        """
        Return parent directory path
        """
        return os.path.dirname(path)

    def _basename(self, path):
        """
        Return file name
        """
        return os.path.basename(path)

    def _joinpath(self, dir_, name):
        """
        Join dir name and file name and return full path
        """
        return os.path.join(dir_, name)
    
    def _normpath(self, path):
        """
        Return normalized path
        """
        return os.path.normpath(path)
    
    def _relpath(self, path):
        """
        Return file path related to root dir
        """
        return ('' if path == self._root_path
            else path[len(self._root_path)+len(self._sep):])
    
    def _abspath(self, path):
        """
        Convert path related to root dir into real path
        """
        return (self._root_path if path == self._sep
            else self._joinpath(self._root_path, path))
    
    def _path(self, path):
        """
        Return fake path started from root dir
        """
        return (self._root_name if path == self._root_path
            else self._joinpath(self._root_name, self._relpath(path)))
    
    def _inpath(self, path, parent):
        """
        Return True if path is children of parent
        """
        try:
            return path == parent or path.startswith('%s%s' % (parent, self._sep))
        except:
            return False
    
    #***************** file stat ********************#

    def _stat(self, path):
        """
        Return stat for given path.
        If file does not exist, it returns empty array or False.
        Stat contains following fields:
        - (int)    size    file size in b. required
        - (int)    ts      file modification time in unix time. required
        - (string) mime    mimetype. required for folders, others - optionally
        - (bool)   read    read permissions. required
        - (bool)   write   write permissions. required
        - (bool)   locked  is object locked. optionally
        - (bool)   hidden  is object hidden. optionally
        - (string) alias   for symlinks - link target path relative to root path. optionally
        - (string) target  for symlinks - link target path. optionally
        """
        stat = {}

        try:
            if path != self._root_path and os.path.islink(path):
                target = self._readlink(path)
                if not target or target == path:
                    stat['mime']  = 'symlink-broken'
                    stat['read']  = False
                    stat['write'] = False
                    stat['size']  = 0
                    return stat
                stat['alias']  = self._path(target)
                stat['target'] = target
                path = target
                size = os.lstat(path).st_size
            else:
                size = os.path.getsize(path)
            
            is_dir = os.path.isdir(path)
            
            stat['mime']  = 'directory' if is_dir else self.mimetype(path)
            stat['ts'] = os.path.getmtime(path)
            stat['read']  = os.access(path, os.R_OK)
            stat['write'] = os.access(path, os.W_OK)
            if stat['read']:
                stat['size'] = 0 if is_dir else size
        except os.error:
            raise exc.FinderError(exc.ERROR_RM, self._path(path))
        stat['locked'] = False
        stat['hidden'] = False
        return stat
    
    def _has_subdirs(self, path):
        """
        Return True if path is dir and has at least one child directory
        """
        for entry in os.listdir(path):
            p = path + self._sep + entry
            if os.path.isdir(p) and not self.has_perm(path=p, name='hidden'):
                return True
        return False

    def _tree_stats(self, path, depth, exclude=None):
        prev_root = ''
        depth_cnt = 0
        stats = []
        try:
            exclude = list(exclude)
        except TypeError:
            exclude = []
        for root, dirs, files in os.walk(path):
            if root in exclude:
                continue
            if prev_root != root:
                prev_root = root
                depth_cnt += 1
                if depth_cnt > depth:
                    break
            for d in dirs:
                stats.append( self.stat(os.path.join(root, d)) )
        return stats

    def _ls_stats(self, path):
        """
        Returns list of stats of items in given path.
        """
        stats = []
        for it in os.listdir(path):
            p = path + self._sep + it
            stats.append(self.stat(p))
        return stats

    def _ls(self, path):
        """
        Returns list of names of items in given path.
        """
        names = []
        for it in os.listdir(path):
            p = path + self._sep + it
            names.append(p)
        return names
    
    def _dimensions(self, path, mime):
        """
        Return object width and height
        Ususaly used for images, but can be realize for video etc...
        Can Raise a NotAnImageError
        """
        raise NotImplementedError()
###        XXX PIL is not ready for Py3k
###        if mime.startswith('image'):
###            try:
###                im = Image.open(path)
###                return '%sx%s' % im.size
###            except:
###                pass
###        raise exc.FinderError(exc.PYM_ERROR_NOT_AN_IMAGE)
    
    #******************** file/dir content *********************#
    def _mimetype(self, path):
        """
        Attempt to read the file's mimetype
        """
        return magic.Magic(mime=True).from_file(
            path.encode('utf-8')).decode('utf-8')
    
    def _readlink(self, path):
        """
        Return symlink target file
        """
        target = os.readlink(path)
        try:
            if target[0] != self._sep:
                target = os.path.dirname(path) + self._sep + target
        except TypeError:
            return None
        
        atarget = os.path.realpath(target)
        if self._inpath(atarget, self._root_realpath):
            return self._normpath(self._root_path
                + self._sep + atarget[len(self._root_realpath) + len(self._sep):])

    def _scandir(self, path):
        """
        Return files list in directory.
        The '.' and '..' special directories are ommited.
        """
        return ['%s%s%s' % (path, self._sep, x) for x in os.listdir(path)]

    def _fopen(self, path, mode='rb'):
        """
        Open file and return file pointer
        """
        return open(path, mode)
    
    def _fclose(self, fp, **kwargs):
        """
        Close opened file
        """
        return fp.close()
    
    #********************  file/dir manipulations *************************#
    
    def _mkdir(self, path, name, mode=None):
        """
        Create dir and return created dir path or raise an os.error
        """
        if mode is None:
            mode = self._options['dirMode']
        path = '%s%s%s' % (path, self._sep, name)
        os.mkdir(path, mode)
        return path

    def _mkfile(self, path, name):
        """
        Create file and return it's path or False on failed
        """
        path = '%s%s%s' % (path, self._sep, name)

        open(path, 'w').close()
        os.chmod(path, self._options['fileMode'])
        return path

    def _symlink(self, source, targetDir, name):
        """
        Create symlink
        """
        return os.symlink(source, '%s%s%s' % (targetDir, self._sep, name))

    def _copy(self, source, targetDir, name):
        """
        Copy file into another file
        """
        return shutil.copy(source, '%s%s%s' % (targetDir, self._sep, name))

    def _move(self, source, targetDir, name):
        """
        Move file into another parent dir.
        Return new file path or False.
        """
        target = '%s%s%s' % (targetDir, self._sep, name)
        return target if os.rename(source, target) else False

    def _unlink(self, path):
        """
        Remove file
        """
        return os.unlink(path)

    def _rmdir(self, path):
        """
        Remove dir
        """
        return os.rmdir(path)

    def _save(self, fp, dir_, name, mime, **kwargs):
        """
        Create new file and write into it from file pointer.
        Return new file path or False on error.
        """
        path = '%s%s%s' % (dir_, self._sep, name)
        target = open(path, 'wb')
        
        read = fp.read(8192)
        while read:
            target.write(read)
            read = fp.read(8192)

        target.close()
        os.chmod(path, self._options['fileMode'])
        
        return path
    
    def _save_uploaded(self, uploaded_file, dir_, name, **kwargs):
        """
        Save the django UploadedFile object and return its new path
        """
        raise NotImplementedError()
    
    def _getContents(self, path):
        """
        Get file contents
        """
        return open(path).read()

    def _filePutContents(self, path, content):
        """
        Write a string to a file.
        """
        f = open(path, 'w')
        f.write(content)
        f.close()

    def _checkArchivers(self):
        """
        Detect available archivers
        """
        raise NotImplementedError()

    def _archive(self, dir_, files, name, arc):
        """
        Create archive and return its path
        """
        raise NotImplementedError()

    def _unpack(self, path, arc):
        """
        Unpack archive
        """
        raise NotImplementedError()

    def _findSymlinks(self, path):
        """
        Recursive symlinks search
        """
        raise NotImplementedError()

    def _extract(self, path, arc):
        """
        Extract files from archive
        """
        raise NotImplementedError()
