#import random
import requests
from bs4 import BeautifulSoup
#from urllib.request import urlopen
import urllib.parse
import re
import textwrap
#import os
import time
#from selenium import webdriver
#import ssl
#import sys
import mysql.connector
import json

#Persistant request session WITH PROXY
#se = requests.Session()





class Iter:


    def __init__(self,limit):
        self.limit = limit


    def __iter__(self):
        self.now = 0
        return self


    def __next__(self):
        now = self.now 
        if now >= self.limit:
            raise StopIteration 
        self.now += 1
        return now






class FileRW:

    def writeli(name, li):
        ff = open(name,'w')
        for i in li:
            ff.write(i)
        ff.close()



class DbTools(object):
    
    def __init__(self, db_main_name, db_sub_name):
        
        self.db = mysql.connector.connect(
            host = "localhost",
            user = "lofter",
            passwd = "dowager",
            )
        self.dbcursor = self.db.cursor()
        db_name = db_main_name + '_'  + db_sub_name
        try:
            self.dbcursor.execute("USE %s" % db_name)
        except Exception as e:
            self.dbcursor.execute("CREATE DATABASE %s" % db_name )
            self.dbcursor.execute("USE %s" % db_name)



    def initDbTable(self, name, types, valnames):
        db = self.db
        dbcursor = self.dbcursor 
        print("Initializing table %s ... " % name)
        dbcursor.execute("DROP TABLE IF EXISTS %s" % name)
        sqlcmd = "CREATE TABLE %s (" % name
        for i in range(0,len(types)):
            sqlcmd += " %s %s," % (valnames[i],types[i])
        sqlcmd += "UNIQUE (%s) );" % valnames[0]
        try:
            dbcursor.execute(sqlcmd)
        except Exception as e:
            print("Something wrong with your data design, please check!")


    def writeDatas(self, name, valnames, vals):
        db = self.db
        dbcursor = self.dbcursor 
        print("Writing datas into table '%s' ..." % name)
        sqlcmd = "REPLACE INTO %s (" % name
        sqlcmd += ",".join(valnames)
        sqlcmd += ") VALUES ( "
        sqlcmd += ",".join(["%s"] * len(valnames))
        sqlcmd += ")"
        #sqlcmd += "ON DUPLICATE KEY UPDATE %s  = %s;" % (valnames[0], valnames[0])
        try:
            dbcursor.executemany(sqlcmd, vals)
            db.commit()
            print("%d updates done on table '%s'." % (dbcursor.rowcount, name))
        except Exception as e:
            print("Something wrong with your command, update failed!")
            print('ERROR info:',e)


    def readDatas(self, name, valnames):
        db = self.db
        dbcursor = self.dbcursor 
        print("Loading datas form table '%s' ..." % name)
        sqlcmd = "SELECT " + ",".join(valnames) + " FROM %s" % name
        try:
            dbcursor.execute(sqlcmd)
            rst = dbcursor.fetchall()
        except Exception as e:
            print("Something wrong with your command, data loading failed!")
            print('ERROR info:',e)
            return []
        print("%d entries loaded from table '%s'." % (len(rst),name))
        return [list(one) for one in rst] 

    def searchDatas(self, name, valnames, cvalname, val):
        sqlcmd = "SELECT %s FROM %s WHERE %s = \"%s\"" % (','.join(valnames), name, cvalname, val)
        #print(sqlcmd)
        try:
            self.dbcursor.execute(sqlcmd)
            rst = self.dbcursor.fetchall()
        except Exception as e:
            print("Something wrong with your command, data loading failed!")
            print('ERROR info:',e)
            return []
       # print("%d entries loaded from table '%s'." % (len(rst),name))
        return [list(one) for one in rst] 
        







