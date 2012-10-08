# -*- coding: utf-8 -*-

ERROR_ACCESS_DENIED = 'errAccess'
ERROR_ARCHIVE = 'errArchive'
ERROR_ARCHIVE_TYPE = 'errArcType'
ERROR_ARC_MAXSIZE = 'errArcMaxSize'
ERROR_ARC_SYMLINKS = 'errArcSymlinks'
ERROR_CONF = 'errConf'
ERROR_CONF_NO_JSON = 'errJSON'
ERROR_CONF_NO_VOL = 'errNoVolumes'
ERROR_COPY = 'errCopy'
ERROR_COPY_FROM = 'errCopyFrom'
ERROR_COPY_ITSELF = 'errCopyInItself'
ERROR_COPY_TO = 'errCopyTo'
ERROR_DIR_NOT_FOUND = 'errFolderNotFound'
ERROR_EXISTS = 'errExists' #'File named "$1" already exists.'
ERROR_EXTRACT = 'errExtract'
ERROR_FILE_NOT_FOUND = 'errFileNotFound' #'File not found.'
ERROR_INVALID_NAME = 'errInvName' #'Invalid file name.'
ERROR_INV_PARAMS = 'errCmdParams'
ERROR_LOCKED = 'errLocked' #'"$1" is locked and can not be renamed, moved or removed.'
ERROR_MKDIR = 'errMkdir'
ERROR_MKFILE = 'errMkfile'
ERROR_MOVE  = 'errMove'
ERROR_NETMOUNT = 'errNetMount'
ERROR_NETMOUNT_FAILED = 'errNetMountFailed'
ERROR_NETMOUNT_NO_DRIVER = 'errNetMountNoDriver'
ERROR_NOT_ARCHIVE = 'errNoArchive'
ERROR_NOT_DIR = 'errNotFolder'
ERROR_NOT_FILE = 'errNotFile'
ERROR_NOT_REPLACE = 'errNotReplace' #Object "$1" already exists at this location and can not be replaced with object of another type.
ERROR_NOT_UTF8_CONTENT  = 'errNotUTF8Content'
ERROR_OPEN = 'errOpen'
ERROR_PERM_DENIED = 'errPerm'
ERROR_RENAME = 'errRename'
ERROR_REPLACE = 'errReplace' #'Unable to replace "$1".'
ERROR_RESIZE = 'errResize'
ERROR_RM = 'errRm' #'Unable to remove "$1".'
ERROR_RM_SRC = 'errRmSrc' #'Unable remove source file(s)'
ERROR_SAVE = 'errSave'
ERROR_TRGDIR_NOT_FOUND = 'errTrgFolderNotFound' #'Target folder "$1" not found.'
ERROR_UNKNOWN_CMD = 'errUnknownCmd'
ERROR_UNKNOWN = 'errUnknown'
ERROR_UNSUPPORT_TYPE = 'errUsupportType'
ERROR_UPLOAD = 'errUpload' #'Upload error.'
ERROR_UPLOAD_FILE = 'errUploadFile' #'Unable to upload "$1".'
ERROR_UPLOAD_FILE_MIME = 'errUploadMime' #'File type not allowed.'
ERROR_UPLOAD_FILE_SIZE = 'errUploadFileSize' #'File exceeds maximum allowed size.'
ERROR_UPLOAD_NO_FILES = 'errUploadNoFiles' #'No files found for upload.'
ERROR_UPLOAD_TOTAL_SIZE = 'errUploadTotalSize' #'Data exceeds the maximum allowed size.'
ERROR_UPLOAD_TRANSFER = 'errUploadTransfer' #'"$1" transfer error.'

PYM_ERROR_VOLUME_NOT_FOUND = 'Volume not found'
PYM_ERROR_VOLUME_ID_NOT_FOUND = 'Volume ID not found'
PYM_ERROR_PATH_UNDEFINED = 'Path undefined'
PYM_ERROR_NOT_AN_IMAGE = 'This is not an image'
PYM_ERROR_EXTRACT_ARCHIVE_FAILED = 'Could not extract archive'
PYM_ERROR_INVALID_ARCHIVE = 'Could not extract archive'
PYM_ERROR_CREATE_ARCHIVE_FAILED = 'Could not extract archive'
PYM_ERROR_RESIZE_IMAGE_FAILED = 'Could not resize image'


class FinderError(Exception):
    """General exception class for elFinder.

    FinderError, like Exception, accepts a list of positional arguments.
    These are treated as in Exception; additional keyword arguments may be
    passed. These can be retrieved later by the exception handler.

    With these keyword arguments it is possible on raising an exception to
    specify special HTTP response headers (key ``headers`` as dict), some
    debug info (key ``debug``) etc.

    Keyword arguments can later be retrieved as properties of the exception
    instance, e.g. ``e.headers`` or ``e.debug``
    """
    
    def __init__(self, *args, **kw):
        super().__init__(*args)
        self.kw = kw

    def __getattr__(self, name):
        try:
            return self.kw[name]
        except KeyError as e:
            raise AttributeError(e)

    def __str__(self):
        s = self.__class__.__name__ + "("
        if self.args:
            s += str(self.args).strip("()")
        if self.kw:
            s += ", " + str(self.kw).strip("{}")
        s += ")"
        return s

    @property
    def response(self):
        """Returns error messages as error data for elFinder client.

        :returns: Dict {'error': [ list of strings ]}
        """
        errors = []
        for msg in self.args:
            if isinstance(msg, str):
                errors.append(msg)
            else:
                try:
                    errors += msg
                except TypeError:
                    errors.append(str(msg))
        if not errors:
            errors = [ ERROR_UNKNOWN ]
        return dict(error=errors)

    @property
    def headers(self):
        """Special HTTP headers to send as response.

        :returns: Dict of HTTP headers or None
        """
        try:
            return self.kw['headers']
        except KeyError:
            return None
