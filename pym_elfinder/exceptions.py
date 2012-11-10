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
PYM_ERROR_INVALID_NAME_POLICY = 'Name policy is invalid'
PYM_ERROR_UNIQUE_NAME = 'Failed to create unique name'
PYM_ERROR_INVALID_PATH = 'Invalid path'
PYM_ERROR_QUOTA_EXCEEDED = 'Quota exceeded ({0:,d} bytes free)'

HTTP_INTERNAL_SERVER_ERROR = 'HTTP/1.x 500 Internal Server Error'
HTTP_ACCESS_DENIED         = 'HTTP/1.x 403 Access Denied';
HTTP_NOT_FOUND             = 'HTTP/1.x 404 Not Found';

class FinderError(Exception):
    """
    General exception class for elFinder.

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
        if 'headers' in kw:
            self._headers = kw['headers']
            del kw['headers']
        else:
            self._headers = None
        if 'status' in kw:
            self._status = kw['status']
            del kw['status']
        else:
            self._status = None

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

    def build_response(self, respond_exceptions=False):
        """
        Returns error messages as error data for elFinder client.

        :param respond_exceptions: Tells whether text of nested exceptions
                                   is included in response or not.
        :returns: Dict {'error': [ list of strings ]}
        """
        errors = []
        for msg in self.args:
            if isinstance(msg, str):
                errors.append(msg)
            elif isinstance(msg, Exception) and not respond_exceptions:
                continue
            else:
                try:
                    errors += msg
                except TypeError:
                    errors.append(str(msg))
        if not errors:
            errors = [ ERROR_UNKNOWN ]
        return dict(error=errors)

    @property
    def status(self):
        """Special HTTP status to send as response.

        :returns: String with HTTP status, or None
        """
        return self._status

    @status.setter
    def status(self, v):
        self._status = v

    @property
    def headers(self):
        """Special HTTP headers to send as response.

        :returns: Dict of HTTP headers, or None
        """
        return self._headers

    @headers.setter
    def headers(self, v):
        self._headers = v


class FinderAccessDenied(FinderError):

    def __init__(self, *args, **kw):
        """
        Sets HTTP status to 403 ACCESS DENIED.
        """
        kw2 = dict(status=HTTP_ACCESS_DENIED).update(kw)
        super().__init__(ERROR_PERM_DENIED, *args, **kw2)


class FinderNotFound(FinderError):

    def __init__(self, *args, **kw):
        """
        Sets HTTP status to 404 NOT FOUND.
        """
        kw2 = dict(status=HTTP_NOT_FOUND).update(kw)
        super().__init__(ERROR_FILE_NOT_FOUND, *args, **kw2)

