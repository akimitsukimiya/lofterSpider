import config
import spider as spiders
import myproviders 


def main():
    myproviders.Tools.cls()
    print('>> LOF SPIDER START SPIDERING !!>>>>>>>>>\n',
        '>> 版本 %s\n' % config.app_version,
        '>> 当前功能')
    options = ('> 1. 将指定tag归档备份到本地数据库',
         '> 2. 更新指定tag的本地数据库',
         '> 3. 将数据库中的图片型博文筛选后导出',
         '> 4. 将数据库中的文档型博文筛选后导出')
    options = dict(zip(('1','2','3','4'), options))
    print('\n'.join(options.values()))
    print('>> 备注: 请在config.py中修改配置信息.')
    
    while True:
        tagName, option = userInput(options)
        spider = spiders.LazyTagSpider(tagName)

        if option is '1':
            spider.baseTagArchive(rebase_level = spiders.DO)
            if config.do_deepbase:
                spider.deepBase1()
        elif option is '2':
            spider.baseTagArchive(rebase_level = spiders.DO_UPDATE)
        elif option is '3':
            spider.packPostsPlain(ptype = spiders.IMAGE)
        else:
            spider.packPostsPlain(ptype = spiders.TEXT)

        go_on = input('\n>> 是否继续使用? y-是 (others)-否 ')
        if go_on in ('y','Y'):
            myproviders.Tools.cls()
            continue
        else:
            print('>> 谢谢使用，再见！')
            break



def userInput(options):
    while True:
        tagName = input('\n>> 请指定tag(仅一个): ' )
        if not tagName:
            print('>> tag不能为空，请重试！')
            continue
        print('>> 已指定tag: ', tagName)
        certain = input('>> 是否确定？y-是 (others)-否: ')
        if certain in ('y','Y'):
            print('>> 设置tag成功！当前工作tag: ', tagName)
            break
        else:
            print('>> 重新指定tag.')
            tagName = ''

    while True:
        print('\n') 
        print('\n'.join(options.values()))
        option = input('>> 请选择功能: ' )
        if option not in options:
            print('>> 输入无效选择，请重试！')
            continue

        print('>> 已选择功能: \n',options[option] )
        certain = input('>> 是否确定？y-是 (others)-否: ')
        if certain in ('y','Y'):
            break
        print('>> 重新选择...')

    print('\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
    print('>> 当前工作tag: ', tagName)
    print('>> 已选功能：\n', options[option])
    print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
    certain = input('>> 按Enter开始，按其他键重新设置.')
    if certain == '':
        return tagName, option
    else: 
        print('\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
        print('>> 重新设置.')
        return userInput(options)


            



main()




   

   






    






























