import os
import traceback
import time
import re
import sys
import html
import MySQLdb
from dotenv import load_dotenv
from datetime import date, datetime, timedelta
from collections import deque
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

# envファイル読み込み
load_dotenv()

'''
	eventページから各イベントのhtmlを成形し、ディクトに格納
'''
def get_event(dict1):
	#月のイベント表の取得
	for a in driver.find_elements_by_css_selector('.tb_basic tr'):
		#対象イベントのソース取得
		tr_html = a.get_attribute('innerHTML')
		#練習以外を省く
		if not re.search("cs_left cs_verticalalign_top eve2_evetype01", tr_html):
			continue

		#日付取得(mm/dd)
		match = re.search(r"(\d?\d)\/(\d?\d)", tr_html)

		if match:
			dict1[match.group(1).zfill(2)+'/'+match.group(2).zfill(2)] = tr_html
			#print(tr_html)

'''
	mail送信
'''
def send_mail(f, t, text):
	# 送信元（適当）
	f = f ? f : 'froommmmm@from.coooo.p';
	t = 


#DB接続
conn = MySQLdb.connect(db='aaaaa', user='aaaaa', passwd='aaaaa', charset='utf8mb4')
c = conn.cursor()

DATE_RANGE = 7

#今日の日付
today = date.today()
#対象となる最も早い日（最小日）
min_date = today - timedelta(DATE_RANGE)
print(min_date)
c.execute('select * from batch_log where act_date > %s', (min_date, ))

#最小日よりも後に実行された（既に対象のデータをカウント済み）
if c.rowcount > 0:
	print('eeeeeeeee')
	sys.exit()

diff_mon = 0
#先月分も取得が必要かチェック（実行日が1~DATE_RANGE日より前の場合）
if min_date.month != today.month:
	diff_mon = today.month - min_date.month


#driverの作成
options = ChromeOptions()
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
driver = webdriver.Chrome(options=options)
print('222')
#クロール対象
domain = 'https://www.c-sqr.net'
login_path = 'loginform.php'

#urljoinでもいいけど
target = '/'.join([domain, login_path])

#login画面へアクセス
driver.get(target)

#スクショ取得
#driver.save_screenshot('circle_result1.png')
print('333')
#ログインのための情報入力しEnter
input_id = driver.find_element_by_name('account')
input_pass = driver.find_element_by_name('password')
input_id.send_keys('aaaaa')
input_pass.send_keys('aaaaa')
input_pass.send_keys(Keys.RETURN)

#スクショ取得
#driver.save_screenshot('circle_result2.png')
print('444')
#次に遷移する画面（当月のイベントページ）
target = 'https://www.c-sqr.net/cs93515/Event_display.html'

driver.get(target)
#スクショ取得
#driver.save_screenshot('circle_result3.png')
#そのままやると要素が見つからないので、最大15秒待ってから取得する
WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CLASS_NAME, 'cs_arial')))
print('555')

dict1 = {}
get_event(dict1)
# 月をまたぐ分だけ前月へ戻りディクトへイベントを格納する
for i in range(diff_mon):
	next_a = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#tbcTitleL > span > a')))
	next_a.click()
	get_event(dict1)

	
urls = []
days = deque([])
for i in range(DATE_RANGE):
		target_day = today - timedelta(i)
		target_day = target_day.strftime("%m/%d")
		if target_day in dict1:
			urls.append(html.unescape(dict1[target_day]))
			days.append(target_day)

domain = 'https://www.c-sqr.net/cs93515/'


hit_mems = []
target_year = date.today().year

try:
	for url_html in urls:
		members = []
		#print(url_html)
		day = days.popleft()
		print(day)
		url = re.search(r"<a href=\"(.*?)\".*", url_html)
		print(url.group(1))
		driver.get(domain + url.group(1))
		#driver.save_screenshot('event_1.png')
		elem = driver.find_element_by_xpath('//*[@id="wrapper_dataobjects_event_tbl"]/div[2]/div[2]/div/p[2]/a')
		elem.click()

		for a in driver.find_elements_by_css_selector('.tb_basic tr'):
			tr_html = a.get_attribute('innerHTML')
			# 参加または当日参加
			join = re.search("○", tr_html)
			today_join = re.search("参加", tr_html)
			# 当日キャンセルの場合
			cancel = re.search("不参加", tr_html)

			# 参加または当日参加の場合
			if (join and not cancel) or today_join:
				member = {}
				member['name'] = re.search(r"<a .*>(.*)</a>", tr_html).group(1)
				#member['id'] = re.search(r"<a .*href=\"(.*?)\">", tr_html).group(1)
				member_id = re.search(r"<a .*person_id=(\d+)\".*", tr_html).group(1)
				print(member_id)
				#c.execute('insert into member_cnt(id, prac) values(%s, %s)', (member_id, member_id))
				member['id'] = member_id
				#member['prac'] = member['name']
				#member['prac'] = date(target_year, int(day[0:2]),int(day[3:5]))
				member['prac'] = datetime(target_year, int(day[0:2]),int(day[3:5])).strftime('%Y-%m-%d')
				# c.execute('select * from member_cnt where id = %s', (member_id, ))
				c.execute('select * from member_cnt where id = %s', (member_id, ))
				#row = c.fetchall()
				print(member['prac'])
				print(member['name'])
				if (c.rowcount + 1) % 3 == 2:
					# 次回無料対象者 ここでメール送る？
					hit_mems.append(member_id)
					print('this muryo men =>' + member_id)
				
				# member表作成処理
				c.execute('select * from members where id = %s', (member_id, ))
				if not c.rowcount:
					c.execute('insert into members(id, name) values(%(id)s, %(name)s)', {'id': member_id, 'name': member['name']})

				members.append(member)

		# ここでメール送る？
		# for ~
		print('try in')
		c.executemany('insert into member_cnt(id, prac) values(%(id)s, %(prac)s)', members)
		
	c.execute('insert into batch_log(act_date) values(%(today)s)', {'today': today})
	# c.executemany('insert into members(id, name) values(%(id)s, %(name)s)', members)
	#コミット
	conn.commit()

except MySQLdb.Error as e:
	print('catch in')
	traceback.print_exc()
	#print(e)
	conn.rollback()


finally:
	# DBを閉じる。
	conn.close()	
	# ブラウザーを終了する。
	driver.quit()  


