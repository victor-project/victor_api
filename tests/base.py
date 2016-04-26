#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "tamchen"

import tornado.testing

class TornadoBaseTestCase(tornado.testing.AsyncHTTPTestCase):
    """
    TestCase with an embedded MongoDB temporary instance.
    Each test runs on a temporary instance of MongoDB. Please note that
    these tests are not thread-safe and different processes should set a
    different value for the listening port of the MongoDB instance with the
    settings `MONGODB_TEST_PORT`.

    A test can access the connection using the attribute `conn`.

    """
    fixtures = []

    def __init__(self, *args, **kwargs):
        super(TornadoBaseTestCase, self).__init__(*args, **kwargs)

    def setUp(self):
        self.db = MongoTemporaryInstance.get_instance()
        self.conn = self.db.conn
        super(TornadoBaseTestCase, self).setUp()

    def tearDown(self):
        super(TornadoBaseTestCase, self).tearDown()
        for db_name in self.conn.database_names():
            self.conn.drop_database(db_name)

class BaseHandlerTestCase(TornadoBaseTestCase):

    json_dump_default = 'custom_json_dumps'

    def setUp(self):
        super(BaseHandlerTestCase, self).setUp()

    def tearDown(self):
        super(BaseHandlerTestCase, self).tearDown()

    def get_app(self):
        import app

        return app.application

    def json_loads(self, obj, excluded_keys=None):
        """
        Python 字典对象转换为 JSON 字典对象
            - dict 转为 json string
            - json string 再转为 dict
        :param obj:
        :param excluded_keys:
        :return:
        """
        return json.loads(self.to_body(obj, excluded_keys=excluded_keys))

    def to_body(self, body, excluded_keys=('created_at', 'updated_at', 'created_by', 'updated_by')):
        """
        生成请求body
            - body 为
        :param body:
        :param excluded_keys:
        :return:
        """
        if not body:
            return ''

        excluded_keys = excluded_keys or ()

        def process_dict(item):
            for k in excluded_keys:
                item.pop(k, None)
            if item.get('_id'):
                item['id'] = item.pop('_id')

        if isinstance(body, dict):
            process_dict(body)
        elif isinstance(body, list):
            for item in body:
                process_dict(item)
        json_dump_default = getattr(utils, self.json_dump_default, None)
        body_string = utils.json_dumps(body, default=json_dump_default) if body else ''
        return body_string

    def to_response(self, request_body, response, **kwargs):
        """
        返回相应结果
        :param request_body:
        :param response:
        :param kwargs:
        :return:
        """
        request_body = json.loads(request_body) if request_body else None
        code = response.code
        response_body = response.body
        if "json" in response.headers.get("Content-Type"):
            response_body = json.loads(response.body.decode('utf-8') or '{}')
        return request_body, code, response_body

    def request(self, url, method, body=None, **kwargs):
        """
        发送请求
        :param url:
        :param method:
        :param body:
        :param kwargs:
        :return:
        """
        body = self.to_body(body, **kwargs)
        response = self.fetch(
            url,
            method=method,
            body=body if method not in ['GET'] else None,
            follow_redirects=False,
            allow_nonstandard_methods=True,
        )
        return self.to_response(body, response)

    def GET(self, url, body=None, **kwargs):
        """
        tornado GET
        :param url:
        :param body:
        :param kwargs:
        :return:
        """
        return self.request(url, 'GET', body, **kwargs)

    def POST(self, url, body=None, **kwargs):
        """
        tornado POST
        :param url:
        :param body:
        :param kwargs:
        :return:
        """
        return self.request(url, 'POST', body, **kwargs)

    def PUT(self, url, body=None, **kwargs):
        """
        tornado POST
        :param url:
        :param body:
        :param kwargs:
        :return:
        """
        return self.request(url, 'PUT', body, **kwargs)

    def DELETE(self, url, body=None, **kwargs):
        """
        tornado DELETE
        :param url:
        :param body:
        :param kwargs:
        :return:
        """
        return self.request(url, 'DELETE', body, **kwargs)
