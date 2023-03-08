import mimetypes
import base64
import hashlib
import os
from odoo import models, api, fields
from odoo.tools.mimetypes import guess_mimetype
from odoo.tools import consteq, pycompat


class OverrideBinaryRecordContent(models.AbstractModel):
    _inherit = 'ir.http'

    def binary_content(self, xmlid=None, model='ir.attachment', id=None, field='datas',
                       unique=False, filename=None, filename_field='name', download=False,
                       mimetype=None, default_mimetype='application/octet-stream',
                       access_token=None):
        """ Get file, attachment or downloadable content

        If the ``xmlid`` and ``id`` parameter is omitted, fetches the default value for the
        binary field (via ``default_get``), otherwise fetches the field for
        that precise record.

        :param str xmlid: xmlid of the record
        :param str model: name of the model to fetch the binary from
        :param int id: id of the record from which to fetch the binary
        :param str field: binary field
        :param bool unique: add a max-age for the cache control
        :param str filename: choose a filename
        :param str filename_field: if not create an filename with model-id-field
        :param bool download: apply headers to download the file
        :param str mimetype: mintype of the field (for headers)
        :param str default_mimetype: default mintype if no mintype found
        :param str access_token: optional token for unauthenticated access
                                 only available  for ir.attachment
        :returns: (status, headers, content)
        """
        record, status = self._get_record_and_check(xmlid=xmlid, model=model, id=id, field=field,
                                                    access_token=access_token)
        read_direct_binary = False
        filehash = None

        if not record:
            return (status or 404, [], None)

        content, headers, status = None, [], None

        if record._name == 'ir.attachment':
            status, content, filename, mimetype, filehash = self._binary_ir_attachment_redirect_content(record,
                                                                                                        default_mimetype=default_mimetype)
        if not content:
            status, content, filename, mimetype, filehash, read_direct_binary = self._binary_record_content(
                record, field=field, filename=filename, filename_field=filename_field,
                default_mimetype='application/octet-stream')

        status, headers, content = self._binary_set_headers(
            status, content, filename, mimetype, unique, filehash=filehash, download=download)

        return status, headers, content, read_direct_binary

    def _binary_record_content(
            self, record, field='datas', filename=None,
            filename_field='name', default_mimetype='application/octet-stream'):

        model = record._name
        mimetype = 'mimetype' in record and record.mimetype or False
        content = None
        filehash = 'checksum' in record and record['checksum'] or False
        # set read_direct_binary to False first
        read_direct_binary = False
        if model == 'ir.attachment':
            read_direct_binary = getattr(record, 'read_direct_binary', False)

        field_def = record._fields[field]
        if field_def.type == 'binary' and field_def.attachment:
            field_attachment = self.env['ir.attachment'].sudo().search_read(
                domain=[('res_model', '=', model), ('res_id', '=', record.id), ('res_field', '=', field)],
                fields=['datas', 'mimetype', 'checksum', 'read_direct_binary'], limit=1)
            if field_attachment:
                mimetype = field_attachment[0]['mimetype']
                content = field_attachment[0]['datas']
                filehash = field_attachment[0]['checksum']
                read_direct_binary = field_attachment[0]['read_direct_binary']

        if not content:
            content = record[field] or ''

        # filename
        default_filename = False
        if not filename:
            if filename_field in record:
                filename = record[filename_field]
            if not filename:
                default_filename = True
                filename = "%s-%s-%s" % (record._name, record.id, field)

        if not mimetype:
            try:
                decoded_content = base64.b64decode(content)
            except base64.binascii.Error:  # if we could not decode it, no need to pass it down: it would crash elsewhere...
                return (404, [], None)
            mimetype = guess_mimetype(decoded_content, default=default_mimetype)

        # extension
        _, existing_extension = os.path.splitext(filename)
        if not existing_extension or default_filename:
            extension = mimetypes.guess_extension(mimetype)
            if extension:
                filename = "%s%s" % (filename, extension)

        if not filehash:
            filehash = '"%s"' % hashlib.md5(pycompat.to_text(content).encode('utf-8')).hexdigest()

        status = 200 if content else 404
        return status, content, filename, mimetype, filehash, read_direct_binary
