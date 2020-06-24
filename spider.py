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

   
# eager spider, do everything 'eagerly', never yield or pause,
# whenever fetching things (either from remote server or from local db), 
# always does its task once and for all...
# Sometimes too eager for large tags, but rather safe when dealing with db update
class EagerTagSpider:

    def __init__(self, tagName, minhot = 0, \
                 blackwords = [], blacktags = [], blackusers = []):
        '''
        tagName - for this is a tag-centered fetching machine
        minhot - useful when filters are wanted for exporting data
        blackwords - another filter for title
        blacktag - for tags field
        blackusers - as how it is named
        '''
        self.tagName = tagName
        self.minhot = minhot
        self.blackwords = blackwords
        self.blacktags = blacktags
        self.blackusers = blackusers
        self.tag = None
        
        # As this is a eager spider,
        # it carries with it a large set of in-memory posts data
        # To make it even more convenient, this set of data is actually the ORM-object
        # managed by a global sqlAlchemy session, can be used as a shortcut to data query
        # whenever needed.
        self.posts = None

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

        ##Initialize database:
        myproviders.DB.init()


    ##############
    ####Baser#####
    ##############


    def getTag(self):
        if not self.tag:
            self.tag = myproviders.DB.syncOneTag(tagName = self.tagName) 
        return self.tag


    def getTagPostArchive(self):
        if self.posts:
            return self.posts
        tagName = self.tagName

        #Sync a tag object from db
        tag = self.getTag()
        posts = myproviders.DB.getTagPosts(tag)
        
        posts = [post for post in posts \
                 if self.checkHot(post, self.minhot)
                ]
        self.posts = posts

        return posts


    def baseTagArchive(self, re = False, maxnum = 0):
        tagName = self.tagName

        ##Query for a tag entry or add a entry to db:
        tag = self.getTag()
        blog_searcher = myproviders.Searchers.web_blog_on_tag_searcher()
        self.tag = tag

        #Get stored blogs
        #blogs_stored  = myproviders.DB.getTagBlogs(tag)

       
        ##TODO: rebase function not yet finished
        if re:
            self.clearBasedData()

        ##Search for blogs under the tagName:
        blogs = blog_searcher(tagName, maxnum = maxnum) #NOTE:try!!
        print('%d blogs found!' % len(blogs))
        
        ##Store blog in db:
        ##Update tag's blog list:
        print('Saving blogs to db...')
        blogs = myproviders.DB.syncBlogs(blogs)
        myproviders.DB.addBlogsToTag(tag, blogs)
        
        ##Search for posts:
        count = 0
        leng = len(blogs)
        for blog in blogs:

            self.baseBlogPosts(blog)             
            count += 1
            print("Basing posts from blogs: %3d / %3d Done." % (count,leng))
                

    def basePostCommentArchive(self):
        #Get posts entries from field
        posts = self.getTagPostArchive()
        #Initialize comment searchers
        comment_searcher = myproviders.Searchers.comment_searcher()
        l2comment_searcher = myproviders.Searchers.l2comment_searcher()
    
        count = 0
        leng = len(posts)
        print('Basing comments...')
        for p in posts:
            ##Search for l1 comments json:
            comments = comment_searcher(p.blogInfo, p) 
            comment_blogs = [c['publisherMainBlogInfo'] for c in comments]
            comment_to_blogs = [c['replyBlogInfo'] for c in comments \
                                if 'replyBlogInfo' in c and c['replyBlogInfo']]
    
            ##Sync l1 comments to db:
            myproviders.DB.syncBlogs(comment_blogs)
            myproviders.DB.syncBlogs(comment_to_blogs)
            myproviders.DB.syncComments(comments)
    
            ##search for l2 comments
            comments = p.comments
            l2_comments = []
            for c in comments:
                l2_comments += l2comment_searcher(p, c)
            comment_blogs = [c['publisherMainBlogInfo'] for c in l2_comments]
            comment_to_blogs = [c['replyBlogInfo'] for c in l2_comments \
                                if 'replyBlogInfo' in c and c['replyBlogInfo']]
    
            #Sync l2 comments to db:
            myproviders.DB.syncBlogs(comment_blogs)
            myproviders.DB.syncBlogs(comment_to_blogs)
            myproviders.DB.syncComments(sorted(l2_comments, key = lambda c:c['publishTime']))
            count += 1
            print("%3d / %3d Done." % (count, leng))


    def baseBlogPosts(self, blog):
        post_searcher = myproviders.Searchers.blog_searcher()
        tag = self.getTag()


        ##Get all based posts
        posts_based = myproviders.DB.getBlogPosts(blog)
        ids_based = [p['id'] for p in posts_based]
        print("%d posts already based." % len(ids_based))

        ##Calculate the unbased posts
        posts_r = [p for p in posts_r \
                   if p['id'] not in ids_based]
        print("%d posts new to base." % len(posts_r))
        
        ##Ignore a fully based blog
        if not posts_r:
            print('Blog %s already based!' % blog['blogNickName'])
            return 0 

        ##Sync posts to db:
        posts = myproviders.DB.syncNewPosts(posts_r)
        myproviders.DB.addNewPostsToTag(tag, posts)
        
        print('Posts synced! Basing images...')

        
        ##Base image posts
        imgposts_raw = [post for post in posts_r if post['type'] == 2]

        for imgp_r in imgposts_raw:
            #image_links json
            image_links = imgp_r['photoLinks']
            try:
                image_links = myproviders.Tools.json_to_string(image_links)
            except:
                continue

            if not image_links:
                continue


            #fix image id
            # for the original image id's contain non-digital char's
            #TODO move this part to another module
            imgcount = 0
            for image_link in image_links:
                imgcount += 1
                image_link['id'] = imgp_r['id'] * 1000 + imgcount
                image_link['postId'] = imgp_r['id']

            #Sync json to db
            try:
                image = myproviders.DB.syncNewImages(image_links)
            except Exception as e:
                print(image_links)
                print(e)
                break
            
        print("%d images based!" % imgcount)
        print("%d posts added from blog %s in total!" % (len(posts), blog['blogNickName'])) 
        return len(posts)


    ################
    ####DeepBaser###
    ################


    def baseRefBlogsFromUrl(self, pusher_blog_url):
        # Initializing searching tools
        info_getter = myproviders.Searchers.blog_info_getter()
        tag = self.getTag()
        # get urls of referenced blogs
        pusher_blog_json = info_getter(pusher_blog_url)
        pusher_blog = myproviders.DB.syncOneBlog(**pusher_blog_json)
        self.baseRefBlogs(pusher_blog)

    
    def baseRefBlogs(self, pusher_blog):
        # Initializing searching tools
        info_getter = myproviders.Searchers.blog_info_getter()
        ref_blog_searcher = myproviders.Searchers.ref_blog_searcher()
        tag = self.getTag()

        ref_blog_urls = ref_blog_searcher(self.tagName, pusher_blog) 

        # get refommended blogs info and sync:
        for blog_url in ref_blog_urls:
            blog_json = info_getter(blog_url)

            #If it is a invalid user, ignore
            if not blog_json:
                continue
            blog = myproviders.DB.syncOneBlog(**blog_json)
        

            #If already based this user, ignore
            if blog in myproviders.DB.getTagBlogs(tag):
                continue
            print("An unadded blog found, basing posts...")
            print("Blog url:", blog_url)
            # add blog to tag
            myproviders.DB.addBlogsToTag(tag, [blog])
            self.baseBlogPosts(blog)


    def deepBase1(self):
        print('######DEEP BASER 1 STARTED ！')
        print('Basing Strategy: Iterate against all post contents to find un-based blogs.')
        tag = self.getTag()
        blogs = myproviders.DB.getTagBlogs(tag)

        for blog in blogs:
            self.baseRefBlogs(blog)


    ###############
    ####NotInUse###
    ###############


    #TODO: This is a very important feature, need to be finished!       
    def clearBasedData(self):
        tag = self.getTag()
        blogs = myproviders.DB.getTagBlogs(tag)
        posts = myproviders.DB.getTagPosts(tag)

        
    #NOTE: deprecated!
    def baseImageArchive(self):
        #Get posts entries from field
        posts = self.getTagPostArchive()
        #Initialize a searcher
        img_searcher = myproviders.Searchers.img_searcher()
        posts = [p for p in posts if p.type == 2]
        count = 0
        leng = len(posts)
        print('Basing images...')
        for post in posts:
            if post.type == 2:
                ##Search for Images
                image_links  = img_searcher(post.blogInfo, post)
                ##Sync to  db
                try:
                    images = myproviders.DB.syncImages(image_links)
                except Exception as e:
                    print(post.blogInfo.homePageUrl + '/view/' + post.permalink)
                    print(image_links)
                    print(e)
                    break
                #Add image lists to post
                myproviders.DB.addImagesToPost(post, images)
            count += 1
            print("%3d / %3d Done." % (count, leng))

    
    #NOTE: deprecated!
    def downloadImages(self, root = 'images'):
        tagName = self.tagName
        #Get posts entries from field
        posts = self.getTagPostArchive()
        #Initialize a downloader
        image_downloader = myproviders.Searchers.img_downloader()

        root = root + '/' + tagName
        #better use absolute dir path
        root = myproviders.Tools.abspath(root)

        if not myproviders.Tools.isdir(root):
            myproviders.Tools.mkdir(root)
        
        posts = [post for post in posts if post.type == 2]
        count = 0
        leng = len(posts)
        print('Start downloading images...')
        for post in posts:
            #Get image lists associated with post
            images = myproviders.DB.getPostImages(post)
            for image in images:
                #Dounload image and get path string 
                path = image_downloader(root, image)
                #Update path on image entry
                image.path = path
                #Sync image entry
                myproviders.DB.syncOneEntry(image)
            count += 1 
            print(count,' / ', leng, ' Downloaded!')


    #NOTE: currently not in use
    def deleteImages(self, root = 'images'):
        #Get posts entries from field
        posts = self.getTagPostArchive()
        #Initialize a downloader

        if not myproviders.Tools.isdir(root):
            return None 
        posts = [post for post in posts if post.type == 2]
        print('Start deleting images...')
        for post in posts:
            #Get image lists associated with post
            images = myproviders.DB.getPostImages(post)
            for image in images:
                path = image.path
                if not path or path == '-':
                    continue
                myproviders.Tools.rm(path)
                #Update path on image entry
                image.path = '-'
                #Sync image entry
                myproviders.DB.syncOneImage(image)
        print('Done.')


    #NOTE: currently not in use
    def downloadNovImages(self, root = ''):
        #Get posts entries from field
        posts = self.getTagPostArchive()
        #Initialize a downloader
        novimage_downloader = myproviders.Searchers.novimg_downloader()

        root = root or self.nov_images_dir
        if not myproviders.Tools.isdir(root):
            myproviders.Tools.mkdir(root)
        
        posts = [post for post in posts if post.type == 1]
        count = 0
        print('Start downloading text blog images...')
        for post in posts:
            
            #Get image lists associated with post
            imgs = myproviders.Tools.getImgs(post.content, post.id)
            imgs = myproviders.DB.syncNovImages(imgs)
            if not len(imgs):
                continue
            for image in imgs:

                #Dounload image and get path string 
                path = novimage_downloader(root, image)
                
                #Update path on image entry
                image.path = path
                #Sync image entry
                myproviders.DB.syncOneEntry(image)


            count += 1 
            print(count, ' Downloaded!')


    #NOTE: deprecated!
    #TODO arguments' default values would better be stored in a global config file
    def packImages(self, minhot = 0, others = '其他', thred = 5):
        print('Packing Images...')
        tagName = self.tagName
        minhot = minhot or self.minhot
        #Get full path of root dir
        root = self.img_dir
        root = myproviders.Tools.abspath(root)

        #Create root dir if not already exists
        if not myproviders.Tools.isdir(root):
            myproviders.Tools.mkdir(root)

        #Sync a tag object from db
        tag = self.getTag()

        #Loop against associated blogs 
        for blog in myproviders.DB.getTagBlogs(tag):

            if blog['blogNickName'] in self.blackusers:
                continue

            #Get all image posts under blog
            posts = myproviders.DB.getBlogPosts(blog)
            posts = [post for post in posts \
                    if post.type == 2 \
                    and tagName in post.tag \
                    and self.excludeBlack(post.tag, self.blacktags) \
                  #  and post.hot >= minhot\
                    ]

            #Get distict  dir path, create if not exists
            user_name = blog.blogNickName
            p_num = len(posts)
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
                for i in range(0, len(images)):
                    #Copy image to distinct dir
                    old = images[i].path
                    if not old:
                        continue
                    ext = myproviders.Tools.extension(old)                
                    new = dir_path + '/%s-%s-%03d.%s'  % (user_name, dt, i+1, ext)
                    #print(new)
                    try: 
                        myproviders.Tools.cp(old, new)
                    except FileNotFoundError as e:
                        # TODO: several kinds of exception could happen if the images are not properly based, 
                        # this handler should be detailed
                        print(e,"\nImages not based properly!")
        # TODO auto zip


    ##############
    ###Exporter###
    ##############


    def dlPackedImages(self, minhot = 0):

        thred = config.image_blog_limit
        other = config.other_img_dir

        print('Directly packing Images...')
        tagName = self.tagName
        #Sync a tag object from db
        tag = self.getTag()

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
            posts = [post for post in posts \
                    if post.type == 2 \
                    and tagName in post.tag \
                    and self.excludeBlack(post.tag, self.blacktags) \
                    and self.checkHot(post, minhot)\
                    ]

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


    def makeAozora(self, minhot = 0, minlen = 0):
        appName = config.app_name

        print('Start making Aozora text...')
        tagName = self.tagName
        tag = self.getTag() 
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
            posts = [p for p in posts \
                    if p.type == 1 \
                    and len(p.content) >= minlen \
                    and tagName in p.tag \
                    and self.checkHot(p, minhot) \
                    and self.excludeBlack(p.title, self.blackwords) \
                    and self.excludeBlack(p.tag, self.blacktags)]
                

            if len(posts)  == 0:
                continue
            posts = self.orderPosts(posts)
            txt += myproviders.Tools.main(blog, posts, self.nov_dir) 
            
            if len(txt) / 1024 / 1024 >= 1:
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
    ###Utils###
    ###########


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




