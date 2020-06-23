from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table,Column, String, Boolean, ForeignKey
from sqlalchemy.dialects.mysql import INTEGER, BIGINT,LONGTEXT, TINYINT,TEXT
from sqlalchemy.orm import sessionmaker, relationship, backref

#Create an engine
db_prefix = 'lofter_'
db_name = 'lofter'
db_url_pattern = 'mysql://lofter:dowager@localhost/%s' 
db_url = db_url_pattern % db_name
engine = create_engine(db_url, echo = False)
Session = sessionmaker(bind = engine)
se = Session()

#Declarative system: describing table & defining mapped class are done together
Base = declarative_base()
metadata = Base.metadata




##TABLES & MODELS##


#When our class is constructed, Declarative replaces all the Column objects with special Python accessors known as descriptors; this is a process known as instrumentation. The “instrumented” mapped class will provide us with the means to refer to our table in a SQL context as well as to persist and load the values of columns from the database.
tag_blog_table = Table('tag_blog_table', metadata, 
                      Column('blogId', INTEGER(11), ForeignKey('blogInfos.blogId'), primary_key=True),
                      Column('tagId', INTEGER(11), ForeignKey('tags.tagId'), primary_key=True)) 

tag_post_table = Table('tag_post_table', metadata, 
                      Column('postId', BIGINT(13), ForeignKey('posts.id'), primary_key=True),
                      Column('tagId', INTEGER(11), ForeignKey('tags.tagId'), primary_key=True)) 


class SuperBase(object):

    def __getitem__(self, item):
         return getattr(self, item)
    
    def cols(self):
        cols = [k for k in self.__dict__ \
               if not k.startswith('_')]
        return cols


class Tag(Base, SuperBase):
    __tablename__ = 'tags'
    tagId = Column(INTEGER(11), primary_key = True)
    tagName = Column(String(50), index = True)
    
    def __repr__(self):
        return "<Tag(tagName='%s')>" % self.tagName


class Blog(Base, SuperBase):
    __tablename__ = 'blogInfos'
    blogId = Column(INTEGER(11), primary_key = True, autoincrement = False)
    blogName = Column(String(50))
    blogNickName = Column(String(50))
    bigAvaImg = Column(String(255))
    avatarBoxImage = Column(String(225))
    keyTag = Column(String(225))
    blogCreateTime = Column(BIGINT(13))
    avaUpdateTime = Column(BIGINT(13))
    rssFileId = Column(BIGINT(13))
    rssGenTime = Column(BIGINT(13))
    postModTime = Column(BIGINT(13))
    postAddTime = Column(BIGINT(13))
    commentRank = Column(BIGINT(13))
    imageProtected = Column(Boolean)
    imageStamp = Column(Boolean)
    imageDigitStamp = Column(Boolean)
    gendar = Column(INTEGER())
    birthday = Column(BIGINT(13))
    novisible = Column(Boolean)
    #auths = 
    isOriginalAuthor = Column(Boolean)
    homePageUrl = Column(String(255))
    signAuth = Column(Boolean)
   # NOTE:complex adjacency list relationships
   # using foreign_keys argument of relationship()
   # motherBlogId = Column(INTEGER(11), ForeignKey('blogInfos.blogId'))
   # fatherBlogId = Column(INTEGER(11), ForeignKey('blogInfos.blogId')) 
   # fatherBlogInfo = relationship('Blog', foreign_keys = [fatherBlogId], backref = 'children_sired', remote_side = [blogId])
   # motherBlogInfo = relationship('Blog', foreign_keys = [motherBlogId], backref = 'children_born', remote_side = [blogId])
    tags = relationship('Tag', secondary = tag_blog_table, \
                       backref = backref('blogs', order_by = blogId))
    #posts = relationship('Post', backref = 'blogInfo')
    
    def __init__(self, **kwargs):
        if 'auths' in kwargs:
            del kwargs['auths']
        super().__init__(**kwargs)

    def __repr__(self):
        return "<Blog(blogId='%d', blogNickName='%s')>" % (self.blogId, self.blogNickName)
    

