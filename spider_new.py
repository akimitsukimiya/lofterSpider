import myproviders
import config

DO_NOT = 0
DO = 1
DO_UPDATE = 2
IMAGE = 2
TEXT = 1

# Use ASCII code to get colorful strings
def colors(color,string):
    '''
    Usage colorful_str = colors('red', normal_str)
    '''
    clrs = {
        'red':u'\u001b[38;5;1m%s\u001b[0m',
        'green':u'\u001b[38;5;2m%s\u001b[0m',
        'yello':u'\u001b[38;5;3m%s\u001b[0m',
        'blue':u'\u001b[38;5;4m%s\u001b[0m',
        'pink':u'\u001b[38;5;5m%s\u001b[0m',
        'cyan':u'\u001b[38;5;6m%s\u001b[0m',
        'white':u'\u001b[38;5;7m%s\u001b[0m',
        'grey':u'\u001b[38;5;0m%s\u001b[0m',
     }
    return clrs[color] % string

printc(color, string):
    print(colors(color, string))

# A better spider
class LazyTagSpider:
    
    def __init__(self, tagName, minhot = config.minhot, \
                 blackwords = [],blacktags = [], blackusers = []\
                ):

        ## basic infos about this tag-centered sprider
        self.tagName = tagName
        self.minhot = minhot
        self.tag = None


        ##initialize database:
        myproviders.db.init()


    ##> get the tag orm-object stored in this spider
    def getTag(self):
        # lazy or not, it does no harm in storing a mere tag orm-object
        if not self.tag:
            tag = {'tagName' : self.tagName}
            self.tag = myproviders.db.syncOneTag(tag)
        
        return self.tag


    ##> iterate against all member blogs to base the archive of one tag
    def baseTagArchive(self, offset = 0, timestamp = 0):

        #get the tag orm-object
        tag = self.getTag()

        earliest = tag.latestPostTime or 0

        #get tag posts searcher
        tag_posts_searcher = myproviders.searchers.web_tag_searcher()

        #initialize tag posts searcher
        tag_posts_searcher.init(self.tagName, earliest = earliest)

        # record id's of based blogs
        blogids_based = []

        count = 0
        for posts in tag_posts_searcher.doSearchGenerator():

            count += 1
            
            # get blogs from posts
            blogs = {p['blogId']:p['blogInfo'] for p in posts if p}\
                    .values()
            blogs = [b for b in blogs \
                     if b['blogId'] not in blogids_based]

            if not blogs:
                continue

            ## base blogs ( or ignore based )
            self.baseblogs(blogs)
            if rebase_level is do:
                print(colors('red', '>> syncing raw posts to db!'))
                images_raw = self.getpostsimages(posts)
                posts = myproviders.db.syncposts(posts)
                images = myproviders.db.syncimages(images_raw)
                myproviders.db.addpoststotag(tag, posts)




            # record based blogs
            blogids_based += [b['blogid'] for b in blogs]

            print(colors('red', '>> lazy spider >> '), \
                      "resume tag searching!")


        info = colors('red', \
                      '>> lazy basing done >> \n>> based blogs: %10d\n>> based posts: %10d'\
                      % (myproviders.db.counttagblogs(tag),\
                        myproviders.db.counttagposts(tag) \
                        ))
        print(info)


    ##> base all posts published by a specific blog, orm-object required 






    ##> base all blogs provided by raw json blog list
    def baseblogs(self, blogs_raw):
        tag = self.getTag()

        blogs = myproviders.db.syncBlogs(blogs_raw)
        myproviders.db.addBlogsToTag(tag, blogs)
    
        # search for posts:
        posts_raw = []
        images_raw = []
        for blog in blogs:

            posts_raw, images_raw = self.getBlogPosts(blog)
            
        
        if not posts_raw:
            return None

        #sync new found posts to db
        posts = myproviders.db.syncNewPosts(posts_raw)
        myproviders.db.addPostsToTag(tag, posts)
        images = myproviders.db.syncNewImages(images_raw)

 
    def getblogposts(self, blog):
        
        # initialize a blog searcher
        post_searcher = myproviders.searchers.blog_searcher()
        earliest = blog.latestPostTime or 0

        ##do blog search
        info = colors('pink', ">> searching blog %s" % blog['blognickname'])
        print(info)
        posts_raw = post_searcher(tagName, blog, earliest = earliest)
        posts_raw = list({p['id'] : p for p in posts_raw}.values())
        info = colors('pink', "   %d posts fetched" % len(posts_raw))
        print(info)

        ##get all based posts
        posts_based = myproviders.db.getblogposts(blog)
        ids_based = [p['id'] for p in posts_based]
        info = colors('pink', ">> %d posts already based." % len(ids_based))
        print(info)

        ##calculate the unbased posts
        posts_raw = [p for p in posts_raw \
                   if p['id'] not in ids_based]
        info = colors('pink', ">> %d posts new to base." % len(posts_raw))
        print(info)

        ##ignore a fully based blog
        if not posts_raw:
            info=colors('pink', '>> blog %s already fully based!' % blog['blognickname'])
            print(info)
         
        images_raw = self.getpostsimages(posts_raw)
        return posts_raw, images_raw


    def getpostsimages(self, posts_raw):
        
        ##base image posts
        imgposts_raw = [post for post in posts_raw if post['type'] == 2]
        
        info = colors('pink', ">> %d new image posts to sync." % len(imgposts_raw))
        print(info)
        images = []

        for imgp_r in imgposts_raw:

            #image_links json
            image_links = imgp_r['photolinks']
            try:
                if image_links.__class__ is str:
                    image_links = image_links.replace("'",'"')
                    image_links = myproviders.tools.json_to_string(image_links)
                elif image_links.__class__ is list:
                    pass
                else:
                    raise exception('can\'t parse image links!')
            except exception as e:
                print(e)
                info = colors('pink', 'xx ignore one image post for it contains invalid links')
                print(info)
                continue

            if not image_links:
                info = colors('pink', 'xx ignore one image post for it contains invalid links')
                print(info)
                continue

            #fix image id
            #todo move this part to another module
            imgcount = 0
            for image_link in image_links:
                imgcount += 1
                image_link['id'] = imgp_r['id'] * 1000 + imgcount
                image_link['postid'] = imgp_r['id']
            images += image_links

        return images 




    ##> base all blogs referred by a pusher blog, orm-object required
    def baserefblogs(self, pusher_blog, rebase_level = do_not):
        '''
        base blogs referred by other blogs
        '''
        # initializing searching tools
        ref_blog_searcher = myproviders.searchers.ref_blog_searcher()
        info_getter = myproviders.searchers.blog_info_getter()
        tag = self.getTag()
        blogs_based = myproviders.db.getTagblogs(tag)
       # blogs_based = [b for b in blogs_based ]

        homepageurls_based = []
        if rebase_level in (do_not,):
            homepageurls_based = [str(b['homepageurl']) for b in blogs_based] 
        
        # search pusher blog and get urls of referred blogs
        info = colors('cyan', '>> starting parsing pusher blog %s to get referred blogs...' \
                     % pusher_blog['blognickname'])
        print(info)
        ref_blog_urls = ref_blog_searcher(self.tagName, pusher_blog) 
        ref_blog_urls = [url for url in ref_blog_urls \
                        if url not in homepageurls_based]
        info = colors('cyan', '   done! %d unbased blogs found !' % len(ref_blog_urls))
        print(info)

        if not len(ref_blog_urls):
            return

        info = colors('cyan', '>> start basing newly found referred blogs...')
        print(info)
        blog_jsons = []
        # get referred blogs info and sync:
        for blog_url in ref_blog_urls:
            
            #info = colors('grey', '>> get bloginfo from url %s.' % blog_url)
            #print(info)
            blog_json = info_getter(blog_url)

            #if it is a invalid user, ignore
            if not blog_json:
                info = colors('grey', 'xx blog %s unregistered!' % blog_url)
                print(info)
                continue

            #info = colors('grey', "oo blog found: %s "\
            #              % blog_json['blognickname'])
            #print(info)
            
            blog_jsons.append(blog_json)

        info = colors('cyan', '>> blog infos fetched. start basing...' )
        print(info)
        bcount,pcount = self.baseblogs(blog_jsons, rebase_level)
        info = colors('cyan', '>> %d new blogs based from referring blog %s.'\
                     % (bcount , pusher_blog['blognickname']))
        print(info)


    ##> base all blogs referred by pusher blogs, urls required
    def baserefblogsfromurl(self, pusher_urls, rebase_level = do_not):
        info_getter = myproviders.searchers.blog_info_getter()
        pusher_blogs = []
        for pusher_url in pusher_urls:
            pusher_blog = info_getter(pusher_url) 
            pusher_blog and pusher_blogs.append(pusher_blog)
        
        info = colors('red', '>>lazy spider>> basing blog by pusher urls...')
        print(info)
        count = 0
        leng = len(pusher_blogs)
        for pusher_blog in pusher_blogs:
            self.baserefblogs(pusher_blog, rebase_level)
            count += 1
            info = colors('red', '>> %d / %d done!' % (count, leng))
            print(info)


    ##> guest pusher blogs by tag name
    def guesspusherblogs(self):

        # get the tag orm-object
        potential_pusher_blogs = myproviders.db.findblogsbynickname(self.tagName)
        
        return potential_pusher_blogs
         

    ##> deepbase strategy 1: base referred blogs by potential pusher blogs in db
    def deepbase1(self, rebase_level = do_not):
        info = colors('red', '>>lazy spider>> strategy deepbase_1 : \
                      base blogs referred by potential pusher blogs...\
                      \n>> guessing pusher blogs...')
        print(info)

        pushers = self.guesspusherblogs()
        
        info = colors('red', '   %d potential pusher blogs found, start iterating.'\
                     % len(pushers))
        print(info)

        count = 0
        leng = len(pushers)
        for pusher_blog in pushers:
            count += 1
            info = colors('red', '>> iterating against potential pushers %d / %d'\
                     % (count, len(pushers)))
            print(info)
            self.baserefblogs(pusher_blog, rebase_level)

        info = colors('red', '>> deepbase_1 finished.')
        print(info)



    #############################################################################################


    #######################################dark region###########################################


    def updatepostsip(self):
        tag = self.getTag()
        tag_searcher = myproviders.searchers.web_tag_searcher()
        tag_searcher.init(self.tagName)
        print('>> start updating posts ip')
        
        for posts in tag_searcher.dosearchgenerator():
            posts = [p for p in posts if p['ip']]
            print('%d posts with ip found, updating...' % len(posts))
            #myproviders.db.updatepostsip(posts)



