import sqlite3, re, json, requests, bs4
import plotly.offline as ply
import plotly.graph_objs as go

class recipe_calculator:
    def __init__(self, DATABASE):
        try:
            self.conn = sqlite3.connect(DATABASE)
        except sqlite3.OperationalError:
            print("Database could not be connected to.")
            return None
        self.curs = self.conn.cursor()
        print("Database connected.")
        self.curr_char = None
        self.select_character()

    ##SELECT A CHARACTER
    def select_character(self):
        while self.curr_char == None:
            # get characters from database
            self.curs.execute("SELECT * from char_data")
            headers = list(map(lambda x: x[0], self.curs.description))
            characters = self.curs.fetchall()

            if len(characters) == 0:
                print("No characters in database.")
                break

            # go through character data and print to console
            for a in range(0, len(characters)):
                out_str = "%s:\n\t%s:\t%s\n\t%s:\t%s\n\t%s:\t%s"
                inserts = [a+1,]
                for b in range(0,len(headers)):
                    inserts.append(headers[b])
                    inserts.append(characters[a][b])
                print(out_str % tuple(inserts))

            # start select character loop
            char_select = None
            while char_select == None:
                char_select = input("Select a character:\n")
                try:
                    char_select = int(char_select)-1
                except:
                    print("Please enter only a number.")
                    char_select = None

            # store select character
            self.curr_char = {}
            for a in range(0,len(headers)):
                self.curr_char[headers[a]] = characters[char_select][a]

    ##UPDATE CHARACTER
    def scrape_data(self):
        # CONSTANTS
        data_tags = ["character__job__level",\
        "character__job__name js__tooltip", "character__job__exp"]

        # GET CHARACTER PAGE AND SOUP
        page = requests.get(self.curr_char["url_link"])
        soup = bs4.BeautifulSoup(page.text, "html.parser")

        # GET JOBS DIV FROM SOUP
        jobs_div = soup.select("div[class=\"character__job__role\"]")[4]
        for a in jobs_div.ul:
            # SQL UPDATE STRING
            update_str = "UPDATE job_data SET job_level=?, job_exp=?,\
            exp_to_level=? WHERE char_id = ? AND job_name =?"

            # PARSE DATA FOR JOB DATA
            inserts = []
            for b in [0,2,1]:
                div_tag = a.select("div[class=\"%s\"]" % data_tags[b])[0].get_text()
                # GET JOB LEVEL
                if b == 0:
                    inserts.append(int(div_tag))
                # GET EXP DATA
                elif b == 2:
                    exps = div_tag.split(" / ")
                    exps = list(map(lambda x: x.replace(',',''), exps))
                    inserts.append(int(exps[0]))
                    inserts.append(int(exps[1]))
                # GET JOB NAME
                elif b == 1:
                    inserts.append(self.curr_char["char_id"])
                    inserts.append(div_tag)
            # UPDATE DATABASE WITH GATHERED DATA
            try:
                self.curs.execute(update_str, tuple(inserts))
                print("UPDATE SUCESSFUL")
                self.conn.commit()
            except:
                print("ERROR UPDATING")

    ##LOG EXP GAIN
    def log_exp(self):
        #GET RECIPE
        recipe_found = False
        recipe = {}

        # RECIPE LOOP
        while not recipe_found:
            # PROMPT USER FOR RECIPE INPUT
            get_recipe = input("Enter the name of the recipe crafted:\t")

            # GET RECIPE FROM DATABASE
            query = "SELECT id, name, job FROM recipes WHERE name like ?"
            self.curs.execute(query, (get_recipe,))
            recipe_headers = list(map(lambda x: x[0], self.curs.description))
            recipe_results = self.curs.fetchall()
            print(recipe_results)

            # CHECK IF QUERY WAS SUCCESFUL
            if len(recipe_results)==0:
                print("no recipes found.")
            else:
                # IF MORE THAN ONE RECIPE, PROMPT FOR USER SELECTION
                if len(recipe_results)>1:
                    while not recipe_found:
                        for a in range(0,len(recipe_results)):
                            out_str = "%d:\t%s\t%s" % (a, recipe_results[a][1]\
                            , recipe_results[a][2])
                            print(out_str)
                        selection = input("Enter the correct recipe: ")
                        
                        # CHECK IF INTERGER INPUT
                        try:
                            selection = int(selection)
                        except:
                            print("Please enter a numeric value.")
                            continue
                        
                        # CHECK IF VALID SELECTION
                        if selection not in range(0,len(recipe_results)):
                            print("Please enter a numeric values in the range shown.")
                        else:
                            #STORE SELECTION TO RECIPE VAR
                            for a in range(0,len(recipe_results[selection])):
                                recipe[recipe_headers[a]] = recipe_results[selection][a]
                            recipe_found = True
                # ONLY ONE MATCH FOUND
                else:
                    for a in range(0,len(recipe_results[0])):
                        recipe[recipe_headers[a]] = recipe_results[0][a]
                    recipe_found = True
        print(recipe)

        #GET QUANTITY
        quantity_found = False
        quantity_crafted = 0
        while not quantity_found:
            get_quantity = input("Enter the quantity crafted: ")
            try:
                get_quantity = int(get_quantity)
            except:
                print("Please enter a numeric value.")
            if get_quantity>0:
                quantity_crafted = get_quantity
                quantity_found = True

        #GET EXPERIENCE
        new_exp = 0
        data_tags = ["character__job__name js__tooltip", "character__job__exp"]
        page = requests.get(self.curr_char["url_link"])
        soup = bs4.BeautifulSoup(page.text, "html.parser")
        div_tag = soup.select("div[class=\"character__job__role\"]")[4]
        for a in div_tag.ul:
            job = a.select("div[class=\"{}\"]".format(data_tags[0]))[0].get_text()
            if job == recipe["job"]:
                exp = a.select("div[class=\"{}\"]".format(data_tags[1]))[0].get_text()
                exp = exp.split(" / ")
                new_exp = int(exp[0])
        use_auto = False
        curr_exp = 0
        self.curs.execute("SELECT job_exp FROM job_data WHERE char_id = ?\
            AND job_name = ?", (self.curr_char["char_id"], recipe["job"]))
        curr_exp = self.curs.fetchall()[0][0]
        print("{}:\t{}".format(new_exp, curr_exp))
        if curr_exp == new_exp:
            print("Website shows same exp as database.")
            print("Enter experience manually.")
            got_entry = False
            while not got_entry:
                new_exp = input("Enter total exp gained: ")
                try:
                    new_exp = int(new_exp)
                    got_entry = True
                except:
                    print("Please enter a numeric value.")
            for a in range(0, quantity_crafted):
                per_exp = new_exp/quantity_crafted
                query = "INSERT INTO exp_records (recipe_id, exp_gained, char_level,\
                    char_id) VALUES(?,?,?,?)"
                self.curs.execute("SELECT job_level FROM job_data WHERE char_id=?\
                    AND job_name=?", (self.curr_char["char_id"],recipe["job"]))
                job_level = self.curs.fetchall()[0][0]
                inserts = [recipe["id"],per_exp,job_level,self.curr_char["char_id"]]
                self.curs.execute(query, tuple(inserts))
                self.conn.commit()
        else:
            answered = False
            while not answered:
                answer = input("Use the difference scraped from the website.y\\n?\n")
                if bool(re.search("y", answer, re.IGNORECASE)):
                    use_auto = True
                    answered = True
                else:
                    answered = True
            if use_auto:
                for a in range(0, quantity_crafted):
                    new_exp-=curr_exp
                    per_exp = new_exp/quantity_crafted
                    query = "INSERT INTO exp_records (recipe_id, exp_gained, char_level\
                        char_id) VALUES(?,?,?,?)"
                    self.curs.execute("SELECT job_level FROM job_data WHERE char_id=?\
                        AND job_name=?", (self.curr_char["char_id"],recipe["job"]))
                    job_level = self.curs.fetchall()[0][0]
                    inserts = [recipe["id"],per_exp,job_level,self.curr_char["char_id"]]
                    self.curs.execute(query, tuple(inserts))
                    self.conn.commit()
            else:
                print("Enter experience manually.")
                got_entry = False
                while not got_entry:
                    new_exp = input("Enter total exp gained: ")
                    try:
                        new_exp = int(new_exp)
                        got_entry = True
                    except:
                        print("Please enter a numeric value.")
                for a in range(0, quantity_crafted):
                    per_exp = new_exp/quantity_crafted
                    query = "INSERT INTO exp_records (recipe_id, exp_gained, char_level\
                        char_id) VALUES(?,?,?,?)"
                    self.curs.execute("SELECT job_level FROM job_data WHERE char_id=?\
                        AND job_name=?", (self.curr_char["char_id"],recipe["job"]))
                    job_level = self.curs.fetchall()[0][0]
                    inserts = [recipe["id"],per_exp,job_level,self.curr_char["char_id"]]
                    print(query)
                    print(inserts)
                    self.curs.execute(query, tuple(inserts))
                    self.conn.commit()

    ##MAKE A PLOT
    def simple_plot(self):
        ids_query = "SELECT recipe_id FROM exp_records GROUP BY recipe_id"
        self.curs.execute(ids_query)
        recipe_ids = self.curs.fetchall()[0]
        fetch_query = "SELECT exp_gained, char_level FROM exp_records WHERE\
            char_id=" + str(self.curr_char["char_id"]) + " AND recipe_id = ?"
        for id in recipe_ids:
            self.curs.execute(fetch_query, (id,))
            data = self.curs.fetchall()
            x_data = list(map(lambda x: x[1], data))
            y_data = list(map(lambda x: x[0], data))
            print(x_data)
            print(y_data)
            trace = go.Scatter(x = x_data, y = y_data, mode = "markers")
            data = [trace]
            ply.plot(data, filename="./basic-line.html")
