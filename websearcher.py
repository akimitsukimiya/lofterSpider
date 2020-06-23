from abc import ABC, abstractmethod
import urllib.parse as urlparse 
import json
import time
import re
import genparse
import config





class Searcher(ABC):
    
    
    def __init__(self, se, url):
        self.se = se
        # NOTE: this is important!!!!!
        # I need DUPLICATE a copy of default headers dict, 
        # normal assignment only get a pointer!!!!
        self._default_headers = dict(se.headers)
        self.url = url
        self.__isset__ = False 
        super().__init__()
        


    @abstractmethod
    def init(self):
        self.__isset__ = True 

    @abstractmethod
    def decorateSession(self):
        pass

    @abstractmethod
    def getRequestData(self, rst):
        pass 

    @abstractmethod
    def parseResult(self, rst):
        pass

    @abstractmethod
    def isContinue(self, rst):
        pass

    @abstractmethod
    def onSearchDone(self):
        pass


    def doSearch(self):
        if not self.__isset__:
            print("Please setup your searcher by calling init(*args, **kwargs) first!")
            return None
        result = []
        url = self.url
        self.decorateSession()
        data = self.getRequestData('')
        while True:
            one_rst_r = self.sepost(url, data)
            one_rst = self.parseResult(one_rst_r)
            result += one_rst
            if not self.isContinue(one_rst_r):
                break
            data = self.getRequestData(one_rst_r)
        self.onSearchDone()
        return result 


    def doSearchGenerator(self):
        if not self.__isset__:
            print("Please setup your searcher by calling init(*args, **kwargs) first!")
            return None
        #result = []
        url = self.url
        self.decorateSession()
        data = self.getRequestData('')
        while True:
            one_rst_r = self.sepost(url, data)
            one_rst = self.parseResult(one_rst_r)
            data = self.getRequestData(one_rst_r)
            #result += one_rst
            if not self.isContinue(one_rst_r):
                break
            yield one_rst
        self.onSearchDone()


    def __call__(self, *args, **kwargs):
        self.init(*args, **kwargs)
        return self.doSearch()




    def sepost(self, url, data):

        while True:
            try:
                rst = self.se.post(url, data)
                if rst and rst.status_code == 200:
                    break
                else:
                    time.sleep(5)
                    continue
            except Exception as e:
                print('ERROR:',e, \
                      '\nSleep 5 seconds and try again...')
                time.sleep(5)
        return rst


    def resetHeaders(self):
        self.se.headers = self._default_headers




#NOTE: !!DEPRECATED!!
class LofterTagSearcher(Searcher):
    

    def __init__(self, se):
        url = "http://api.lofter.com/v2.0/newTag.api?product=lofter-android-6.9.2" 
        self.__isset__ = False
        super().__init__(se,url)


    def init(self, tag_name):
        self.tag_name = tag_name
        self.__offset__ = 0
        self.__isset__ = True 
        print("Lofter tag searcher ready!")
        #print('Fetched: %9d' % self.__offset__, end = '')


    def decorateSession( self):
        if not hasattr(self, '__isDecorated__'):
            self.__isDecorated__ = False
        if self.__isDecorated__:
            return None
        headers =  {
                'User-Agent': 'LOFTER-Android 6.9.2 (MI MAX 2; Android 7.1.1; null) WIFI',
		'Content-Type':'application/x-www-form-urlencoded; charset=utf-8',
                'Host':'api.lofter.com',
		'Connection':'Keep-Alive',
		'Accept-Encoding':'gzip'       			
                }
        self.se.headers.update(headers)
        self.__isDecorated__ = True
        return None


    def getRequestData(self, rst):
        limit = config.tag_search_limit
        if not rst:
            self.__offset__ += 0
        else:
            self.__offset__ +=  len(rst.json()['response']['items'])
            #print('Fetched: %9d' % self.__offset__)

        req_data = {
            'method':'newTagSearch',
            'tag':self.tag_name,
            'type':'new',
            'offset':str(self.__offset__),
            'limit':str(limit)
             }
        return req_data


    def parseResult(self, rst):
        try:
            rst_p = rst.json()['response']['items']
            rst_p = [r['post'] for r in rst_p if r]
        except Exception as e:
            print(rst.json())
            print('ERROR:', e)
            return []
        return rst_p


    def isContinue(self, rst):
        try:
            isBreak = not len(rst.json()['response']['items'])
            return not isBreak
        except Exception as e:
            print("ERROR:", e)
            return False 


    def onSearchDone(self):
        print('Fetched: %9d' % self.__offset__)
        self.tag_name = ''
        self.__isset__ = False
        self.__offset__ = 0
        self.resetHeaders()
        return None