class DBSpider:

    def __init__(self, tagName, minhot = config.minhot, blackwords = [],\
                blacktags = [], blackusers = []):

        ## Basic infos about this tag-centered sprider
        self.tagName = tagName
        self.tag = myproviders.DB.syncOneTag(tagName = tagName)
        self.minhot = minhot
        self.blackwords = set(config.blackwords + blackwords)
        self.blacktags = set(config.blacktags + blacktags)
        self.blackusers = set(config.blackusers +  blackusers)

        ## Storing dir infos 
        # Read the dir info's from global config
        if not myproviders.Tools.isdir(config.data_export_dir):
            myproviders.Tools.mkdir(config.data_export_dir)
        # Seperate tag dir
        self.tag_dir = config.data_export_dir  + '/'+ tagName
        if not myproviders.Tools.isdir(self.tag_dir):
            myproviders.Tools.mkdir(self.tag_dir)

        #image and nov dir's under tag dir
        self.img_dir = self.tag_dir + '/' + config.image_dir_name
        self.nov_dir = self.tag_dir + '/' + config.nov_dir_name
        #self.nov_images_dir = self.nov_dir + '/nov_images'

    


    ###############
    ###Epub&Mobi###
    ###############


    def dlPackedImages(self, minhot = 0):

        thred = config.image_blog_limit
        other = config.other_img_dir

        print('Directly packing Images...')
        tagName = self.tagName
        #Sync a tag object from db
        tag = self.tag

        minhot = minhot or self.minhot
        #Get full path of root dir
        root = self.img_dir
        root = myproviders.Tools.abspath(root)


        #Initialize a downloader
        image_downloader = myproviders.Searchers.img_downloader()

        #Create root dir if not already exists
        if not myproviders.Tools.isdir(root):
            myproviders.Tools.mkdir(root)


        #Loop against associated blogs 
        for blog in myproviders.DB.getTagBlogs(tag):

            if blog['blogNickName'] in self.blackusers:
                continue

            #Get all image posts under blog
            posts = myproviders.DB.getBlogPosts(blog)
            posts = self.filterPosts(posts)

            #Get distict  dir path, create if not exists
            user_name = blog.blogNickName
            p_num = len(posts)

            #Ignore pure text blog
            if not p_num:
                continue
            
            #Get folder name according to blog nick name
            user_name = user_name.replace('/','_')
            if p_num >= thred:
                dir_path = root + '/' + user_name
            else:
                dir_path = root + '/' + others
            if not myproviders.Tools.isdir(dir_path):
                myproviders.Tools.mkdir(dir_path)

            #Loop against image posts under blog
            for post in posts:
                
                #Get post time in string
                dt = myproviders.Tools.dt(post.publishTime)
                
                #Get image entries under this post
                images = post.images
                if not len(images):
                    continue

                #Start downloading 
                for i in range(0, len(images)):
                    #Do download
                    old = image_downloader(dir_path, images[i])

                    #Ignore invalid images
                    if not old:
                        continue
 
                    #Get image extension
                    ext = myproviders.Tools.extension(old)   

                    #Name the image properly
                    new = dir_path + '/%s-%s-%03d.%s'  % (user_name, dt, i+1, ext)
                    try: 
                        myproviders.Tools.rn(old, new)
                    except FileNotFoundError as e:
                        print(e,"\nImages not renamed properly!")

            p_num and print("%d done!" % p_num)


    #TODO: unfinished
    def makeAozora(self, minhot = 0, minlen = 0):
        appName = config.app_name

        print('Start making Aozora text...')
        tagName = self.tagName
        tag = self.tag 
        txt0 = 'Lofter #%s #Archive%0d\n%s\n' 
        minhot = minhot or self.minhot

        #Get full path of root dir
        root = self.nov_dir
        #Create root dir if not already exists
        if not myproviders.Tools.isdir(root):
            myproviders.Tools.mkdir(root)
        #root = myproviders.Tools.abspath(root)

        #Get blogs ordered by post num
        blogs = myproviders.DB.getTagBlogs(tag)
        blogs = self.orderBlogs(blogs, order_by = '')

        count = 1
        txt = txt0 % (tagName, count, appName)
        for blog in blogs:

            #exclude blacklist users
            if blog['blogNickName'] in self.blackusers:
                continue

            #All text posts on a blog
            posts = myproviders.DB.getBlogPosts(blog)
            posts = self.filterPosts(posts, ptype = 1)

            if len(posts)  == 0:
                continue
            posts = self.orderPosts(posts)
            txt += myproviders.Tools.main(blog, posts, self.nov_dir) 
            
            if len(txt)*3 / 1024 / 1024 /2 >= config.max_epub_size:
                # TODO add time to filename
                fname = root + '/' + tagName + str(count) + '_raw.txt'
                with open(fname, 'w', encoding = 'utf-8') as f:
                    f.write(txt)
                count += 1
                txt = txt0 % (tagName, count, appName)
                print('%d txt\'s made.' % count)
         
        if len(txt) < 50:
            return None
        fname = root + '/' + tagName + str(count) + '_raw.txt'
        with open(fname, 'w', encoding = 'utf-8') as f:
            f.write(txt)



    def aozoraEpub3(self, delRaw = False):
        tools = myproviders.Tools
        root = self.nov_dir
        if not tools.isdir(root):
            print(root)
            print('No aozora text found !')
            return None
        
        print('Start converting aozora txt to epub ...')
        #convert to epub
        pjroot = myproviders.Tools.abspath('.')

        #go to aozora convertor dir
        #so root need to be a abs path now:
        root = myproviders.Tools.abspath(root)
        myproviders.Tools.cd(pjroot + '/' + \
                            'AozoraEpub3')
       
        for fname in tools.ls(root):
            if fname.endswith('txt'):
                myproviders.Tools.to_epub(root + '/' + \
                                      fname)
                if delRaw:
                    myproviders.Tools.rm(root + '/' + \
                                        fname)
                
        # go back to pjroot
        myproviders.Tools.cd(pjroot)
        print('Epub ebooks done !' )



    def makeMobi(self):
        tools = myproviders.Tools
        root = self.nov_dir
        root = tools.abspath(root)
        
        if not tools.isdir(root):
            print(root)
            print('No aozora text found !')
            return None
        
        print('Start converting eppub to mobi ...')
        #convert to epub
        pjroot = tools.abspath('.')
        #go to aozora convertor dir
        tools.cd(pjroot + '/' + 'AozoraEpub3')
       
        # convert
        for fname in tools.ls(root):
            if fname.endswith('epub'):
                tools.to_mobi(root + '/' + fname)
        # go back to pjroot
        tools.cd(pjroot)
        print('Mobi ebooks done !' )





    ###########
    ###PLAIN###
    ###########
           




    def packPostsPlain(self, ptype):
        #tagName = self.tagName
        
        if ptype not in (IMAGE, TEXT):
            print('Please assign a valid post type!')
            return

        main_dir =  self.img_dir if ptype is IMAGE \
                else self.nov_dir

        

        if not myproviders.Tools.isdir(main_dir):
            myproviders.Tools.mkdir(main_dir)

        links_f = ptype is TEXT and  open(main_dir + '/外链.txt', 'w')

        # Iterate against blogs
        #NOTE: unfinished, Generator approach for being lazy
        blogs  = myproviders.DB.getTagBlogs(self.tag)
        bcount = 0
        bleng = len(blogs)
        for blog in blogs:
            bcount += 1
            print('On blog %s' % blog['blogNickName'])
            print('%d / %d' % (bcount, bleng))


            # Exclude black users 
            if blog['blogNickName'] in self.blackusers:
                continue

            posts = myproviders.DB.getBlogPosts(blog)
            posts = self.filterPosts(posts, ptype = ptype)
            if not posts:
                continue

            if ptype is IMAGE and  config.image_blog_limit \
               and len(posts) < config.image_blog_limit:
                author_dir = main_dir + '/' + \
                        config.other_img_dir
            else:
                author_dir = main_dir + '/' + \
                        myproviders.Tools.fix_fname(blog['blogNickName'])

            if not myproviders.Tools.isdir(author_dir):
                myproviders.Tools.mkdir(author_dir)

            for post in posts:

                fname = myproviders.Tools.get_plain_txt_fname(blog, post)
                fname = myproviders.Tools.fix_fname(fname)
                body, urls, image_urls = myproviders.Tools.make_plain_body(blog, post)

                # Download Images
                count = 0
                
                leng = len(image_urls)
                image_paths = []

                if ptype is IMAGE:
                    image_urls = [myproviders.Tools.img_url(i['middle']) \
                                 for i in myproviders.DB.getPostImages(post)
                                 ]

                for image_url in image_urls:
                    ext = myproviders.Tools.extension(image_url)   
                    iname = fname + ' (%03d)' % (count +1) +  '.' + ext 
                    path = self.downloasImage(author_dir, iname, image_url)
                    if not path:
                        iname = "(图片已失效！)"
                    image_paths.append(iname)
                    count += 1

                # Make Ref & links
                links = (urls or image_urls) and \
                        myproviders.Tools.make_links(blog['blogNickName']+'/'+fname+'.txt',\
                                                    urls, image_urls)
                ref = myproviders.Tools.make_ref( urls, image_paths )
                body = body + ref

                links and ptype is TEXT and links_f.write(links)

                try:
                    with open(author_dir + '/' + fname + '.txt', 'w', encoding = 'utf-8') as f:
                        f.write(body)
                        f.close()
                except Exception as e:
                    print('ERROR writing file:', e)


        ptype is TEXT and links_f.close()
                


    ###########
    ###Utils###
    ###########



    def downloasImage(self, root, fname, image_url):
        downloader = myproviders.Searchers.url_img_downloader()
        path = downloader(root, image_url, fname = fname )
        return path



    def filterPosts(self, posts, ptype = 0):
        posts = [p for p in posts \
                if self.tag in myproviders.DB.getPostTags(p) \
                and (not ptype or p['type'] is ptype)
                and self.checkHot(p, self.minhot) \
                and self.excludeBlack(p['title'], self.blackwords) \
                and self.excludeBlack(p['tag'], self.blacktags)
                ]
        return posts



    def orderBlogs(self, blogs, order_by = 1):
        # TODO add more cases
        key = lambda e : len(myproviders.DB.getBlogPosts(e))
        l = sorted(blogs, key = key, reverse = True)
        return l


    def orderPosts(self, posts):
        # TODO add collection infos
        collections = set([p['collectionId'] for p in posts])
        s_posts = {i:[p for p in posts if p['collectionId'] == i] \
                  for i in collections}
        key = lambda e:e['publishTime']
        l =[]
        for col in s_posts:
            l += sorted(s_posts[col], key = key)
        return l


    def excludeBlack(self, string, blacklist):
        for b in blacklist:
            if string and b in string:
                return False
        return True


    def checkHot(self, post, mh):
        hot = post.hot
        hot = post.hot or 0
        if hot >= mh:
            return True
        return False





