# -*- coding: utf-8 -*-

import re
import os
import copy
import mimetypes
from base64 import b64encode, b64decode
try:
    from collections.abc import Callable
except ImportError:
    from collections import Callable

from .. import exceptions as exc


class VolumeDriver(object):
    
    DRIVER_ID = 'a'
    """Driver ID.

    Must conform to /^[a-z][a-z0-9]*$/. Used as part of volume ID.
    """

    def __init__(self, finder):
        """
        Base class of volume drivers.
        """
        # ---[ private attribs ]-------
        self._finder = finder
        # Renamed from "_id"
        self._volume_id = None
        self._is_mounted = False
        # Renamed from "_defaults"
        self._default_ace = None
        # Renamed from "_attributes"
        self._acl = []
        # Renamed from "_access"
        self._access_policy = None
        # (DEFAULT_OPTIONS are defined at the bottom)
        self._options = copy.deepcopy(self.__class__.DEFAULT_OPTIONS)
        self._sep = os.sep
        self._root_path = None
        # Renamed from "onlyMimes"
        self._only_mimes = None
        # Renamed from "uploadAllow"
        self._upload_allow = []
        # Renamed from "uploadDeny"
        self._upload_deny = []
        # Renamed from "uploadOrder"
        self._upload_order = []
        # Renamed from uploadMaxSize
        self._upload_max_size = 2*1024*1024
        """
        Maximum size of a single uploaded file in bytes.
        """
        # Renamed from "disabled"
        self._disabled_cmds = None
        # Renamed from "treeDeep"
        self._tree_depth = 1
        # Renamed from "tmbSize"
        self._tmb_size  = 48
        # Renamed from "_URL"
        self._url = ''
        # Renamed from "tmbURL"
        self._tmb_url = ''
        # Renamed from "nameValidator"
        self.name_policy = None
        self._archivers = None
        self._max_size = 0
        """
        Quota max size in bytes.

        Is set during mount initialization from volume options.
        """
        self._used_size = 0
        """
        Quota used size in bytes.

        Call :meth:`update_quota()` to set this value correctly. Is updated by Finder
        on each command call.
        """
        # ---[ public attribs ]-------

    # ===[ MOUNT ]=======

    def mount(self, opts):
        # Init
        self._init_options(opts)
        self._init_archivers()

        # Perform mount
        self._before_mount()
        self._perform_mount()
        self._after_mount()

        # Successfully mounted
        self._is_mounted = True
        return True

    def umount(self):
        self._is_mounted = False

    def _perform_mount(self):
        root = self._stat(self._root_path)
        if not root['read'] and not root['write']:
            raise exc.FinderError(exc.ERROR_PERM_DENIED)
        
        if root['read']:
            pass
        else:
            self._options['URL'] = ''
            self._options['tmbURL'] = ''
            self._options['tmbPath'] = ''
            #read only volume
            self._acl.insert(0, {
                'pattern' : r'.*',
                'read' : False
            })

    def _init_archivers(self):
        """Init archivers.

        Is called during mount initialisation. Override in concrete driver
        implementation if necessary.
        """
        pass

    def _before_mount(self):
        """Init volume during mount.

        Is called after options are initialized. Override in concrete driver
        implementation if necessary.
        """
        pass

    def _after_mount(self):
        """Postprocess volume during mount.

        Is called after mount took place. Override in concrete driver
        implementation if necessary.
        """
        pass

    def _init_options(self, opts):
        self._check_required_options(opts)
        self._options.update(opts)

        self._init_volume_id()
        self._init_security()
        self._init_paths()
        self._init_uploads()
        self._init_thumbs()

        self._tree_depth = int(self._options.get('tree_depth', self._tree_depth))
        if self._tree_depth < 1:
            self._tree_depth = 1
        
        self._url = self._options.get('URL', self._url)

    def _init_thumbs(self):
        self._tmb_size  = int(self._options.get('tmbSize', self._tmb_size))
        if self._tmb_size < 1:
            self._tmb_size = 48
        self._tmb_url = self._options.get('tmbURL', self._tmb_url)

    def _init_uploads(self):
        self._upload_allow  = self._options.get('uploadAllow', self._upload_allow)
        self._upload_deny   = self._options.get('uploadDeny', self._upload_deny)
        self._upload_order  = self._options.get('uploadOrder', self._upload_order)
        self._upload_max_size = self._options.get('uploadMaxSize', self._upload_max_size)

    def _init_paths(self):
        self._sep = self._options.get('separator', os.sep)
        # Root path
        self._root_path = self._normpath(self._options['path'])
        self._root_alias = self._options.get('alias',
            self._basename(self._root_path))

    def _init_security(self):
        # Disabled commands
        self._disabled_cmds = self._options.get('disabled_cmds', [])
        # Show only these mimes
        self._only_mimes    = self._options.get('onlyMimes', self._only_mimes)
        # Default ACE
        self._default_ace = {
            'read'   : self._options['default_ace'].get('read', True),
            'write'  : self._options['default_ace'].get('write', False),
            'locked' : False,
            'hidden' : False
        }
        # Root ACE
        self._acl.append( {
            'pattern' : r'^{0}$'.format(re.escape(self._sep)),
            'locked' : True,
            'hidden' : False
        })
        # ACEs of other dirs/files
        if self._options['acl']:
            for ace in self._options['acl']:
                # ACE must contain pattern and at least one rule
                if 'pattern' in ace and len(ace) > 1:
                    self._acl.append(ace)
        # Access policy
        self._access_policy = self._options['access_policy']
        # Name policy
        self.name_policy = self._options.get('name_policy', r'^[^_.]')
        # Quota
        self._max_size = self._options.get('max_size', 5*1024*1024) # Default 20MB

    def _init_volume_id(self):
        # XXX Generating ID automatically by incrementing a class variable is not
        # XXX threadsafe!
        if not 'id' in self._options:
            raise exc.FinderError(exc.PYM_ERROR_MISSING_VOL_ID)
        self._volume_id = '{0}{1}_'.format(
            self.__class__.DRIVER_ID, self._options['id'])
        self._is_mounted = True

    def _check_required_options(self, opts):
        if not 'path' in opts or not opts['path']:
            raise exc.FinderError(exc.PYM_ERROR_PATH_UNDEFINED)

    # ===[ PUBLIC API ]=======

    def stat_file(self, hash_):
        """
        Returns file info.
        """
        return self.stat(self.decode(hash_))

    def stat_dir(self, hash_, resolveLink=False):
        """
        Returns folder info.
        """
        stat = self.stat_file(hash_)
        if resolveLink and 'thash' in stat:
            stat = self.stat_file(stat['thash'])
        if stat['mime'] != 'directory' or self.is_hidden(stat):
            raise exc.FinderError(exc.ERROR_DIR_NOT_FOUND)
        return stat

    def stat(self, path):
        """
        Returns info for given path.
        """
        stat = self._stat(path)

        stat['hash'] = self.encode(path)
        is_root = (path == self._root_path)
        if is_root:
            stat['volumeid'] = self.volume_id
            if self._root_alias:
                stat['name'] = self._root_alias
            else:
                stat['name'] = self._basename(path)
        else:
            if not 'name' in stat:
                stat['name'] = self._basename(path)
            if not 'phash' in stat:
                stat['phash'] = self.encode(self._dirname(path))

        if not 'mime' in stat:
            stat['mime'] = self.mimetype(stat['name'])
        if not 'size' in stat or stat['mime'] == 'directory':
            stat['size'] = 0

        stat['read'] = int(self.acl_perm(path=path, perm_name='read', val=stat.get('read', None)))
        stat['write'] = int(self.acl_perm(path=path, perm_name='write', val=stat.get('write', None)))

        if is_root:
            stat['locked'] = 1
        elif self.acl_perm(path=path, perm_name='locked', val=self.is_locked(stat)):
            stat['locked'] = 1
        elif 'locked' in stat:
            del stat['locked']

        if is_root and 'hidden' in stat:
            del stat['hidden']
        elif self.acl_perm(path=path, perm_name='hidden', val=self.is_hidden(stat)) \
                or not self.mime_accepted(stat['mime']):
            stat['hidden'] = 0 if is_root else 1
        elif 'hidden' in stat:
            del stat['hidden']

        if stat['read'] and not self.is_hidden(stat):
            if stat['mime'] == 'directory':
                #for dir - check for subdirs
                if self._options['checkSubfolders']:
                    if 'dirs' in stat:
                        if stat['dirs']:
                            stat['dirs'] = 1
                        else:
                            del stat['dirs']
                    elif 'alias' in stat and 'target' in stat:
                        stat['dirs'] = int(self._has_subdirs(stat['target']))
                    elif self._has_subdirs(path):
                        stat['dirs'] = 1
                else:
                    stat['dirs'] = 1
            else:
                #for files - check for thumbnails
                pass # Not implemented yet
        
        if 'alias' in stat and 'target' in stat:
            stat['thash'] = self.encode(stat['target'])
            del stat['target']

        return stat
   
    def update_quota(self):
        self._update_quota()

    # Renamed from scandir()
    def ls_stats_hash(self, hash_):
        """
        Returns list of stats of items in given hash.
        """
        if not self.stat_dir(hash_)['read']:
            raise exc.FinderError(exc.ERROR_PERM_DENIED)
        return self.ls_stats(self.decode(hash_))

    # Renamed from getScandir()
    def ls_stats(self, path):
        """
        Returns list of stats of items in given path.

        Items that have permission ``hidden`` set or whose mime-type is
        forbidden, are not listed.
        """
        stats = [ st for st in self._ls_stats(path)
            if not self.is_hidden(st) 
                and self.mime_accepted(st['mime'])
        ]
        return stats

    # Renamed from ls()
    def ls_names_hash(self, hash_):
        """
        Returns list of names of items inside given hash.
        """
        if not self.stat_dir(hash_)['read']:
            raise exc.FinderError(exc.ERROR_PERM_DENIED)
        path = self.decode(hash_)
        items = [ stat['name'] for stat in self.ls_stats(path)
            if not self.is_hidden(stat) and self.mime_accepted(stat['mime']) ]
        return items

