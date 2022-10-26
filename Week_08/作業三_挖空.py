from tkinter import *
import tkinter as tk
from functools import partial
from unittest.mock import seal
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer


from tkinter import *
from tkinter import ttk
import tkinter as tk
from functools import partial
from unittest.mock import seal
import numpy as np
import pandas as pd
import math
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer


class main_screen:
    def __init__(self, root, tfidf_matrix, tfidf, item_df):
        self.filter_df = None
        self.filtered_df = None
        self.filter_list = []
        self.stop = 0
        self.filter = 0
        self.root = root
        self.root.protocol("WM_DELETE_WINDOW", self.callback)
        self.frame = tk.Frame(self.root)
        self.frame2 = tk.Frame(self.root)
        self.search_result = None
        self.selected_item_id = None
        self.newWindow = None
        self.other_app = None

        self.hint = Label(self.frame, text='Enter word to search:', font=('Times', 20))
        self.hint2 = Label(self.frame2, text='    Attribute filter:', font=('Times', 20))
        self.input = Entry(self.frame, font=('Times', 20))
        self.listbox = tk.Listbox(root, height=20, font=('Times', 20), selectmode=tk.SINGLE)
        action_with_arg = partial(self.update_screen, tfidf_matrix, tfidf, item_df)
        self.buttn = Button(self.frame, text='search', font=('Times', 20), command = action_with_arg)
        self.buttn2 = Button(self.frame2, text='filter', font=('Times', 20), command = self.get_selection_check_box)
        self.selection_box = ttk.Combobox(self.frame2, values=[], font=('Times', 20))

        self.hint.pack(side=LEFT)
        self.input.pack(side=LEFT, fill='x', expand=1)
        self.buttn.pack(side=RIGHT)
        self.hint2.pack(side=LEFT, fill='x', expand=1)
        self.selection_box.pack(side=LEFT)
        self.buttn2.pack(side=RIGHT)
        self.frame.pack(side=TOP)
        self.frame2.pack(side=TOP)
        self.listbox.pack(side=BOTTOM, fill='x')

        self.input.focus_set()
        
    def update_screen(self, tfidf_matrix, tfidf, item_df):
        self.search_result = search(self.input.get(), tfidf_matrix, tfidf, item_df)
        self.filter_df = self.search_result.copy()
        self.listbox.delete(0,END)
        for index, row in self.search_result.iterrows():
            self.listbox.insert(tk.END, f'{index+1:3}' + '| ' + row['title'])
        self.attribute_df = self.filter_df.drop(['Unnamed: 0', 'index', 'cate', 'scores', 'title', 'desc', 'scores'], axis=1)
        self.selection_box['values'] = list(self.attribute_df.columns )

    def update_screen_for_filter(self):
        self.listbox.delete(0,END)
        for index, row in self.search_result.iterrows():
            self.listbox.insert(tk.END, f'{index+1:3}' + '| ' + row['title'])
        
    def get_selection_check_box(self):
        if self.filter == 0:
            self.filter = 1

    def callback(self):
        self.root.quit()
        self.stop = 1
    

class select_attribute_value_screen:
    def __init__(self, root, attribute_df, attribute, app):
        self.app = app
        self.attribute_df = attribute_df
        self.root = root
        self.root.protocol("WM_DELETE_WINDOW", self.callback)
        self.root.geometry("500x580") # set the root dimensions
        self.check_boxes = []
        self.vars = []
        self.text = []

        for attribute_value in list(set(attribute_df[attribute])):
            try:
                if not math.isnan(attribute_value):
                    self.vars.append(tk.IntVar())
                    self.check_boxes.append(tk.Checkbutton(self.root, text=attribute_value, variable=self.vars[-1], onvalue=1, offvalue=0))
                    self.text.append(attribute_value)
            except:
                self.vars.append(tk.IntVar())
                self.check_boxes.append(tk.Checkbutton(self.root, text=attribute_value, variable=self.vars[-1], onvalue=1, offvalue=0))
                self.text.append(attribute_value)
        for c in self.check_boxes:
            c.pack()
        
        self.buttn = Button(self.root, text='search', font=('Times', 20), command = self.find)
        self.buttn.pack()

    def find(self):
        final = []
        for v, t in zip(self.vars, self.text):
            if v.get() == 1:
                final.append(t)
        self.app.filter_list = final
        self.root.destroy()
    
    def callback(self):
        self.app.filter = 3
        

