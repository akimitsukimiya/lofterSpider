import config
import spider as spiders
import myproviders 





def main():
    myproviders.Tools.cls()
    print(myproviders.Tools.string_fill(u' LOF SPIDER START SPIDERING ', u'>', True))
    print(myproviders.Tools.string_fill(u' 完全备份老福特Tag档案·筛选屏蔽·排版导出', u'>', True))
    print(myproviders.Tools.string_fill(u' 版本 %s ' % config.app_version, u'>', True))
    options = (u'1. 将指定tag归档备份到本地数据库',
         u'2. 更新指定tag的本地数据库',
         u'3. 将数据库中的图片型博文筛选后导出',
         u'4. 将数据库中的文档型博文筛选后导出',
         u'5. 将数据库中的文档型博文筛选后制作成epub电子书')
    options = dict(zip(('1','2','3','4','5'), options))
    #print('\n'.join(options.values()))
    print(myproviders.Tools.string_fill(u' 备注: 请在config.py中修改配置信息. ', r'>', True))
    print(myproviders.Tools.string_fill(u'', r'>'))
    
    while True:
        tagName, option = userInput(options)

        if option is '1':
            spider = spiders.LazyTagSpider(tagName)
            spider.baseTagArchive(rebase_level = spiders.DO)
            if config.do_deepbase:
                spider.deepBase1()
        elif option is '2':
            spider = spiders.LazyTagSpider(tagName)
            spider.baseTagArchive(rebase_level = spiders.DO_UPDATE)
        elif option is '3':
            spider = spiders.DBSpider(tagName)
            spider.packPostsPlain(ptype = spiders.IMAGE)
        elif option is '4':
            spider = spiders.DBSpider(tagName)
            spider.packPostsPlain(ptype = spiders.TEXT)
        elif option is '5':
            spider = spiders.DBSpider(tagName)
            spider.makeAozora()
            spider.aozoraEpub3(delRaw = \
                               config.del_raw_after_converting_aozora)

        go_on = input(u'\n>> 是否继续使用? y-是 (others)-否 ')
        if go_on in ('y','Y'):
            myproviders.Tools.cls()
            continue
        else:
            print(u'>> 谢谢使用，再见！')
            break



def userInput(options):
    while True:
        tagName = input(u'\n>> 请指定tag(仅一个): \n>> ' )
        if not tagName:
            print(u'>> tag不能为空，请重试！')
            continue
        print(u'>> 已指定tag: ', tagName)
        certain = input(u'>> 是否确定？y-是 (others)-否: \n>> ')
        if certain in (u'y','Y'):
            print(u'>> 设置tag成功！当前工作tag: ', tagName)
            break
        else:
            print(u'>> 重新指定tag.')
            tagName = ''

    while True:
        print('\n') 
        print('\n'.join(options.values()))
        option = input(u'>> 请选择功能: \n>> ' )
        if option not in options:
            print(u'>> 输入无效选择，请重试！')
            continue

        print(u'>> 已选择功能: \n',options[option] )
        certain = input(u'>> 是否确定？y-是 (others)-否: \n>> ')
        if certain in ('y','Y'):
            break
        print(u'>> 重新选择...')

    print(u'\n')
    print(myproviders.Tools.string_fill(u'', r'>'))
    print(u'>> 当前工作tag: ', tagName)
    print(u'>> 已选功能：\n', options[option])
    print(myproviders.Tools.string_fill(u'', r'>'))
    certain = input(u'>> 按Enter开始，按其他键重新设置.')
    if certain == '':
        return tagName, option
    else: 
        print(myproviders.Tools.string_fill(u'', r'>'))
        print(myproviders.Tools.string_fill(u'>> 重新设置.', r'>'))
        return userInput(options)


if __name__ == '__main__':
    main()




   

   






    






