# Search all posts under the tag, but use web POST request
class LofterWebTagSearcher(Searcher):
    

    def __init__(self, se):
        url = "http://www.lofter.com/dwr/call/plaincall/TagBean.search.dwr" 
        self.__isset__ = False
        super().__init__(se, url)


    def init(self, tag_name, timestamp = '0', earliest = '0',\
             limit = config.tag_search_limit or 500, offset = 0, maxnum = 0):
        self.tag_name = tag_name
        self.__offset__ = offset
        self.__limit__ = limit
        self.__maxnum__ = maxnum
        self.__timestamp__ = str(timestamp)
        self.__earliest__ = str(earliest)
        self.__fetched__ = 0
        self.__allfetched__ = 0
        self.__isset__ = True 
        print("Lofter web tag searcher ready!")
        #print('Fetched: %9d' % self.__offset__, end = '')


    def decorateSession(self):
        if not hasattr(self, '__isDecorated__'):
            self.__isDecorated__ = False
        if self.__isDecorated__:
            return None
        headers =  {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36',
		'Content-Type':'text.plain',
                'Host':'www.lofter.com',
		'Connection':'Keep-Alive',
		'Accept-Encoding':'gzip,deflate',
                'Referer': 'http://www.lofter.com/tag/%s?tab=archive'\
            % urlparse.quote(self.tag_name),
                'Origin': 'http://www.lofter.com'
                }
        self.se.headers.update(headers)
        self.__isDecorated__ = True
        return None


    def getRequestData(self, rst):
        limit = 500
        req_data = {
            'callCount' : '1', 
            'scriptSessionId' : '${scriptSessionId}187', 
            'httpSessionId' : '', 
            'c0-scriptName' : 'TagBean', 
            'c0-methodName' : 'search', 
            'c0-id' : '0', 
            'c0-param0' : 'string:%s' % urlparse.quote(self.tag_name) , 
            'c0-param1' : 'number:0', 
            'c0-param2' : 'string:', 
            'c0-param3' : 'string:new', 
            'c0-param4' : 'boolean:false', 
            'c0-param5' : 'number:', 
            'c0-param6' : 'number:%d' % limit, 
            'c0-param7' : 'number:%d' % self.__offset__, 
            'c0-param8' : 'number:%s' % self.__timestamp__, 
             'batchId' : '123456'
             }
        return req_data


    def parseResult(self, rst):
        try:
            dwr_string = rst.text
            
            #parse the dwr string
            resp_list = genparse.parseDwrString(dwr_string)
            fetched_raw = len(resp_list)
            self.__offset__ += fetched_raw 

            resp_list = [r['post'] for r in resp_list if r \
                        and r['post']['publishTime'] >= int(self.__earliest__)]
            #record the fetched num
            self.__fetched__ = len(resp_list)
            self.__allfetched__ += self.__fetched__

            #strip the non-valid result
            if self.__fetched__:
                self.__timestamp__ = resp_list[-1]['publishTime']

            print('Fetched:', self.__fetched__)
            print('Offset:', self.__offset__)
            

        except Exception as e:
            print('ERROR:', e)
            self.__fetched__ = 0
            with open('error.log', 'a+') as f:
                f.write(rst.text)
            resp_list =  []
        time.sleep(1)
        return resp_list


    def isContinue(self, rst):
        try:
            isBreak = not self.__fetched__ 
            if self.__maxnum__ and self.__offset__ >= self.__maxnum__:
                isBreak = True
            return not isBreak
        except Exception as e:
            print("ERROR:", e)
            return False 


    def onSearchDone(self):
        print('Total Fetched: %9d' % self.__allfetched__)
        self.tag_name = ''
        self.__isset__ = False
        self.__offset__ = 0
        self.__timestamp__ = '0'
        self.__allfetched__ = 0
        self.__earliest__ = '0'
        self.__maxnum__ = 0
        self.resetHeaders()
        return None