class detail_item_screen:
    def __init__(self, root, selected_item_id, search_result):
        self.root = root
        self.root.geometry("1200x480") # set the root dimensions
        self.root.pack_propagate(False) # tells the root to not let the widgets inside it determine its size.
        self.root.resizable(0, 0) # makes the root window fixed in size.

        self.selected_item_id = selected_item_id
        self.search_result = search_result.iloc[selected_item_id]
        self.search_result = self.search_result.drop(['Unnamed: 0', 'index', 'cate', 'scores'])

        # Frame for TreeView
        self.frame1 = tk.LabelFrame(self.root, text="Product Information", font=('Times', 20))
        self.frame1.place(height=250, width=1200)

        # Frame for open file dialog
        self.btn_frame = tk.LabelFrame(root, font=('Times', 20))
        self.btn_frame.place(height=70, width=400, rely=0.65, relx=0.33)

        # Button
        self.quitButton = tk.Button(self.btn_frame, text="Quit", command = self.close_windows, font=('Times', 20))
        self.quitButton.place(rely=0.3, relx=0.4)

        ## Treeview Widget
        self.tv1 = ttk.Treeview(self.frame1)
        s = ttk.Style()
        s.configure('.', font=('Times', 15))
        s.configure('Treeview.Heading', font=('Times', 15))
        self.tv1.place(relheight=1, relwidth=1) # set the height and width of the widget to 100% of its container (frame1).

        self.treescrolly = tk.Scrollbar(self.frame1, orient="vertical", command=self.tv1.yview) # command means update the yaxis view of the widget
        self.treescrollx = tk.Scrollbar(self.frame1, orient="horizontal", command=self.tv1.xview) # command means update the xaxis view of the widget
        self.tv1.configure(xscrollcommand=self.treescrollx.set, yscrollcommand=self.treescrolly.set) # assign the scrollbars to the Treeview Widget
        self.treescrollx.pack(side="bottom", fill="x") # make the scrollbar fill the x axis of the Treeview widget
        self.treescrolly.pack(side="right", fill="y") # make the scrollbar fill the y axis of the Treeview widget

        self.display_product_information()

    def display_product_information(self):

        self.clear_data()
        for i in self.search_result.index:
            try:
                if math.isnan(self.search_result[i]):
                    self.search_result = self.search_result.drop(i)
            except:
                pass
        self.tv1["column"] = list(self.search_result.index)
        self.tv1["show"] = "headings"
        for column in self.tv1["columns"]:
            self.tv1.heading(column, text=column) # let the column heading = column name

        self.df_rows = self.search_result.to_numpy().tolist() # turns the dataframe into a list of lists
        self.tv1.insert("", "end", values=self.df_rows) # inserts each list into the treeview. For parameters see https://docs.python.org/3/library/tkinter.ttk.html#tkinter.ttk.Treeview.insert
        for i in self.search_result.index:
            if len(self.search_result[i]) > 10:
                self.tv1.column(i, minwidth=0, width= 20 * (len(self.search_result[i])))
        return None

    def clear_data(self):
        self.tv1.delete(*self.tv1.get_children())
        return None

    def close_windows(self):
        self.root.destroy()


    #----------------------------------------------------------------------------------------------------------------------------------
    # 你可能需要修改的部分
    #----------------------------------------------------------------------------------------------------------------------------------


def search(query, tfidf_matrix, tfidf, item_df):
    score = np.zeros(tfidf_matrix.shape[1])

    # 將 query 字串轉成 tfidf 向量
    que_tfidf = 轉換tfidf向量的方法([query])

    # 計算 query 與 100,000 筆商品的 cosine similarity
    scores = cosine_similarity(que_tfidf,tfidf_matrix)

    # 輸出排序後的前50個index (按照 cosine similarity 降冪排序)
    top_50_indices = np.argsort(-scores[0])[:50]
    scores = scores[0][top_50_indices]

    # 將相似度最高的前50筆商品，從 item_df 取出
    search_result = 
    
    search_result['scores'] = scores
    
    return search_result

def main():

    ## ===========================================
    ## Load data
    ## ===========================================

    # product item
    item_df = pd.read_csv('./momo_product_10w.csv')
    
    ## ===========================================
    ## Build model
    ## ===========================================

    #Define a TF-IDF Vectorizer Object. Remove all english stopwords
    tfidf = TfidfVectorizer(token_pattern=r"(?u)\b\w\w+\b", ngram_range=(1,2))

    #Construct the required TF-IDF matrix by applying the fit_transform method on the overview feature
    # 建立 100,000 筆商品的 tf-idf 矩陣
    tfidf_matrix = 
    
    #Output the shape of tfidf_matrix
    tfidf_matrix.shape

    #----------------------------------------------------------------------------------------------------------------------------------
    # 你可能需要修改的部分
    #----------------------------------------------------------------------------------------------------------------------------------

    root = tk.Tk()
    root.geometry("1420x640")
    app = main_screen(root, tfidf_matrix, tfidf, item_df)
    
    while True:
        app.root.update()
        if app.listbox.curselection():
            app.selected_item_id = app.listbox.curselection()[0]
            app.newWindow = tk.Toplevel(app.root)
            app.other_app = detail_item_screen(app.newWindow, app.selected_item_id, app.search_result)
            app.listbox.selection_clear(0, 'end')
        
        if app.filter == 1:
            if app.selection_box.get() == '':
                app.filter = 0
            else:
                app.newWindow = tk.Toplevel(app.root)
                app.other_app = select_attribute_value_screen(app.newWindow, app.filter_df, app.selection_box.get(), app)
                app.filter = 2
        
        if len(app.filter_list) > 0:
             app.search_result = app.filter_df[app.filter_df[app.selection_box.get()].isin(app.filter_list)]
             app.update_screen_for_filter()
             app.filter = 0
             app.filter_list = []
        
        if app.filter == 3:
            app.filter = 0

        if app.stop == 1:
            break
    
if __name__ == '__main__':
    main()




    


    