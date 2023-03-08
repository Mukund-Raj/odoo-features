from odoo import models, fields, api
from odoo.tools import human_size
import base64
import os
import logging

_logger = logging.getLogger(__name__)


class SaveAttachmentInBinary(models.Model):
    """
    The main purpose for this to directly save the binary data ,no base64 conversion,
    For this:
    context `bytes_attachment_data`: true
    """
    _inherit = 'ir.attachment'
    # this field to bypass odoo default base64 conversion and deal with binary data directly
    read_direct_binary = fields.Boolean('Direct read/write binary')

    @api.model
    def _file_read(self, fname, bin_size=False):
        full_path = self._full_path(fname)
        r = ''
        try:
            if bin_size:
                r = human_size(os.path.getsize(full_path))
            else:
                if self._context.get('read_direct_binary', False):
                    with open(full_path, 'rb') as fd:
                        r = fd.read()
                else:
                    with open(full_path, 'rb') as fd:
                        r = base64.b64encode(fd.read())

        except (IOError, OSError):
            _logger.info("_read_file reading %s", full_path, exc_info=True)
        return r

    @api.depends('store_fname', 'db_datas')
    def _compute_datas(self):
        bin_size = self._context.get('bin_size')
        for attach in self:
            if attach.store_fname:
                attach.datas = attach.with_context({'read_direct_binary': attach.read_direct_binary})._file_read(
                    attach.store_fname, bin_size)
            else:
                attach.datas = attach.db_datas

    @api.model
    def _file_write(self, value, checksum):
        if self._context.get('bytes_attachment_data'):
            # no need to convert the value into binary, it is already in binary
            bin_value = value
        else:
            bin_value = base64.b64decode(value)

        fname, full_path = self._get_path(bin_value, checksum)
        if not os.path.exists(full_path):
            try:
                with open(full_path, 'wb') as fp:
                    fp.write(bin_value)
                # add fname to checklist, in case the transaction aborts
                self._mark_for_gc(fname)
            except IOError:
                _logger.info("_file_write writing %s", full_path, exc_info=True)
        return fname

    def _get_datas_related_values(self, data, mimetype):
        # compute the fields that depend on datas
        if self._context.get('bytes_attachment_data'):
            bin_data = data
        else:
            bin_data = base64.b64decode(data) if data else b''
        values = {
            'file_size': len(bin_data),
            'checksum': self._compute_checksum(bin_data),
            'index_content': self._index(bin_data, mimetype),
            'store_fname': False,
            'db_datas': data,
        }
        if data and self._storage() != 'db':
            values['store_fname'] = self._file_write(data, values['checksum'])
            values['db_datas'] = False
        return values
