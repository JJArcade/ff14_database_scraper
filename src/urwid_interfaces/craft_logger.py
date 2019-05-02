import urwid, os, re, sys
##IMPORT RECIPE TOOL
include_path = os.path.expanduser('~')
include_path = os.path.join(include_path, "Documents", 
       "code_projects", "ff14_database_scraper", "src")
sys.path.insert(0, include_path)
from recipe_calculator import recipe_calculator as rc

class main_app():
    def __init__(self):
        self.name = u"Crafting Log"

        # generate buttons
        self.make_options()
        self.job_display()

        # make main fill
        self.solid_fill = urwid.SolidFill(u'\N{MEDIUM SHADE}')
        # move job list into filler
        temp = self.all_jobs
        #temp2 = urwid.Pile([temp, self.btn_pile])
        self.main_page_layout = urwid.Padding(temp,
                align='center',width=('relative',90))
        #self.line_box =  urwid.LineBox(self.btn_pile, self.name)
        self.line_box = urwid.LineBox(self.main_page_layout, self.name)
        self.overlay = urwid.Overlay(self.line_box, self.solid_fill,
                align='center', width=('relative',90), valign='middle',
                height=('relative',90), min_width=20, min_height=10)

        # palette
        pal = [ ('normal', 'black', 'light gray'),
                ('complete', 'black', 'dark red')]

        # main loop
        self.loop = urwid.MainLoop(self.overlay, pal, unhandled_input=self.exit_on_q)

    def make_options(self):
        self.btns = []

        # select character
        chr_btn = urwid.Button(u"Select Character",
                None, None)
        self.btns.append(chr_btn)

        # log crafting
        log_btn = urwid.Button(u"Log Crafting",
                None, None)
        self.btns.append(log_btn)

        # put buttons into listbox
        #self.btn_pile = urwid.ListBox(urwid.SimpleFocusListWalker(self.btns))
        self.btn_pile = urwid.Columns(self.btns)

    
    def job_display(self):
        # start building job layout
        job_title = urwid.Text(u'JOB', align='left')
        job_level = urwid.Text(u'28', align='right')
        temp_columns = urwid.Columns([job_title, job_level], 1)
        

        # custom progress bar
        class JobProgressBar(urwid.ProgressBar):
            def get_text(self):
                return "{} / {}".format(self.current, self.done)
        
        #job_progress = JobProgressBar(('normal','white','black'),('complete','white','dark cyan'))
        job_progress = JobProgressBar('normal', 'complete', 1000, 10000)
        job_progress.render((70,))
        job_container = urwid.Pile([temp_columns, job_progress])
        job_container = urwid.Filler(job_container)
        job_container = urwid.BoxAdapter(job_container, 3)
        list_of_jobs = [job_container, job_container]

        job_list = urwid.ListBox(urwid.SimpleListWalker(list_of_jobs))

        self.all_jobs = job_list


    def exit_on_q(self, key):
        if key in ('q', 'Q'):
            raise urwid.ExitMainLoop()

##MAIN LOOP
if __name__ == "__main__":
    app = main_app()
    app.loop.run()
