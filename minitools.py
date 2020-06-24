import inspect
from datetime import datetime
import re
import os
import shutil




def printJson(object_json, h = 0):
    s = strJson(object_json, 0)
    print(s)

                
def strJson(object_json, h = 0):
    s = ''
    try:
        ks = list(object_json.keys())
    except Exception as e:
        if object_json.__class__ is list:
            l = [strJson(i, h+1) for i in object_json]
            s += '[' + \
                    (',\n' + '\t'*h).join(l) + \
                    ']'
            return s
        else:
            return str(object_json)
    for k in ks:
        #if k == '__builtins__':
        #    break
        s += '\n'
        s += '\t'*h
        s += k + ' : ' + strJson( object_json[k], h+1 )
    return s

                
def printDict(a_dict):
    ks = a_dict.keys()
    s = ''
    for k in ks:
        s += '\n'
        s += k + ' : ' + str(a_dict[k])
    print(s)
    return None

                
def printFunc(func):
    try:
        print(inspect.getsource(func))
    except Exception as e:
        print("ERROR: ", e)
    return None

                
def dir2Dict(obj):
    rst = {key:getattr(obj,key) for key in dir(obj) }
    return rst

                
def printKeyClass(a_dict):
    s = [key + ':' + str(a_dict[key].__class__)  for key in a_dict]
    print('\n'.join(s))

                
def getTimeFromIntStamp(ts):
    ts = ts/1000
    dt = datetime.fromtimestamp(ts)
    dt = dt.strftime('%Y-%m-%d')
    return dt
                
                
def getExtension(string):
    s = re.sub(r'.*\.([^\.]*)', r'\1', string)
    return s


def humanSize(num):
    """
    this function will convert bytes to MB.... GB... etc
    """
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0



#This iterable is in itself an iterator
class MyIter:


    def __init__(self,limit):
        self.limit = limit

    def __call__(self, limit):
        self.limit = limit
        return self

    #Reset the state of Iterator
    def __iter__(self):
        self.now = 0
        return self

    #This is what called lazy --
    #the values are not generated until they are requested
    #Return the next object each call
    def __next__(self):
        now = self.now 
        if now >= self.limit:
            raise StopIteration 
        self.now += 1
        return now



def printColors():
    import sys
    for i in range(0, 256):
        sys.stdout.write(u'\u001b[38;5;%dm%3d\t' % (i, i))
    print(u'\u001b[0m')


def fix(text):
    return text.encode('utf-8','ignore').decode('unicode-escape','ignore').encode('utf-8','ignore').decode('utf-8','ignore')


def fixFile(fname):
    f = open(fname, 'r')
    text = f.read()
    f.close()
    text =  text.encode('utf-8','ignore').decode('unicode-escape','ignore').encode('utf-8','ignore').decode('utf-8','ignore')
    f = open(fname, 'w')
    f.write(text)
    f.close()


def stripiImageUrl(url):
    url = re.sub(r'(https?://[^\?]*)\?[^/]*',r'\1',url)
    return url


def fixFname(fname):
    resp = r'^[\.]+|[\.]+$|[\\\/\:\|\<\>\*\?\"]+|[\t\n]+'
    fname = re.sub(resp, r'_', fname)
    return fname


def cls():
    '''
    clear screen
    '''
    name = os.name
    if name is 'nt': 
        ##this is a windows system
        _ = os.system('cls')
    if name is 'posix':
        ##linux or mac
        _ = os.system('clear')


def fixWinPrint():
    import io
    import sys
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer,encoding='utf-8')


def findChinese(string):
    zn_p = r'[\u4e00-\u9fff]|[\u3000-\u303f]|[\uff00-\uffef]'
    return re.findall(zn_p,string)


def graphicLen(string):
    li = list(string)
    zn_len = len(findChinese(string))
    graphic_len = len(li) + zn_len  #Every Chinese char takes two space
    return graphic_len

def stringFill(string, place_holder = ' ', center = False):
    # Get the width of current console
    cols = shutil.get_terminal_size((45,45))[0]
    glen = graphicLen(string)
    lnum = round(glen//cols) + 1
    flen = lnum*cols - glen
    if center:
        lflen = round(flen//2) 
        string = place_holder * lflen + string
        string += place_holder * (flen - lflen)
    else:
        string += place_holder *  flen  
    return string

    



