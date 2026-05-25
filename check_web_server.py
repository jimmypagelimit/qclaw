#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查 album-tracker Web 服务器是否运行
"""
import urllib.request
import urllib.error

url = 'http://localhost:3456'
try:
    req = urllib.request.Request(url, method='HEAD')
    with urllib.request.urlopen(req, timeout=3) as response:
        print(f'Web 服务器运行正常 (status={response.status})')
        print('需要停止服务器才能操作数据库')
        print('执行: taskkill /PID <pid> /F')
except Exception as e:
    print(f'Web 服务器未运行 (or not accessible): {e}')
    print('可以直接操作数据库')
