# -*- coding:utf-8 -*-
import urllib
import urllib2
import cookielib
import time
import re
import shutil
import os

class Canon():

    def __init__(self,ipaddr,outPath):
        print "Canon构造函数，IP=" + ipaddr
        self.ipaddr = ipaddr
        self.outPath = outPath
        self.picsPaths = []
        self.boxsNames = []
        self.version = "V1.0"
        self.goonRun = "true"
        self.wb = ""
        self.ib = ""

    #重新尝试其他端口
    def reloadPort(self):
        commonport = ["8000", "8080", "80", "8081", "8089"]
        for item in commonport:
            try:
                url = "http://" + self.ipaddr + ":" + item + "/"
                request = urllib2.Request(url)
                index_html = urllib2.urlopen(request, timeout=20).read()
                if "twelcome.cgi" in index_html:
                    self.ipaddr = self.ipaddr + ":" + item
                    print "确认新IP=" + self.ipaddr
                    return index_html
                elif "<head>" in index_html:
                    self.ipaddr = self.ipaddr + ":" + item
                    print "确认新IP=" + self.ipaddr
                    return index_html
            except Exception, e:
                print Exception, e
            print "排除[" + item + "]端口"

    def getCookies(self):
        print "Canon获得Cookies"
        hosturl = 'http://' + self.ipaddr + '/'
        cj = cookielib.LWPCookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj), urllib2.HTTPHandler)
        urllib2.install_opener(opener)
        #获得首页页面
        index_html = urllib2.urlopen(hosturl).read()

        # 请求页面有异常情况则切换端口
        if "Not Acceptable" in index_html:
            print "需要重定向端口"
            index_html = self.reloadPort()
        elif "404 Not Found" in index_html:
            print "需要重定向端口"
            index_html = self.reloadPort()
        elif "wt2parser.cgi" in index_html:
            print "需要重定向端口"
            index_html = self.reloadPort()
        elif "The document has moved" in index_html:
            print "需要重定向端口"
            index_html = self.reloadPort()

        #页面中存在重定向提示，则重定向
        reMeta = re.findall("<META http-equiv=Refresh content=\"0; URL=http://(.*?)/rps/\">", index_html)
        if reMeta.__len__() > 0:
            print "需要跳转[http://"+reMeta[0]+"/rps/]"
            self.ipaddr = reMeta[0]
            index_html = self.getHtml("/rps/")

        #页面中存在登录相关表单，则需要登录
        if "name=\"login\" action=\"/login\" method=\"post\"" in index_html:
            print "需要登录"
            index_html = self.postRequest("/login",{
                "user_type_generic":"true",
                "deptid":"7654321",
                "password":"7654321",
                "uri":"\%2Frps\%2F"
            }).read()
            if "name=\"login\" action=\"/login\" method=\"post\"" in index_html:
                print "登录失败程序中止"
                self.goonRun = "false"
                return
            if "document.sdl.conf.value = \"no\"" in index_html:
                print "提醒修改密码，自动取消"
                index_html = self.postRequest("/PwdConfirm", {
                    "conf":"no"
                }).read()
        elif "name=\"loginFrm\" action=\"/checkLogin.cgi\" autocomplete=\"off\" method=\"post\"" in index_html:
            print "需要登录，目前暂时不支持这种登录界面"
            return

        #进入首页后判断版本信息
        if "this.copyright" in index_html:
            print "确认版本为V2.0"
            self.version = "V2.0"
        else:
            print "确认版本为V1.0"

    def getHtml(self,pageUrl):
        print "Canon获得页面"+pageUrl
        headers={
            # 'Accept-Encoding' : 'gzip, deflate, sdch',
            'Accept-Encoding' : 'deflate, sdch',
            'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language' : 'zh-CN,zh;q=0.8',
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
        }
        url = 'http://' + self.ipaddr + pageUrl
        request = urllib2.Request(url, headers=headers)
        response = urllib2.urlopen(request)
        return response.read()

    def getImgResponse(self,reUrl):
        print "Canon GET图片请求"+reUrl
        headers = {
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
            'Upgrade-Insecure-Requests': '1'
        }
        url = 'http://' + self.ipaddr + reUrl
        request = urllib2.Request(url, headers=headers)
        response = urllib2.urlopen(request)
        return response

    def getResponse(self,reUrl):
        print "Canon GET请求"+reUrl
        headers = {
            # 'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Encoding': 'deflate, sdch',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
        }
        url = 'http://' + self.ipaddr + reUrl
        request = urllib2.Request(url, headers=headers)
        response = urllib2.urlopen(request)
        return response

    def postRequest(self,reUrl,postData):
        print "Canon POST请求" + reUrl
        url = 'http://' + self.ipaddr + reUrl
        postData = urllib.urlencode(postData)
        headers = {
            # 'Accept-Encoding': 'gzip, deflate',
            'Accept-Encoding': 'deflate',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
        }
        request = urllib2.Request(url, postData, headers=headers)
        response = urllib2.urlopen(request)
        return response

    def getTime(self):
        return str(int(time.time()))+"000"

    def downLoadImg(self,boxName,doc):
        docId = doc["docId"]
        pageCount = doc["pageCount"]
        pageTime = doc["pageTime"]
        pageTime = pageTime.replace(":", "-")
        pageTime = pageTime.replace("/", "-")
        pageTime = pageTime.replace(" ", "-")
        pageTime_split = pageTime.split("-")
        pageTime = pageTime_split[0] + "-" + pageTime_split[1] + "-" + pageTime_split[2] + " " \
                   + pageTime_split[3] + "-" + pageTime_split[4] + "-" + pageTime_split[5]
        for i in range(1,int(pageCount)+1):
            if self.ib == "":
                    imgU = "/image.tif?BOX_No=" + boxName + "&DocID=" + docId + "&PageNo=" + str(i) + "&Mode=TIFF&EFLG=true&Dummy=" + self.getTime()
                    rep = self.getImgResponse(imgU)
                    html = rep.read()
                    if "<head>" in html:
                        imgU = "/image.tif?BOX_No=" + boxName + "&DocID=" + docId + "&PageNo=" + str(i) + "&Mode=THUMB&EFLG=true&Dummy=" + self.getTime()
                        rep = self.getImgResponse(imgU)
                        html = rep.read()
                        if "<head>" in html:
                            imgU = "/image.jpg?B=" + boxName + "&D=" + docId + "&P=" + str(i) + "&M=PJPEG&EFLG=true&Dummy=" + self.getTime()
                            rep = self.getImgResponse(imgU)
                            with open(os.path.join(self.outPath, pageTime + "_" + str(i) + ".jpg"), 'wb') as fp:
                                shutil.copyfileobj(rep, fp)
                            self.ib = "PJPEG"
                        else:
                            with open(os.path.join(self.outPath, pageTime + "_" + str(i) + ".tif"), 'wb') as fp:
                                shutil.copyfileobj(rep, fp)
                            self.ib = "THUMB"
                    else:
                        with open(os.path.join(self.outPath, pageTime + "_" + str(i) + ".tif"), 'wb') as fp:
                            shutil.copyfileobj(rep, fp)
                            self.ib = "TIFF"
            elif self.ib == "THUMB":
                with open(os.path.join(self.outPath, pageTime + "_" + str(i) + ".tif"), 'wb') as fp:
                    imgU = "/image.tif?BOX_No=" + boxName + "&DocID=" + docId + "&PageNo=" + str(i) + "&Mode=THUMB&EFLG=true&Dummy=" + self.getTime()
                    rep = self.getImgResponse(imgU)
                    shutil.copyfileobj(rep, fp)
            elif self.ib == "TIFF":
                with open(os.path.join(self.outPath, pageTime + "_" + str(i) + ".tif"), 'wb') as fp:
                    imgU = "/image.tif?BOX_No=" + boxName + "&DocID=" + docId + "&PageNo=" + str(i) + "&Mode=TIFF&EFLG=true&Dummy=" + self.getTime()
                    rep = self.getImgResponse(imgU)
                    shutil.copyfileobj(rep, fp)
            elif self.ib == "PJPEG":
                with open(os.path.join(self.outPath, pageTime + "_" + str(i) + ".jpg"), 'wb') as fp:
                    imgU = "/image.jpg?B=" + boxName + "&D=" + docId + "&P=" + str(i) + "&M=PJPEG&EFLG=true&Dummy=" + self.getTime()
                    rep = self.getImgResponse(imgU)
                    shutil.copyfileobj(rep, fp)



    def downLoadLogs(self):
        print "CanonV1下载日志"
        html = self.getHtml("/jlp.cgi?Flag=Html_Data&LogType=0&Dummy=" + self.getTime())
        if "/media/ms_err.gif" in html:
            print "非一般直接获取日志方式"
            uurs = ["jpl","jcl","jsl","jlr","jfl","jrl"]
            for uur in uurs:
                with open(os.path.join(self.outPath, uur + ".html"), 'wb') as fp:
                    shutil.copyfileobj(self.getResponse("/" + uur + ".cgi?Dummy=" + self.getTime()), fp)
            return
        print "一般直接获取日志方式"
        for logType in range(0, 7):
            with open(os.path.join(self.outPath, "Print&Copy_" + str(logType) + ".html"), 'wb') as fp:
                shutil.copyfileobj(self.getResponse("/jlp.cgi?Flag=Html_Data&LogType="+str(logType)+"&Dummy=" + self.getTime()), fp)

    def downLoadLogsV2(self):
        print "CanonV2下载日志"
        self.getHtml("/rps/nativetop.cgi?RUIPNxBundle=&CorePGTAG=PGTAG_JOB_PRT_STAT&Dummy=" + self.getTime())
        print "一般直接获取日志方式"
        #打印与复印日志
        for logType in range(0, 6):
            with open(os.path.join(self.outPath, "Print&Copy_" + str(logType) + ".html"), 'wb') as fp:
                shutil.copyfileobj(self.getResponse("/rps/jlp.cgi?Flag=Html_Data&LogType=" + str(logType) + "&Dummy=" + self.getTime()), fp)
        #发送日志
        with open(os.path.join(self.outPath, "Send.html"), 'wb') as fp:
            shutil.copyfileobj(self.getResponse("/rps/jls.cgi?Flag=Html_Data&CorePGTAG=4&Dummy=" + self.getTime()), fp)
        #传真发送日志
        with open(os.path.join(self.outPath, "SendFax.html"), 'wb') as fp:
            shutil.copyfileobj(self.getResponse("/rps/jlf.cgi?Flag=Html_Data&LogType=TX&Dummy=" + self.getTime()), fp)
        #传真接收日志
        with open(os.path.join(self.outPath, "ReceiveFax.html"), 'wb') as fp:
            shutil.copyfileobj(self.getResponse("/rps/jlf.cgi?Flag=Html_Data&LogType=RX&Dummy=" + self.getTime()), fp)
        #接收日志
        with open(os.path.join(self.outPath, "Receive.html"), 'wb') as fp:
            shutil.copyfileobj(self.getResponse("/rps/jlr.cgi?Flag=Html_Data&CorePGTAG=6&Dummy=" + self.getTime()), fp)
        #存储日志
        with open(os.path.join(self.outPath, "Save.html"), 'wb') as fp:
            shutil.copyfileobj(self.getResponse("/rps/jlsv.cgi?Flag=Html_Data&CorePGTAG=8&Dummy=" + self.getTime()), fp)

    def getBoxNamesList(self):
        print "Canon获取有效盒子列表"
        html = self.getHtml("/bpbl.cgi?BoxKind=UserBox&Dummy=" + self.getTime())
        # boxslists = re.findall("<b>(.*?)</b></a></td><td>.*?</td><td>(.*?)</td></tr>", html)
        # print html
        boxslists = re.findall("box_01.*?\n.*?<b>(.*?)</b></a></td><td>.*?</td><td>(.*?)</td></tr>", html)
        if boxslists.__len__() > 0:
            for item in boxslists:
                # count = int(item[1])
                print item[0]+":盒子有内容且无密码"
                # if count > 0:
                self.boxsNames.append(item[0])


    def getBoxNamesListV2(self):
        print "Canon获取有效盒子列表"
        self.getHtml("/rps/nativetop.cgi?RUIPNxBundle=&CorePGTAG=PGTAG_BOX_USER&Dummy=" + self.getTime())
        html = self.getHtml("/rps/bpbl.cgi?CorePGTAG=16&BoxKind=UserBox&FromTopPage=1&Dummy=" + self.getTime())
        # print html
        boxslists = re.findall("<a href=\"javascript:box_documents\(\'(.*?)\'\)\">.*?</a></span></td><td></td><td>(.*?)</td></tr>", html)
        if boxslists.__len__() > 0:
            for item in boxslists:
                count = int(item[1])
                print item[0]+"="+item[1]+"%"
                if count > 0:
                    self.boxsNames.append(item[0])

    #获得某个盒子中各分页的HTML，合并成数组
    def getPageHtmls(self,boxName):
        htmls = []
        # 获得每一个有内容的盒子里文档的表格
        self.getHtml("/blogin.cgi?BOX_No=" + boxName + "&Cookie=&Dummy=" + self.getTime())
        if self.wb == "":
            try:
                self.wb = "bdocs.cgi"
                rep = self.getResponse("/bdocs.cgi?BOX_No=" + boxName + "&DocStart=1&DIDS=&Dummy=" + self.getTime())
            except Exception, e:
                self.wb = "bcomdocs.cgi"
                rep = self.postRequest("/bcomdocs.cgi",{
                    "BOX_No" : boxName,
                    "DocStart" : "1",
                    "Dummy" : self.getTime()
                })
        elif self.wb == "bdocs.cgi":
            rep = self.getResponse("/bdocs.cgi?BOX_No=" + boxName + "&DocStart=1&DIDS=&Dummy=" + self.getTime())
        elif self.wb == "bcomdocs.cgi":
            rep = self.postRequest("/bcomdocs.cgi", {
                "BOX_No": boxName,
                "DocStart": "1",
                "Dummy": self.getTime()
            })
        html = rep.read()
        htmls.append(html)
        pageStr = re.findall("<option value=\"0\" selected>(.*?)-", html)
        for pageStart in pageStr:
            if int(pageStart) > 1:
                if  self.wb == "bdocs.cgi":
                    html = self.getHtml("/bdocs.cgi?BOX_No=" + boxName + "&DocStart=" + pageStart + "&DIDS=&Dummy=" + self.getTime())
                    htmls.append(html)
                elif self.wb == "bcomdocs.cgi":
                    html = self.postRequest("/bcomdocs.cgi", {
                        "BOX_No": boxName,
                        "DocStart": "1",
                        "Dummy": self.getTime()
                    }).read()
                    htmls.append(html)
        return htmls

    #获得页面中的文档列表详情
    def getDocslist(self,html):
        doclist = re.findall("javascript:doc_pages\(\'(.*?)\'\).*?<b>(.*?)</b>.*?<div align=\"left\">(.*?)</div></td><td><font.*?>(.*?)</font>", html)
        docslist = []

        # 获得每一个文档的ID，名字，页数
        if doclist.__len__() > 0:
            for doc in doclist:
                docslist.append({
                    "docId" : doc[0],
                    "docName" : doc[1],
                    "pageCount" : doc[2],
                    "pageTime" : doc[3]
                })
        return docslist

    def process(self):
        print "Canon过程方法"
        self.getCookies()

        if self.goonRun == "false":
            return

        if self.version == "V1.0":
            print "执行V1.0方案"
            # 下载所有日志
            self.downLoadLogs()
            #获得100盒子及其容量占用率
            self.getBoxNamesList()
            if self.boxsNames.__len__() > 0:
                for boxName in self.boxsNames:
                    #获得盒子内所有的页面
                    htmls = self.getPageHtmls(boxName)
                    for html in htmls:
                        #获得文档列表
                        docslist = self.getDocslist(html)
                        if docslist.__len__() > 0:
                            for doc in docslist:
                                self.downLoadImg(boxName,doc)

        elif self.version == "V2.0":
            print "执行V2.0方案"
            # 下载所有日志
            self.downLoadLogsV2()
            # 获得100盒子及其容量占用率
            self.getBoxNamesListV2()
            if self.boxsNames.__len__() > 0:
                for boxName in self.boxsNames:
                    print boxName + "盒子有数据"