class LofterSpider(object):
   
    def __init__(self):
        tag_name = '吉莱'
        db_name = 'lofter'
        self.search = self.Search('' , tag_name, 100)
        self.parse = self.Parse()
        self.data_tools = self.LofterDb(db_name, tag_name) 


    def initAllTables(self):
        names = ['works', 'blogs']
        for name in names:
            self.data_tools.initTable(self.datainfo.table_infos[name])


    def getNovTxtFiles(self):
        [vals,contents] = self.data_tools.readTable('contents')
        scontents = [self.data_tools.structureData(vals, content) for content in contents]
        #scontents = sorted(scontents, key = lambda x : x['author'], reverse = 0 )
        authors = list(set([one['author'] for one in scontents]))
        print('>>>>>>>>>>>>>>>>>>>>>>>>>')
        print('Start making txt files...')
        for author in authors:
            sc = [ i for i in scontents if i['author'] == author ]
            sc = sorted(sc, key = lambda x:int(x['time']), reverse = 0)
            aozoras = [ i['auzora'] for i in sc ]
            
        print('<<<<<<<<<<<<<<<<<<<<<<<<<','\n\n\n\n')

        
    def getNovContents(self):
        [vals, works] = self.data_tools.searchTable('works', 'type', '1')
        sworks = [self.data_tools.structureData(vals, work) for work in works]
        urls = []
        print('>>>>>>>>>>>>>>>>>>>>>>>>>')
        for work in sworks: 
            #print(work) 
            blog = self.data_tools.searchDatas('blogs', ['homePageUrl','blogNickName'],'blogId', work['blogId'])[0]
            work['author'] = blog[1]
            work['blogUrl'] = blog[0]
            urls.append(work['blogUrl']+'/post/'+work['permalink'])
        htmls = self.search.getContents(urls[301:350])
        [titles, plains, aozoras] = self.parse.doParsePages(urls[301:350], htmls)
        authors = [work['author'] for work in sworks[301:350]]
        permalinks = [work['permalink'] for work in sworks[301:350]]
        times = [work['time'] for work in sworks[301:350]]
        valnames = ['permalink','title','author','time','plain','aozora']
        vals = self.parse.transpose([permalinks,titles, authors, times, plains, aozoras])
        self.data_tools.writeDatas('contents', valnames, vals)       
       # FileRW.writeli('tmp6', contents)
        print('<<<<<<<<<<<<<<<<<<<<<<<<<','\n\n\n\n')


    def doThoroughSearch(self):
        
        #Search tag archive
        print('>>>>>>>>>>>>>>>>>>>>>>>>>')
        rsp = self.search.doSearchTag()
        print('<<<<<<<<<<<<<<<<<<<<<<<<<','\n\n\n\n')

        print('>>>>>>>>>>>>>>>>>>>>>>>>>')
        #Parse works
        [val_works, works] = self.parse.doParseRsp(rsp,'1')
        #Parse blogs
        [val_blogs, blogs] = self.parse.doParseRsp(rsp,'3')
        print('<<<<<<<<<<<<<<<<<<<<<<<<<','\n\n\n\n')
        
        print('>>>>>>>>>>>>>>>>>>>>>>>>>')
        #Save works
        self.data_tools.writeDatas('works', val_works, works )
        #Save blogs
        self.data_tools.writeDatas('blogs', val_blogs, blogs )
        print('<<<<<<<<<<<<<<<<<<<<<<<<<','\n\n\n\n')


        print('>>>>>>>>>>>>>>>>>>>>>>>>>')
        works_b = []
        #Parse works again
        val_index = list(map(lambda x:val_blogs.index(x), ['blogId','homePageUrl','blogNickName']))
        for a_blog in blogs:
            args = list(map(lambda x:a_blog[x], val_index))
            rsp = self.search.doSearchBlog(args[0], args[1], args[2])
            [val_works_b, works_bp] = self.parse.doParseRsp(rsp,'2')
            works_b.append(works_bp)
        #Save works
        self.data_tools.writeDatas('works', val_works_b, works_b)
        print('<<<<<<<<<<<<<<<<<<<<<<<<<','\n\n\n\n')
        

