# coding: utf8
from __future__ import absolute_import
import re
from flask import g
from farbox_bucket.bucket import get_bucket_pages_configs, get_bucket_site_configs
from farbox_bucket.client.dump_template import get_template_content_from_name
from farbox_bucket.utils import get_value_from_data, string_types



def get_template_source(template_name):
    bucket = getattr(g, 'bucket', None)
    pages_configs = get_bucket_pages_configs(bucket)
    template_source = get_template_content_from_name(template_name, pages_configs)
    just_template_name = re.sub(r'\.(jade|html|htm)$', '', template_name)
    template_name_without_dot = just_template_name.replace('.', '_')
    template_name_without_dot2 = just_template_name.replace('.', '/')
    template_source = template_source or get_template_content_from_name(just_template_name, pages_configs)
    template_source = template_source or get_template_content_from_name(template_name_without_dot, pages_configs)
    if '.' in template_name:
        template_source = template_source or get_template_content_from_name(template_name_without_dot2, pages_configs)
    return template_source



def has_template_by_name(name_or_path, templates_info=None ):
    if not isinstance(templates_info, dict):
        templates_info = get_pages_configs()
    template_content = get_template_content_from_name(name_or_path, templates_info)
    if not template_content:
        return False
    else:
        return True



def get_pages_configs():
    bucket = getattr(g, 'bucket', None)
    pages_configs = get_bucket_pages_configs(bucket) or {}
    if not isinstance(pages_configs, dict):
        pages_configs = {}
    return pages_configs


def get_template_static_resource_content(relative_filepath):
    pages_configs = get_pages_configs()
    raw_content = pages_configs.get(relative_filepath) or ''
    return raw_content




def get_site_configs():
    bucket = getattr(g, 'bucket', None)
    if not bucket:
        return {}
    site_configs = get_bucket_site_configs(bucket)
    if not isinstance(site_configs, dict):
        site_configs = {}
    return site_configs


def just_get_site_config(config_key, default_value=None):
    bucket = getattr(g, 'bucket', None)
    if not bucket:
        if default_value is not None:
            return default_value
        else:
            return None
    site_configs = get_bucket_site_configs(bucket) or {}
    value = site_configs.get(config_key, default_value)
    return value


def get_site_config_int(config_key, default_value=None):
    # 确保是以 int 的形式返回
    value = just_get_site_config(config_key, default_value)
    try:
        value = int(float(value))
    except:
        pass
    if not isinstance(value, int):
        value = None
    return value


def get_site_config(fields, type_required=None, default_value=None):
    if isinstance(type_required, list):
        type_required = tuple(type_required)
    bucket = getattr(g, 'bucket', None)
    if not bucket:
        if default_value is not None:
            return default_value
        else:
            return None
    site_configs = get_bucket_site_configs(bucket)
    if not isinstance(fields, (list, tuple)):
        fields = [fields]
    for field in fields:
        if not isinstance(field, string_types):
            continue
        field_value = get_value_from_data(site_configs, field)
        if field_value is not None:
            if type_required:
                if isinstance(field_value, type_required):
                    return field_value
            else:
                return field_value
    if default_value is not None:
        return default_value
    else:
        return None


