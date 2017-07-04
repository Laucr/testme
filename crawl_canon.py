#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import Canon
import json

json_raw = open("canon.json").read()
canon = json.loads(json_raw)
print len(canon)
for country in canon:
	for ip in country:
		try:
			if not os.path.exists(ip):
				os.mkdir(ip)
		except Exception, e:
			pass
		try:
			instance = Canon.Canon(ip, ip)
			instance.process2_getPics()
			print ip, "finished."
		except Exception, e:
			print ip, "failed."