# A better spider
class LazyTagSpider:
    
    def __init__(self, tagName, minhot = config.minhot, blackwords = [],\
                blacktags = [], blackusers = []):

        ## Basic infos about this tag-centered sprider
        self.tagName = tagName
        self.minhot = minhot
        self.blackwords = set(config.blackwords + blackwords)
        self.blacktags = set(config.blacktags + blacktags)
        self.blackusers = set(config.blackusers +  blackusers)
        self.tag = None

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

        ##Initialize database:
        myproviders.DB.init()


    ##> Get the tag orm-object stored in this spider
    def getTag(self):
        # Lazy or not, it does no harm in storing a mere tag orm-object
        if not self.tag:
            tag = {'tagName' : self.tagName}
            self.tag = myproviders.DB.syncOneTag(**tag)
        
        return self.tag


    def getLastestPublishTimeInDb(self):

        latest = myproviders.DB.getLastestPost(self.tagName)
        if latest:
            latest = latest[0]['publishTime']
        else:
            latest = 0
        return latest


    ##> Iterate against all member blogs to base the archive of one tag
    def baseTagArchive(self, rebase_level = DO_NOT, offset = 0, timestamp = 0):

        #Get the tag orm-object
        tag = self.getTag()

        #Get tag posts searcher
        tag_posts_searcher = myproviders.Searchers.web_tag_searcher()
        if rebase_level in (DO_NOT,DO_UPDATE):
            earliest = self.getLastestPublishTimeInDb() + 1
        else:
            earliest = 0
        #Initialize tag posts searcher
        tag_posts_searcher.init(self.tagName, earliest = earliest,\
                                timestamp = timestamp, offset = offset)

        # Record id's of based blogs
        blogIds_based = []
        if rebase_level is DO_NOT:
            blogs_based = myproviders.DB.getTagBlogs(tag)
            blogIds_based += [b['blogId'] for b in blogs_based]
        

        #Use the generator doSearch method
        #to search posts from a tag
        print(colors('red', '>>LAZY SPIDER>> '), \
              "Start tag searching !")
        count = 0
        plen = 0
        blen = 0
        for posts in tag_posts_searcher.doSearchGenerator():

            count += 1
            
            # Get blogs from posts
            blogs = {p['blogId']:p['blogInfo'] for p in posts if p}\
                    .values()
            blogs = list(blogs)
            blogs = [b for b in blogs if b['blogId'] not in blogIds_based]
            print(colors('red', '>> %d based blogs recorded!' % len(blogIds_based)))
            print(colors('red', '>> %d tag search done: ' % count))
            print(colors('green', '>> %d new blogs found!' % len(blogs)))

            if not blogs:
                continue

            ## Base blogs ( or ignore based )
            bcount, pcount = self.baseBlogs(blogs, rebase_level)
            plen += pcount
            blen += bcount


            # Record based blogs
            blogIds_based += [b['blogId'] for b in blogs]

            print(colors('red', '>> LAZY SPIDER >> '), \
                      "Resume tag searching!")
        info = colors('red', '>> LAZY BASING DONE !\n>> Based blogs: %10d\n>> Based posts: %10d'\
                      % (blen,plen))
        print(info)


    ##> Base all posts published by a specific blog, orm-object required 
    def baseBlogPosts(self, blog, rebase_level = DO_NOT):
        tagName = self.tagName
        
        # Initialize a blog searcher
        post_searcher = myproviders.Searchers.blog_searcher()
        if rebase_level in (DO_NOT, DO_UPDATE):
            earliest = self.getLastestPublishTimeInDb() + 1
        else:
            earliest = 0

        ##Do blog search
        info = colors('pink', ">> Searching blog %s" % blog['blogNickName'])
        print(info)
        posts_raw = post_searcher(tagName, blog, earliest = earliest)
        posts_raw = list({p['id'] : p for p in posts_raw}.values())
        info = colors('pink', "   %d posts fetched" % len(posts_raw))
        print(info)

        ##Get all based posts
        posts_based = myproviders.DB.getBlogPosts(blog)
        ids_based = [p['id'] for p in posts_based]
        info = colors('pink', ">> %d posts already based." % len(ids_based))
        print(info)

        ##Calculate the unbased posts
        posts_raw = [p for p in posts_raw \
                   if p['id'] not in ids_based]
        info = colors('pink', ">> %d posts new to base." % len(posts_raw))
        print(info)

        ##Ignore a fully based blog
        if not posts_raw:
            info=colors('pink', '>> Blog %s already fully based!' % blog['blogNickName'])
            print(info)
         
        yield 'posts_raw', posts_raw
        
        ##Base image posts
        imgposts_raw = [post for post in posts_raw if post['type'] == 2]
        
        info = colors('pink', ">> %d new image posts to base." % len(imgposts_raw))
        print(info)

        for imgp_r in imgposts_raw:

            #image_links json
            image_links = imgp_r['photoLinks']
            try:
                image_links = myproviders.Tools.json_to_string(image_links)
            except:
                info = colors('pink', 'xx Ignore one image post for it contains invalid links')
                print(info)
                continue

            if not image_links:
                info = colors('pink', 'xx Ignore one image post for it contains invalid links')
                print(info)
                continue

            #fix image id
            #TODO move this part to another module
            imgcount = 0
            for image_link in image_links:
                imgcount += 1
                image_link['id'] = imgp_r['id'] * 1000 + imgcount
                image_link['postId'] = imgp_r['id']

            yield 'images_raw',image_links
        

        info = colors('pink',\
                      ">> %d posts added from blog %s in total." \
                      % (len(posts_raw), blog['blogNickName'] or '')) 
        print(info)


    ##> Base all blogs provided by raw json blog list
    ##> NEVER input based blog_jsons with flag DO_NOT!!!
    def baseBlogs(self, blogs_raw, rebase_level = DO_NOT):
        tag = self.getTag()

        print(colors('green', '>> Syncing blogs to db...'))
        if rebase_level is DO_NOT:
            blogs = myproviders.syncNewBlogs(blogs_raw)
            myproviders.DB.addNewBlogsToTag(tag, blogs)
        else:
            blogs = myproviders.DB.syncBlogs(blogs_raw)
            myproviders.DB.addBlogsToTag(tag, blogs)
    
        # Search for posts:
        bcount = 0
        leng = len(blogs)
        posts_raw = []
        images_raw = []
        for blog in blogs:

            #Search for blog posts one at a time
            for yname,yval in self.baseBlogPosts(blog, rebase_level):
                if yname == 'posts_raw':
                    posts_raw += yval
                if yname == 'images_raw':
                    images_raw += yval


            bcount += 1
            info = colors('green',\
                         ">> Searching new posts from blogs: %3d / %3d Done." % (bcount, leng))
            print(info)
        
        if not posts_raw:
            return len(blogs),0

        

        #Sync new found posts to db
        print(colors('blue', '>> Syncing %d posts to db...' % len(posts_raw)))
        posts = myproviders.DB.syncNewPosts(posts_raw)
        myproviders.DB.addNewPostsToTag(tag, posts)
        info =  colors('blue', '>> %d newly fetched posts synced.' % len(posts))
        print(info)

        #Sync new found images to db
        images = myproviders.DB.syncNewImages(images_raw)
        info =  colors('blue', '>> %d newly fetched imaged synced.' % len(images))
        print(info)

        return len(blogs), len(posts_raw)
 

    ##> Base all blogs referred by a pusher blog, orm-object required
    def baseRefBlogs(self, pusher_blog, rebase_level = DO_NOT):
        '''
        Base blogs referred by other blogs
        '''
        # Initializing searching tools
        ref_blog_searcher = myproviders.Searchers.ref_blog_searcher()
        info_getter = myproviders.Searchers.blog_info_getter()
        tag = self.getTag()
        blogs_based = myproviders.DB.getTagBlogs(tag)
       # blogs_based = [b for b in blogs_based ]

        homePageUrls_based = []
        if rebase_level in (DO_NOT,):
            homePageUrls_based = [str(b['homePageUrl']) for b in blogs_based] 
        
        # Search pusher blog and get urls of referred blogs
        info = colors('cyan', '>> Starting parsing pusher blog %s to get referred blogs...' \
                     % pusher_blog['blogNickName'])
        print(info)
        ref_blog_urls = ref_blog_searcher(self.tagName, pusher_blog) 
        ref_blog_urls = [url for url in ref_blog_urls \
                        if url not in homePageUrls_based]
        info = colors('cyan', '   Done! %d unbased blogs found !' % len(ref_blog_urls))
        print(info)

        if not len(ref_blog_urls):
            return

        info = colors('cyan', '>> Start basing newly found referred blogs...')
        print(info)
        blog_jsons = []
        # get referred blogs info and sync:
        for blog_url in ref_blog_urls:
            
            #info = colors('grey', '>> Get blogInfo from url %s.' % blog_url)
            #print(info)
            blog_json = info_getter(blog_url)

            #If it is a invalid user, ignore
            if not blog_json:
                info = colors('grey', 'xx Blog %s unregistered!' % blog_url)
                print(info)
                continue

            #info = colors('grey', "oo Blog found: %s "\
            #              % blog_json['blogNickName'])
            #print(info)
            
            blog_jsons.append(blog_json)

        info = colors('cyan', '>> Blog infos fetched. Start basing...' )
        print(info)
        bcount,pcount = self.baseBlogs(blog_jsons, rebase_level)
        info = colors('cyan', '>> %d new blogs based from referring blog %s.'\
                     % (bcount , pusher_blog['blogNickName']))
        print(info)


    ##> Base all blogs referred by pusher blogs, urls required
    def baseRefBlogsFromUrl(self, pusher_urls, rebase_level = DO_NOT):
        info_getter = myproviders.Searchers.blog_info_getter()
        pusher_blogs = []
        for pusher_url in pusher_urls:
            pusher_blog = info_getter(pusher_url) 
            pusher_blog and pusher_blogs.append(pusher_blog)
        
        info = colors('red', '>>LAZY SPIDER>> Basing blog by pusher urls...')
        print(info)
        count = 0
        leng = len(pusher_blogs)
        for pusher_blog in pusher_blogs:
            self.baseRefBlogs(pusher_blog, rebase_level)
            count += 1
            info = colors('red', '>> %d / %d Done!' % (count, leng))
            print(info)


    ##> Guest pusher blogs by tag name
    def guessPusherBlogs(self):

        # Get the tag orm-object
        potential_pusher_blogs = myproviders.DB.findBlogsByNickName(self.tagName)
        
        return potential_pusher_blogs
         

    ##> DeepBase strategy 1: base referred blogs by potential pusher blogs in db
    def deepBase1(self, rebase_level = DO_NOT):
        info = colors('red', '>>LAZY SPIDER>> Strategy DeepBase_1 : \
                      base blogs referred by potential pusher blogs...\
                      \n>> Guessing pusher blogs...')
        print(info)

        pushers = self.guessPusherBlogs()
        
        info = colors('red', '   %d potential pusher blogs found, start iterating.'\
                     % len(pushers))
        print(info)

        count = 0
        leng = len(pushers)
        for pusher_blog in pushers:
            count += 1
            info = colors('red', '>> Iterating against potential pushers %d / %d'\
                     % (count, len(pushers)))
            print(info)
            self.baseRefBlogs(pusher_blog, rebase_level)

        info = colors('red', '>> DeepBase_1 finished.')
        print(info)



    #############################################################################################


    #TODO: unfinished
    def makeAozora(self, minhot = 0, minlen = 0):
        appName = config.app_name

        print('Start making Aozora text...')
        tagName = self.tagName
        tag = self.getTag() 
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
            
            if len(txt) / 1024 / 1024 >= 1:
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
        blogs  = myproviders.DB.getTagBlogs(self.getTag())
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
                


    def downloasImage(self, root, fname, image_url):
        downloader = myproviders.Searchers.url_img_downloader()
        path = downloader(root, image_url, fname = fname )
        return path



    def filterPosts(self, posts, ptype = 0):
        posts = [p for p in posts \
                if self.tagName in p['tag'] \
                and (not ptype or p['type'] is ptype)
                and self.checkHot(p, self.minhot) \
                and self.excludeBlack(p['title'], self.blackwords) \
                and self.excludeBlack(p['tag'], self.blacktags)
                ]
        return posts



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
        


    def orderBlogs(self, blogs, order_by = 1):
        # TODO add more cases
        key = lambda e : len(myproviders.DB.getBlogPosts(e))
        l = sorted(blogs, key = key, reverse = True)
        return l
