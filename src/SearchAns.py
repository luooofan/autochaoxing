# coding=utf-8
##
# Author       : Luoofan
# Date         : 2020-03-11 09:15:44
# LastEditorsPlease set LastEditors
# LastEditTime2020-05-04 14:06:10
# Description  :SearchAns
# FilePath\src\SearchAns.py
#

import tkinter as tk
from tkinter import ttk
from ast import literal_eval
from re import sub
from urllib.parse import quote
from requests import post
from requests import get
from queryans import QueryAns

win = tk.Tk()
win.title("SearchAns")
win.geometry('505x230')  # 设定窗口大小

# win.resizable(0, 0)  # Disable resizing the GUI
tabControl = ttk.Notebook(win)  # Create Tab Control

tab1 = ttk.Frame(tabControl)  # Create a tab
tabControl.add(tab1, text="Normal")  # Add the tab

#tab2 = ttk.Frame(tabControl)  # Add a second tab
#tabControl.add(tab2, text="Exact")  # Make second tab visible

tabControl.pack(expand=1, fill="both")  # Pack to make visible

# Tab1控件介绍
monty = ttk.LabelFrame(tab1, text="Main")
monty.grid(column=0, row=0, padx=10, pady=4, ipady=5)
# tab1 input
ttk.Label(monty, text="题目:", font=('Arial', 12), width=5).grid(column=0, row=0, padx=5)  # , sticky='E')
queText = tk.Text(monty, font=('Arial', 12), width=40, height=3)
queText.grid(column=1, row=0, rowspan=2)  # ,sticky='W')
# tab1 button

'''
def query_ans_normal(ev=None):
    global res
    q = quote(queText.get('0.0', 'end'))
    url = 'http://api.xmlm8.com/tk.php?t='+q
    ret_da = literal_eval(get(url).text)
    res.set("que:"+ret_da['tm']+'\n'+"ans:"+ret_da['da'])
    queText.delete('1.0', 'end')'''

def query_ans_normal(ev=None):
    #global res
    infodic = {
        'question': str(queText.get('0.0', 'end')),
        'type': '其他',
        'course':'',
        'courseID': ''
    }
    resText.delete('1.0','end')
    QA=QueryAns(**infodic)
    #res.set(str(QA.work()))
    resText.insert('1.0', str(QA.work()))
    queText.delete('1.0', 'end')




queText.bind("<Return>", query_ans_normal)
go = ttk.Button(monty, text='Go', width=5, command=query_ans_normal)
go.grid(column=2, row=0, rowspan=2, sticky="n" + "s", padx=5)
# tab1 output
ttk.Label(monty, text="结果:", font=('Arial', 12), width=5).grid(column=0, row=3, padx=5, pady=5)
#res = tk.StringVar()
resText = tk.Text(monty,font=('Arial', 12), width=46, height=5)
resText.grid(column=1, row=3, rowspan=3, columnspan=2, pady=5, sticky="n"+"s")
#tk.Label(monty, height=5, textvariable=res, font=('Arial', 12), width=45, wraplength=400, justify='left', anchor='w').grid(
#    column=1, row=3, rowspan=3, columnspan=2, pady=5, sticky="n"+"s")
#for child in monty.winfo_children():
#    child.grid_configure(padx=5, pady=1)


#win.iconbitmap('../img/searchans.ico')
win.mainloop()
