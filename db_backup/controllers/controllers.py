import os

from odoo.addons.web.controllers.main import Binary
from odoo.http import request
from odoo import http
import base64
import logging
from ..models.backup_tools import get_db_backup_path

_logger = logging.getLogger(__name__)

class OverrideAttachmentAccess(Binary):
    @http.route(['/web/content',
                 '/web/content/<string:xmlid>',
                 '/web/content/<string:xmlid>/<string:filename>',
                 '/web/content/<int:id>',
                 '/web/content/<int:id>/<string:filename>',
                 '/web/content/<int:id>-<string:unique>',
                 '/web/content/<int:id>-<string:unique>/<string:filename>',
                 '/web/content/<int:id>-<string:unique>/<path:extra>/<string:filename>',
                 '/web/content/<string:model>/<int:id>/<string:field>',
                 '/web/content/<string:model>/<int:id>/<string:field>/<string:filename>'], type='http', auth="public")
    def content_common(self, xmlid=None, model='ir.attachment', id=None, field='datas',
                       filename=None, filename_field='name', unique=None, mimetype=None,
                       download=None, data=None, token=None, access_token=None, **kw):

        # send read_direct_binary as False ,hoping if down the road it changes then we will not have to
        # decode it using b64decode
        status, headers, content = request.env['ir.http'].with_context({'read_direct_binary': False}).binary_content(
            xmlid=xmlid, model=model, id=id, field=field, unique=unique, filename=filename,
            filename_field=filename_field, download=download, mimetype=mimetype, access_token=access_token)

        if status != 200:
            return request.env['ir.http']._response_by_status(status, headers, content)
        else:
            read_direct_binary = False
            if model == 'ir.attachment':
                read_direct_binary = request.env[model].browse([id])
            if not read_direct_binary or not read_direct_binary[0]['read_direct_binary']:
                content_base64 = base64.b64decode(content)
            else:
                content_base64 = content
            headers.append(('Content-Length', len(content_base64)))
            response = request.make_response(content_base64, headers)
        if token:
            response.set_cookie('fileToken', token)
        return response

    @http.route('/backup/download/<int:id>', type='http', auth='user', methods=['GET'])
    def download_backup_files(self, id):
        assert request.params['backup'] and request.params['db']
        backup_file = request.params['backup']
        db_name = request.params['db']
        _logger.info(f'Backup downloaded of {backup_file} of {db_name} db')
        full_path = os.path.join(get_db_backup_path(db_name),backup_file)
        return http.send_file(full_path, as_attachment=True)