###    def ls(self, path):
###        # Make sure we are not accidentally called with a hash instead of path
###        assert path.startswith(self.volume_id) == False

    def tree_stats(self, hash_='', depth=0, exclude=None):
        """
        Return subfolders for required folder or False on error
        """
        if not depth:
            depth = self._tree_depth
        if exclude:
            exclude = self.decode(exclude)
        path = self.decode(hash_) if hash_ else self._root_path
        
        stat = self.stat(path)
        if stat['mime'] != 'directory':
            return []
        
        dirs = self._tree_stats(path, depth, exclude)
        dirs[:0] = [ stat ]
        return dirs

    def mkdir(self, cur, name):
        """
        Creates directory and returns its stat

        :param cur: Hash of current directory
        :param name: Name of subdirectory to create
        """

        # Check that command is not disabled
        self.check_command('mkdir')
        # Check that name is valid
        self.check_name(name)

        # Need write permission on current dir 
        cur_stat = self.stat_dir(cur)
        if not self.is_writeable(cur_stat):
            raise exc.FinderError(exc.ERROR_PERM_DENIED)
        
        # Do not overwrite existing object
        cur_path = self.decode(cur)
        new_path = self._joinpath(cur_path, name)
        try:
            self.stat(new_path)
            exists = True
        except exc.FinderError:
            exists = False
        if exists:
            raise exc.FinderError(exc.ERROR_EXISTS, name)

        # Create subdir and return its stat
        return self.stat( self._mkdir(cur_path, name) )

    def mkfile(self, cur, name):
        """
        Creates file and returns its stat

        :param cur: Hash of current directory
        :param name: Name of file to create
        """

        # Check that command is not disabled
        self.check_command('mkfile')
        # Check that name is valid
        self.check_name(name)

        # Need write permission on current dir 
        cur_stat = self.stat_dir(cur)
        if not self.is_writeable(cur_stat):
            raise exc.FinderError(exc.ERROR_PERM_DENIED)
        
        # Do not overwrite existing object
        cur_path = self.decode(cur)
        new_path = self._joinpath(cur_path, name)
        try:
            self.stat(new_path)
            exists = True
        except exc.FinderError:
            exists = False
        if exists:
            raise exc.FinderError(exc.ERROR_EXISTS, name)

        # Create file and return its stat
        return self.stat( self._mkfile(cur_path, name) )
    
    def paste(self, src_vol, src, dst, cut=False):
        """
        Paste file to destination

        :param src_vol: Source volume
        :param src: Hash of source dir/file
        :param dst: Hash of destination dir/file
        :param cut: True=Move (Source is deleted), False=Copy
        """
        # Check that command is not disabled
        if cut:
            self.check_command('move')
        else:
            self.check_command('copy')
        
        src_stat = self.stat_file(src)
        src_path = self.decode(src)
        dst_stat = self.stat_dir(dst)
        dst_path = self.decode(dst)
        
        # Check quota
        if self.free_size < src_stat['size']:
            raise exc.FinderError(exc.PYM_ERROR_QUOTA_EXCEEDED.format(self.free_size))
        # Must have write permission on destination and read on source
        if not self.is_writeable(dst_stat) or not self.is_readable(src_stat):
            raise exc.FinderError(exc.ERROR_PERM_DENIED)
        # On move, do not allow to remove source if source or one of its
        # children is locked
        if cut:
            if src_vol.find_child_by_perm(src_path, 'locked'):
                raise exc.FinderError(exc.ERROR_PERM_DENIED)
        # If dst subitem exists...
        dst_fullpath = self._joinpath(dst_path, src_stat['name'])
        can_overwrite = False
        try:
            dstfull_stat = self.stat(dst_fullpath)
        except exc.FinderError:
            dstfull_stat = False # Dst does not exist
        else:
            # Can overwrite dstfull if ...
            can_overwrite = (
                # ... have write permission on dstfull 
                self.is_writeable(dstfull_stat)
                # ... overwriting is allowed in options
                and self._options.get('copyOverwrite', False)
                # ... neither dstfull nor any of its children are locked
                and not self.find_child_by_perm(dst_fullpath, 'locked', True)
                # ... and src and dstfull are of same type, i.e.
                #     do not replace file with dir or dir with file.
                and self.is_same_type(src_stat['mime'], dstfull_stat['mime'])
            )

        if dstfull_stat and can_overwrite:
            dst_name = self.unique_name(dst_path, src_stat['name'])
        else:
            dst_name = src_stat['name']
        
        # Copy/move inside current volume
        if (src_vol == self):
            if cut:
                added = self.stat(self.move(src_path, dst_path, dst_name))
                removed = src # Hash!
            else:
                added = self.stat(self.copy(src_path, dst_path, dst_name))
                removed = None
            return (added, removed)
        
        #copy/move from another volume
        raise NotImplementedError("Copying/Moving over different volumes is not yet implemented.")

    def move(self, src_path, dst_path, name):
        """
        Moves file or directory.

        :returns: Destination path.
        """
        return self._move(src_path, dst_path, name)

    def copy(self, src_path, dst_path, name):
        """
        Copies file or directory.

        :returns: Path to the newly created file or directory.
        """
        return self._copy(src_path, dst_path, name)

    def duplicate(self, hash_):
        """
        Create copy of item.

        Name of copy will be original name suffixed with "(copy #)", where "#"
        is a running number.
        """
        self.check_command('duplicate')
        
        path = self.decode(hash_)
        dir_ = self._dirname(path)
        new_name = self.unique_name(dir_, self._basename(path))

        # Check quota
        stat = self.stat(path)
        if self.free_size < stat['size']:
            raise exc.FinderError(exc.PYM_ERROR_QUOTA_EXCEEDED.format(self.free_size))
        # TODO check permission to create new item.

        return self.stat(self.copy(path, dir_, new_name))

    def remove(self, hash_):
        """
        Removes item.

        Only an empty directory gets removed.

        :param hash_: Hash of item to remove
        :returns: Full path of removed item
        """
        self.check_command('duplicate')
        path = self.decode(hash_)
        # TODO check permission to remove this item.
        return self.encode(self._remove(path))

    def upload(self, fo, dst):
        """
        Stores uploaded file.

        Object of uploaded file must have properties ``filename`` and
        ``file``, which is a file descriptor.

        :param fo: Object of uploaded file
        :param dst: Hash of destination directory
        """
        # Command "upload" allowed?
        self.check_command('upload')

        dst_dir_stat = self.stat_dir(dst)
        dst_dir_path = self.decode(dst)
        dst_fn = fo.filename

        # Filename OK?
        self.check_name(dst_fn)
        dst_f_path = self._joinpath(dst_dir_path, dst_fn)
        
        # Allowed to write into dst dir?
        if not self.is_writeable(dst_dir_stat):
            raise exc.FinderError(exc.ERROR_PERM_DENIED)
        # If file exists, allowed to overwrite?
        try:
            stat = self.stat(dst_f_path)
        except exc.FinderError:
            pass # File does not exist -> upload OK
        else:
            if (
                not self._options['uploadOverwrite']
                or not self.is_writeable(stat)
                or self.is_locked(stat)
            ):
                raise exc.FinderError(exc.ERROR_PERM_DENIED)

        # Check size
        def get_size(fd):
            fd.seek(0, os.SEEK_END) # Seek to the end of the file
            size = fd.tell() # Get the position of EOF
            fd.seek(0) # Reset the file position to the beginning
            return size
        sz = get_size(fo.file)
        if sz > self._upload_max_size:
            raise exc.FinderError(exc.ERROR_UPLOAD_FILE_SIZE)
        # Check quota
        if self.free_size < sz:
            raise exc.FinderError(exc.PYM_ERROR_QUOTA_EXCEEDED.format(self.free_size))

        # TODO Check mime types
        
        # Save file on volume and return its stat
        return self.stat( self._save_uploaded(fo.file, dst_dir_path, dst_fn) )

    def rename(self, target, name):
        """
        Renames item.

        :param target: Hash of item to rename
        :param name: New name
        :returns: 2-tuple:
                  [0] List of stats of added items,
                  [1] List of hashes of removed items
        """
        self.check_command('rename')
        src = self.decode(target)
        dst = self._joinpath(self._dirname(src), name)
        # Do not allow renaming to an existing item (which would be
        # overwritten)
        if self._exists(dst):
            raise exc.FinderError(exc.ERROR_EXISTS, name)
        added = self.stat(self._rename(src, dst))
        removed = target # Hash!
        return (added, removed)

    def file(self, target):
        """
        Returns file-like object and info for target as a dict.

        Key ``file`` is a file-like object, i.e. it sports methods like ``read()``
        etc. E.g. if volume driver is LocalFileSystem, ``file`` is a file
        descriptor of an open file.

        ``file`` is suitable to be attached to framework's response object to
        be streamed to client. E.g. for Pyramid::
        
            response.app_iter = finder.response['file']

        ``stat`` is the info as obtained from :meth:`~pym_elfinder.volume.volumedriver.VolumeDriver.stat()`.

        :param target: Hash of file
        :returns: Dict with keys ``file`` and ``stat``
        """
        # Command is enabled?
        self.check_command('file')
        path = self.decode(target)
        # Target exists?
        try:
            stat = self.stat(path)
        except exc.FinderError as e:
            raise exc.FinderNotFound(e)
        # Target is not a directory?
        if stat['mime'] == 'directory':
            raise exc.FinderNotFound()
        # Have read permission?
        if not self.is_readable(stat):
            raise exc.FinderAccessDenied()
        # Open target as file-like object
        try:
            fd = self._file(path)
        except exc.FinderError as e:
            raise exc.FinderNotFound(e)
        # Return result
        return dict(
            file = fd,
            stat = stat
        )

    def get_content(self, target):
        """
        :param target: Hash of file
        :returns: File content as bytes or, for text files, as str
        """
        # Command is enabled?
        self.check_command('get')
        path = self.decode(target)
        # Target exists?
        try:
            stat = self.stat(path)
        except exc.FinderError as e:
            raise exc.FinderError(exc.ERROR_FILE_NOT_FOUND, e)
        # Target is not a directory?
        if stat['mime'] == 'directory':
            raise exc.FinderError(exc.ERROR_NOT_FILE)
        # Have read permission?
        if not self.is_readable(stat):
            raise exc.FinderError(exc.ERROR_PERM_DENIED)
        # Get content
        if self.is_binary(stat):
            encoding = None
        else:
            encoding = 'UTF-8'
        return self._get_content(path, encoding=encoding)

    def put_content(self, target, content, mime=None):
        """
        Puts new content into existing file.

        :param target: Hash of file
        :param content: Contents to write into file; str for text files,
                         bytes for binary
        :param mime: ???
        :returns: Stat info of changed file
        """
        # Command is enabled?
        self.check_command('put')
        path = self.decode(target)
        # Check quota
        if self.free_size < len(content):
            raise exc.FinderError(exc.PYM_ERROR_QUOTA_EXCEEDED.format(self.free_size))
        # Target exists?
        # We allow only writing to an existing file, changing its content.
        try:
            stat = self.stat(path)
        except exc.FinderError as e:
            raise exc.FinderError(exc.ERROR_FILE_NOT_FOUND, e)
        # Target is not a directory?
        if stat['mime'] == 'directory':
            raise exc.FinderError(exc.ERROR_NOT_FILE)
        # Have write permission?
        if not self.is_writeable(stat):
            raise exc.FinderError(exc.ERROR_PERM_DENIED)
        # Put content
        if self.is_binary(stat):
            encoding = None
        else:
            encoding = 'UTF-8'
        return self.stat(self._put_content(path, content, encoding=encoding))


    # ===[ HELPERS ]=======

    def unique_name(self, path, name, suffix=" (copy #)"):
        """
        Returns a unique new name for given item.

        If a hashmark ('#') is present in ``suffix``, it is replaced by a
        running number.
        """
        name, ext = os.path.splitext(name)
        num = 0
        re_suff = re.escape(suffix).replace(r"\#", r"(\d+)") + "$"

        # Check whether name already has a suffix. If so, determine its number. 
        # Don't bother if suffix shall not contain a number.
        if '#' in suffix:
            m = re.match(re_suff, name)
            if m:
                num = int(m.group(1))

        # Remove old suffix from name
        name = re.sub(re_suff, '', name)
        # Build and append new suffix
        cnt = 0
        while True:
            num += 1
            new_name = name + suffix.replace("#", str(num)) + ext
            if not self._exists(self._joinpath(path, new_name)):
                return new_name
            cnt += 1
            if cnt >= 1000:
                raise exc.FinderError(exc.PYM_ERROR_UNIQUE_NAME, name)
        return name + ext
   
    def check_name(self, name):
        """
        Checks that given name conforms to a certain policy.

        Policy is set in options as either regular expression or callable.

        :raises: :class:`..exceptions.FinderError`
        """
        # Options must define a name policy
        if not self.name_policy:
           raise exc.FinderError(exc.PYM_ERROR_INVALID_NAME_POLICY)
        # Policy may be a regex
        if isinstance(self.name_policy, str):
            if not re.search(self.name_policy, name):
                raise exc.FinderError(exc.ERROR_INVALID_NAME)
        # ... or a callable
        elif isinstance(self.name_policy, Callable):
            self.name_policy(name) # Must raise ERROR_INVALID_NAME
        # ... if it's neither it is an error
        else:
            raise exc.FinderError(exc.PYM_ERROR_INVALID_NAME_POLICY)

    def check_command(self, cmd, exc_args=None):
        """
        Checks that command may be executed.

        At the moment, only checks that command is not disabled in options.

        :raises: :class:`..exceptions.FinderAccessDenied`
        """
        if exc_args is None:
            exc_args = []
        # Check that command is not diabled
        if cmd in self._disabled_cmds:
            raise exc.FinderAccessDenied(exc.ERROR_PERM_DENIED, cmd, exc_args)

    def debug_info(self):
        """Returns debug info for client."""
        return dict(id=self.volume_id, name=self.name(),
            quota="{0:,d} of {1:,d}".format(self.used_size, self.max_size))

    # Is function, not property. Child classes can override this more easily.
    def name(self):
        return __name__

    def find_child_by_perm(self, path, perm, val=None):
        """
        Returns nearest child (or self) that has given permission.

        Checks whether given path or one of its children has that permission
        set. If ``val`` is given, permission must have this value, if ``val``
        is omitted, just the presence of the permission is checked.

        :param path: Path of item where search starts
        :param perm: Name of permission
        :param val: A permission value
        :returns: Path of found item, or None
        """
        try:
            # Fetch info about given path
            stat = self.stat(path)
        except exc.FinderError:
            # If we have no info (because path does not exist or other error
            # occured) no child is found.
            return None

        # Check whether required perm is present, and optionally has required
        # value.
        if perm in stat:
            if val is None:
                return path
            else:
                if stat[perm] == val:
                    return path

        # Given path did not match, shall we look further?

        # If given path is not a directory, we are done
        if stat['mime'] != 'directory':
            return None

        # Search path's children.
        children_stats = self.ls_stats(path)
        for stat in children_stats:
            child_path = self._joinpath(path, stat['name'])
            # Child is a directory, recurse.
            if stat['mime'] == 'directory':
                found = self.find_child_by_perm(child_path, perm, val)
                if found:
                    return found
            # Child is regular item
            else:
                if perm in stat:
                    if val is None:
                        return child_path
                    else:
                        if stat[perm] == val:
                            return child_path
        # Looked everywhere - found nothing
        return None

    
    def acl_perm(self, path, perm_name, val=None):
        """
        Checks whether item has requested permission.

        :param path: Path of dir or file
        :param name: Name of permission
        :param val: 
        """
        # Invalid perm name is undefined
        if not perm_name in self._default_ace:
            return None

        perm = None

        # Call access policy
        if self._access_policy:
            perm = self._access_policy(self, path, perm_name)
            if perm != None:
                return perm

        # Check ACL if no access policy set or access policy returned None
        # for given path.
        path = self._relpath(path).replace(self._sep, '/')
        path = '/%s' % path

        for ace in self._acl:
            if perm_name in ace and re.search(ace['pattern'], path):
                perm = ace[perm_name]
        
        # If permission is found, return it
        if perm is not None:
            return perm
        # ...else if prev setting is given, return that
        if val is not None:
            return val
        # ...else return default permission
        return self._default_ace[perm_name]

    def is_same_type(mime1, mime2):
        """
        Returns True if both args are directories or both are files.
        """
        return (
            (mime1 == 'directory' and mime2 == 'directory')
            or
            (mime1 != 'directory' and mime2 != 'directory')
        )

    def is_readable(self, stat=None):
        """
        Returns True if item is readable.

        Item is given as ``stat``. If left out, returns
        readability of volume.

        If attribute 'read' is missing, returns False.
        """
        if not stat:
            stat = self._stat(self._root_path)
        return stat.get('read', False)

    def is_writeable(self, stat=None):
        """
        Returns True if item is writeable.

        Item is given as ``stat``. If left out, returns
        writeability of volume.

        If attribute 'write' is missing, returns False.
        """
        if not stat:
            stat = self._stat(self._root_path)
        return stat.get('write', False)
    
    def is_hidden(self, stat=None):
        """
        Returns True if item is hidden.

        Item is given as ``stat``. If left out, returns
        hiddenness of volume.

        If attribute 'hidden' is missing, returns False.
        """
        if not stat:
            stat = self._stat(self._root_path)
        return stat.get('hidden', False)
    
    def is_locked(self, stat=None):
        """
        Returns True if item is locked.

        Item is given as ``stat``. If left out, returns
        lockedness of volume.

        If attribute 'locked' is missing, returns True.
        """
        if not stat:
            stat = self._stat(self._root_path)
        return stat.get('locked', True)

    def is_cmd_disabled(self, cmd):
        """
        Returns True if command is disabled by options.
        """
        return cmd in self._disabled_cmds


    def mimetype(self, path, name=''):
        """
        Returns mimetype of given path.
        """
        mime = self._mimetype(path)
        # Mime may be empty if e.g. the tested file is empty. And an empty
        # file we create e.g. with our mkfile()
        if not mime or mime in ['inode/x-empty', 'application/empty']:
            prev_mime = mime
            mime = self.mimetype_internal_detect(name if name else path)
            if not mime:
                mime = prev_mime
        return mime

    def mimetype_internal_detect(self, path):
        """
        Detect file mimetype using "internal" method
        """
        return mimetypes.guess_type(path)[0]
    
    def mime_accepted(self, mime, mimes=None, empty=True):
        """
        Return True if mime is in required mimes list
        """
        if mimes is None:
            mimes = []
        if not mimes:
            mimes = self._only_mimes
        if not mimes:
            return empty
        return (mime == 'directory'
            or 'all' in mimes
            or 'All' in mimes
            or mime in mimes
            or mime[0:mime.find('/')] in mimes
        )

    def is_binary(self, stat_or_mime):
        """
        Returns True if mime-type indicates binary type.

        :param stat_or_mime: A dict with stat info that has key "mime" or
                             mime-type as string
        :returns: True/False
        """
        mime = stat_or_mime['mime'] if 'mime' in stat_or_mime else stat_or_mime
        return not mime.lower().startswith("text/")
    
    def get_open_init_options(self, hash_):
        """
        Return volume options required by client on command open-init
        """
        r = {
            'path' : self._aliaspath(self.decode(hash_)),
            'url' : self._url,
            'tmbUrl' : self._tmb_url,
            'disabled' : self._disabled_cmds,
            'separator' : self._sep,
            'copyOverwrite' : self._options['copyOverwrite'],
            'archivers' : {}
        }
        try:
            r['archivers']['create'] = list( self._archivers['create'].keys() )
        except (TypeError, KeyError):
            r['archivers']['create'] = None
        try:
            r['archivers']['extract']= list( self._archivers['extract'].keys() )
        except (TypeError, KeyError):
            r['archivers']['extract'] = None
        return r

    # ===[ PATH HANDLING ]=======

    def root_hash(self):
        """
        Returns hash of root path.
        """
        return self.encode(self._root_path)
    
    def default_hash(self):
        """
        Returns hash of default path.

        Default path is either ``root_path`` or `start_path``. The latter is not
        implemented yet.
        """
        return self.encode(self._root_path)
    
    def encode(self, path):
        """
        Encodes path into hash.
        """
        # Make sure, path does not contain any '..'
        path = self._normpath(path)
        # Cut ROOT from path for security reasons; even if hacker decodes the
        # path he will not know the root. #files hashes will also be valid,
        # even if root changes.
        p = self._relpath(path)
        # If reqested root dir path is empty, then assign '/' as we
        # cannot leave it blank for crypt
        if not p:
            p = self._sep
        # Encrypt path and return hash
        hash_ = self.encrypt(p)
        # Hash is used as ID in HTML; that means it must contain vaild chars.
        # Make base64 html-safe and prepend volume ID.
        hash_ = b64encode(
                hash_.encode('utf-8')
            ).decode('ascii') \
            .translate(
                str.maketrans('+/=', '-_.')
            )
        # Remove dots '.' at the end (used to be '=' in base64, before the
        # translation)
        hash_ = hash_.rstrip('.')
        # Prepend volume ID to make hash unique
        return self.volume_id + hash_
    
    def decode(self, hash_):
        """
        Decodes path from hash.
        """
        if hash_ == '':
            # Open-init may call us with empty hash.
            return ''
        if not hash_.startswith(self.volume_id):
            raise exc.FinderError(
                "Invalid hash '{0}'. Does not start with volume ID '{1}'".format(
                    hash_, self.volume_id))
        # Cut volume ID after it was prepended in encode
        h = hash_[len(self.volume_id):]
        # Replace HTML safe base64 to normal
        h = h.translate(str.maketrans('-_.', '+/='))
        # Fill with '='
        h += "=" * ((4 - len(h) % 4) % 4)
        h = b64decode(h.encode('ascii')).decode('utf-8')
        # Decrypt hash and return path
        path = self.decrypt(h) 
        # Make sure, path does not contain any '..'
        path = self._normpath(path)
        # Prepend ROOT to path after it was cut in encode
        return self._abspath(path) 
    
    def encrypt(self, path):
        """
        Returns encrypted path.

        .. todo:: Implement path encryption
        """
        # TODO Implement path encryption
        return path
    
    def decrypt(self, hash_):
        """
        Returns uncrypted path.

        .. todo:: Implement path decryption
        """
        # TODO Implement path decryption
        return hash_

    # ===[ PROPERTIES ]=======

    @property
    def driver_id(self):
        """Driver ID. Used as part of volume ID."""
        return self._driver_id

    @property
    def volume_id(self):
        """Volume ID. Used as prefix of file hashes."""
        return self._volume_id

    @property
    def is_mounted(self):
        """Tells whether this volume is properly mounted or not."""
        return self._is_mounted

    @property
    def max_size(self):
        """Returns max quota in bytes."""
        return self._max_size

    @property
    def used_size(self):
        """
        Returns used size on bytes.
        
        Is calculated on invocation of a command.
        """
        return self._used_size

    @property
    def free_size(self):
        """Returns free size in bytes."""
        return self._max_size - self._used_size

    DEFAULT_OPTIONS = {
            'id' : '',
            #root directory path
            'path' : '',
            #root url, not set to disable sending URL to client (replacement for old "fileURL" option)
            'URL' : '',
            #open this path on initial request instead of root path
            'startPath' : '',
            #how many subdirs levels return per request
            # Renamed from 'treeDeep' : 1,
            'tree_depth' : 1,
            #directory separator. required by client to show paths correctly
            'separator' : os.sep,
            #directory for thumbnails
            'tmbPath' : '.tmb',
            #mode to create thumbnails dir
            'tmbPathMode' : 0o777,
            #thumbnails dir URL. Set it if store thumbnails outside root directory
            'tmbURL' : '',
            #thumbnails size (px)
            'tmbSize' : 48,
            #thumbnails crop (True - crop, False - scale image to fit thumbnail size)
            'tmbCrop' : True,
            #thumbnails background color (hex #rrggbb or 'transparent')
            'tmbBgColor' : '#ffffff',
            #on paste file -  if True - old file will be replaced with new one, if False new file get name - original_name-number.ext
            'copyOverwrite' : True,
            #if True - join new and old directories content on paste
            'copyJoin' : True,
            #on upload -  if True - old file will be replaced with new one, if False new file get name - original_name-number.ext
            'uploadOverwrite' : True,
            #filter mime types to show
            'onlyMimes' : [],
            #mimetypes allowed to upload
            'uploadAllow' : [],
            #mimetypes not allowed to upload
            'uploadDeny' : [],
            #order to proccess uploadAllow and uploadDeny options
            'uploadOrder' : ['deny', 'allow'],
            #maximum upload file size. NOTE - this is size for every uploaded files
            #'uploadMaxSize' : 0,
            #files dates format. CURRENTLY NOT IMPLEMENTED
            'dateFormat' : 'j M Y H:i',
            #files time format. CURRENTLY NOT IMPLEMENTED
            'timeFormat' : 'H:i',
            #if True - every folder will be check for children folders, otherwise all folders will be marked as having subfolders
            'checkSubfolders' : True,
            #allow to copy from this volume to other ones?
            'copyFrom' : True,
            #allow to copy from other volumes to this one?
            'copyTo' : True,
            #list of commands disabled on this root
            # Renamed from "disabled"
            'disabled_cmds' : [],
            #regexp or function name to validate new file name
            # Renamed from "acceptedName"
            'name_policy' : r'^[^_.]',
            #callable to control file permissions
            # Renamed from 'accessControl'
            'access_policy': None,
            #default permissions. not set hidden/locked here - take no effect
            # Renamed from 'defaults'
            'default_ace' : {
                'read' : True,
                'write' : True
            },
            #files attributes
            # Is in fact the ACL
            # Renamed from 'attributes'
            'acl': [],
            #Allowed archive's mimetypes to create. Leave empty for all available types.
            'archiveMimes' : [],
            #Manual config for archivers. See example below. Leave empty for auto detect
            'archivers' : {},
        }
