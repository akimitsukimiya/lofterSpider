# coding: utf-8
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import csv
import config


#Create an engine
db_prefix = config.db_prefix
db_name = config.db_name
if config.db_type is 'sql':
    db_url_pattern = 'sqlite:///%s.db'  
db_url = db_url_pattern % (db_prefix + db_name)
engine = create_engine(db_url, echo = False)
Session = sessionmaker(bind = engine)
se = Session()


## METHODS ##
     
def initDb(metadata):
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



## QUERY & SYNC ##

def taylorJson(cols, json_object):
    j = {c:json_object[c] for c in \
        set(cols) & set(json_object.keys())}
    return j
    

def getOneEntry(session, base_cls, id_val):
    entry = session.query(base_cls)\
            .get(id_val)
    return entry


def syncOneTayloredJson(session, base_cls, json_object):
    entry = base_cls(**json_object)
    try:
        entry = session.merge(entry)
        session.commit()
    except Exception as e:
        print('xx ERROR on merging json: ', e) 
        session.rollback()
        return None
    return entry


def syncOneJson(session, base_cls, json_object):
    cols = [c.name for c in base_cls.__mapper__.columns]
    json_object = taylorJson(cols, json_object) 
    return syncOneTayloredJson(session, base_cls, json_object)


def syncJsonList(session, base_cls, json_list):
    cols = [c.name for c in base_cls.__mapper__.columns]
    json_list = [taylorJson(cols, j) for j in json_list]
    entry_list = [syncOneTayloredJson(session, base_cls, j)\
                  for j in json_list]
    return entry_list


# Use this instead of the upper method to sync 
# a json object list to db
# If it is certain that those records are not yet recorded
def syncFreshJsonList(session, base_cls,  json_list):
    cols = [c.name for c in base_cls.__mapper__.columns]
    json_list = [taylorJson(cols, j) for j in json_list]
    entry_list =[base_cls(j) for j in json_list]
    try:
        session.add_all(entry_list)
        session.commit()
    except Exception as e:
        #print(json_list)
        print('xx ERROR syncing fresh json list :',e)
        session.rollback()
    return entry_list


#NOTE: may consume too much memory!
# The entry should already be synced!
def extendM2MChildren(session, parent, new_children, children_ref):
    try:
        getattr(parent, children_ref).extend(new_children)
        session.commit()
    except Exception as e:
        print('xx ERROR on extending M2M relationship :', e)
        session.rollback()



## DELETE SOMETHING ##

def delEntries(session, entry_list):
    for entry in entry_list:
        try:
            session.delete(entry)
            session.commit()
        except Exception as e:
            print("xx ERROR on deleting entry :", e)


def delM2MOwnChildren(session, parent, children_ref, parent_ref):
    children = getattr(parent, children_ref)
    children = [c for c in children \
                if len(getattr(c, parent_ref)) is 1]  
    delEntries(session, children)


def delM2MParent(session, parent, children_ref, parent_ref):
    delM2MOwnChildren(session, parent, children_ref, parent_ref)
    delEntries(session, [parent])


## NOTE:Sometime unfriendly to memory!!
#eg: pickle.dumps(blog) after query with lazy load mode: 1001bytes
###  pickle.dumps(blog) after calling blog.posts: 746.7KB
## NOTE:When getting attr with is foreigned-key linked alien object, 
## sometime a query needs to be emitted,
## which brings complexity to the process, eg. the connection may be lost after long appended
## thus should not be done by client modules, 
## all the getattr jobs should be redirected here
def getM2MChildren(parent, children_ref):
    try:
        l = getattr(parent, children_ref)
    except Exception as e:
        ## TODO : different kinds of exceptions should be defluenced
        print("xx Error getting M2M children: ", e)
        return []
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


def countM2MChildren(session, children_cls, children_col, parent):
    query = session.query(children_cls)\
            .with_parent(parent, children_col)
    return query.count() 

