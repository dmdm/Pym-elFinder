# coding: utf-8

from importlib import import_module
import time

from . import exceptions as exc
from . import API_VERSION

class Finder:

    COMMANDS = {
        'open' : { 'target' : False, 'tree' : False, 'init' : False, 'mimes' : False },
        'ls' : { 'target' : True, 'mimes' : False , '__func__' : 'ls_hash'},
        'tree' : { 'target' : True , '__func__' : 'tree_stats'},
        'parents' : { 'target' : True },
        'tmb' : { 'targets' : True },
        'file' : { 'target' : True, 'download' : False, 'request' : False },
        'size' : { 'targets' : True },
        'mkdir' : { 'target' : True, 'name' : True },
        'mkfile' : { 'target' : True, 'name' : True, 'mimes' : False },
        'rm' : { 'targets' : True },
        'rename' : { 'target' : True, 'name' : True, 'mimes' : False },
        'duplicate' : { 'targets' : True },
        'paste' : { 'dst' : True, 'targets' : True, 'cut' : False, 'mimes' : False },
        'upload' : { 'target' : True, 'FILES' : True, 'mimes' : False, 'html' : False },
        'get' : { 'target' : True },
        'put' : { 'target' : True, 'content' : '', 'mimes' : False },
        'archive' : { 'targets' : True, 'type_' : True, 'mimes' : False },
        'extract' : { 'target' : True, 'mimes' : False },
        'search' : { 'q' : True, 'mimes' : False },
        'info' : { 'targets' : True, 'options': False },
        'dim' : { 'target' : True },
        'resize' : {'target' : True, 'width' : True, 'height' : True, 'mode' : False, 'x' : False, 'y' : False, 'degree' : False },
        'netmount'  : { 'protocol' : True, 'host' : True, 'path' : False, 'port' : False, 'user' : True, 'pass' : True, 'alias' : False, 'options' : False}
    }

    def __init__(self, opts, cache, session=None):
        # ---[ private attribs ]-------
        self._opts = opts
        self._cache = cache
        self._session = session
        self._cmd = None
        self._cmd_args = None
        self._surplus_args = None
        self._headers = None
        self._response = None
        self._exception = None
        self._time = time.time()
        # ---[ public attribs ]-------
        self.debug = False
        """
        Debug mode.
        """
        self.mount_errors = None
        """
        List of exceptions that may have occured during mounting the volumes.
        """
        self.upload_error = None
        """
        Exception that occured during upload.
        """
        self.volumes = dict() 
        """
        Dict of mounted volumes, key is volume ID.
        """
        self.default_volume = None
        """
        Default volume.
        """
        self.respond_exceptions = False
        """
        Tells whether messages of nested exceptions are sent to client or not.

        Nested exceptions may be OSError, and displaying them in the client
        exposes full path information!
        """

    def mount_volumes(self):
        self.volumes = {}
        self.mount_errors = []
        for root_opts in self._opts['roots']:
            # Import driver
            driver = root_opts['driver']
            try:
                if isinstance(driver, str):
                    driver_module = import_module(driver)
                else:
                    driver_module = import_module(driver[0], package=driver[1])
            except ImportError as e:
                self.mount_errors.append(e)
                continue
            # Create instance of volume
            volume = driver_module.Driver(self)
            # Mount volume
            try:
                volume.mount(root_opts)
            except exc.FinderError as e:
                self.mount_errors.append(e)
                continue
            self.volumes[volume.volume_id] = volume
            # First root in opts becomes default volume
            if not self.default_volume and volume.is_readable():
                self.default_volume = volume
        if self.mount_errors:
            pass # TODO Log mount errors
        return (len(self.mount_errors) > 0)

    def run(self, cmd, cmd_args, **kw):
        self._response = {}
        self._headers = []
        self._exception = None
        try:
            # Execute command
            result = self.run_command(cmd, cmd_args)
            if 'headers' in result:
                self._headers = result['headers']
                del result['headers']
            self._response = result
        except exc.FinderError as e:
            # TODO Log error
            self._response = e.build_response(
                respond_exceptions=self.respond_exceptions)
            if e.headers:
                self._headers = e.headers
            self._exception = e
            # Reraise
            raise

    # ===[ COMMAND HANDLING ]=======
    
    def run_command(self, cmd, cmd_args):
        """Checks and runs given command and returns result dict.
        """
        if not self.volumes:
            raise exc.FinderError("No volumes mounted. Maybe you forgot to call finder.mount_volumes()?")
        self.check_command(cmd, cmd_args)
        try:
            func = 'cmd_' + self.__class__.COMMANDS[cmd]['__func__']
        except KeyError:
            func = 'cmd_' + cmd
        result = getattr(self, func)(**cmd_args)
        if self.debug:
            result['debug'] = {
                'connector' : 'Pym-elFinder',
                'time' : time.time() - self._time,
                'upload' : self.upload_error,
                'volumes' : [],
                'mountErrors' : self.mount_errors
            }
            for id_, volume in self.volumes.items():
                result['debug']['volumes'].append(volume.debug_info())
        return result

    def check_command(self, cmd, cmd_args):
        """Checks validity of command and its arguments.

        After the check, finder's properties ``cmd``, ``cmd_args``
        and ``surplus_args`` are set.
        """
        # Check that command exists
        if not self.command_exists(cmd):
            raise exc.FinderError(exc.ERROR_UNKNOWN_CMD, cmd)
        # Allowed arguments
        args_def = self.command_args(cmd)
        # Check that command has all required arguments
        for arg, is_req in args_def.items():
            if arg.startswith('__'):
                continue
            if is_req and not arg in cmd_args:
                raise exc.FinderError(exc.ERROR_INV_PARAMS, cmd, arg)
        # Remove inapplicable arguments
        self._surplus_args = dict()
        for k, v in cmd_args.items():
            if k not in args_def:
                self._surplus_args[k] = v
        for k in self._surplus_args:
            del cmd_args[k]
        # Store cmd and args
        self._cmd = cmd
        self._cmd_args = cmd_args

    def command_exists(self, cmd):
        """Checks that command exists.
        
        A command exists if it is listed in ``Finder.COMMANDS``, and
        the finder instance has a callable attribute for it ('cmd_' + cmd).

        :returns: True/False
        """
        try:
            func = 'cmd_' + self.__class__.COMMANDS[cmd]['__func__']
        except KeyError:
            func = 'cmd_' + cmd
        return (cmd in self.COMMANDS
            and hasattr(self, func)
            and callable(getattr(self, func))
        )

    def command_args(self, cmd):
        """Returns arguments info for given command.

        :param cmd: The command.
        :returns: Dict; keys are arguments, values tell whether argument is
                  required (True) or not (False). None if command does not
                  exist.
        """
        return self.COMMANDS[cmd] if self.command_exists(cmd) else None

    # =======================================================================

    # ===[ COMMANDS ]=======

    def cmd_open(self, target='', init=False, tree=False):
        """
        **Command**: Open a directory
        
        Return:
            An array with following elements:
                :cwd:          opened directory information
                :files:        opened directory content [and dirs tree if kwargs['tree'] is ``True``]
                :api:          api version (if kwargs['init'] is ``True``)
                :uplMaxSize:   The maximum allowed upload size (if kwargs['init'] is ``True``)
                :error:        on failed
        """
        if not init and not target:
            raise exc.FinderError(exc.ERROR_INV_PARAMS, 'open')
        hash_ = 'default folder' if init else '#' + target
        
        try:
            volume = self._volume_from_hash(target)
        except exc.FinderError as e:
            if init:
                volume = self.default_volume
            else:
                raise

        if init:
            try:
                cwd = volume.stat_dir(hash_=volume.default_hash(), resolveLink=True)
            except exc.FinderError as e:
                raise exc.FinderError(exc.ERROR_OPEN, hash_, e)
        else:
            try:
                cwd = volume.stat_dir(hash_=target, resolveLink=True)
            except exc.FinderError as e:
                raise exc.FinderError(exc.ERROR_OPEN, hash_, e)
        if not cwd['read']:
            raise exc.FinderError(exc.ERROR_OPEN, hash_, exc.ERROR_PERM_DENIED)

        files = []
        # Fetch complete tree spanning all volumes
        if tree:
            for id_ in self.volumes:
                files += self.volumes[id_].tree_stats(exclude=target)
        
        # Add items of CWD to files
        # XXX Why does this have try...except, and tree() above does not?
        try:
            for f in volume.ls_stats_hash(cwd['hash']):
                if f not in files:
                    files.append(f)
        except exc.FinderError as e:
            raise exc.FinderError(exc.ERROR_OPEN, cwd['name'], e)
        
        result = {
            'cwd' : cwd,
            'files' : files
        }

        if init:
            result['options'] = volume.get_open_init_options(target)
            result['api'] = API_VERSION
            result['netDrivers'] = [] # TODO list( self._netDrivers.keys() )
            result['uplMaxSize'] = '2M'

        return result

    def cmd_tree_stats(self, target):
        """
        Returns tree of subdirs of requested directory.
        
        :param target: Hash of directory
        :returns: Dict(tree=list(...))
        """
        volume = self._volume_from_hash(target)
        tree = volume.tree_stats(target)
        return dict(tree=tree)

    def cmd_ls_hash(self, target):
        """
        Returns list of item names in requested directory.
        
        :param target: Hash of directory
        :returns: Dict(list=list(...))
        """
        volume = self._volume_from_hash(target)
        names = volume.ls_names_hash(target)
        return dict(list=names)

    def cmd_mkdir(self, target, name):
        """
        Creates a new directory
        """
        volume = self._volume_from_hash(target)
        return dict(added=[volume.mkdir(target, name)])

    def cmd_mkfile(self, target, name):
        """
        Creates a new file
        """
        volume = self._volume_from_hash(target)
        return dict(added=[volume.mkfile(target, name)])

    def cmd_paste(self, targets, dst, cut=False, mimes=[]):
        """
        Copies or moves source items to destination.

        :param targets: List of source items.
        :param dst: Hash of destination
        :param cut: True=Move (i.e. remove source items after copy);
                    False=Copy
        :param mimes: Purpose?
        """
        # XXX TODO What about mimes?
        cut = bool(int(cut))
        result = dict(added=[], removed=[])
        dst_vol = self._volume_from_hash(dst)
        # "targets" are in fact the source items
        for src in targets:
            src_vol = self._volume_from_hash(src)
            added, removed = dst_vol.paste(src_vol, src, dst, cut)
            if added:
                result['added'].append(added)
            if removed:
                result['removed'].append(removed)
        return result

    def cmd_duplicate(self, targets):
        """
        Duplicates source items.

        Name of copy will be original name suffixed with "(copy #)", where "#"
        is a running number.

        :param targets: List of source items.
        """
        result = dict(added=[])
        # "targets" are in fact the source items
        for target in targets:
            vol = self._volume_from_hash(target)
            added = vol.duplicate(target)
            if added:
                result['added'].append(added)
        return result

    def cmd_rm(self, targets):
        """
        Removes items.

        Only empty diresctories will be removed.

        :param targets: List of items.
        """
        result = dict(removed=[])
        for target in targets:
            vol = self._volume_from_hash(target)
            removed = vol.remove(target)
            if removed:
                result['removed'].append(removed)
        return result




    # =======================================================================

    # ===[ HELPERS ]=======

    def _volume_from_hash(self, hash_):
        """
        Returns volume instance from given hash.

        :param hash_: Volume ID is extracted from this hash
        :returns: Instance of volume driver
        """
        for id_, v in self.volumes.items():
            if hash_.startswith(id_):
                return v
        raise exc.FinderError(exc.PYM_ERROR_VOLUME_NOT_FOUND, hash_)


    # ===[ PROPERTIES ]=======

    @property
    def headers(self):
        return self._headers

    @property
    def response(self):
        return self._response

    @property
    def exception(self):
        return self._exception

    @property
    def cache(self):
        return self._cache