class LofterBlogOnTagSearcher(LofterTagSearcher):
    

                
    def doSearch(self):
        posts = super().doSearch()
        blogs = {p['blogInfo']['blogId']:p['blogInfo'] for p in posts if p}.values()
        blogs = list(blogs)
        print("Blog Fetched: %9d" % len(blogs))
        return blogs






#NOTE !!NOT IN USE!!
class LofterBlogOnWebTagSearcher(LofterWebTagSearcher):
    

                
    def doSearch(self):
        posts = super().doSearch()
        blogs = {p['blogInfo']['blogId']:p['blogInfo'] for p in posts if p}.values()
        blogs = list(blogs)
        print("Blog Fetched: %9d" % len(blogs))
        return blogs





# iterate on a specific blog
# get all posts under the tag
class LofterBlogTagSearcher(Searcher):


    def __init__(self, se):
        url = "http://api.lofter.com/v2.0/blogHomePage.api?product=lofter-android-6.9.2" 
        self.__isset__ = False
        super().__init__(se,url)


    def init(self, tag_name, blog, earliest = '0', \
             limit = config.blog_search_limit or 200):
        self.tag_name = tag_name
        self.blog = blog
        self.__limit__ = limit
        self.__earliest__ = str(earliest)
        self.__offset__ = 0
        self.__fetched__ = 0
        self.__raw_fetched__ = 0
        self.__isset__ = True 
       # self.lofterLogin(self.se)

    def lofterLogin(self, se):
        headers =  {
                'User-Agent': 'LOFTER-Android 6.9.2 (MI MAX 2; Android 7.1.1; null) WIFI',
                #'Content-Type':'application/x-www-form-urlencoded; charset=utf-8',
                'Host':'api.lofter.com',
		'Connection':'Keep-Alive',
		'Accept-Encoding':'gzip'
                }
        se.headers.update(headers)
        url = "http://api.lofter.com/v2.0/autoLogin.api?product=lofter-android-6.9.2"
        rst = se.get(url)


    def decorateSession(self):
        if not hasattr(self, '__isDecorated__'):
            self.__isDecorated__ = False
        if self.__isDecorated__:
            return None
        headers =  {
                'User-Agent': 'LOFTER-Android 6.9.2 (MI MAX 2; Android 7.1.1; null) WIFI',
		'Content-Type':'application/x-www-form-urlencoded; charset=utf-8',
                'Host':'api.lofter.com',
		'Connection':'Keep-Alive',
		'Accept-Encoding':'gzip'       			
                }
        self.se.headers.update(headers)
        self.__isDecorated__ = True
        return None


    def getRequestData(self, rst):
        self.__offset__ += self.__raw_fetched__
        url =  self.blog['homePageUrl']
        if not url:
            url = self.blog['blogName'] + '.lofter.com'
        req_data = {
            'method':'getPostLists',
            'blogdomain': url.replace('https://',''),
            'offset':str(self.__offset__),
            #'checkpwd' : '1',
            'targetblogid':str(self.blog['blogId']),
            'returnData':'1',
            'supportposttype':'1,2,3,4,5,6',
            'needgetpoststat':'1',
            'limit':str(self.__limit__)
             }
        return req_data


    def parseResult(self, rst):
        try:
            # Parse response
            rst_p = rst.json()['response']['posts']
            # Total fetched
            self.__raw_fetched__ = len(rst_p)
            
            # Valid fetched
            rst_p = [one['post'] for one in rst_p if rst_p and \
                     one and  self.tag_name in one['post']['tagList'] \
                     and one['post']['publishTime'] >= int(self.__earliest__)]
            self.__fetched__ += len(rst_p)

        except Exception as e:
            print(self.blog['homePageUrl'])
            print('ERROR:', e)
            print(rst.json())
            time.sleep(5)
            self.__raw_fetched__ = -1
            return []
        return rst_p


    def isContinue(self, rst):
        try:
            isBreak = not self.__raw_fetched__ \
                    or rst.json()['response']['posts'] == [None] 
            if self.__raw_fetched__ == -1:
                isBreak = False
            return not isBreak
        except Exception as e:
            print("ERROR:", e)
            return False 
   

    def onSearchDone(self):
        print('Blog Search Done!')
        print("Fetechd: ", self.__fetched__)
        self.tag_name = ''
        self.blog = {}
        self.__isset__ = False
        self.__offset__ = 0
        self.__raw_fetched__ = -1
        self.__fetched__ = 0
        self.resetHeaders()
        return None

    




    