###########################################################################################################
############CLASS DATAINFO#################################################################################
    class LofterDb(DbTools):

        def __init__(self, db_name, tag_name):
            super().__init__(db_name,tag_name)
            self.table_info = {}
            self.table_info['works'] = {
                'name':'works',
                'valnames':['permalink','type','title','blogId','blogUrl','tags','time','collection'],
                'types':['VARCHAR(255)','CHAR(8)','TEXT','VARCHAR(255)','VARCHAR(255)','TEXT','VARCHAR(255)','VARCHAR(255)']
            }

            self.table_info['blogs'] =  {
                'name':'blogs',
                'valnames':['blogId','homePageUrl','blogNickName'],
                'types':['VARCHAR(255)','VARCHAR(255)','VARCHAR(255)']
                }
            self.table_info['contents'] = {
                    'name':'contents',
                    'valnames':['permalink','title','author','time','plain','aozora'],
                    'types':['VARCHAR(255)','VARCHAR(255)','VARCHAR(255)','VARCHAR(255)','LONGTEXT','LONGTEXT']
                    }

        def readTable(self, name):
            valnames = self.table_info[name]['valnames']
            rst = self.readDatas( name, valnames )
            return valnames, rst


        def initTable(self, name):
            valnames = self.table_info[name]['valnames']
            types = self.table_info[name]['types']
            self.initDbTable(name,types,valnames)
        

        def searchTable(self, name, cvalname, cval):
            valnames = self.table_info[name]['valnames']
            novs = self.searchDatas(name, valnames, cvalname, cval)
            return valnames,novs

        def structureData(self, valnames, val):
            rst = {}            
            
            if len(valnames) != len(val):
                raise Exception("Lengths don't match, Please check!")
            for i in Iter(len(val)):
                rst[valnames[i]] = val[i]
            return rst

        def plainListData(self, sval):
            lval = []
            keys = []
            for vn in sval:
                keys.append(vn)
                lval.append(sval[vn])
            return keys,lval
        




############CLASS DATAINFO#################################################################################
###########################################################################################################

