# coding: utf-8
from sqlalchemy import create_engine
from sqlalchemy import CheckConstraint, Column, ForeignKey, Integer, String, Table, Text, text
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import NullType
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, backref
import csv
import config


#Create an engine
db_prefix = config.db_prefix
db_name = config.db_name
db_url_pattern = 'sqlite:///%s.db'  
db_url = db_url_pattern % (db_prefix + db_name)
engine = create_engine(db_url, echo = False)
Session = sessionmaker(bind = engine)
se = Session()


Base = declarative_base()
metadata = Base.metadata


class SuperBase(object):

    def __getitem__(self, item):
         return getattr(self, item)
    
    def cols(self):
        cols = [k for k in self.__dict__ \
               if not k.startswith('_')]
        return cols

t_tag_blog_table = Table(
    'tag_blog_table', metadata,
    Column('blogId', ForeignKey('blogInfos.blogId'), primary_key=True, nullable=False),
    Column('tagName', ForeignKey('tags.tagName'), primary_key=True, nullable=False, index=True)
)

t_tag_post_table = Table(
    'tag_post_table', metadata,
    Column('postId', ForeignKey('posts.id'), primary_key=True, nullable=False),
    Column('tagName', ForeignKey('tags.tagName'), primary_key=True, nullable=False, index=True)
)


class Blog(Base,SuperBase):
    __tablename__ = 'blogInfos'

    blogId = Column(Integer, primary_key=True)
    blogName = Column(String(50), server_default=text("NULL"))
    blogNickName = Column(String(50), server_default=text("NULL"))
    bigAvaImg = Column(String(255), server_default=text("NULL"))
    homePageUrl = Column(String(255), server_default=text("NULL"))

    tags = relationship('Tag', secondary='tag_blog_table',\
                        backref = backref('blogs', order_by=blogId))




class Tag(Base,SuperBase):
    __tablename__ = 'tags'
    tagId = Column(Integer)
    tagName = Column(String(50), primary_key = True, index=True, server_default=text("NULL"))


class Post(Base,SuperBase):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True)
    blogId = Column(ForeignKey('blogInfos.blogId'), index=True, server_default=text("NULL"))
    publisherUserId = Column(Integer, server_default=text("NULL"))
    collectionId = Column(Integer, server_default=text("NULL"))
    title = Column(String(50), server_default=text("NULL"))
    publishTime = Column(Integer, server_default=text("NULL"))
    modifyTime = Column(Integer, server_default=text("NULL"))
    tag = Column(String(255), server_default=text("NULL"))
    #citeParentPostId = Column(Integer, server_default=text("NULL"))
    #citeParentBlogId = Column(Integer, server_default=text("NULL"))
    #citeRootPostId = Column(Integer, server_default=text("NULL"))
    #citeRootBlogId = Column(Integer, server_default=text("NULL"))
    type = Column(Integer, server_default=text("NULL"))
    #ip = Column(String(20), server_default=text("NULL"))
    digest = Column(Text)
    content = Column(Text)
    hot = Column(Integer, server_default=text("NULL"))
    permalink = Column(String(50), server_default=text("NULL"))

    tags = relationship('Tag', secondary='tag_post_table',\
                        backref = backref('posts', order_by = id) 
                       )
    blogInfo = relationship('Blog', backref = backref('posts', order_by = id) )


class Comment(Base,SuperBase):
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True)
    postId = Column(ForeignKey('posts.id'), index=True, server_default=text("NULL"))
    blogId = Column(ForeignKey('blogInfos.blogId'), index=True, server_default=text("NULL"))
    publisherUserId = Column(ForeignKey('blogInfos.blogId'), index=True, server_default=text("NULL"))
    content = Column(Text)
    publishTime = Column(Integer, server_default=text("NULL"))
    replyToUserId = Column(ForeignKey('blogInfos.blogId'), index=True, server_default=text("NULL"))
    replyToResponseId = Column(ForeignKey('comments.id'), index=True, server_default=text("NULL"))
    replyToL2ResponseId = Column(ForeignKey('comments.id'), index=True, server_default=text("NULL"))
    ip = Column(String(20), server_default=text("NULL"))



    blogInfo = relationship('Blog', foreign_keys = [blogId],\
                           backref = backref('comments', order_by = id))
    publisherMainBlogInfo = relationship('Blog', foreign_keys = [publisherUserId])
    replyBlogInfo = relationship('Blog', foreign_keys = [replyToUserId]) 
    replyToComment = relationship('Comment', 
                                  backref = backref('comments', order_by = id),
                                  foreign_keys = [replyToResponseId], 
                                  remote_side = [id]
                                 )  



class Image(Base,SuperBase):
    __tablename__ = 'images'

    id = Column(Integer, primary_key=True)
    small = Column(Text)
    middle = Column(Text)
    origin = Column(Text)
    raw = Column(String(255), server_default=text("NULL"))
    path = Column(String(255), unique=True, server_default=text("NULL"))
    postId = Column(ForeignKey('posts.id'), index=True, server_default=text("NULL"))

    post = relationship('Post', backref = backref('images', order_by = id))