class Post(Base, SuperBase):
    __tablename__ = 'posts'
    id = Column(BIGINT(13), primary_key = True, autoincrement = False)
    blogId = Column(INTEGER(11), ForeignKey('blogInfos.blogId'))
    publisherUserId = Column(INTEGER(11))
    collectionId = Column(INTEGER(11))
    isContribute = Column(Boolean)
    title = Column(String(50))
    publishTime = Column(BIGINT(13))
    modifyTime = Column(BIGINT(13))
    isPublished = Column(Boolean)
    allowView = Column(TINYINT(1))
    valid = Column(TINYINT(1))
    rank = Column(TINYINT(1))
    tag = Column(String(255))
    moveFrom = Column(String(50))
    citeParentPostId = Column(BIGINT(13))
    citeParentBlogId = Column(INTEGER(11))
    citeRootPostId = Column(BIGINT(13))
    citeRootBlogId = Column(INTEGER(11))
    type = Column(TINYINT(1))
    ip = Column(String(20))
    digest = Column(LONGTEXT)
    #firstImageUrl
    cctype = Column(TINYINT(1))
    locationId = Column(INTEGER(11))
    forbidShare = Column(TINYINT(1))
    allowReward = Column(TINYINT(1))
    top = Column(TINYINT(1))
    payView = Column(TINYINT(1))
    realPublisherUserIdUpdate = Column(BIGINT(13))
    example = Column(INTEGER())
    sourceLink = Column(String(255))
    pos =  Column(INTEGER())
    afterPostId = Column(BIGINT(13))
    prePostId = Column(BIGINT(13))
    freeWords = Column(INTEGER())
    payViewExpire = Column(Boolean)
    content = Column(LONGTEXT)
    originalType = Column(TINYINT(1))
    noticeLinkTitle = Column(String(50))
    hot = Column(INTEGER(11))
    firstImageUrlForAnti = Column(String(255))
    viewRank = Column(INTEGER())
    permalink = Column(String(50))
    dirPostType = Column(TINYINT(1))
    needPay = Column(Boolean)
    payingView = Column(Boolean)
    
    #hotComments = relationship('Comment', backref = 'post')
    comments = relationship('Comment', order_by = 'Comment.id')
    tags = relationship('Tag', secondary = tag_post_table, 
                        backref = backref('posts', order_by = id) 
                       )
    blogInfo = relationship('Blog', backref = backref('posts', order_by = id) )

    def __init__(self, **kwargs):
        #keys = list(kwargs.keys())
        #for kw in keys:
        #    if kw not in Post.__dict__:
        #        del kwargs[kw]
        #print(kwargs.keys())
        super().__init__(**kwargs)

    def __repr__(self):
        return "<Post(id='%d', title='%s')>" % (self.id, self.title)
    

class Comment(Base, SuperBase):
    __tablename__ = 'comments'
    id = Column(BIGINT(13), primary_key = True, autoincrement = False)
    postId = Column(BIGINT(13), ForeignKey('posts.id'))
    blogId = Column(INTEGER(11), ForeignKey('blogInfos.blogId')) 
    publisherUserId = Column(INTEGER(11), ForeignKey('blogInfos.blogId'))
    content = Column(LONGTEXT)
    publishTime = Column(BIGINT(13))
    replyToUserId = Column(INTEGER(11), ForeignKey('blogInfos.blogId')) 
    replyToResponseId = Column(BIGINT(13), ForeignKey('comments.id')) 
    replyToL2ResponseId = Column(BIGINT(13), ForeignKey('comments.id')) 
    ip = Column(String(20))

    blogInfo = relationship('Blog', foreign_keys = [blogId],\
                           backref = backref('comments', order_by = id))
    publisherMainBlogInfo = relationship('Blog', foreign_keys = [publisherUserId])
    replyBlogInfo = relationship('Blog', foreign_keys = [replyToUserId]) 
    replyToComment = relationship('Comment', 
                                  backref = backref('comments', order_by = id),
                                  foreign_keys = [replyToResponseId], 
                                  remote_side = [id]
                                 )  
    #replyToL2Comment = relationship('Comment', 
    #                               backref = 'l2Comments',
    #                               foreign_keys = [replyToL2ResponseId],
    #                               remote_side = [id]
    #                             )


    def __repr__(self):
        return "<Comment(userId='%d', content='%s')>" % (self.publisherUserId, self.content)
    

class Image(Base, SuperBase):
    __tablename__ = 'images'
    id = Column(BIGINT(20), primary_key = True, autoincrement = False)
    #small = Column(TEXT)
    middle = Column(TEXT)
    origin = Column(TEXT)
    raw = Column(String(255))
    path = Column(String(255), unique = True)
    postId = Column(BIGINT(13), ForeignKey('posts.id'))

    post = relationship('Post', backref = backref('images', order_by = id))

    def __repr__(self):
        return "<Image(id='%d')>" % (self.id)


