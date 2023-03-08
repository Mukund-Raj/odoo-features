import os
import shutil
import tempfile
import json
import odoo.tools
import logging

_logger = logging.getLogger(__name__)
from decorator import decorator
from odoo.exceptions import AccessDenied


def my_check_db_management_enabled(method):
    def if_db_mgt_enabled(method, self, *args, **kwargs):
        if not odoo.tools.config['list_db']:
            _logger.error('Database management functions blocked, admin disabled database listing')
            raise AccessDenied()
        return method(self, *args, **kwargs)

    return decorator(if_db_mgt_enabled, method)


check_db_management_enabled = my_check_db_management_enabled


def get_db_backup_path(db_name):
    assert db_name != '' or db_name is not False
    try:
        # path where odoo stores most of his stuff
        # data dir is default local/share/Odoo
        data_dir = odoo.tools.config['data_dir']
        # join it with backups folder
        backups_path = os.path.join(data_dir, 'backups', db_name)
        if not os.path.exists(backups_path):
            os.makedirs(backups_path)
        return backups_path
    except Exception as e:
        _logger.critical(f'Error occurred {str(e)}')
        raise ValueError('Backup path not found')


def dump_db_manifest(cr):
    pg_version = "%d.%d" % divmod(cr._obj.connection.server_version / 100, 100)
    cr.execute("SELECT name, latest_version FROM ir_module_module WHERE state = 'installed'")
    modules = dict(cr.fetchall())
    manifest = {
        'odoo_dump': '1',
        'db_name': cr.dbname,
        'version': odoo.release.version,
        'version_info': odoo.release.version_info,
        'major_version': odoo.release.major_version,
        'pg_version': pg_version,
        'modules': modules,
    }
    return manifest


def dump_sql_db(db_name, stream, backup_format='zip'):
    """Dump database `db` into file-like object `stream` if stream is None
    return a file object with the dump """
    _logger.info('DUMP DB: %s format %s', db_name, backup_format)

    cmd = ['pg_dump', '--no-owner']
    cmd.append(db_name)

    if backup_format == 'zip':
        with odoo.tools.osutil.tempdir() as dump_dir:
            with open(os.path.join(dump_dir, 'manifest.json'), 'w') as fh:
                db = odoo.sql_db.db_connect(db_name)
                with db.cursor() as cr:
                    json.dump(dump_db_manifest(cr), fh, indent=4)
            cmd.insert(-1, '--file=' + os.path.join(dump_dir, 'dump.sql'))
            odoo.tools.exec_pg_command(*cmd)
            if stream:
                odoo.tools.osutil.zip_dir(dump_dir, stream, include_dir=False)
            else:
                t = tempfile.TemporaryFile()
                odoo.tools.osutil.zip_dir(dump_dir, t, include_dir=False,
                                          fnct_sort=lambda file_name: file_name != 'dump.sql')
                t.seek(0)
                return t
    else:
        cmd.insert(-1, '--format=c')
        stdin, stdout = odoo.tools.exec_pg_command_pipe(*cmd)
        if stream:
            shutil.copyfileobj(stdout, stream)
        else:
            return stdout


def get_size_format(b, factor=1024, suffix="B"):
    """
    Scale bytes to its proper byte format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if b < factor:
            return f"{b:.2f}{unit}{suffix}"
        b /= factor
    return f"{b:.2f}Y{suffix}"


def get_directory_size(directory):
    """Returns the `directory` size in bytes."""
    total = 0
    try:
        # print("[+] Getting the size of", directory)
        for entry in os.scandir(directory):
            if entry.is_file():
                # if it's a file, use stat() function
                total += entry.stat().st_size
            elif entry.is_dir():
                # if it's a directory, recursively call this function
                total += get_directory_size(entry.path)
    except NotADirectoryError:
        # if `directory` isn't a directory, get the file size then
        return os.path.getsize(directory)
    except PermissionError:
        # if for whatever reason we can't open the folder, return 0
        return 0
    return total


def dump_filestore(db_name, stream, backup_format='zip'):
    with odoo.tools.osutil.tempdir() as dump_dir:
        if backup_format == 'zip':
            filestore = odoo.tools.config.filestore(db_name)
            if os.path.exists(filestore):
                shutil.copytree(filestore, os.path.join(dump_dir, 'filestore'))
            if stream:
                # size = get_directory_size(filestore)
                # size_in_mb = get_size_format(size,suffix='M')
                odoo.tools.osutil.zip_dir(dump_dir, stream, include_dir=False)
                _logger.info('Filestore zipped')
            else:
                t = tempfile.TemporaryFile()
                odoo.tools.osutil.zip_dir(dump_dir, t, include_dir=False,
                                          fnct_sort=lambda file_name: file_name != 'dump.sql')
                t.seek(0)
                return t
