##Parse the text post content into aozora form
import re
from datetime import datetime
from bs4 import BeautifulSoup


class Patterns:

    center_of_page = "［＃ページの左右中央］"
    page_turner = "［＃改ページ］"

    h1_title_form = "［＃１字下げ］［＃大見出し］%s［＃大見出し終わり］"
    h2_title_form = "［＃１字下げ］［＃中見出し］%s［＃中見出し終わり］"
    h1_tags_form="［＃２字下げ］［＃ここから１段階小さな文字］%s［＃ここで小さな文字終わり］"
    second_title_form = "［＃１字下げ］［＃ここから２段階小さな文字］%s［＃ここで小さな文字終わり］"
    h2_author_form="［＃１字下げ］［＃小見出し］%s［＃小見出し終わり］"
    kudos_form="热度：%s"

   # h1_tags_form="［＃地から１字上げ］［＃ここから１段階小さな文字］%s［＃ここで小さな文字終わり］"
   # h2_tags_form="［＃地から１字上げ］［＃ここから２段階小さな文字］%s［＃ここで小さな文字終わり］"
    h2_sum_form="\n［＃ここから４字下げ］\n［＃ここから１段階小さな文字］\n%s\n［＃ここで小さな文字終わり］\n［＃ここで字下げ終わり］\n"

    link_form='<a href="%s"> ➢ </a>'
    bold_form=r"［＃太字］\1［＃太字終わり］"
    hr = "［＃区切り線］"

    rare = '⦻'
    trivial = '([^%s]*)' % rare
    #rare = '⦑%s⦀%s⦀%s⦒

    html_patterns = {
        'img' : ('img',{'src':True},'src'),
        'br' : ('br',{},''),
        'bold' : ('strong', {}, ''),
        'link' : ('a',{'href':True},'href'),
        'underline': ('span', {'type':'text-decoration:underline;'}, ''),
        'through' : ('span', {'type':'text-decoration:through;'}, ''),
        'quote': ('blockquote',{}, ''),
        'p' : ('p',{},'')
    }

    aozora_patterns = {
        #'img' : (r'［＃画像（\2）入る］'),
        'img' : (r'\n［＃枠囲み］\2［＃枠囲み終わり］ 查看图片 ［＃破線枠囲み］'),
        'br' : (r'\n'),
        'bold' : (r'［＃ここから太字］\1［＃ここで太字終わり］'),
        #'link' : (r'［＃枠囲み］\2［＃枠囲み終わり］\1［＃破線枠囲み］'),
        'link' : (r'［＃枠囲み］\2［＃枠囲み終わり］\1［＃破線枠囲み］'),
        #'link' : (r'<a href = "\2">\1<\a>'),
        'underline' : (r'［＃「\1」に傍線］'),
        'through' : (r'［＃取消線］\1［＃取消線終わり］'),
        'quote' : (r'［＃ここから２字下げ］\n［＃ここから１段階小さな文字］' + \
                   r'\1［＃ここで小さな文字終わり］\n［＃ここで字下げ終わり］'),
        'p' : (r'\1\n')


    }

    escape_patterns = (
        (r'---+', '\n' + hr + '\n' ),
        (r'《([^》]*)》',r'≪\1≫'),
        (r'《',r'≪'),
        (r'》',r'≫'),
        ('※', ''),
    )

    t_escape_patterns = (
        (r'《([^》]*)》',r'≪\1≫'),
        (r'《',r'≪'),
        (r'》',r'≫'),
        ('※', ''),
        (r'【(\d*)】',r' \1 '),
        (r'【[^】]*】',''),
        (r'\[[^\]]*\]',''),
    )

    image_ext = ['jpg','png','jpeg','gif','tiff',\
                'JPG','PNG','JPEG','GIF','TIFF']


def escapeAozora(text):
    for p in Patterns.escape_patterns:
        text = re.sub(p[0], p[1], text)
    return text



def escapeTitle(text):
    if not text:
        return '无题'
    for p in Patterns.t_escape_patterns:
        text0 = text
        #print(p[0],p[1], text)
        text = re.sub(p[0], p[1], text0)
        text = text or text0
    return text

