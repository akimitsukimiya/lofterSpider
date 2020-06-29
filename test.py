import sqlbase as base
import linkdb as db
import time
import timeit
import random
tag1_raw = {'tagName' : 'tag1', \
            'noCol' : 'shouldnotappear',
            'noCol1' : 'shouldnotappear',
            'noCol2' : 'shouldnotappear',
           }
tag2_raw = {'tagName' : 'tag2',\
            'noCol' : 'shouldnotappear',
            'noCol1' : 'shouldnotappear',
           }
for  i in range(0, 50):
    tag2_raw['nocol' + str(i)] = i
blog1 = {
    'blogId' : 12345,
    'blogNickName' : 'blog1',
    'homePageUrl' : 'https://not.a.url.com',

    }

post1 = {
    'id' : 2234,
    'title': 'title 1',
    'publishTime' : 12345678,
    'hi' : 'hi',
    'content' : 'english '*10000,
    'hey' : 'hey',
    'type' : 1,
    'hot' : 50,
    'blogId' : 12345, 
    'permalink' : 'qewrwqqklgwqjltj'
}
post2 = {
    'id' : 3345678,
    'title': 'title 1',
    'publishTime' : 12345678,
    'hi' : 'hi',
    'content' : 'english '*10090,
    'hey' : 'hey',
    'type' : 2,
    'hot' : 50,
    'blogId' : 12345, 
    'permalink' : 'qewrwqqklgwqjltj'
}


#db.initDb(base.metadata)


# test Tag
#start = time.time()t
tags = db.syncJsonList(db.se, base.Tag, [tag1_raw, tag2_raw])
#print(time.time()  - start)
# 10000 - 27
# 100 - 1.4


# test Post
#start = time.time()
#db.syncJsonList(db.se, base.Post, [post1, post2] * 500)
#print(time.time()  - start)
# 10000 - 39.4
# 500 - 1.9
# 100 - 0.4
#blogs = db.syncJsonList(db.se, base.Blog, [blog1])
# test Post
#post_list = [post1, post2]
#for i in range(0, 100):
#    post1['id'] +=  i 
#    post_list.append(dict(post1))
#posts = db.syncJsonList(db.se, base.Post, post_list)
# print(time.time()  - start)
# 100000 - 360
# 10000 - 37
# 500 - 1.8
# 100 - 0.2
#start = time.time()
#db.extendM2MChildren(db.se, tags[0], 'posts', posts)
#test Post
#start = time.time()
#db.se.delete(tags[0])
#db.se.commit()
#db.syncJsonList(db.se, base.Post, [post1, post2] * 10000)
#print(time.time()  - start)
# 10000 - 40
# 500 - 1.9
# 100 - 0.4

#a = list(range(1, 100000))
#b = list(range(50000, 150000))
#random.shuffle(a) 
#random.shuffle(b)

#def test():
#    c = set(a) & set(b)

#perf = timeit.timeit('test()',\
#                     setup = 'from __main__ import test', \
#                     number = 100)
#print(perf)
#print(blogs)


#db.se.delete(blogs[0])
#db.se.commit()

def func_a(a,b,c):
    print(a,b,c)

func_a('b','c',a = 'a')
    