# iterate against a specific blog which recommends other blogs' posts
# and get all blogs recommended
class LofterRefBlogSearcher(LofterBlogTagSearcher):


    def parseResult(self, rst):
        posts_json = super().parseResult(rst)
        htmls = [p['content'] for p in posts_json if p]
        ref_blogs = genparse.getBlogsFromHtmls(htmls)
        
        return ref_blogs

    def doSearch(self):
        ref_blogs = super().doSearch()
        return list(set(ref_blogs))
        





class LofterCommentSearcher(Searcher):


    def __init__(self, se): 
        url = "http://api.lofter.com/v2.0/commentsWithStatus.api?product=lofter-android-6.9.2" 
        self.__isset__ = False
        super().__init__(se,url)


    def init(self, blog, post):
        self.postid = post['id'] 
        self.blogid = blog['blogId']
        self.__offset__ = 0
        self.__isset__ = True 


    def decorateSession(self):
        if not hasattr(self, '__isDecorated__'):
            self.__isDecorated__ = False
        if self.__isDecorated__:
            return None
        headers =  {
                'User-Agent': 'LOFTER-Android 6.9.2 (MI MAX 2; Android 7.1.1; null) WIFI',
		'Content-Type':'application/x-www-form-urlencoded; charset=utf-8',
                'Host':'api.lofter.com',
		'Connection':'Keep-Alive',
		'Accept-Encoding':'gzip'       			
                }
        self.se.headers.update(headers)
        self.__isDecorated__ = True
        return None


    def getRequestData(self, rst):
        limit = config.comment_search_limit or 50
        if not rst:
            self.__offset__ += 0
        else:
            self.__offset__ +=  len(rst.json()['response']['recentComments'])
        req_data = {
            'blogid':str(self.blogid),
            'postid':str(self.postid),
            'offset':str(self.__offset__),
            'limit':str(limit)
             }
        return req_data


    def parseResult(self, rst):
        try:
            rst_p = rst.json()['response']['recentComments']
            rst_p = [one for one in rst_p if one]
        except Exception as e:
            print('ERROR:', e)
            return []
        return rst_p


    def isContinue(self, rst):
        try:
            isBreak = not len(rst.json()['response']['recentComments'])
            return not isBreak
        except Exception as e:
            print("ERROR:", e)
            return False 
   

    def onSearchDone(self):
        #print("Comments Fetechd: ", self.__offset__)
        self.blogid = ''
        self.postid = ''
        self.__isset__ = False
        self.__offset__ = 0
        self.resetHeaders()
        return None




