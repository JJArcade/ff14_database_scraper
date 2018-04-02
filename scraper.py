import sys, os
import bs4, requests

# get web page
page = requests.get("https://na.finalfantasyxiv.com/lodestone/playguide/db/recipe/?category2=0&category3=0")
# pass to beautiful soup
theSoup = bs4.BeautifulSoup(page.text, 'html.parser')
#get item blocks in html page
select_string="td[class='db-table__body--light latest_patch__major__item']"
s_items = theSoup.select(select_string)

#go through all items
i = 1
for x in s_items:
	img_link = x.img['src']
	info = x.select("div[class='db-table__link_txt']")
	job = info[0].find_all('a')[0].string
	recipe = info[0].find_all('a')[1].string
	out_string = "Recipe %s\nJob:\t%s\nName:\t%s" %(i,job,recipe)
	print(out_string)
	i+=1