###########################################################################################################
############INNER CLASS PARSE##############################################################################
    class Parse:

        def __init__(self):
            self.description = "THIS OBJECT IS DESIGNED FOR PARSING RAW RESPONSES FROM SERVER."


        def getRspPatternInfos(self, cat):
            if cat == '1':
                desc = "works from tag search result"
                ##For parsing raw string from tag search.
                rst = {}
                rst['permalink'] = 's[\d]*\.permalink="([^"]*)";s[\d]*\.photo'
                rst['title'] = 's[\d]*\.title="([^"]*)";s[\d]*\.top'
                rst['time'] = 's[\d]*\.publishTime=([\d]*);s[\d]*\.publisher'
                rst['type'] = 's[\d]*\.type=([\d]);s[\d]*\.valid'
                #rst['tags'] = 's[\d]*\.tag="([^"]*)";s[\d]*\.tagList'
                rst['blogId'] = 's[\d]*\.blogId=([\d]*);s[\d]*\.blogInfo=s[\d]*;'
                #rst['blogId'] = 's[\d]*\.blogId=([\d]*);s[\d]*\.blogInfo='
                rst['collection'] = 's[\d]*\.collectionId=([\d]*);s[\d]*\.content'
            elif cat == '2':
                desc = "works from blog search result"
                ##For parsing raw string from blog search.
                rst = {}
                rst['permalink'] = 's[\d]*\.permalink="([^"]*)";s[\d]*\.noticeLinkTitle'
                rst['type'] = 's[\d]*\.type=([\d]);s[\d]*\.valid'
                rst['time'] = 's[\d]*\.time=([\d]*);s[\d]*\.type'
                rst['blogId'] = 's[\d]*\.blogId=([\d]*);s[\d]*\.cctype'
                rst['collection'] = 's[\d]*\.collectionId=([\d]*);s[\d]*\.dayOfMonth'
                rst['title'] = 's[\d]*\.noticeLinkTitle="?([^;"]*)"?;'
            elif cat == '3':
                desc = "blogs from tag search result"
                ##For parsing raw string from blog search.
                rst = {}
                rst['homePageUrl'] = 's[\d]*\.homePageUrl="([^"]*)";s[\d]*\.image'
                rst['blogId'] = 's[\d]*\.blogId=([\d]*);s[\d]*\.blogName'
                rst['blogNickName'] = 's[\d]*\.blogNickName="([^"]*)";s[\d]*\.blogStat'
            else:
                rst = {}
            return desc,rst


        def getNovPagePatternInfos(self, cat):
            rst = []
            if cat == '1':
                desc = "html patterns"
                rst.append(['link','a',{},'href'])
                rst.append(['img','img',{},'src'])
                rst.append(['bold','strong',{},''])
                rst.append(['underline','span',{'type':'text-decoration:underline;'},''])
                rst.append(['through','span',{'type':'text-decoration:through;'},''])
                rst.append(['quote','blockquote',{},[]])

            elif cat == '2':
                decs = "aozora patterns" 
                rst.append(['title',r'［＃地から１字上げ］［＃大見出し］\1［＃大見出し終わり］'])
                rst.append(['title_link', r'［＃地から１字上げ］［＃ここから２段階小さな文字］<a href="\2"> ➣ </a>［＃ここで小さな文字終わり］'])
                rst.append(['link',r'［＃枠囲み］\2［＃枠囲み終わり］\1［＃破線枠囲み］'])
                rst.append(['img',r'［＃と\1の図（\2）入る］'])
                rst.append(['bold',r'［＃太字］\1［＃太字終わり］'])
                rst.append(['underline',r'［＃「\1」に傍線］'])
                rst.append(['through',r'［＃取消線］\1［＃取消線終わり］'])
                rst.append(['quote',r'［＃ここから２字下げ］\n［＃ここから１段階小さな文字］\n\1\n［＃ここで小さな文字終わり］\n［＃ここで字下げ終わり］'])
            
            elif cat == '3':
                decs = 'author front  page patterns'