# NOTE  deprecated !
#Change images url:
def fixImageUrl(tags, images, root, embed = False):
    if embed and len(images) == len(tags):
        aozorap = Patterns.aozora_patterns['img']
        for i in range(0,l):
            image = images[i]
            tag = tags[i]
            path = image.path
            path = path.replace(root + '/','')
            txt = re.sub(r'(b)(.*)',aozorap, 'b' + path)
            tag.replace_with(txt)
        return None
        
    else:
        aozorap  = Patterns.aozora_patterns['link']
        for tag in tags:
            try:    
                src = tag['src']
            except Exception as e:
                continue
            #a = soup.new_tag('a')
            #a['href'] = src
            #a.string = '查看图片'
            a = re.sub(r'( 查看图片 )(.*)', aozorap, \
                      ' 查看图片 ' + src)
            tag.replace_with(a)
        return None
            


#Form content into aozora text
def htmlToAozora(html, images, root):
    
    soup = BeautifulSoup(html, 'html5lib')
    html_patterns = Patterns.html_patterns 
    aozora_patterns = Patterns.aozora_patterns
    rare = Patterns.rare
    trivial = Patterns.trivial
    simple = trivial + rare + trivial
    for pname in html_patterns:
        html = html_patterns[pname]
        aozora = aozora_patterns[pname]
        tags = soup.findAll(html[0], html[1])

        #if pname is 'img':
        #    fixImageUrl(tags, images, root)
        #    continue


        for tag in tags:

            # special case 1
            #if tag.findAll('img'):
            #    contents = reversed(tag.contents)
            #    [tag.insert_after(c) for c in contents]
            #    tag.unwrap()
            #    print('WARNING: ignoring %s tag, \
            #          for it contains images.' % pname)
            #    continue


            txt = tag.text
            # special case 2
            if pname is 'link':
                txt = txt.replace('\n', '  ')


            ultra = html[2] and tag[html[2]]
            strg = txt + rare + ultra
            strg = re.sub(simple, aozora, strg)
            tag.replace_with(strg)


    content =  soup.text
    content = escapeAozora(content)
    return content


#Get Image Infos from content
def htmlImages(html, pid):
    soup = BeautifulSoup(html, 'html5lib')
    imgp = Patterns.html_patterns['img']
    imgs = []
    for tag in soup.findAll(imgp[0], imgp[1]):
        img = {}
        img['url'] = tag[imgp[2]]
        img['postId'] = pid
        imgs.append(img)
    return imgs



#Make a title page
def makeAuthorTitlePage(homePageUrl, blogNickName, blogName, avatar_path = ''):
    rare = Patterns.rare
    trivial = Patterns.trivial
    nick_f = Patterns.h1_title_form
    name_f = Patterns.h1_tags_form
    center = Patterns.center_of_page
    turner = Patterns.page_turner
    href_f = Patterns.aozora_patterns['link'] 
    href = blogName + rare + homePageUrl
    simple = trivial + rare + trivial  
    name_href = re.sub( simple, href_f, href)
            #name_f % name_href + \
    strg = '\n' + turner + '\n'+  center + '\n\n\n' + \
            nick_f % blogNickName + '\n' + \
            '\n\n' + \
            turner + '\n'
    strg = escapeAozora(strg)
    return strg


def makeTitle(title, url, hot, tags, blogNickName):
    rare = Patterns.rare
    trivial = Patterns.trivial
    author_f = Patterns.h2_author_form
    title_f = Patterns.h2_title_form
    tags_f = Patterns.second_title_form
    link_f = Patterns.link_form
    kudos_f = Patterns.kudos_form 
    hearts =  kudos_f % str(hot)  
    title = escapeTitle(title)
    tags = re.sub(r',',' / ', tags)
    strg = '\n' + author_f % blogNickName + '\n' + \
            title_f % title + link_f % url + '\n\n' + \
            tags_f % tags +  '\n' + \
            tags_f % hearts + '\n\n\n' 
    return strg


def posts2Aozora(blog, posts, root):
    turner = Patterns.page_turner
    strg = ''
    
    blogName = blog['blogName']
    homePageUrl = blog['homePageUrl']
    if not homePageUrl:
        homePageUrl = 'https://' + blogName + '.lofter.com'
    blogNickName = blog['blogNickName']

    author_page = makeAuthorTitlePage(homePageUrl, blogNickName, blogName)
    strg += author_page

    for post in posts:
        title = post['title']
        url = homePageUrl + '/post/' + post['permalink']
        hot = post['hot']
        tags = post['tag']
        title = makeTitle(title, url, hot, tags, blogNickName)
        html = post['content']
        if not html:
            continue
        content = htmlToAozora(html, post.novImages, root)
        
        strg += title
        strg += content
        strg += turner
        strg += '\n'

    return strg


