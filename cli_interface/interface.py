#!/usr/bin/env python3

import urwid
import sqlite3

conn = sqlite3.connect("../recipes")
curr = conn.cursor()

curr.execute("SELECT job FROM recipes GROUP BY JOB")
headers = list(map(lambda x: x[0], curr.description))
#print(headers[0])
#print("".ljust(20,"-"))
jobs = []
for a in curr.fetchall():
    #print(a[0])
    jobs.append(a[0])

def menu(title, choices):
    body = [urwid.Text(title), urwid.Divider()]
    for c in choices:
        button = urwid.Button(c)
        urwid.connect_signal(button, 'click', item_chosen, c)
        body.append(urwid.AttrMap(button, None, focus_map="reversed"))
    return urwid.ListBox(urwid.SimpleFocusListWalker(body))

def list_recipes(job):
    sel_string = "SELECT name, r_level FROM recipes WHERE job=?"
    curr.execute(sel_string, (job,))
    headers =  list(map(lambda x: x[0], curr.description))
    out_headers = ""
    for a in headers:
        out_headers+=a.ljust(20, " ")
    body = [urwid.Text(out_headers), urwid.Divider()]
    for a in curr.fetchall():
        out_txt = u""
        for b in a:
            out_txt+=str(b).ljust(20, " ")
        body.append(urwid.Text(out_txt))
    return urwid.ListBox(urwid.SimpleFocusListWalker(body))

def item_chosen(button, choice):
    main.original_widget = list_recipes(choice)

def q_on_exit(key):
    if key in ('q', 'Q'):
        conn.close()
        raise urwid.ExitMainLoop()

main = urwid.Padding(menu(u"Jobs", jobs), left=2, right=2)
top = urwid.Overlay(main, urwid.SolidFill(u'\N{MEDIUM SHADE}'),
        align='center', width=('relative', 60),
        valign='middle', height=('relative', 60),
        min_width=20, min_height=9)
urwid.MainLoop(top,unhandled_input=q_on_exit,
        palette=[('reversed', 'standout', '')]).run()

