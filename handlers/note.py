#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "tamchen"

import heapq

nums = [1, 8, 2, 23, 7, -4, 18, 23, 42, 37, 2]
print(heapq.nlargest(3, nums))  # Prints [42, 37, 23]
print(heapq.nsmallest(3, nums))  # Prints [-4, 1, 2]

import redis

cache = redis.StrictRedis(host='localhost', port=6379)

# 1. 简单的get和set操作
print(u'====set操作:')
cache.set('blog:title', u'the5fire的技术博客')
print(cache.get('blog:title'))

# 真实应用场景,批量set和get
for i in range(10):
    cache.mset({
        'blog:post:%s:title' % i: u'文章%s标题' % i,
        'blog:post:%s:content' % i: u'文章%s的正文' % i
    })

post_list = []
for i in range(10):
    post = cache.mget('blog:post:%s:title' % i, 'blog:post:%s:content' % i)
    if post:
        post_list.append(post)

for title, content in post_list:
    print(title, content)

# 2、 hashed类型的操作
print(u'====hashed操作:')
cache.hset('blog:info', 'title', u'the5fire的技术博客')
cache.hset('blog:info', 'url', u'http://www.the5fire.com')

blog_info_title = cache.hget('blog:info', 'title')
print(blog_info_title)

blog_info = cache.hgetall('blog:info')
print(blog_info)

# 同样hashed类型的set和get也可以进行批量操作
cache.hmset('blog:info', {
    'title': 'the5fire blog',
    'url': 'http://www.the5fire.com',
})
blog_info1 = cache.hmget('blog:info', 'title', 'url')
print(blog_info1)

# 3、lists类型的操作
print(u'====lists操作：')
cache.lpush('blog:tags', 'python')
cache.lpush('blog:tags', 'linux')
tags = cache.lrange('blog:tags', 0, 2)
print(tags)

# 对应的还有rpush，lpop，rpop，更多可以看红丸的redis实战

# 4、sets类型的操作
print(u'====sets操作：')
cache.sadd('blog:category:python', '001')
cache.sadd('blog:category:python', '002')
# cache.sadd('blog:category:python', '001', '002')

print(cache.smembers('blog:category:python'))
cache.srem('blog:category:python', '001')
print(cache.smembers('blog:category:python'))
