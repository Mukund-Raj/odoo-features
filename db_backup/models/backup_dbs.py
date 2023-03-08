from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.service.db import exp_dump
import os
import shutil
import tempfile
import json
import odoo.tools
import logging
import base64

_logger = logging.getLogger(__name__)


class ToBackupDBs(models.Model):
    _name = 'backup.db'
    _inherit = 'mail.thread'

    _description = 'Backup dbs'

    name = fields.Char('DB Name', required=True, index=True, copy=False)
    # display name for db backup, we don't want to reveal the actual database name in notifications
    display_name = fields.Char(string='Display name')
    backups_to_keep = fields.Integer('Backups to keep', default=3)
    with_sql = fields.Boolean('SQL backup', default=True)
    with_data = fields.Boolean('File Store Backup')
    rel_all_backups = fields.One2many('db_backup.db_backup', 'backup_db', string='All Backups')
    # partners to notify, if backup created/failed
    backup_notified_partners = fields.Many2many('res.partner', string='Partners to notify')

    def action_start_db_backup(self):
        self.env['db_backup.db_backup'].process_backup_data(self)

    def notify_partners_for_backup(self, sql=False, filestore=False, parent_id=False):
        subject = f'Backup Created For {self.display_name}, Dated: {fields.Date.today().strftime("%d %B, %Y")}'
        body = f'<p>Backup generated </p' \
               f'</br></br> <ol><li> DB Content: {sql}</li><li> FS: {filestore}</li></ol>'
        admin_user = self.env.ref('base.user_admin')
        try:
            # get default from address can be false if mail-catchall address is not defined or the email_from
            # is not defined in the odoo config
            default_email_address = self.env['ir.mail_server']._get_default_from_address()

            # if default_email_address is  false then assign the current company email
            if not default_email_address:
                default_email_address = self.env.company.email
            email_from = f"{self.env.company.name}<{default_email_address}>"

            message = self.with_context(mail_no_update_email_from=True).message_notify(subject=subject, body=body,
                                                                                       partner_ids=self.backup_notified_partners.ids,
                                                                                       author_id=admin_user.partner_id.id,
                                                                                       email_from=email_from,
                                                                                       parent_id=parent_id
                                                                                       )
            return message.id or False

        except Exception as e:
            body = f"""
            <p class="text-danger"><b>Exception occur while notifying,</b></p>
            <p> {str(e)} </p> 
            """
            self.with_context(mail_no_update_email_from=True).message_notify(subject=subject, body=body,
                                                                             partner_ids=self.backup_notified_partners.ids,
                                                                             author_id=admin_user.partner_id.id,
                                                                             email_from=f"{self.env.company.name} <{self.env.company.email}>",
                                                                             parent_id=parent_id
                                                                             )
