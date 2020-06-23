all_modules = ['websearcher', 'minitools', 'myinjector', 'myproviders']

dependency = ['requests','SQLAlchemy','mysqlclient','bs4','html5lib']


####### APP INFO ####################
app_name = 'Lof小蜘蛛'
author = 'AkimiC.'
app_version = 'v1.0.0'


####### BASING STRATEGY #############
do_deepbase = False

####### DATA STORAGE ################

# The root dir where all exported data should be stored
data_export_dir = 'archive'

# The name of folder within which text posts should be stored 
nov_dir_name = '文章'

# The name for folder within which image posts should be stored
image_dir_name = '图片'

# When packing images, don't make author folder for auhors who post less than:
image_blog_limit = 10
# rather, put their images in one large folder named
other_img_dir = '其他'

# Do you want to delete the raw txt files with aozora chuki
# after converting them to epub ?
del_raw_after_converting_aozora = False

######## SEARCHER BEHAVIOR ##########

# How many records the searcher prefer to fetch on every query
# when searching tag
tag_search_limit = 500
# when searching blog
blog_search_limit = 200
comment_search_limit = 50

######## DB INFO ####################

# What db type do you use (now sql only!!)
db_type = 'sql'

# How do you want to call your db
db_name = 'friend'

# Your db name can be appended after a prefix
db_prefix = 'lofter_'


####### USER PREFERENCE ############

# The hated authors you always want to block
blackusers = [] # eg: ['blogNickName1', 'blogNickName2']

# The hated tags you always want to block
blacktags = []

# The hated words you don't want to see in anyone's post title
blackwords = []

#blacktags = ['黄喻','叶喻','叶黄','all黄','all喻','喻all']
#blackwords = ['出本', '占tag致歉','求文']
#blackusers = ['一路春白','芒草遇风','聆雪']

# If you run this thing without any runtime configuration
# how do you want to set the minimum hot you want to export your posts
minhot = 0
