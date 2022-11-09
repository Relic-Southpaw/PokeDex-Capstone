# -*- coding: utf-8 -*-

import sys
import types

import inflect

import requests

from .clients import HTTPHypermediaClient
from .constants import DEFAULT_VALID_STATUS_CODES
from .exceptions import BadURLException

if sys.version_info[0] == 3:
    # Py3
    from urllib.parse import urlparse
else:
    # Py2
    from urlparse import urlparse


class BaseResource(object):
    """
    A simple representation of a resource.

    Usage:

        from beckett.resources import BaseResource

        class Product(BaseResource):

            class Meta:
                name = 'Product'
                identifier = 'slug'
                attributes = (
                    'slug',
                    'name',
                    'price',
                    'discount'
                )

        # Data will usually come straight from the client method
        >>> data = {'name': 'Tasty product', 'slug': 'sluggy'}
        >>> product = Product(**data)
        <Product | sluggy>
        >>> product.name
        'Tasty product'

    """

    class Meta:
        # The name of this resource, used in __str__ methods.
        name = 'Resource'
        # The name of the resource used in the URL, i.e. 'resources'
        resource_name = None
        # The key with which you uniquely identify this resource.
        identifier = 'id'
        # Acceptable attributes that you want to display in this resource.
        attributes = (identifier,)
        # subresources are complex attributes within a resource
        subresources = {}
        # HTTP status codes that are considered "acceptable"
        # when calling this resource
        valid_status_codes = DEFAULT_VALID_STATUS_CODES
        # HTTP Methods that work on this resource
        methods = (
            'get',
        )
        # When receiving paginated results, use this key to render instances.
        pagination_key = 'results'

    def __init__(self, **kwargs):
        self._subresource_map = getattr(self.Meta, 'subresources', {})
        self.set_attributes(**kwargs)

    def __str__(self):
        """
        Returns a string representation based on the `self.Meta.name`
        and `self.Meta.identifier` attribute value.
        """
        return '<{} | {}>'.format(
            self.Meta.name, getattr(self, self.Meta.identifier))

    def set_subresources(self, **kwargs):
        """
        For each subresource assigned to this resource, generate the
        subresource instance and set it as an attribute on this instance.
        """
        for attribute_name, resource in self._subresource_map.items():
            sub_attr = kwargs.get(attribute_name)
            if isinstance(sub_attr, list):
                # A list of subresources is supported
                value = [resource(**x) for x in sub_attr]
            else:
                # So is a single resource
                value = resource(**sub_attr)
            setattr(self, attribute_name, value)

    def set_attributes(self, **kwargs):
        """
        Set the resource attributes from the kwargs.
        Only sets items in the `self.Meta.attributes` white list.

        Subclass this method to customise attributes.

        Args:
            kwargs: Keyword arguements passed into the init of this class
        """
        if self._subresource_map:
            self.set_subresources(**kwargs)
            for key in self._subresource_map.keys():
                # Don't let these attributes be overridden later
                kwargs.pop(key, None)
        for field, value in kwargs.items():
            if field in self.Meta.attributes:
                setattr(self, field, value)

    @classmethod
    def get_resource_url(cls, resource, base_url):
        """
        Construct the URL for talking to this resource.

        i.e.:

        http://myapi.com/api/resource

        Note that this is NOT the method for calling individual instances i.e.

        http://myapi.com/api/resource/1

        Args:
            resource: The resource class instance
            base_url: The Base URL of this API service.
        returns:
            resource_url: The URL for this resource
        """
        if resource.Meta.resource_name:
            url = '{}/{}'.format(base_url, resource.Meta.resource_name)
        else:
            p = inflect.engine()
            plural_name = p.plural(resource.Meta.name.lower())
            url = '{}/{}'.format(base_url, plural_name)
        return cls._parse_url_and_validate(url)

    @classmethod
    def get_url(cls, url, uid, **kwargs):
        """
        Construct the URL for talking to an individual resource.

        http://myapi.com/api/resource/1

        Args:
            url: The url for this resource
            uid: The unique identifier for an individual resource
            kwargs: Additional keyword argueents
        returns:
            final_url: The URL for this individual resource
        """
        if uid:
            url = '{}/{}'.format(url, uid)
        else:
            url = url
        return cls._parse_url_and_validate(url)

    @staticmethod
    def get_method_name(resource, method_type):
        """
        Generate a method name for this resource based on the method type.
        """
        return '{}_{}'.format(method_type.lower(), resource.Meta.name.lower())

    @classmethod
    def _parse_url_and_validate(cls, url):
        """
        Recieves a URL string and validates it using urlparse.

        Args:
            url: A URL string
        Returns:
            parsed_url: A validated URL
        Raises:
            BadURLException
        """
        parsed_url = urlparse(url)
        if parsed_url.scheme and parsed_url.netloc:
            final_url = parsed_url.geturl()
        else:
            raise BadURLException
        return final_url