class LofterL2CommentSearcher(Searcher):


    def __init__(self, se): 
        url = "http://api.lofter.com/v2.0/commentsL2.api?product=lofter-android-6.9.2" 
        self.__isset__ = False
        super().__init__(se,url)


    def init(self, post, comment):
        self.postId = post['id'] 
        self.commentId = comment['id']
        self.__offset__ = 0
        self.__isset__ = True 


    def decorateSession(self):
        if not hasattr(self, '__isDecorated__'):
            self.__isDecorated__ = False
        if self.__isDecorated__:
            return None
        headers =  {
                'User-Agent': 'LOFTER-Android 6.9.2 (MI MAX 2; Android 7.1.1; null) WIFI',
		'Content-Type':'application/x-www-form-urlencoded; charset=utf-8',
                'Host':'api.lofter.com',
		'Connection':'Keep-Alive',
		'Accept-Encoding':'gzip'       			
                }
        self.se.headers.update(headers)
        self.__isDecorated__ = True
        return None


    def getRequestData(self, rst):
        limit = config.comment_search_limit or 50
        if not rst:
            self.__offset__ += 0
        else:
            self.__offset__ +=  len(rst.json()['response']['comments'])
        req_data = {
            'commentId':str(self.commentId),
            'postId':str(self.postId),
            'offset':str(self.__offset__),
            'limit':str(limit)
             }
        return req_data


    def parseResult(self, rst):
        try:
            rst_p = rst.json()['response']['comments']
            rst_p = [one for one in rst_p if one]
        except Exception as e:
            print('ERROR:', e)
            return []
        return rst_p


    def isContinue(self, rst):
        try:
            isBreak = not len(rst.json()['response']['comments'])
            return not isBreak
        except Exception as e:
            print("ERROR:", e)
            return False 
   

    def onSearchDone(self):
        #print("L2 Comments Fetechd: ", self.__offset__)
        self.commentId = ''
        self.postId = ''
        self.__isset__ = False
        self.__offset__ = 0
        self.resetHeaders()
        return None
    


#NOTE deprecated
class LofterImageSearcher(Searcher):


    def __init__(self, se): 
        url = "http://api.lofter.com/v1.1/publicPostsWithStatus.api?product=lofter-android-6.9.2" 
        self.__isset__ = False
        super().__init__(se,url)


    def init(self, blog, post):
        self.postid = post['id'] 
        url =  blog['homePageUrl']
        if not url:
            url = blog['blogName'] + '.lofter.com'
        self.blogdomain = url.replace('https://', '')
        self.__offset__ = 0
        self.__isset__ = True 


    def decorateSession(self):
        if not hasattr(self, '__isDecorated__'):
            self.__isDecorated__ = False
        if self.__isDecorated__:
            return None
        headers =  {
                'User-Agent': 'LOFTER-Android 6.9.2 (MI MAX 2; Android 7.1.1; null) WIFI',
		'Content-Type':'application/x-www-form-urlencoded; charset=utf-8',
                'Host':'api.lofter.com',
		'Connection':'Keep-Alive',
		'Accept-Encoding':'gzip'       			
                }
        self.se.headers.update(headers)
        self.__isDecorated__ = True
        return None


    def getRequestData(self, rst):
        req_data = {
            'blogdomain':str(self.blogdomain),
            'postid':str(self.postid),
            'offset': 0,
            'supportposttypes': '1,2,3,4,5,6'
             }
        return req_data


    def parseResult(self, rst):
        try:
            #rst_p = rst.json()['response']
            rst_p = rst.json()['response']['posts'][0]['post']['photoLinks']
            
        except Exception as e:
            print('ERROR:', e)
            return ''
        return rst_p


    def isContinue(self, rst):
        return False
   

    def onSearchDone(self):
        #print("L2 Comments Fetechd: ", self.__offset__)
        self.postid = None
        self.blogdomain = ''
        self.__isset__ = False
        self.__offset__ = 0
        self.resetHeaders()
        return None
    

    def doSearch(self):
        if not self.__isset__:
            print("Please setup your searcher by calling init(*args, **kwargs) first!")
            return None
        url = self.url
        self.decorateSession()
        data = self.getRequestData('')
        one_rst_r = self.sepost(url, data)
        one_rst = self.parseResult(one_rst_r)
        one_rst=json.loads(one_rst)
        for i in range(0,len(one_rst)):
            one_rst[i]['id'] = self.postid * 1000 + i
        self.onSearchDone()
        return one_rst




