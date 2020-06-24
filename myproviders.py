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

if config.db_type is 'sql':
    import linksql as db
else :
    import linkmysql as db


class Searchers:
    se = providers.Singleton(requests.Session)
    wse = providers.Singleton(requests.Session)
    tag_searcher = providers.Singleton(websearcher.LofterTagSearcher, se)
    web_tag_searcher = providers.Singleton(websearcher.LofterWebTagSearcher, se)
    blog_searcher = providers.Singleton(websearcher.LofterBlogTagSearcher, wse)
    ref_blog_searcher = providers.Singleton(websearcher.LofterRefBlogSearcher, se)
    blog_info_getter = providers.Singleton(websearcher.LofterBlogInfoGetter, se)
    blog_on_tag_searcher = providers.Singleton(websearcher.LofterBlogOnTagSearcher, se)
    web_blog_on_tag_searcher = providers.Singleton(websearcher.LofterBlogOnWebTagSearcher, wse)
    comment_searcher = providers.Singleton(websearcher.LofterCommentSearcher, se)
    l2comment_searcher = providers.Singleton(websearcher.LofterL2CommentSearcher, se)
    img_searcher = providers.Singleton(websearcher.LofterImageSearcher, se)
    img_downloader = providers.Singleton(websearcher.LofterImageDownloader, se)
    novimg_downloader = providers.Singleton(websearcher.LofterNovImageDownloader, se)
    url_img_downloader = providers.Singleton(websearcher.ImageDownloader,se)
    
     
   
class DB:
    session = providers.Callable(db.getse)
    init = providers.Callable(db.initDb)
    use = providers.Callable(db.changeDb)
    syncOneTag = providers.Callable(db.syncOneJson, session, db.Tag, 'tagName')
    syncOneBlog = providers.Callable(db.syncOneJson, session, db.Blog, 'blogId')
    syncOnePost = providers.Callable(db.syncOneJson, session, db.Post, 'id')
    syncOneImage = providers.Callable(db.syncOneJson, session, db.Image, 'id')
    syncOneNewImage = providers.Callable(db.syncOneUncheckedJson, session, db.Image)
    syncOneEntry = providers.Callable(db.syncOneEntry, session)
    syncBlogs = providers.Callable(db.syncJsonList, session, db.Blog, 'blogId' )     
    syncNewBlogs = providers.Callable(db.syncUncheckedJsonList, session, db.Blog )     
    syncPosts = providers.Callable(db.syncJsonList, session, db.Post, 'id' )     
    syncNewPosts = providers.Callable(db.syncUncheckedJsonList, session, db.Post )     
    syncComments = providers.Callable(db.syncJsonList, session, db.Comment, 'id' )     
    syncImages = providers.Callable(db.syncJsonList, session, db.Image, 'id' )     
    syncNewImages = providers.Callable(db.syncUncheckedJsonList, session, db.Image )     
    syncNovImages = providers.Callable(db.syncJsonList, session, db.NovImage, 'url' )     
    addBlogsToTag = providers.Callable(db.extendAssociatedList, session, list_key = 'blogs', id_key = 'blogId')
    addPostsToTag = providers.Callable(db.extendAssociatedList, session, list_key = 'posts', id_key = 'id')
    addNewPostsToTag = providers.Callable(db.extendUncheckedAssociatedList, session, list_key = 'posts')
    addNewBlogsToTag = providers.Callable(db.extendUncheckedAssociatedList, session, list_key = 'blogs')
    addImagesToPost = providers.Callable(db.extendAssociatedList, session, list_key = 'images', id_key = 'id')
    getTagPosts = providers.Callable(db.getAssociatedList,child_key = 'posts')
    getPostImages = providers.Callable(db.getAssociatedList,child_key = 'images')
    getTagBlogs = providers.Callable(db.getAssociatedList, child_key = 'blogs') 
    getBlogPosts = providers.Callable(db.getAssociatedList, child_key = 'posts') 
    delete = providers.Callable(db.delEntryList, session)
    findBlogsByNickName = providers.Callable(db.queryEntryList, session, db.Blog, 'blogNickName')

    #getTagBlogsGen = providers.Callable(db.queryEntryListGen, gense, db.Blog,\
    #                                   db.Tag.tagName, [db.tag_blog_table, db.Tag])
    makeTagCsv =providers.Callable(db.exportJoinedCsv, session, \
                                  db.Post, [db.Blog], \
                                  db.Post.__mapper__.columns + \
                                  [db.Blog.blogNickName, db.Blog.blogName, db.Blog.homePageUrl],\
                                    'tag')
    getLastestPost = providers.Callable(db.queryEntryList, session, db.Post,\
                                       'tag', order_by = db.Post.id, desc = True, limit = 1 )

    #updatePostsIp = providers.Callable(db.updateCols, session, db.Post, 'ip')
    


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

    img_url = minitools.stripiImageUrl
    main = aozoratext.posts2Aozora
    getImgs = aozoratext.htmlImages
    
    get_plain_txt_fname = aozoratext.makePlainFname 