class NovImage(Base, SuperBase):
    __tablename__ = 'novImages'
    id = Column(BIGINT(20), primary_key = True)
    url = Column(String(255))
    path = Column(String(255), unique = True)
    postId = Column(BIGINT(13), ForeignKey('posts.id'))

    post = relationship('Post', backref = backref('novImages', order_by = id))

    def __repr__(self):
        return "<NovImage(id='%d')>" % (self.id)








    








##METHODS##

     
def initDb():
    metadata.create_all(engine, checkfirst = True)

# CONFIG CONNECTION ##
## TODO: how to get back connections when all are lost ?

def resetSession():
    se.close()
    se = Session()

## a somewhat refreshing method for a session
def setSessionEngine(e):
    session.bind = e

def aNewSession():
    se = Session() 
    return se


## change to another db #####
def changeDb(new_db_name = 'private'):
    global db_name, db_url, db_prefix, engine, Session, se, gense
    
    name = db_prefix + new_db_name 
    url = db_url_pattern % name
    db_name = name
    db_url = url
    # dispost of old engine, create new engine
     
    engine.dispose()
    engine = create_engine(db_url)
    #print(db_name, db_url, engine)
    
    # close old session, configure sessionmaker, create new session
    se.close()
    Session.configure(bind = engine)
    se = Session()
    gense = Session()


def getse():
    global se
    return se 





## PROCESS DECLARATIVE OBJECTS ##
## create and attach to a existing session, ie.sync to db##
def getEntryFromJson(base_cls, json_object):
    keys = list(json_object.keys())
    base_dict = base_cls.__dict__
    
    for k in keys:
        k_cls = json_object[k] and json_object[k].__class__
        if k not in base_dict:
            del json_object[k]
        elif k_cls not in [str, int]:
            del json_object[k]

    return base_cls(**json_object)

'''
Add a **Json_Object into db if not exist, 
or get the existed entry object from db
syntax entry = syncOneJson(session, base_class, key_for_primary_id, **json_object)
'''
def syncOneJson(session, base_cls, id_key, **json_object):
    u_entry = getEntryFromJson(base_cls, json_object)
    entry = (session.query(base_cls)
         .filter(getattr(base_cls, id_key) == json_object[id_key])
         .first())
    
    if entry:
        for k in u_entry.cols():
            u_entry[k] and setattr(entry, k, u_entry[k])
    else:
        entry = u_entry
    try:
        session.add(entry)
        session.commit()
    except Exception as e:
        print(json_object)
        print('DB ERROR:',e)
        session.rollback()
    return entry

# Use this instead of the upper methos to sync a json object to db
# If it is certain that those records are not yet recorded
def syncOneUncheckedJson(session, base_cls, **json_object):
    entry = getEntryFromJson(base_cls, json_object)
    try:
        session.add(entry)
        session.commit()
    except Exception as e:
        print(json_object)
        print('DB ERROR:',e)
        session.rollback()
    return entry




def syncOneEntry(session, entry):
    try:
        session.add(entry)
        session.commit()
    except Exception as e:
        print('DB ERROR:',e)
        session.rollback()

##NOTE:Extremely unfriendly to memory!!
def syncJsonList(session, base_cls, id_key, json_list):
    entry_list = [syncOneJson(session, base_cls, id_key, **i) for i in json_list]
    return entry_list



# Use this instead of the upper methos to sync a json object to db
# If it is certain that those records are not yet recorded
def syncUncheckedJsonList(session, base_cls,  json_list):
    #entry_list = [syncOneUncheckedJson(session, base_cls, **i) for i in json_list]
    entry_list = [getEntryFromJson(base_cls, json_object) for json_object in json_list]
    try:
        session.add_all(entry_list)
        session.commit()
    except Exception as e:
        #print(json_list)
        print('DB ERROR:',e)
        session.rollback()
    return entry_list





def syncJsonListGen(session, base_cls, id_key, json_list):
    for j in json_list:
        yield syncOneJson(session, base_cls, id_key, **j) 

##MANIPULATE THE DB##
## DO SOME UPDATE##

##NOTE:Maybe unfriendly to memory!!
def checkUpdateList(session, base_cls, id_key, update_list):
    id_col = getattr(base_cls, id_key)
    #update_keys = [i[id_key] for i in update_list]
    #existed_keys =[i[0] for i in session.query(id_col).filter(id_col.in_(update_keys)).all()]
    #checked_list = [i for i in update_list if i[id_key] not in existed_keys]
    query = session.query(id_col)
    checked_list = [i for i in update_list if not  query.filter(id_col == i[id_key]).first()]
    return checked_list


