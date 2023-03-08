# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.service.db import exp_dump
import os
import shutil
import tempfile
import json
import odoo.tools
import logging
import base64

_logger = logging.getLogger(__name__)
from decorator import decorator
from odoo.exceptions import ValidationError

from .backup_tools import dump_sql_db, dump_filestore, get_db_backup_path

base_download_url = '/backup/download'


class db_backup(models.Model):
    _name = 'db_backup.db_backup'
    _description = 'db_backup.db_backup'
    _order = 'create_date desc'

    backup_db = fields.Many2one('backup.db', string='Database Backup')
    backup_sql_file = fields.Char('Backup SQL file')
    backup_data_file = fields.Char('Backup data file')

    # type = fields.Selection([('sql','SQL'),('filestore','File Store')], string='Dump Type')

    # backup_file = fields.Many2many('ir.attachment', relation='all_file_db_backup', string='Db Backup')

    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, rec.backup_db.display_name))
        return result

    def create_sql_db_backup(self):
        """
        Pass in the database name for which you want the backup for
        :param name:database name
        :return:
        """
        try:
            t = tempfile.TemporaryFile(mode='w+b')
            dump_sql_db(self.backup_db.name, t)
            t.seek(0)
            if t:
                backup_path = get_db_backup_path(self.backup_db.name)
                ext = 'zip'
                file_name = "{:%Y_%m_%d_%H_%M_%S}_{db_name}_sql.{ext}".format(fields.Datetime.now(),
                                                                              db_name=self.backup_db.name,
                                                                              ext="zip" if ext == "zip" else ext)
                full_file_path = os.path.join(backup_path, file_name)
                with open(full_file_path, 'wb') as f:
                    shutil.copyfileobj(t, f)
                t.close()
                _logger.info('SQL backup  saved')
                self.write({'backup_sql_file': file_name})
                return True
        except Exception as e:
            _logger.critical(f'Backup creation failed with {(str(e))}')
            return False

    def action_create_file_store_backup(self):
        self.ensure_one()
        self.create_file_store_backup()

    def create_file_store_backup(self):
        """
        Pass in the database name for which you want the backup for
        :param name:database name
        :return:
        """
        try:
            assert self.backup_db
            t = tempfile.TemporaryFile(mode='w+b')
            dump_filestore(self.backup_db.name, t)
            t.seek(0)
            if t:
                backup_path = get_db_backup_path(self.backup_db.name)
                ext = 'zip'
                file_name = "{:%Y_%m_%d_%H_%M_%S}_{db_name}_dump.{ext}".format(fields.Datetime.now(),
                                                                               db_name=self.backup_db.name,
                                                                               ext="zip" if ext == "zip" else ext)
                full_file_path = os.path.join(backup_path, file_name)
                with open(full_file_path, 'wb') as f:
                    shutil.copyfileobj(t, f)
                t.close()
                _logger.info('File-store backup saved')
                self.write({'backup_data_file': file_name})
                return True
        except Exception as e:
            _logger.critical(f'Backup creation failed with {(str(e))}')
            return False

    def start_daily_backup(self):
        dbs = self.env['backup.db'].search([])
        self.process_backup_data(dbs)

    def process_backup_data(self, dbs):
        mail_parent_id = False
        for single_db in dbs:
            db_backup_rec = self.create({'backup_db': single_db.id})

            sql_backup = False
            filestore_backup = False

            # create sql backup
            if single_db.with_sql:
                sql_backup = db_backup_rec.create_sql_db_backup()
            # create file store backup
            if single_db.with_data:
                filestore_backup = db_backup_rec.create_file_store_backup()
            # when both are backup are done
            mail_parent_id = single_db.notify_partners_for_backup(sql=f'{sql_backup}/{single_db.with_sql}',
                                                                  filestore=f'{filestore_backup}/{single_db.with_data}',
                                                                  parent_id=mail_parent_id)

    def gc_collect_db_backups(self):
        """
        This method is responsible for marking db.backup record as GC, and deletes them
        :return:
        """
        # fetch all current DBs records for which the backup has been generated
        all_dbs = self.env['backup.db'].search([])
        for db in all_dbs:
            # find the total number of backups for that,field for that is  `backups_to_keep`
            top_n_backups = self.search([('backup_db', '=', db.id)], limit=db.backups_to_keep, order='create_date desc')
            to_gc_backups = self.search([('backup_db', '=', db.id)]) - top_n_backups
            self.unlink_actual_files(to_gc_backups)
            # unlink all to_gc_backups records from database
            to_gc_backups.unlink()

    def unlink_actual_files(self, records_to_unlink):
        """
        This method is actually responsible for deleting files from the directory
        """
        for backup_rec in records_to_unlink:
            backup_path = get_db_backup_path(backup_rec.backup_db.name)
            # full SQL path
            for backup_type in ['backup_sql_file', 'backup_data_file']:
                try:
                    backup_type_path = getattr(backup_rec, backup_type)
                    if not backup_type_path:
                        _logger.error("Continuing as no backup path found")
                        continue
                    backup_file_full_path = os.path.join(backup_path, backup_type_path)
                    if os.path.exists(backup_file_full_path) and os.path.isfile(backup_file_full_path):
                        try:
                            os.unlink(backup_file_full_path)
                            _logger.info(f'Backup File {backup_rec.backup_sql_file} checked & removed')
                        except (OSError, IOError) as e:
                            _logger.info(f'Error while GC Backups {str(e)}')
                    else:
                        _logger.info('File does not exist or is not a file')
                except Exception as e:
                    _logger.error(f"Error while deleting backups, {str(e)}")

    def unlink(self):
        # cleaning up files from os-level as well
        self.unlink_actual_files(self)
        super(db_backup, self).unlink()

    def file_not_found_exception(self):
        notification = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('File does not exist'),
                'type': 'danger',
                'message': 'No backup found',
                'sticky': (True),
            }
        }
        return notification

    def download_sql_backup(self):
        if not all([self.backup_sql_file, self.id]):
            return self.file_not_found_exception()

        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': f'{base_download_url}/{self.id}?db={self.backup_db.name}&backup={self.backup_sql_file}'
        }

    def download_filestore_backup(self):
        if not all([self.backup_data_file, self.id]):
            return self.file_not_found_exception()

        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': f'{base_download_url}/{self.id}?db={self.backup_db.name}&backup={self.backup_data_file}'
        }
