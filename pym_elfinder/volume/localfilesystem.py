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
        Returns directory name of path.
        """
        return os.path.dirname(path)

    def _basename(self, path):
        """
        Returns file name of path.
        """
        return os.path.basename(path)

    def _joinpath(self, *args):
        """
        Joins given arguments with directory separator.
        """
        return os.path.join(*args)
    
    def _normpath(self, path):
        """
        Returns normalized path, i.e. removes '..', obsolete '/' etc.
        """
        return os.path.normpath(path)
    
    def _relpath(self, path):
        """
        Converts absolute path into path relative to root.
        """
        if path == self._root_path:
            return ''
        elif path == '':
            return '' # On command open-init we get called with empty path
        else:
            if not path.startswith(self._root_path + self._sep):
                raise exc.FinderError(exc.PYM_ERROR_INVALID_PATH, path)
            return path[len(self._root_path)+len(self._sep):]
    
    def _abspath(self, path):
        """
        Converts relative path into absolute path starting with root.
        """
        if path == self._sep:
            return self._root_path
        else:
            return self._joinpath(self._root_path, path)
    
    def _aliaspath(self, path):
        """
        Replaces root path part of ``path`` with root's alias name.
        """
        if path == self._root_path:
            return self._root_alias
        else:
            return self._joinpath(self._root_alias, self._relpath(path))
    
    def _inpath(self, path, parent):
        """
        Returns True if path is parent or child of parent.
        """
        path = path.rstrip(self._sep)
        parent = path.rstrip(self._sep)
        return (path == parent
            or path.startswith(parent + self._sep)
        )
    
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
                stat['alias']  = self._aliaspath(target)
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
        except OSError:
            raise exc.FinderError(exc.ERROR_RM, self._aliaspath(path))
        stat['locked'] = False
        stat['hidden'] = False
        return stat

    def _update_quota(self):
        top = self._root_path
        self._used_size = 0
        for root, dirs, files in os.walk(top):
            self._used_size += sum(
                os.path.getsize(os.path.join(root, name)) for name in files)
        return self._used_size
    
    def _has_subdirs(self, path):
        """
        Returns True if path is dir and has at least one child directory.
        """
        #if 'some_dir' in path:
        #    import ipdb; ipdb.set_trace()
        for entry in os.listdir(path):
            p = path + self._sep + entry
            if os.path.isdir(p) and not self.acl_perm(path=p, perm_name='hidden'):
                return True
        return False

    def _tree_stats(self, path, depth, exclude=None):
        """
        Returns list of stats of all directories in a tree.

        :param path: Start in this directory
        :param depth: Go maximum this deep.
        :param exclude: List of (sub)directories to exclude from result
        :returns: List of stats
        """
        prev_root = ''
        depth_cnt = 0
        stats = []
        if not exclude:
            exclude = []
        elif isinstance(exclude, str):
            exclude = [ exclude ]
        for root, dirs, files in os.walk(path):
            if prev_root != root:
                prev_root = root
                depth_cnt += 1
                if depth_cnt > depth:
                    break
            for d in dirs:
                if self._joinpath(root, d) in exclude:
                    continue
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

    def _ls_names(self, path):
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
   
    def _exists(self, path):
        return os.path.exists(path)

    #******************** file/dir content *********************#
    def _mimetype(self, path):
        """
        Returns path's mimetype.
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

    def _file(self, path):
        """
        Returns file-like object for given path.

        File is opened in binary mode for reading.
        """
        try:
            fd = open(path, 'rb')
        except (OSError, IOError) as e:
            raise exc.FinderError(e)
        return fd

    def _get_content(self, path, encoding=None):
        """
        Returns content of file.

        If ``encoding`` is None, opens the file in binary mode and returns a
        bytes string.

        If ``encoding`` is set, opens the file in text mode and uses the given
        encoding to transform the content into a unicode string.

        :param path: Path to file
        :param encoding: Encoding to use for text files
        :returns: File content as bytes (binary mode) or str (text mode)
        """
        mode = 'rt' if encoding else 'rb'
        try:
            with open(path, mode, encoding=encoding) as fd:
                s = fd.read()
        except (OSError, IOError) as e:
            raise exc.FinderError(exc.ERROR_OPEN, e)
        return s

    def _put_content(self, path, content, encoding=None):
        """
        Writes new content into a file

        If ``encoding`` is None, opens the file in binary mode. If ``encoding``
        is set, opens the file in text mode and uses the given encoding to
        transform the unicode content into encoded byte string.

        :param path: Path of file that will be changed
        :param content: New content
        :param encoding: Encoding to use for text files
        :returns: Path of changed file
        """
        flags = os.O_WRONLY | os.O_EXCL | os.O_TRUNC
        if encoding:
            bytes_ = content.encode(encoding)
        else:
            flags |= os.O_BINARY
            bytes_ = content
        try:
            fd = os.open(path, flags)
            try:
                os.write(fd, bytes_)
            except (OSError, IOError) as e:
                raise
            finally:
                os.close(fd)
        except (OSError, IOError) as e:
            raise exc.FinderError(exc.ERROR_SAVE, e)
        return path

    
    #********************  file/dir manipulations *************************#
    
    def _mkdir(self, cur_path, name, mode=None):
        """
        Creates a directory if it does not exist.

        :param path: Path of current directory
        :param name: Name of directory to create
        :param mode: Octal mode
        :returns: Absolute name of created dir
        :raises: FinderError if dir exists or any OSError occured
        """
        if mode is None:
            mode = self._options['dirMode']
        path = self._joinpath(cur_path, name)
        try:
            os.mkdir(path, mode)
        except OSError as e:
            raise exc.FinderError(exc.ERROR_MKDIR, e, name)
        return path

    def _mkfile(self, cur_path, name, mode=None):
        """
        Creates a file if it does not exist.

        :param path: Path of current directory
        :param name: Name of file to create
        :param mode: Octal mode
        :returns: Absolute name of created file
        :raises: FinderError if file exists or any OSError occured
        """
        if mode is None:
            mode = self._options['fileMode']
        path = self._joinpath(cur_path, name)
        try:
            os.open(path, os.O_CREAT | os.O_EXCL, mode)
            # In Python 3.3 we can use the new "x" mode for built-in open()
        except OSError as e:
            raise exc.FinderError(exc.ERROR_MKFILE, e, name)
        return path

    def _copy(self, src, dst_dir, name):
        """
        Copies a file or directory.

        :param src: 
        :returns: Path to the newly created file or directory.
        """
        dst = self._joinpath(dst_dir, name)
        try:
            if os.path.isdir(src):
                shutil.copytree(src, dst) # Py3.3: shutil.copy() itself returns dst
            else:
                shutil.copy(src, dst) # Py3.3: shutil.copytree() itself returns dst
            return dst
        except (IOError, OSError) as e: # Py3.3: OSError; <Py3.3: IOError
            raise exc.FinderError(exc.ERROR_COPY, e)

    def _move(self, src, dst_dir, name):
        """
        Moves a file or directory.
        
        :returns: Destination path.
        """
        dst = self._joinpath(dst_dir, name)
        try:
            shutil.move(src, dst) # Py3.3: shutil.move() itself returns dst
            return dst
        except (IOError, OSError) as e:
            raise exc.FinderError(exc.ERROR_MOVE, e)

    def _remove(self, path):
        try:
            if os.path.isdir(path):
                os.rmdir(path)
            else:
                os.unlink(path)
        except OSError as e:
            raise exc.FinderError(exc.ERROR_RM, self._basename(path), e)
        return path