#center_of_page="［＃ページの左右中央］\n"
#nov_title_form="［＃地から１字上げ］［＃大見出し］%s［＃大見出し終わり］\n"
#nov_author_form="［＃地から１字上げ］［＃小見出し］%s［＃小見出し終わり］\n\n"
#nov_tags_form="［＃地から１字上げ］［＃ここから２段階小さな文字］%s［＃ここで小さな文字終わり］\n"
#nov_kudos_form="［＃地から１字上げ］［＃ここから１段階小さな文字］Kudos %s［＃ここで小さな文字終わり］\n\n"
#entry_tags_form="［＃地から１字上げ］［＃ここから２段階小さな文字］%s［＃ここで小さな文字終わり］\n"
#entry_kudos_form="［＃地から１字上げ］［＃ここから１段階小さな文字］Kudos %s［＃ここで小さな文字終わり］\n\n"
#nov_sum_form="\n%s\n"
#pixiv_link_form='［＃地から１字上げ］［＃ここから２段階小さな文字］<a href="%s">⇒PIXIV PAGE</a>［＃ここで小さな文字終わり］ \n'
#page_turner="\n\n［＃改ページ］\n"
#series_title_form="\n［＃２字下げ］［＃ここから１段階小さな文字］%s［＃ここで小さな文字終わり］"
#chapter_title_form = "\n［＃２字下げ］［＃中見出し］%s［＃中見出し終わり］\n"
#chapter_sum_form="\n［＃ここから４字下げ］\n［＃ここから１段階小さな文字］\n%s\n［＃ここで小さな文字終わり］\n［＃ここで字下げ終わり］\n"
#bold_form=r"［＃太字］\1［＃太字終わり］"
#ruby_form=r'｜\1《\2》'
#link_form=r'<a href="\2">\1</a>'
            else:
                desc = ''
            return rst

        def getRareChar(self):
            plain_p = r'⦑%s⦀%s⦀%s⦒'
            #null_p = '⦻'
            null_p = r' '
            sap_p = r'⦀'
            r_p  = r'⦒'
            return [plain_p,null_p,sap_p,r_p]

        def formAuthorPages(self, authors, urls):
            return
            

        def doParsePages(self, urls, htmls):
            contents_p = []
            contents_a = []
            titles = []
            leng = len(htmls)
            print("\n\nStart parsing pages...")
            for i in Iter(leng):
                [title,content_p] = self.htmlToPlain(urls[i], htmls[i])
                contents_p.append(content_p)
                contents_a.append(self.plainToAozora(urls[i], content_p))
                titles.append(title)
                print('Parsed: %d / %d' % (i+1, leng))
            return titles, contents_p, contents_a
                
        def htmlToPlain(self, url, html):
            rare = self.getRareChar()
            plain_p = rare[0]
            null_p = rare[1]
            content = ''
            bs = BeautifulSoup(self.dedent(html), 'html5lib')
            #print(url)
            div_title_pattern = re.compile(r'text')
            content_soup = bs.find('div',{'class':'art-text'})
            if not content_soup:
                print("RARE PATTERN!!")
                raise Exception('Rare Pattern!!')
                return '',''
            title_soup = content_soup.find('h2')
            title = title_soup.text.strip()
            print(title)
            content += plain_p % ('title', title, null_p)
            content += '\n'
            content += plain_p % ('title_link', null_p, url)
            title_soup.replace_with('')
            html_patterns = self.getNovPagePatternInfos('1')
            for p in html_patterns:
                pattern = p[0]
                for one_soup in content_soup.findAll(p[1],p[2]):
                    one_txt = one_soup.text
                    one_ultra = ''
                    if p[3]:
                        one_ultra = one_soup[p[3]]
                    one_str = plain_p % (pattern, one_txt or null_p, one_ultra or null_p)
                    one_soup.replace_with(one_str)
            content += '\n' + content_soup.text
            return title, content

        def plainToAozora(self, url, plain):
            rare = self.getRareChar()
            plain_p = rare[0]
            null_p = rare[1]
            sep_p = rare[2]
            right_p = rare[3]
            aozora = plain
            aozora_p = self.getNovPagePatternInfos('2')
            for p in aozora_p:
                pattern = p[0]
                pp = plain_p % (pattern,r'([^%s]*)' % sep_p,r'([^%s]*)' % right_p )
                aozora = re.sub(pp, p[1], aozora, flags=re.DOTALL)
            return aozora
            

            


        def dedent(self, string):
            return re.sub(r'\n\s+','\n',string)


        def doParseRsp(self, rsp, cat):
            #table_info = self.datainfo.table_infos['works']
            [desc,pattern_info] = self.getRspPatternInfos(cat)
            print("Parsing %s!" %  desc)
            val_list = list(pattern_info.keys())
            pattern_list = map(lambda x:pattern_info[x], val_list)
            try:
                rst = self.parsePatterns(pattern_list, rsp)
                print("Parsed %d %s!" % (len(rst),desc))
            except Exception as e:
                print("Something goes wrong when trying to do parsing!")
                print("ERROR info: ", e)
                return 0,0
            return val_list,rst





        def parsePatterns(self, pattern_strs, raw_strs):
            rst=[]
            rst = list(map(lambda x:re.compile(x).findall(raw_strs), pattern_strs))
            fix = lambda li:[self.fixTextEncoding(i) for i in li]
            rst = [fix(row) for row in rst]
            try:
                li = self.transpose(rst)
                return self.distinct(li)
            except Exception as e:
                print("Something wrong with transposing!")
                print("ERROR info: ", e)
                return ''
   
        def distinct(self, li):
            rst = []
            for i in li:
                if i not in rst:
                    rst.append(i)
            return rst

        def fixTextEncoding(self,text):
            return text.encode('utf-8','ignore').decode('unicode-escape','ignore').encode('utf-8','ignore').decode('utf-8','ignore')
    
        def transpose(self, mtrx):
            lens = list(map(lambda x:len(x), mtrx))
            #print(lens)
            if max(lens) != min(lens):
                raise Exception('Row lengths not even, transpose failed !')
            indexs = list(range(0,lens[0]))
            aRow  = lambda i:list(map(lambda x:x[i],mtrx)) 
            rst = list(map(aRow, indexs))
            return rst