class NovImage(Base,SuperBase):
    __tablename__ = 'novImages'

    id = Column(Integer, primary_key=True)
    url = Column(String(255), server_default=text("NULL"))
    path = Column(String(255), unique=True, server_default=text("NULL"))
    postId = Column(ForeignKey('posts.id'), index=True, server_default=text("NULL"))

    post = relationship('Post', backref = backref('novImages', order_by = id))



##METHODS##

     
def initDb():
    metadata.create_all(engine, checkfirst = True)

# CONFIG CONNECTION ##
## TODO: how to get back connections when all are lost ?

def resetSession():
    global se
    se.close()
    se = Session()

## a somewhat refreshing method for a session
def setSessionEngine(e):
    session.bind = e


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
    cols =[col.name for col in \
           base_cls.__mapper__.columns]

    for k in keys:
        k_cls = json_object[k] and json_object[k].__class__
        if k not in cols:
            del json_object[k]
        elif k_cls not in [str, int, bool]:
            del json_object[k]

    return base_cls(**json_object)

'''
Add a **Json_Object into db if not exist, 
or get the existed entry object from db
syntax entry = syncOneJson(session, base_class, key_for_primary_id, **json_object)
'''
def syncOneJson(session, base_cls, id_key, **json_object):
    u_entry = getEntryFromJson(base_cls, json_object)
    entry = session.query(base_cls)\
         .filter(getattr(base_cls, id_key) == json_object[id_key])\
         .first()
    cols =[col.name for col in \
           base_cls.__mapper__.columns]
    if entry:
        for k in cols:
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



# Use this instead of the upper method to sync 
# a json object list to db
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

#NOTE: may consume too much memory!
def extendAssociatedList(session, root_entry, entry_list, list_key, id_key):
    #list_stored = getattr(root_entry, list_key)
    #list_stored = getAssociatedList(root_entry, list_key)
    #key_list_stored = [i[id_key] for i in list_stored]  
    #list_update = [i for i in entry_list \
    #               if i[id_key] not in key_list_stored]
    #if not list_update:
    #    return None
    #base_cls = entry_list[0].__class__
    #forceListUpdate(session, base_cls, list_update)
    try:
        getattr(root_entry, list_key).extend(entry_list)
        session.commit()
    except Exception as e:
        print('DB ERROR:', e)
        session.rollback()


#def associateMany(session, asc_tbl, one, many):



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


def queryEntryList(session, base_cls, key_col_name, key_val, order_by = '', desc = False, limit = 0):
    query = session.query(base_cls)\
           .filter(getattr(base_cls, key_col_name).like('%' + str(key_val) + '%'))
    if order_by and desc:
        query = query.order_by(order_by.desc())
    elif order_by:
        query = query.order_by(order_by)
    if limit:
        query = query.limit(limit)

    return query.all()





# NOTE: should be very careful! This method will block all other queries!!
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
def exportCsv(session, base_cls, key, key_val, outfile):
    f = open(outfile, 'w') 
    out = csv.writer(f)
    cols = [col.name for col in base_cls.__mapper__.columns]
    out.writerow(cols)
    query = session.query(base_cls)\
            .filter(getattr(base_cls, key).like(key_val))

    for entry in query.all():
        out.writerow([getattr(entry, col) for col in cols])
    f.close()



def exportJoinedCsv(session, base_cls, join_cls_list, cols, key, key_val, outfile):
    f = open(outfile, 'w') 
    out = csv.writer(f)
    out.writerow([col.name for col in cols])
    print(cols)
    query = session.query(*cols)
    for j in join_cls_list:
        query = query.join(j)
    query = query.filter(getattr(base_cls, key).like('%' + str(key_val) + '%'))

    for entry in query.all():
        out.writerow([getattr(entry, col.name) for col in cols])
    f.close()


def updateCol(session, base_cls, key, key_val, col_key, col_val):
    query = session.query(base_cls)\
            .filter(getattr(base_cls, key) == key_val)\
            .update({col_key : col_val})


def updateCols(session, base_cls, col_key, cols_json):
    prikey = base_cls.__mapper__.primary_key[0]
    prikeyname = prikey.name
   # privals = [cols_json[prikeyname] for r in cols_json]
    for col in cols_json:
        updateCol(session, base_cls, prikeyname, col[prikeyname],\
                 col_key, col[col_key])


def countM2MChildren(session, child_cls, child_col, parent):
    query = session.query(child_cls)\
            .with_parent(parent, child_col)
    return query.count() 


def getFirstM2MChild(session, child_cls, child_col, parent,\
                    order_key = '', desc = False):
    query = session.query(child_cls)\
            .with_parent(parent, child_col)
    if order_key and desc:
        query = query.order_by(order_key.desc())
    elif order_key:
        query = query.order_by(order_key)

    return query.first() 