###    def _unlink(self, path):
###        """
###        Removes a file.
###        """
###        os.unlink(path)
###        return path
###
###    def _rmdir(self, path):
###        """
###        Removes an empty directory.
###        """
###        os.rmdir(path)
###        return path

    def _save_uploaded(self, fd, dst_path, filename):
        """
        Save the uploaded file object and return its new path.

        :param fd: File descriptor of uploaded file
        :param dst_path: Path of destination directory
        :param filename: Basename of uploaded file
        :returns: Path to uploaded file

        Test code to learn nested try..except..finally constructs:

        .. code-block:: python

            class Ex(Exception):
                pass

            class Ex2(Exception):
                pass

            def open_fd():
                print("FD opened")

            def open_dst_fd():
                #raise Ex("ERROR on open DST FD")
                print("DST FD opened")

            def copy():
                raise Ex("ERROR on copy")
                print("copy")

            def close_dst_fd():
                print("DST FD closed")

            def close_fd():
                print("FD closed")

            def two():
                open_fd()
                try:
                    open_dst_fd()
                    try:
                        copy()
                    except Ex as e:
                        print("INNER ERROR:", e)
                        raise Ex2(e)
                    finally:
                        close_dst_fd()
                except Ex as e:
                    print("OUTER ERROR:", e)
                    raise Ex2(e)
                finally:
                    close_fd()

            two()
        """
        dst_file_path = self._joinpath(dst_path, filename)
        try:
            dst_fd = open(dst_file_path, 'wb')
            try:
                shutil.copyfileobj(fd, dst_fd)
            # copyfileobj may raise several exceptions, so catch them all.
            # E.g. - UnsupportedOperation if src is not readable,
            #      - AttributeError if args are of wrong type, e.g.
            #        have no attr "read()"
            #      - etc
            except Exception as e:
                raise exc.FinderError(exc.ERROR_UPLOAD, e)
            finally:
                # Copy failed, but certainly close destination file
                dst_fd.close()
        # Catch error on opening dst fd
        except (OSError, IOError) as e:
            raise exc.FinderError(exc.ERROR_UPLOAD, e)
        finally:
            # Under all circumstances close the uploaded file
            fd.close()
        return dst_file_path

    def _rename(self, src, dst):
        try:
            os.rename(src, dst)
        except OSError as e:
            raise exc.FinderError(exc.ERROR_RENAME, e)
        return dst