############CLASS PARSE####################################################################################
###########################################################################################################









###########################################################################################################
############CLASS SEARCH###################################################################################
    class Search:

        def __init__(self, my_id = '', tag_name = '', req_num = 0):
            self.root_url = "http://www.lofter.com/"
            #self.my_id = '483671349'
            self.my_id = my_id or ""
            self.tag_name = tag_name or "吉莱"
            self.req_num = req_num or 100
            self.se = requests.Session()
            self.se.headers.update(self.makeSeHeaders())
            self.doLogin()
        




        def doLogin(self):
            url = 'http://api.lofter.com/v2.0/autoLogin.api?product=lofter-android-6.9.2'
            rsp = self.sepost(url,{},{})
            #print(rsp.headers)

        def makeSeHeaders(self):
            return {
                'User-Agent': 'LOFTER-Android 6.9.2 (MI MAX 2; Android 7.1.1; null) WIFI',
		#'market':'xiaomi',
		#'deviceid':'00000000-3a36-8330-e3c5-26674095d98b',
		#'dadeviceid':'7e79e397b30040eb48ea162a877561f276974d91',
		#'androidid':'2600e3fbbb191d29',
		#'cookie':'NTESwebSI=1565A5F9269DC0FD6F2FCC87003624A2.hzayq-lofter-app45.server.163.org-8010; Path=/; HttpOnly',
		#'cookie':'usertrack=O2/vPF7YAjE+41H/tD3gAg==; expires=Thu, 03-Jun-21 20',:04:01 GMT; domain=lofter.com; path=/
		'Content-Type':'application/x-www-form-urlencoded; charset=utf-8',
		#'Content-Length':'91',
                #'market':'xiaomi',
                'Host':'api.lofter.com',
		'Connection':'Keep-Alive',
		'Accept-Encoding':'gzip'       			
                    }
             




        def doSearchTag(self):
            req_num =  self.req_num
            post_url = "http://api.lofter.com/v2.0/newTag.api?product=lofter-android-6.9.2"
            tag_name = self.tag_name
            fetched_num = 0
            print("Searching tag archive on %s..." % tag_name)
            rst =[]
            while 1:
                req_data = self.makeTagSearchReqData(tag_name, req_num, fetched_num)
                one = self.sepost(post_url, req_data, {}).json()['response']['items']
                if not one:
                    break 
                one = [i['post'] for i in  one if i]
                rst += one
                fetched_num = len(rst)
                print("%d records fetched ..." % fetched_num)
            print("Tag search done, %d records fetched in total." % fetched_num)
            return rst
    
        def makeTagSearchReqData(self, tag_name, limit = 100, offset = 0):
            req_data = {
                'method':'newTagSearch',
                'tag':tag_name,
              #  'firstpermalink':'',
                'type':'new',
                'offset':str(offset),
                'limit':str(limit)
                    }
            return req_data


        def makeMobileHeaders(self):
            headers = {
                    'User-Agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1'
                    }
            return headers
    
    
        def countFetched(self, rsp):
            time_pattern_t = re.compile('(s[\d]*)\.publishTime=[\d]*;')
            fetched_num = len(time_pattern_t.findall(rsp))
            return fetched_num 
            
    
            
    
        def makeBlogSearchHeaders(self, blogUrl):
            blogUrl = blogUrl.replace("https://",'')
            req_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36',
            'Host': blogUrl,
            'Referer': "http://" + blogUrl + "/view",
            'Accept-Encoding': 'gzip, deflate'
                    }
            return req_headers 
    
        def makeBlogSearchReqData(self, blogUrl, blogId, time_stamp,req_num = 0, tag_name = ''):
            req_num = req_num or self.req_num
            #nm = fetched_num or 0
            #myid = my_id or ""
            tag_name = tag_name or self.tag_name 
            req_data = {
            'callCount':'1',
            'scriptSessionId':'${scriptSessionId}187',
            'httpSessionId':'',
            'c0-scriptName':'ArchiveBean',
            'c0-methodName':'getArchivePostByTag',
            'c0-id':'0',
            'c0-param0':'number:%s' % blogId,
            'c0-param1':'string:%s' % urllib.parse.quote(tag_name),
            'c0-param2':'number:%s' % time_stamp, #Time Stamp
            'c0-param3':'number:%d' % req_num, #Num of Entries fetched each time
            'batchId':'123456'
                    }
            return req_data
    
        def getTimestamps(self, rsp = ''):
            time_pattern_b= re.compile('s[\d]*\.time=([\d]*);s[\d]*\.type')
            times = time_pattern_b.findall(rsp)
            return times
           

        def doSearchBlog(self, blogId, blogUrl, blogName):
            req_num = self.req_num
            post_url = blogUrl + "/dwr/call/plaincall/ArchiveBean.getArchivePostByTag.dwr"
            is_continue = True 
            fetched_num = 0
            tag_name = self.tag_name 
            rsp = ''
            req_headers = self.makeBlogSearchHeaders(blogUrl)
            time_stamp = str(round(time.time()*1000))
            print("Searching archive on blog %s..." % blogName )
            while is_continue:
                req_data = self.makeBlogSearchReqData(blogUrl, blogId, time_stamp, req_num, tag_name)
                try:
                    one_rsp = self.sepost(post_url, req_headers, req_data)
                    time.sleep(1)
                except Exception as e:
                    print("Something wrong !")
                    print("ERROR info:", e)
                    break
                times = self.getTimestamps(one_rsp)
                is_continue = not (not times)
                fetched_num += len(times)
                if times:
                    time_stamp = times[-1]
                rsp += one_rsp
                print("%d records fetched ..." % fetched_num)
            print("Blog search done, %d records fetched in total." % fetched_num)
            return rsp 



        def seget(self, url, rq_headers = {}):
            while 1:
                try:
                    rst =  self.se.get(url, headers = rq_headers ).text
                    time.sleep(1)
                    break
                except Exception as e:
                    print('ERROR:',e,'\nSleep 5 seconds and try again...')
                    time.sleep(5)
            return rst

        def sepost(self, url, rq_data, rq_headers):
            while 1:
                try:
                    rst =  self.se.post(url, data = rq_data, headers = rq_headers)
                    time.sleep(1)
                    break
                except Exception as e:
                    print('ERROR:',e,'\nSleep 5 seconds and try again...')
                    time.sleep(5)
            return rst



        def getContents(self, urls):
            #    rst = list(map(lambda url: self.seget(url),urls))
            print("Start fetching work pages...")
            rst = []
            leng = len(urls)
            count = 0
            for url in urls:
                try:
                    count += 1
                    rst.append(self.seget(url, self.makeMobileHeaders()))
                    print('Fetched: %d / %d' % (count,leng))
                except Exception as e:
                    print("ERROR info:", e)
                    return []
            return rst



       


    def run(self):
        #self.data_tools.initTable('contents')
       # self.doThoroughSearch()
        #self.getNovContents()
        rst = self.search.doSearchTag()
        return  rst




def strJson(object_json, h = 0):
    s = ''
    try:
        ks = list(object_json.keys())
    except Exception as e:
        return str(object_json)
    for k in ks:
        s += '\n'
        s += '\t'*h
        s += k + ' : ' + strJson( object_json[k], h+1 )
    return s


#search = LofterSpider()
#rst = search.run()
#lofter = Lofter();
#html = se.get('http://mifusharu.lofter.com/post/1f4c6d69_1261aff7').text
#print(html)



