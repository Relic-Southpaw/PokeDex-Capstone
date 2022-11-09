# -*- coding: utf-8 -*-

from requests.status_codes import codes

DEFAULT_VALID_STATUS_CODES = (
    codes.ok,  # 200
    codes.created,  # 201
    codes.no_content,  # 204
)

HTTP_GET = 'GET'
HTTP_POST = 'POST'
HTTP_PATCH = 'PATCH'
HTTP_PUT = 'PUT'
HTTP_DELETE = 'DELETE'

VALID_METHODS = (
    HTTP_GET,
    HTTP_POST,
    HTTP_PATCH,
    HTTP_PUT,
    HTTP_DELETE
)

# Methods that require a unique ID to access
SINGLE_RESOURCE_METHODS = (
    HTTP_GET,
    HTTP_PUT,
    HTTP_PATCH,
    HTTP_DELETE,
)
