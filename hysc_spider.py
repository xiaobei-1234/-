import requests, os, lxml, time, csv, random
from bs4 import BeautifulSoup


'''
定义登录方法
需要两个参数：login_url, headers
data字典存储用户名及密码信息
'''
def login(login_url, headers):
    data = {
        'name': '1161764559@qq.com',
        'password': '',    # 输入密码
        'remember': 'false',
    }

    try:
        r = s.post(login_url, headers=headers, data=data)
        r.raise_for_status()
        print('登录成功！')
        return True
    except:
        print('登录失败！')


'''
定义获取网页的方法
返回res.text,即网页HTML
'''
def get_one_page(url, headers):
    res = s.get(url, headers=headers)
    if res.status_code == 200:
        return res.text
    # return None


'''
定义网页解析内容
使用BeautifulSoup的CSS选择器select选取所有评论
返回comments列表
'''
def parse_one_page(html):
    soup = BeautifulSoup(html, 'lxml')
    user_names = soup.select('span[class="comment-info"] a')
    comment_times = soup.select('span[class="comment-time "]')
    comments = soup.select('span[class="short"]')
    
    for user_name, comment_time, comment in zip(user_names, comment_times, comments):
        infos = map(list, zip(user_name, comment_time, comment))
        yield infos


'''
定义保存到文件的方法
使用追加方式，由于有中文，增加参数encoding='utf-8'
'''
def save_file(info, COMMENTS_FILE_PATH):
    with open(COMMENTS_FILE_PATH, 'a+', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(info)


'''
定义主方法
调用各个函数
设置头部信息和登录URL
'''
def main():
    login_url = 'https://accounts.douban.com/j/mobile/login/basic'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'Referer': 'https://accounts.douban.com/passport/login_popup?login_source=anony',
    }

    # 如果login()为True，执行程序
    if login(login_url, headers=headers):

        '''
        判断文件名是否存在，如果存在，移除
        '''
        COMMENTS_FILE_PATH = 'hysc_comments.csv'
        if os.path.exists(COMMENTS_FILE_PATH):
            os.remove(COMMENTS_FILE_PATH)

        '''
        设置条件循环
        如果comments为空列表，说明已经是最后一页，停止循环
        '''
        start_num = 0
        while True:
            url = 'https://movie.douban.com/subject/1905462/comments?start=' + str(start_num * 20) + '&limit=20&sort=new_score&status=P'

            # 调用get_one_page()
            html = get_one_page(url, headers)

            soup = BeautifulSoup(html, 'lxml')
            comment_items = soup.select('div[class="comment-item"]')

            '''
            增加条件判断
            判断len(comment_items)
            为1，则终止循环
            '''
            if len(comment_items) == 1:
                print('已经是最后一页了！')
                break
            else:
                # 调用parse_one_page()
                # parse_one_page(html)
                infos = parse_one_page(html)
                # print(infos)
                for info in infos:
                    for info in info:
                        info[1] = info[1].strip()
                        info[2] = info[2].replace('\n', '').replace('\r', '')
                        print(info)
                        save_file(info, COMMENTS_FILE_PATH)
                print('第' + str(start_num + 1) + '页已保存...')
                
            start_num += 1
            # 随机翻页延时
            time.sleep(random.randint(1, 5))


if __name__ == '__main__':
    # 生成Session对象，用于保存Cookies
    s = requests.Session()
    main()