class HypermediaResource(BaseResource, HTTPHypermediaClient):
    """
    A HypermediaResource is similar to a BaseResource except
    it understands relationships between attributes that
    are URLs to related registered resources.
    """
    class Meta(BaseResource.Meta):
        # HypermediaResource requires a base_url attribute
        base_url = NotImplemented
        related_resources = ()

    def __init__(self, *args, **kwargs):
        super(HypermediaResource, self).__init__(*args, **kwargs)
        self.session = requests.Session()

    def set_related_method(self, resource, full_resource_url):
        """
        Using reflection, generate the related method and return it.
        """
        method_name = self.get_method_name(resource, 'get')

        def get(self, **kwargs):
            return self._call_api_single_related_resource(
                resource, full_resource_url, method_name, **kwargs
            )

        def get_list(self, **kwargs):
            return self._call_api_many_related_resources(
                resource, full_resource_url, method_name, **kwargs
            )

        if isinstance(full_resource_url, list):
            setattr(
                self, method_name,
                types.MethodType(get_list, self)
            )
        else:
            setattr(
                self, method_name,
                types.MethodType(get, self)
            )

    def match_urls_to_resources(self, url_values):
        """
        For the list of valid URLs, try and match them up
        to resources in the related_resources attribute.

        Args:
            url_values: A dictionary of keys and URL strings that
                        could be related resources.
        Returns:
            valid_values: The values that are valid
        """
        valid_values = {}
        for resource in self.Meta.related_resources:
            for k, v in url_values.items():
                resource_url = resource.get_resource_url(
                    resource, resource.Meta.base_url)
                if isinstance(v, list):
                    if all([resource_url in i for i in v]):
                        self.set_related_method(resource, v)
                        valid_values[k] = v
                elif resource_url in v:
                    self.set_related_method(resource, v)
                    valid_values[k] = v
        return valid_values

    def set_attributes(self, **kwargs):
        """
        Similar to BaseResource.set_attributes except
        it will attempt to match URL strings with registered
        related resources, and build their get_* method and
        attach it to this resource.
        """
        if not self.Meta.related_resources:
            # Just do what the normal BaseResource does
            super(HypermediaResource, self).set_attributes(**kwargs)
            return

        # Extract all the values that are URLs
        url_values = {}
        for k, v in kwargs.items():
            try:
                if isinstance(v, list):
                    [self._parse_url_and_validate(i) for i in v]
                else:
                    self._parse_url_and_validate(v)
                url_values[k] = v
            except BadURLException:
                # This is a badly formed URL or not a URL at all, so skip
                pass
        # Assign the valid method values and then remove them from the kwargs
        assigned_values = self.match_urls_to_resources(url_values)
        for k in assigned_values.keys():
            kwargs.pop(k, None)
        # Assign the rest as attributes.
        for field, value in kwargs.items():
            if field in self.Meta.attributes:
                setattr(self, field, value)


class SubResource(object):
    """
    A "mini resource" within a larger resource. Similarly to BaseResource but
    minus some features.

    Consider the following JSON for a "Book" resource:

    ```json
    {
        "author": {
            "name": "Earnest"
        },
        "title": "A Farewell to Arms"
    }
    ```
    I can use this class to transform the "author" attribute into
    a typed resource.
    """

    class Meta:
        # The name of this Subresource, used in __str__ methods.
        name = 'SubResource'
        # The key with which you uniquely identify this resource.
        identifier = 'id'
        # Acceptable attributes that you want to display in this resource.
        attributes = (identifier,)

    def __init__(self, **kwargs):
        self.set_attributes(**kwargs)

    def __str__(self):
        """
        Returns a string representation based on the `self.Meta.name`
        and `self.Meta.identifier` attribute value.
        """
        return '<{} | {}>'.format(
            self.Meta.name, getattr(self, self.Meta.identifier, ''))

    def set_attributes(self, **kwargs):
        """
        Set the resource attributes from the kwargs.
        Only sets items in the `self.Meta.attributes` white list.

        Args:
            kwargs: Keyword arguements passed into the init of this class
        """
        for field, value in kwargs.items():
            if field in self.Meta.attributes:
                setattr(self, field, value)