# 0419add
#########################################################################################################

    def process1_getLogs(self):
        print "Canon过程方法"
        self.getCookies()

        if self.goonRun == "false":
            return

        if self.version == "V1.0":
            print "执行V1.0方案"
            # 下载所有日志
            self.downLoadLogs()
            # #获得100盒子及其容量占用率
            # self.getBoxNamesList()
            # if self.boxsNames.__len__() > 0:
            #     for boxName in self.boxsNames:
            #         #获得盒子内所有的页面
            #         htmls = self.getPageHtmls(boxName)
            #         for html in htmls:
            #             #获得文档列表
            #             docslist = self.getDocslist(html)
            #             if docslist.__len__() > 0:
            #                 for doc in docslist:
            #                     self.downLoadImg(boxName,doc)

        elif self.version == "V2.0":
            print "执行V2.0方案"
            # 下载所有日志
            self.downLoadLogsV2()
            # # 获得100盒子及其容量占用率
            # self.getBoxNamesListV2()
            # if self.boxsNames.__len__() > 0:
            #     for boxName in self.boxsNames:
            #         print boxName + "盒子有数据"

    def process2_getPics(self):
        print "Canon过程方法"
        self.getCookies()

        if self.goonRun == "false":
            return

        if self.version == "V1.0":
            print "执行V1.0方案"
            # # 下载所有日志
            # self.downLoadLogs()
            # 获得100盒子及其容量占用率
            self.getBoxNamesList()
            if self.boxsNames.__len__() > 0:
                for boxName in self.boxsNames:
                    # 获得盒子内所有的页面
                    htmls = self.getPageHtmls(boxName)
                    for html in htmls:
                        # 获得文档列表
                        docslist = self.getDocslist(html)
                        if docslist.__len__() > 0:
                            for doc in docslist:
                                self.downLoadImg(boxName, doc)

        elif self.version == "V2.0":
            print "执行V2.0方案"
            # # 下载所有日志
            # self.downLoadLogsV2()
            # 获得100盒子及其容量占用率
            self.getBoxNamesListV2()
            if self.boxsNames.__len__() > 0:
                for boxName in self.boxsNames:
                    print boxName + "盒子有数据"
#########################################################################################################
