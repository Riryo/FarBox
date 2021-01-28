# coding: utf8
from flask import g, Response
from gevent import spawn
from farbox_bucket.bucket.usage.bucket_usage_utils import increase_request_for_bucket, increase_bandwidth_for_bucket


def update_usage_statistics(response):
    bucket = getattr(g, "bucket", None)
    if not bucket:
        return

    if not isinstance(response, Response):
        return
    # requests + 1
    spawn(increase_request_for_bucket, bucket)

    if response.status_code not in [301, 302, ]:
        bandwidth = response.content_length
        if bandwidth:
            spawn(increase_bandwidth_for_bucket, bucket, bandwidth)