#NOTE deprecated
class LofterImageDownloader(Searcher):


    def __init__(self, se): 
        url = ''
        self.__isset__ = False
        super().__init__(se,url)


    def init(self,  root, image, fname = ''):
        self.fname = fname
        self.root = root 
        self.image = image
        self.__offset__ = 0
        self.__isset__ = True 


    def decorateSession(self):
        self.resetHeaders()


    def getRequestData(self, rst):
        pass

    def parseResult(self, rst):
        pass

    def isContinue(self, rst):
        return False
   

    def onSearchDone(self):
        #print("L2 Comments Fetechd: ", self.__offset__)
        self.root = None
        self.image = None
        self.__isset__ = False
        self.resetHeaders()
        return None
    

    def doSearch(self):
        self.decorateSession()
        if not self.__isset__:
            print("Please setup your searcher by calling init(*args, **kwargs) first!")
            return None
        url = self.image['middle']
        url = re.sub(r'(http.*/[^?]*)?[^/]*', r'\1', url)
        rst = self.seget(url)
        if not rst:
            return None
        rst = rst.content
        path = self.root + '/' + self.fname or re.sub(r'http.*/([^/]*)', r'\1', url)
        with open(path, 'wb') as f:
            f.write(rst)
        return path


    def seget(self, url):
        while True:
            try:
                rst =  self.se.get(url)
                break
            except Exception as e:
                print(url)
                print('ERROR:',e,'\nSkip 1...')
                rst = ''
                break
        return rst
    


#NOTE deprecated
class LofterNovImageDownloader(LofterImageDownloader):
    def doSearch(self):
        self.decorateSession()
        if not self.__isset__:
            print("Please setup your searcher by calling init(*args, **kwargs) first!")
            return None
        url = self.image['url']
        url = re.sub(r'(http.*/[^?]*)?[^/]*', r'\1', url)
        rst = self.seget(url).content
        path = self.root + '/' + re.sub(r'http.*/([^/]*)', r'\1', url)

        with open(path, 'wb') as f:
            f.write(rst)
        return path



class LofterBlogInfoGetter(LofterBlogTagSearcher):



    def init(self, blog_url):
        self.blog_url = blog_url
        self.__isset__ = True


    def getRequestData(self, rst):
        req_data = {
            'method':'getBlogInfoDetail',
            'blogdomain': genparse.getDomain(self.blog_url),
            'returnData':'1',
            'needgetpoststat':'1',
             }
        return req_data


    def parseResult(self, rst):
        rsp = rst and rst.json()['response']
        if rst and rsp:
            rst_p = rsp['blogInfo']
        else:
            return ''
        return [rst_p]


    def isContinue(self, rst):
        return False


    def onSearchDone(self):
        #print("L2 Comments Fetechd: ", self.__offset__)
        self.blog_url = None
        self.__isset__ = False
        self.resetHeaders()
        return None

    def doSearch(self):
        rst = super().doSearch()
        if not rst:
            return None
        return rst[0]




class ImageDownloader(Searcher):


    def __init__(self, se): 
        url = ''
        self.__isset__ = False
        super().__init__(se,url)


    def init(self,  root, image_url, fname = ''):
        self.fname = fname
        self.root = root 
        self.image_url = image_url
        self.__offset__ = 0
        self.__isset__ = True 


    def decorateSession(self):
        self.resetHeaders()


    def getRequestData(self, rst):
        pass


    def parseResult(self, rst):
        pass


    def isContinue(self, rst):
        return False
   

    def onSearchDone(self):
        #print("L2 Comments Fetechd: ", self.__offset__)
        self.root = None
        self.image = None
        self.__isset__ = False
        self.resetHeaders()
        self.fname = ''
        return None
    

    def doSearch(self):
        self.decorateSession()
        if not self.__isset__:
            print("Please setup your searcher by calling init(*args, **kwargs) first!")
            return None
        url = self.image_url
        rst = self.seget(url)
        if not rst:
            return None
        rst = rst.content
        path = self.root + '/' + self.fname or re.sub(r'http.*/([^/]*)', r'\1', url)
        try:
            with open(path, 'wb') as f:
                f.write(rst)
                f.close()
        except Exception as e:
            print('ERROR occurred when trying go write image to disk!')
            print(e)
        self.onSearchDone()
        return path


    def seget(self, url):
        while True:
            try:
                rst =  self.se.get(url, timeout = 15)
                break
            except Exception as e:
                # ConnectTimeoutError
                # ReadTimeout
                print(url)
                print('ERROR:',e,'\nSkip 1...')
                rst = ''
                break
        return rst
