import sys, os, sqlite3, re
import bs4, requests

# SET WEB PAGE
webPage="https://na.finalfantasyxiv.com/lodestone/playguide/db/recipe/?category2=%s&page=%s"
jobs = list(range(5,8))
#CONNECT AND PREPARE DATABASE
conn = sqlite3.connect("recipes")
curr = conn.cursor()
curr.execute("PRAGMA foriegn_keys = ON") #ENABLE FORIEN KEYS


#CONTINUE RECIPE IDS
curr.execute("SELECT MAX(id) FROM recipes")
maxID = curr.fetchall()[0]
k = maxID[0]+1
for j in jobs:
	pageNo = 1
	end_of_recipes = False
	print("START OF NEW JOB".center(20,'_'))
	i=1 #OVERALL
	while not end_of_recipes:
		# get web page
		page = requests.get(webPage %(j,pageNo))
		# pass to beautiful soup
		theSoup = bs4.BeautifulSoup(page.text, 'html.parser')
		#get item blocks in html page
		select_string="td[class='db-table__body--light latest_patch__major__item']"
		s_items = theSoup.select(select_string)
		if len(s_items)>0:
			#go through all items
			for x in s_items:
				#have to go up a level for levels
				parent = x.parent.find_all('td')
				recipe_level = None
				item_level = None
				#GET RECIPE LEVEL
				if parent[1].string is not None:
					if bool(re.search('[0-9]+', parent[1].string)):
						recipe_level = int(parent[1].string)
				if parent[2].string is not None:
					if bool(re.search('[0-9]+', parent[2].string)):
						item_level = int(parent[2].string)
				if recipe_level == None:
					recipe_level = 0
				if item_level == None:
					item_level = 0
				img_link = x.img['src']
				info = x.select("div[class='db-table__link_txt']")
				job = info[0].find_all('a')[0].string
				recipe = info[0].find_all('a')[1].string
				#GET IMAGE INFORMATION AND SAVE PATH
				imageGet = requests.get(img_link)
				#make a directory for thumbnails
				savePath = "./pics/%s" %(job)
				savePath+="/%s_%s.png" %(job,recipe)
				#PRINT OUTPUT
				out_format = (k,job,recipe,item_level,recipe_level,img_link)
				out_string = "Recipe %s\nJob:\t%s\nName:\t%s\nItem Lvl:\t%s\nRec. Lvl:\t%s\nImg Path:\t%s\n" %out_format
				#STORE DATA TO TABLE
				insertString = "INSERT INTO recipes (id, name, job, r_level, i_level, thumb_path) VALUES (%s,\"%s\",\"%s\",%s,%s,\"%s\")"
				insertString = insertString % (k,recipe,job,recipe_level,item_level,savePath)
				#DEBUG SECTION
				if i==1:
					print(out_string)
					print(insertString)
				curr.execute(insertString)

				#GET RECIPE MATERIALS AND CRYSTALS
				#get recipe page link
				recipeLink = x.select('a[class]')[0]['href']
				recipeURL = "https://na.finalfantasyxiv.com"+recipeLink	#needs to be appended with main site
				recipePage = requests.get(recipeURL)
				rSoup = bs4.BeautifulSoup(recipePage.text, 'html.parser')
				#isolate table with needed info
				rTable = rSoup.select("div[class='db-view__data__inner']")
				materials = rTable[0]
				material_list = materials.find_all('ul')
				#cycle through and store materials
				for y in material_list:
					mQuantity = y.span.string
					mName = y.select("a[class]")[0].string
					#store in database
					mInsertString = "INSERT INTO materials (name, quantity, recipe_id) VALUES (\"%s\",%s,%s)"
					mInsertString = mInsertString % (mName,mQuantity,k)
					curr.execute(mInsertString)
					#DEBUG LINE
					if i==1:
						print(mInsertString)
				k+=1
				i+=1
		else:
			end_of_recipes=True
			conn.commit()
		pageNo+=1
conn.close()
print("ALL DONE!")
