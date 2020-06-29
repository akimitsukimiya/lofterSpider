from sqlalchemy.orm import relationship,backref
from sqlalchemy import CheckConstraint, Column, ForeignKey, Integer, String, Table, Text, Boolean, text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class SuperBase(object):

    def __getitem__(self, item):
         return getattr(self, item)
    

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


class Tag(Base,SuperBase):
    __tablename__ = 'tags'
    tagId = Column(Integer)
    tagName = Column(String(50), primary_key = True, index=True)
    isThoroughBased = Column(Boolean)
    latestPostTime = Column(Integer, server_default=text("NULL"))
    



class Blog(Base,SuperBase):
    __tablename__ = 'blogInfos'

    blogId = Column(Integer, primary_key=True)
    blogName = Column(String(50), server_default=text("NULL"))
    blogNickName = Column(String(50), server_default=text("NULL"))
    bigAvaImg = Column(String(255), server_default=text("NULL"))
    homePageUrl = Column(String(255), server_default=text("NULL"))
    latestPostTime = Column(Integer, server_default=text("NULL"))
    

    tags = relationship('Tag', secondary='tag_blog_table',\
                        backref = backref('blogs', order_by=blogId))



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
    type = Column(Integer, server_default=text("NULL"))
    digest = Column(Text)
    content = Column(Text)
    hot = Column(Integer, server_default=text("NULL"))
    permalink = Column(String(50), server_default=text("NULL"))

    tags = relationship('Tag', secondary='tag_post_table',\
                        backref = backref('posts', order_by = id) 
                       )
    blogInfo = relationship('Blog', backref = backref('posts', order_by = id, cascade = 'all, delete, delete-orphan') )


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

    post = relationship('Post', backref = backref('images', order_by = id, cascade = 'all, delete, delete-orphan'))


class NovImage(Base,SuperBase):
    __tablename__ = 'novImages'

    id = Column(Integer, primary_key=True)
    url = Column(String(255), server_default=text("NULL"))
    path = Column(String(255), unique=True, server_default=text("NULL"))
    postId = Column(ForeignKey('posts.id'), index=True, server_default=text("NULL"))

    post = relationship('Post', backref = backref('novImages', order_by = id))