def htmlToPlain(html):
    # Get page soup and pattern infos
    soup = BeautifulSoup(html, 'html5lib')
    html_patterns = Patterns.html_patterns  
    
    # Setup images and urls list
    image_urls = []
    urls = []
    urls_count = 0
    images_count = 0
    url_form = '[链接#%d]'
    image_form = '[图片#%d]'

    # Loop against tags to form text 
    for pname in html_patterns:
        html = html_patterns[pname]
        tags = soup.findAll(html[0], html[1])

        for tag in tags:
            
            if tag.findAll('img'):
                contents = reversed(tag.contents)
                [tag.insert_after(c) for c in contents]
                tag.unwrap()
                print('WARNING: ignoring %s tag, \
                      for it contains images.' % pname)
                continue
            
            txt = tag.text
            extra = html[2] and tag[html[2]]
            extra = re.sub(r'(https?://[^\?]*)\?.*', r'\1', extra)

            if extra and not isImage(extra):
                urls_count += 1
                txt =  txt and '(%s)' % txt
                txt += url_form % urls_count
                urls.append(extra)
            elif extra:
                images_count += 1
                txt = txt and '(%s)' % txt
                txt += image_form % images_count 
                image_urls.append(extra)

            if pname =='br':
                txt = '\n'
            if pname == 'p':
                txt += '\n'


            tag.replace_with(txt)

    content =  soup.text
    return content, urls, image_urls


def makePlainTitle(title, blogNickName, url, strtime, tags):
    txt = ''
    txt += '    标题: %s\n' % title or ' '
    txt += '    作者: %s\n' % blogNickName
    txt += '原文地址: %s\n' % url
    txt += '发布时间: %s\n' % strtime
  #  txt += '    热度: %s\n' % str(hot)
    txt += '    tags: %s\n' % tags
    txt += '\n'
    txt += '===========版权属于LOFTER的原作者============\n\n'
    return txt


def makePlainRef(urls, images):
    txt =''
    txt += '\n\n'
    txt += '===========版权属于LOFTER的原作者============\n\n'
    url_form = '[链接#%d]'
    image_form = '[图片#%d]'
    c = 0
    for image in images:
        c += 1
        txt += image_form % c + ' ' + image + '\n'
    c = 0
    txt += '\n'
    for url in urls:
        c += 1
        txt += url_form % c + ' ' + url + '\n'
    return txt


def makePlainFname(blog, post):
    fname = (post['title'] or '') + \
            ' By ' + blog['blogNickName'] +\
            ' ' + datetime.fromtimestamp(post['publishTime']/1000).strftime('%Y-%m-%d')
    fname = fname.replace('/', '_')
    return fname


def makePlainLinks(fname, urls, images):
    txt =''
    txt += '=================================================================\n'
    url_form = '[链接]'
    image_form = '[图片]'
    txt += '[博文地址] %s\n' % fname
    for image in images:
        txt += image_form + ' ' + image + '\n'
    for url in urls:
        txt += url_form  + ' ' + url + '\n'
    txt += '=================================================================\n'
    return txt


# Make a plain text body for a post, return string, urls, image_urls
def makePlainBody(blog, post):
    homePageUrl = blog['homePageUrl'] or 'https://%s.lofter.com' % blog['blogName']
    url = homePageUrl +'/post/'+post['permalink']
    title = post['title'] or '无题'
    blogNickName = blog['blogNickName']
    timestamp = post['publishTime']
    strtime = datetime.fromtimestamp(timestamp/1000)\
            .strftime('%Y-%m-%d %H:%M:%S') 
    tags = post['tag']
    html = post['content'] or ''
    
    title = makePlainTitle(title, blogNickName, url, strtime, tags )
    body, urls, image_urls = htmlToPlain(html)
    body = title + body

    return body, urls, image_urls
    

def isImage(url):
    image_ext = Patterns.image_ext
    last4 = url[-4:]
    last3 = url[-3:]
    if last4 in image_ext or last3 in image_ext:
        return True
    return False
 