def checkUpdateListGen(session, base_cls, id_key, update_list):
    id_col = getattr(base_cls, id_key)
    #update_keys = [i[id_key] for i in update_list]
    #existed_keys =[i[0] for i in session.query(id_col).filter(id_col.in_(update_keys)).all()]
    #checked_list = [i for i in update_list if i[id_key] not in existed_keys]
    query = session.query(id_col)
    for i in update_list:
        if not  query.filter(id_col == i[id_key]).first():
            yield i


def forceListUpdate(session, base_cls, update_list):
    for entry in update_list:
        try:
            session.add(entry)
            session.commit()
        except Exception as e:
            print(e)
            session.rollback()


def extendAssociatedList(session, root_entry, entry_list, list_key, id_key):
    #list_stored = getattr(root_entry, list_key)
    list_stored = getAssociatedList(root_entry, list_key)
    key_list_stored = [i[id_key] for i in list_stored]  
    list_update = [i for i in entry_list if i[id_key] not in key_list_stored]
    #print( '!!!!!!',list_update)
    if not list_update:
        return None
    base_cls = entry_list[0].__class__
    forceListUpdate(session, base_cls, list_update)
    try:
        getattr(root_entry, list_key).extend(list_update)
        session.commit()
    except Exception as e:
        print('DB ERROR:', e)
        session.rollback()


# If it is certain that those records are already synced but not yet associated
def extendUncheckedAssociatedList(session, root_entry, entry_list, list_key):
    try:
        getattr(root_entry, list_key).extend(entry_list)
        session.commit()
    except Exception as e:
        print('DB ERROR:', e)
        session.rollback()





## DELETE SOMETHING ##


def delEntryList(session, entry_list):
    for entry in entry_list:
        try:
            session.delete(entry)
            session.commit()
        except Exception as e:
            print('Unable to delete entry !!')
            print("DB ERROR:", e)
#

def delEntryListInOrder(session, entry_list, order_key, re = False):
    ordered_list = sorted(entry_list, \
                          key = lambda e:getattr(e, order_key),\
                          reverse = re)
    for entry in ordered_list:
        try:
            session.delete(entry)
            session.commit()
        except Exception as e:
            print('Unable to delete entry !!')
            print("DB ERROR:", e)




## QUERY WITH INTER TABLES RELATED ##
## LOADING RELATIONSHIPS ##

## NOTE:Extremely unfriendly to memory!!
#eg: pickle.dumps(blog) after query with lazy load mode: 1001bytes
###  pickle.dumps(blog) after calling blog.posts: 746.7KB
## NOTE:When getting attr with is foreigned-key linked alien object, 
## sometime a query needs to be emitted,
## which brings complexity to the process, eg. the connection may be lost after long appended
## thus should not be done by client modules, 
## all the getattr jobs should be redirected here
def getAssociatedList(root_entry, child_key):
    try:
        l = getattr(root_entry, child_key)
    except Exception as e:
        ## TODO : different kinds of exceptions should be defluenced
        print("DB Error!", e)
        return []
    return l


##NOTE: Friendly to memory, expensive of queries
#list_ref_key: which foreign key the list objects use the ref the root 
#limit: number of entries queried each time
def getAssociatedListGen(session, root_entry, list_cls, root_id_key, list_ref_key, limit):
    root_cls = root_entry.__class__
    query = session.query(list_cls)\
            .filter(getattr(list_cls, list_ref_key) == getattr(root_entry, root_id_key))
    for entry in query.yield_per(limit):
        yield entry
   

def getOrderedList(root_entry, child_key, sort_against, default):
    l = getAssociatedList(root_entry, child_key)
    l = sorted(l, \
               key = lambda e:getattr(e, sort_against) or default)
    return l 


def queryEntryList(session, base_cls, key_col_name, key_val):
    query = session.query(base_cls)\
           .filter(getattr(base_cls, key_col_name).like('%' + str(key_val) + '%'))
    return query.all()

def queryEntryListGen(session, base_cls, key_col, join_cls_list, key_val, limit = 10):
    query = session.query(base_cls)
    for j in join_cls_list:
        query = query.join(j)
    query = query.filter(key_col == key_val)
    for entry in query.yield_per(limit):
        yield entry

#def getOrderedEntyrListGen(session, base_cls,  , limit):
#    root_cls = root_entry.__class__
#    query = session.query(list_cls)\
#            .filter(getattr(list_cls, list_ref_key) == getattr(root_entry, root_id_key))
#    for entry in query.yield_per(limit):
#        yield entry
