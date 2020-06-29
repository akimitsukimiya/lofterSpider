import myinjector as providers
import requests
import websearcher
import os
from shutil import copy 
from datetime import datetime
import minitools
import aozoratext
import subprocess 
import json
import config
import linkdb as db

if config.db_type is 'sql':
    import sqlbase as base
else :
    import mysqlbase as base


class Searchers:
    se = providers.Singleton(requests.Session)
    wse = providers.Singleton(requests.Session)
    web_tag_searcher = providers.Singleton(websearcher.LofterWebTagSearcher, wse)
    blog_searcher = providers.Singleton(websearcher.LofterBlogTagSearcher, se)
    ref_blog_searcher = providers.Singleton(websearcher.LofterRefBlogSearcher, se)
    blog_info_getter = providers.Singleton(websearcher.LofterBlogInfoGetter, se)
    web_blog_on_tag_searcher = providers.Singleton(websearcher.LofterBlogOnWebTagSearcher, wse)
    comment_searcher = providers.Singleton(websearcher.LofterCommentSearcher, se)
    l2comment_searcher = providers.Singleton(websearcher.LofterL2CommentSearcher, se)
    url_img_downloader = providers.Singleton(websearcher.ImageDownloader,se)
    
     
   
class DB:
    session = providers.Callable(db.getse)
    init = providers.Callable(db.initDb)
    use = providers.Callable(db.changeDb)
    syncOneTag = providers.Callable(db.syncOneJson, session, base.Tag )
    syncOneBlog = providers.Callable(db.syncOneJson, session, base.Blog)
    syncOnePost = providers.Callable(db.syncOneJson, session, base.Post)
    syncOneImage = providers.Callable(db.syncOneJson, session, base.Image)
    syncOneEntry = providers.Callable(db.syncOneEntry, session)
    syncBlogs = providers.Callable(db.syncJsonList, session, base.Blog)     
    syncNewBlogs = providers.Callable(db.syncFreshJsonList, session)     
    syncPosts = providers.Callable(db.syncJsonList, session, base.Post)     
    syncNewPosts = providers.Callable(db.syncFreshJsonList, session, base.Post )     
    syncComments = providers.Callable(db.syncJsonList, session, base.Comment )     
    syncImages = providers.Callable(db.syncJsonList, session, base.Image)     
    syncNewImages = providers.Callable(db.syncFreshJsonList, session, base.Image )     
    addBlogsToTag = providers.Callable(db.extendM2MChildren, session, children_ref = 'blogs')
    addPostsToTag = providers.Callable(db.extendM2MChildren, session, children_ref = 'posts')
    addImagesToPost = providers.Callable(db.extendM2MChildren, session, children_ref = 'images')
    getTagPosts = providers.Callable(db.getM2MChildren,children_ref = 'posts')
    getPostImages = providers.Callable(db.getM2MChildren,children_ref = 'images')
    getTagBlogs = providers.Callable(db.getM2MChildren, children_ref = 'blogs') 
    getBlogPosts = providers.Callable(db.getM2MChildren, children_ref = 'posts') 
    getPostTags = providers.Callable(db.getM2MChildren, children_ref = 'tags') 
    delete = providers.Callable(db.delEntries, session)
    makeTagCsv =providers.Callable(db.exportJoinedCsv, session, \
                                  base.Post, [base.Blog], \
                                  base.Post.__mapper__.columns + \
                                  [base.Blog.blogNickName, base.Blog.blogName, base.Blog.homePageUrl],\
                                    'tag')
    getLastestPost = providers.Callable(db.queryEntryList, session, base.Post,\
                                       'tag', order_by = base.Post.id, desc = True, limit = 1 )

    countTagPosts = providers.Callable(db.countM2MChildren, session, \
                                     base.Post, 'posts') 
    countTagBlogs = providers.Callable(db.countM2MChildren, session, \
                                     base.Blog, 'blogs')


class Tools:
    cls = minitools.cls
    fixWinPrint = minitools.fixWinPrint
    pwd = os.getcwd
    apwd = providers.Callable(os.path.abspath, '.')
    abspath = os.path.abspath

    mkdir = os.mkdir
    isdir = os.path.exists
    ls = os.listdir
    cp = copy
    rn = os.rename
    rm = os.remove
    dt = minitools.getTimeFromIntStamp
    cd = os.chdir 
    string_fill = minitools.stringFill
    extension = minitools.getExtension
    # TODO some config can be moved to global config file
    to_epub = providers.ListArgsCallable(subprocess.call, \
                                         ['java','-cp','AozoraEpub3.jar','AozoraEpub3',\
                                         '-enc','UTF-8','-t','4', '-hor']) 
    to_mobi = providers.ListArgsCallable(subprocess.call, \
                                         ['./kindlegen'])
    json_to_string = json.loads
    make_plain_body = aozoratext.makePlainBody
    make_ref = aozoratext.makePlainRef
    make_links = aozoratext.makePlainLinks
    fix_fname = minitools.fixFname

    img_url = minitools.stripImageUrl
    main = aozoratext.posts2Aozora
    getImgs = aozoratext.htmlImages
    
    get_plain_txt_fname = aozoratext.makePlainFname 
