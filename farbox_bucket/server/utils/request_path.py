# coding: utf8
import re
import urllib
from flask import request, g
from farbox_bucket.utils import get_value_from_data, string_types
from farbox_bucket.server.utils.site_resource import get_site_config
from farbox_bucket.utils.url import get_url_without_prefix

def split_path(path):
    # 将一个path转为以/分割的parts，如果有包含~~的，则以~~为第一个split
    path = urllib.unquote(path)
    path = re.sub(r'/page/\d+/?$', '/', path) # 去掉/page/1这样的后缀

    if '~~' in path:
        # /blog/post/~this/is/post/path
        head, tail = path.split('~~', 1)
        parts = [head.strip('/')] + tail.split('/')
    else:
        parts = path.split('/')

    return filter(lambda x: x, parts)


def get_offset_path(path, offset=1):
    # /a/b/c/d 如果 offset=1, 则获得 b/c/d, 如果是2，则是 c/d
    if not offset or not isinstance(offset, int):
        return path
    else:
        raw_path = path
        path = path.lstrip('/')
        parts = split_path(path)
        path = '/'.join(parts[offset:])
        if raw_path.endswith('/'):
            path += '/'
        return path


def get_request_offset_path(offset=1, path=None):
    # 得到偏移几个单位的url，头没有  /
    if path is None:
        path = get_request_path()
    path = get_offset_path(path, offset)
    return path.lstrip('/')

def get_request_path_without_prefix():
    path = get_request_path()
    return get_url_without_prefix(path)


def get_request_offset_path_without_prefix(offset=1):
    path = get_request_path_without_prefix()
    return get_request_offset_path(offset, path=path)




def get_request_path():
    # 去掉/page/<int> 这样分页信息后的path, 并且不以/开头
    path_got = getattr(g, 'url_path', None)
    if path_got:
        return path_got
    path = get_request_path_for_bucket() # 保留大小写，想获取 tags 的时候，需要区分大小写敏感的
    page_finder = re.compile(r'(.*?)/page/(\d+)/?$')
    page_result = page_finder.search(path)
    if page_result:
        path, page = page_result.groups()
        g.page = int(page) #存在g里面，这样后面供页面使用的函数，可以取这个值
    path ='/' + path.lstrip('/')
    g.url_path = path
    return path





def get_request_path_for_bucket(path=None):
    if path is None:
        request_path = request.path
    else:
        request_path = path
    bucket = getattr(g, 'bucket', None)
    if bucket and bucket in request_path:
        try:
            request_path = re.search('/%s/\w+(/.*|$)'%bucket, request_path).group(1)
        except:
            pass
    return request_path


def auto_bucket_url_path(url_path):
    if not url_path.startswith('/'):
        return url_path
    if url_path.startswith('/__'):
        return url_path
    if url_path.startswith('#'):
        return url_path
    request_path = request.path
    bucket = getattr(g, 'bucket', None)
    if bucket and bucket in request_path:
        p1, p2 = request_path.split(bucket, 1)
        prefix = p1 + bucket + '/' + p2.strip('/').split('/')[0]
        if url_path.lstrip('/').startswith(prefix.lstrip('/')):
            return url_path
        url_path = prefix + '/' + url_path.lstrip('/')
    return url_path




def get_doc_url(doc):
    if not isinstance(doc, dict):
        return ''
    if not doc:
        return ''
    url = ''
    # 主要处理日志的 url 这个属性
    if 'url_path' in doc and doc.get('_type')=='post':
        hide_post_prefix = get_site_config('hide_post_prefix', default_value=False)
        if hide_post_prefix:
            url = '/' + doc['url_path']
        else:
            url = '/post/' + doc['url_path']
    elif doc.get('_type') in ['file', 'image'] and doc.get('path'):
        url = '/' + doc['path']
    if not url: # last
        url = doc.get('url') or ''
    if url:
        url = auto_bucket_url_path(url)
    return url



def get_bucket_from_url(url):
    if url and isinstance(url, string_types):
        c = re.search('/bucket/(\w+)/', url)
        if c:
            return c.group(1)
    return None