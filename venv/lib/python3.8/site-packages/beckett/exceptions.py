# -*- coding: utf-8 -*-


class BadURLException(Exception):
    """ An Invalid URL was parsed """


class InvalidStatusCodeError(Exception):
    """ An invalid status code was returned for this resource """

    def __init__(self, status_code, expected_status_codes):
        self.status_code = status_code
        self.expected_status_codes = expected_status_codes

    def __str__(self):
        return 'Received status code: {}, expected: {}'.format(
            self.status_code, self.expected_status_codes
            )


class MissingUidException(Exception):
    """ A uid attribute was missing! """
