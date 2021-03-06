
# coding=utf-8
# from multiprocessing.sharedctypes import synchronized
# from threading import Thread
# from multiprocessing import Process
# import multiprocessing
# from math import ceil
# from multiprocessing import Process
# from multiprocessing.sharedctypes import synchronized
import json
import operator
import os
import time
import requests
from tkinter import *
import tkinter
import tkinter.messagebox
from tkinter import filedialog
import Stemmer
import linecache
import queue
import shutil
import ast
# import gensim
# from gensim.models import KeyedVectors
# import nltk
# # nltk.download('wordnet')
from nltk.corpus import wordnet
from tkinter.filedialog import askopenfilename


class GUI:
    entry_Resources_Path = ''
    entry_Save_Path = ''
    entry_Queries_Path = ''
    entry_Stemming_Bool = 0
    list_cities = set()
    global cities_posting
    global main_index
    global main_dictionary
    global docs_dictionary
    global number_of_docs
    global total_length_of_docs
    global avgdl

    number_of_individual_queries = 0

    def __init__(self, root):
        self.topFrame = Frame(root)
        window_width = 300
        window_height = 370
        position_right = int(root.winfo_screenwidth() / 2 - window_width / 2)
        position_down = int(root.winfo_screenheight() / 2 - window_height / 2)
        root.title("Boogle")
        root.geometry("300x370+{}+{}".format(position_right, position_down))
        root.resizable(0, 0)
        self.text_Resources_Path = Label(root, text="Resources Path:")
        self.text_Save_Path = Label(root, text="Save Path:")
        self.entry_Resources_Path = Entry(root)
        self.entry_Save_Path = Entry(root)
        self.button1 = Button(text="Browse...", fg='black', command=lambda: self.browse_folder())
        self.button2 = Button(text="Browse...", fg='black', command=lambda: self.browse_save_file())
        self.text_Resources_Path.grid(row=0)
        self.text_Save_Path.grid(row=1)
        self.entry_Resources_Path.grid(row=0, column=1)
        self.entry_Save_Path.grid(row=1, column=1)
        self.button1.grid(row=0, column=2)
        self.button2.grid(row=1, column=2)
        self.start_button = Button(text="Start", fg='black', command=lambda: self.start_work())
        self.start_button.grid(row=3, column=1)
        self.entry_Stemming_Bool = tkinter.IntVar()
        self.stemmerLabel = Checkbutton(root, text="Stemming", variable=self.entry_Stemming_Bool)
        self.stemmerLabel.grid(row=3, column=0)

        self.text_Queries_Path = Label(root, text="Queries Path:")
        self.text_Query = Label(root, text="Query:")
        self.entry_Queries_Path = Entry(root)
        self.entry_Query = Entry(root)
        self.queryButton = Button(text="Browse...", fg='black', command=lambda: self.browse_queries_folder())
        self.runButton = Button(text="Run", fg='black', command=lambda: self.start_search())
        self.text_Queries_Path.grid(row=5)
        self.text_Query.grid(row=6)
        self.entry_Queries_Path.grid(row=5, column=1)
        self.entry_Query.grid(row=6, column=1)
        self.runButton.grid(row=7, column=1)
        self.queryButton.grid(row=5, column=2)
        self.entry_Semantic_Bool = tkinter.IntVar()
        self.semanticLabel = Checkbutton(root, text="Semantic", variable=self.entry_Semantic_Bool)
        self.semanticLabel.grid(row=7, column=0)
        self.cityButton = Button(text="Cities Filter", fg='black', command=lambda: self.city_filter())
        self.cityButton.grid(row=4, column=1)

        self.language = Label(root, text="Language:")
        self.language.grid(row=8, column=0)
        self.language_list = Listbox(root, width=20, height=5)
        self.language_list.grid(row=8, column=1)
        self.reset_button = Button(text="Reset", fg='black', command=lambda: self.reset())
        self.reset_button.grid(row=9, column=1)
        self.dictionary_button = Button(text="Show Dictionary", fg='black', command=lambda: self.show_dictionary())
        self.dictionary_button.grid(row=10, column=1)
        self.load_dictionary_button = Button(text="Load Dictionary", fg='black',
                                             command=lambda: self.load_dictionary())
        self.load_dictionary_button.grid(row=11, column=1)
        self.text_status_label = Label(root, text="Status: ")
        self.status_text_string = StringVar()
        self.text_status = Label(root, textvariable=self.status_text_string, fg="blue")
        self.status_text_string.set("Ready to start")
        self.text_status_label.grid(row=12, column=0)
        self.text_status.grid(row=12, column=1)

        self.city_into_query = ""

    # need to add the paths and the errors
    def start_work(self):
        global main_dictionary
        global number_of_docs
        global total_length_of_docs
        global avgdl
        main_dictionary = {}
        number_of_docs = 0
        total_length_of_docs = 0
        avgdl = 0
        if self.entry_Resources_Path.get() == '' or self.entry_Save_Path.get() == '':
            tkinter.messagebox.showerror("Error", "Please fill in Resources Path and Save Path")
            # self.entry_Resources_Path = ''
            # self.entry_Save_Path = ''

        else:
            self.status_text_string.set("Loading, please wait...")
            self.text_status.config(fg="Red")

            start = time.time()

            # # print("work on it")
            # if self.entry_Stemming_Bool.get() == 1:
            #     print("with stemmer")
            # else:
            #     print("without stemmer")

            root_folder_path = g.entry_Resources_Path.get()
            stop_words_path = root_folder_path + '/stop_words.txt'
            save_path = g.entry_Save_Path.get()

            # lock = multiprocessing.Lock()

            # processes = []

            stemming_bool = self.entry_Stemming_Bool.get()
            read_file = ReadFile(root_folder_path)
            number_of_threads = len(read_file.file_names_split)
            read_file.read_city_language(save_path)

            self.language_list.delete(0, END)
            for language in sorted(read_file.language_dictionary):
                self.language_list.insert(END, language)

            # for city in sorted(read_file.cities):
            #     self.list_cities.add(city)

            main_index.set_stemming_bool(stemming_bool)

            for city in read_file.cities:
                cities_posting[city] = {}

            # ------ Parsing Without Threads ------

            for iteration_index in range(number_of_threads):
                (docs_texts, docs_properties) = read_file.read()
                parser = Parse(iteration_index, stop_words_path, stemming_bool, read_file.cities)
                parser.parse(docs_texts, docs_properties)
                # print('Done Parse %d' % iteration_index)

            # ------ Parsing With Threads ------

            # for thread_index in range(number_of_threads):
            #     process = Process(target=concurrent_parsing, args=[read_file, stop_words_path, thread_index])
            #     process.start()
            #     processes.append(process)
            #
            # # Finish threads
            # for process in processes:
            #     process.join()

            # ------ Indexing Without Threads ------

            # print('Start Updating Cities Posting')

            cp = open((self.entry_Save_Path.get() + '/cities_posting.txt'), 'w')
            for key in sorted(cities_posting.keys()):
                cp.write(key + str(cities_posting[key]).replace(' ', '') + '\n')

            # print('Done Updating Cities Posting')

            ending = ''
            if stemming_bool:
                ending = '_with_stemming'

            avgdl = float(total_length_of_docs) / number_of_docs

            # print('Start Indexing')

            indexer_index = 0
            q = queue.Queue()

            for i in range(number_of_threads):
                q.put(('parser_%d_terms' % i) + ending + '.txt')

            # print('Start Merging')

            final_merged_file_path = ''

            while q.qsize() > 1:
                q.put(main_index.merge_two_posting_files(q.get(), q.get(), indexer_index))
                indexer_index += 1

            # print('Done Merging')

            if indexer_index == 0:
                final_merged_file_path = ('parser_0_terms%s.txt' % ending)
            else:
                final_merged_file_path = (('merge%d' % (indexer_index - 1)) + ending + '.txt')

            main_index.build_index_dictionary(save_path, final_merged_file_path)

            if os.path.exists(save_path + '/posting%s.txt' % ending):
                os.remove(save_path + '/posting%s.txt' % ending)
            os.rename(final_merged_file_path, 'posting%s.txt' % ending)
            shutil.move('posting%s.txt' % ending, save_path)

            # os.rename(save_path + '/' + final_merged_file_path, save_path + '/posting%s.txt' % ending)
            # shutil.move(final_merged_file_path, root_folder_path)
            # shutil.move(root_folder_path + '/' + final_merged_file_path, save_path)

            docs_file_name = ('parser_docs' + ending + '.txt')
            docs_file = open(docs_file_name, "ab")
            # for doc in sorted(docs_dictionary.keys(), key=str.lower):
            for doc in docs_dictionary.keys():
                str_max_tf = str(docs_dictionary[doc]['max_tf'])
                str_max_term = str(docs_dictionary[doc]['max_term'])
                str_num_of_terms = str(docs_dictionary[doc]['num_of_terms'])
                str_doc_length = str(docs_dictionary[doc]['doc_length'])
                str_doc_entities = str(docs_dictionary[doc]['entities'])
                docs_file.write("<" + doc + "~" + str_max_tf + "~" + str_max_term + '~'
                                + str_num_of_terms + "~" + docs_dictionary[doc]['doc_city'] + "~"
                                + str_doc_length + "~" + str_doc_entities.replace(' ', '') + ">\n")
            docs_file.write("@@@")
            docs_file.close()

            if os.path.exists(save_path + '/parser_docs%s.txt' % ending):
                os.remove(save_path + '/parser_docs%s.txt' % ending)
            shutil.move('parser_docs%s.txt' % ending, save_path)

            # if os.path.exists(save_path + '/posting%s.txt' % ending):
            #     os.remove(save_path + '/posting%s.txt' % ending)

            erase_index = 0

            while os.path.exists('parser_%d_terms.txt' % erase_index):
                os.remove('parser_%d_terms.txt' % erase_index)
                erase_index += 1
            erase_index = 0
            while os.path.exists('parser_%d_terms_with_stemming.txt' % erase_index):
                os.remove('parser_%d_terms_with_stemming.txt' % erase_index)
                erase_index += 1
            erase_index = 0
            while os.path.exists('merge%d.txt' % erase_index):
                os.remove('merge%d.txt' % erase_index)
                erase_index += 1
            erase_index = 0
            while os.path.exists('merge%d_with_stemming.txt' % erase_index):
                os.remove('merge%d_with_stemming.txt' % erase_index)
                erase_index += 1

            while not q.empty():
                q.get()

            # print('Done Indexing')

            finish = time.time()

            self.status_text_string.set("Done!")
            self.text_status.config(fg="Green")

            finish_window = Toplevel(root)
            window_width = 250
            window_height = 100
            position_right = int(root.winfo_screenwidth() / 2 - window_width / 2)
            position_down = int(root.winfo_screenheight() / 2 - window_height / 2)
            finish_window.geometry("250x100+{}+{}".format(position_right, position_down))
            num_of_docs_label = Label(finish_window, text="Number of indexed documents: %d" % number_of_docs)
            num_of_terms_label = Label(finish_window,
                                       text="Number of unique terms: %d" % (len(main_dictionary.keys())))
            total_runtime = float("{0:.2f}".format(finish-start))
            runtime_label = Label(finish_window, text=("Total Runtime (seconds): %s" % total_runtime))
            num_of_docs_label.grid(row=0, column=1)
            num_of_terms_label.grid(row=1, column=1)
            runtime_label.grid(row=2, column=1)

    def start_search(self):
        global docs_dictionary
        if self.entry_Queries_Path.get() == '' and self.entry_Query.get() == '' and self.city_into_query == '':
            tkinter.messagebox.showerror("Error", "Please fill Query or Queries Path")
        elif len(docs_dictionary.keys()) == 0:
            tkinter.messagebox.showerror("Error", "Please load dictionaries")
        elif self.entry_Resources_Path.get() == '':
            tkinter.messagebox.showerror("Error", "Please fill resources path so we can get the stop words")
        else:
            search_results_window = Toplevel(root)
            # save_queries_results_window = Toplevel(root)
            window_width = 250
            window_height = 500
            position_right = int(root.winfo_screenwidth() / 2 - window_width / 2)
            position_down = int(root.winfo_screenheight() / 2 - window_height / 2)
            search_results_window.geometry("250x500+{}+{}".format(position_right, position_down))
            # save_queries_results_window.geometry("150x250+{}+{}".format(position_right, position_down))
            ranker = 0

            # init the stemming and the stop words path
            stop_words_path = self.entry_Resources_Path.get() + '/stop_words.txt'
            stemming_bool = self.entry_Stemming_Bool.get()
            semantic_bool = self.entry_Semantic_Bool.get()

            # one query from the entry query
            if self.entry_Query.get() != '' or (self.city_into_query != '' and self.entry_Query.get() == ''):
                self.number_of_individual_queries += 1
                q = str(self.entry_Query.get()) + " " + str(self.city_into_query)
                query_after_parsing = []
                query_tokens = []
                # //////////////////////////////////////////
                # check if we need to fill the entries again
                # //////////////////////////////////////////

                parser = Parse(0, stop_words_path, stemming_bool, "")
                query_tokens = parser.get_tokens(q)
                query_after_parsing = parser.parse_document("only_one_query", query_tokens)
                new_query_after_parsing = " ".join(query_after_parsing)
                searcher = Searcher(new_query_after_parsing, self.entry_Semantic_Bool.get())
                searcher.docs_containing_current_terms.clear()
                searcher.find_docs_containing_current_terms()
                ranker = Ranker(searcher.docs_containing_current_terms, searcher.query_terms)
                ranker.rank()

                frame1 = Frame(search_results_window)
                frame1.pack()

                results_save_button = Button(frame1, text="Save Results",
                                             command=lambda: self.save_query_results
                                             (": %d" % self.number_of_individual_queries,
                                              ranker.ranked_docs))
                results_save_button.pack(side="top")

                frame2 = Frame(search_results_window)
                frame2.pack()

                vsb = Scrollbar(search_results_window, orient="vertical")
                text = Text(search_results_window, width=40, height=20, yscrollcommand=vsb.set)
                vsb.config(command=text.yview)
                vsb.pack(side="right", fill="y")
                text.pack(side="left", fill="both", expand=True)

                i = 1
                for doc_tuple in ranker.ranked_docs:
                    doc_index = Label(search_results_window, text="%d." % i)
                    i += 1
                    doc_name = doc_tuple[0]
                    doc_button = Button(search_results_window, text=doc_name,
                                        command=lambda doc_name=doc_name: self.doc_entities(doc_name))
                    text.window_create("end", window=doc_index)
                    text.window_create("end", window=doc_button)
                    text.insert("end", "\n")

                # if len(ranker.relevant_docs.keys()) > 0:
                #     i = 0
                #     minimum_score = 0.5
                #     current_score = ranker.ranked_docs[i][1]
                #     while current_score > minimum_score and i < 50:
                #         doc_index = Label(search_results_window, text="%d." % (i + 1))
                #         doc_name = ranker.ranked_docs[i][0]
                #         doc_button = Button(search_results_window, text=doc_name,
                #                             command=lambda doc_name=doc_name: self.doc_entities(doc_name))
                #         text.window_create("end", window=doc_index)
                #         text.window_create("end", window=doc_button)
                #         text.insert("end", "\n")
                #         i += 1
                #         current_score = ranker.ranked_docs[i][1]

                # rank_range = min(50, len(ranker.docs_ranks)) + 1
                # for i in range(1, rank_range):
                #     doc_index = Label(search_results_window, text="%d." % i)
                #     doc_name = ranker.docs_ranks[i - 1][0]
                #     doc_button = Button(search_results_window, text=doc_name,
                #                         command=lambda doc_name=doc_name: self.doc_entities(doc_name))
                #     text.window_create("end", window=doc_index)
                #     text.window_create("end", window=doc_button)
                #     text.insert("end", "\n")

            # many queries from queries doc
            else:
                queries_results_after_all = {}
                queries = self.get_queries_from_doc()
                for query_number in queries:
                    q = queries[query_number]['query_text']
                    parser = Parse(0, stop_words_path, stemming_bool, "")
                    query_tokens = parser.get_tokens(q)
                    query_doc_name = "query " + query_number
                    query_after_parsing = parser.parse_document(query_doc_name, query_tokens)
                    new_query_after_parsing = " ".join(query_after_parsing)
                    searcher = Searcher(new_query_after_parsing, self.entry_Semantic_Bool.get())
                    searcher.docs_containing_current_terms.clear()
                    searcher.find_docs_containing_current_terms()
                    ranker = Ranker(searcher.docs_containing_current_terms, searcher.query_terms)
                    ranker.rank()
                    queries_results_after_all[query_number] = []
                    for doc in ranker.ranked_docs:
                        queries_results_after_all[query_number].append(doc[0])

                frame1 = Frame(search_results_window)
                frame1.pack()
                queries_alert = Label(frame1, text="Boogle has finished searching!")
                queries_alert.pack(side="top")
                queries_alert = Label(frame1, text="Please save the results:")
                queries_alert.pack(side="top")
                queries_results_save_button = Button(frame1, text="Save Results",
                                             command=lambda queries_results_after_all=queries_results_after_all:
                                             self.save_queries_results(queries_results_after_all))
                queries_results_save_button.pack(side="top")

                # if len(ranker.relevant_docs.keys()) > 0:
                #     i = 0
                #     minimum_score = 0.5
                #     current_score = ranker.ranked_docs[i][1]
                #     while current_score > minimum_score and i < 50:
                #         doc_index = Label(search_results_window, text="%d." % (i + 1))
                #         doc_name = ranker.ranked_docs[i][0]
                #         doc_button = Button(search_results_window, text=doc_name,
                #                             command=lambda doc_name=doc_name: self.doc_entities(doc_name))
                #         text.window_create("end", window=doc_index)
                #         text.window_create("end", window=doc_button)
                #         text.insert("end", "\n")
                #         i += 1
                #         current_score = ranker.ranked_docs[i][1]

                # rank_range = min(50, len(ranker.docs_ranks)) + 1
                # for i in range(1, rank_range):
                #     doc_index = Label(search_results_window, text="%d." % i)
                #     doc_name = ranker.docs_ranks[i - 1][0]
                #     doc_button = Button(search_results_window, text=doc_name,
                #                         command=lambda doc_name=doc_name: self.doc_entities(doc_name))
                #     text.window_create("end", window=doc_index)
                #     text.window_create("end", window=doc_button)
                #     text.insert("end", "\n")

    def browse_save_file(self):
        if len(self.entry_Save_Path.get()) > 0:
            self.entry_Save_Path.delete(0, len(root.file_save_name))
        # print("choose a folder")
        root.file_save_name = filedialog.askdirectory()
        self.entry_Save_Path.insert(0, root.file_save_name)
        # print(root.file_save_name)

    def browse_folder(self):
        if len(self.entry_Resources_Path.get()) > 0:
            self.entry_Resources_Path.delete(0, len(root.folder_name))
        # print("choose a folder")
        root.folder_name = filedialog.askdirectory()
        self.entry_Resources_Path.insert(0, root.folder_name)
        # print(root.folder_name)

    def browse_queries_folder(self):
        if len(self.entry_Queries_Path.get()) > 0:
            self.entry_Queries_Path.delete(0, len(root.queries_folder_name))
        # print("choose a folder")
        root.queries_folder_name = askopenfilename()
        self.entry_Queries_Path.insert(0, root.queries_folder_name)
        # print(root.queries_folder_name)

    def reset(self):
        global main_dictionary
        #     need to delete thus label from the label
        if self.entry_Save_Path.get() == '':
            tkinter.messagebox.showerror("Error", "Please fill in a Save Path")
        else:
            if self.entry_Resources_Path is not None:
                self.entry_Resources_Path.delete(0, END)
            if self.entry_Save_Path is not None:
                self.entry_Save_Path.delete(0, END)
            self.language_list.delete(0, END)
            main_dictionary = {}

            if os.path.exists(root.file_save_name + '/posting.txt'):
                os.remove(root.file_save_name + '/posting.txt')
            if os.path.exists(root.file_save_name + '/posting_with_stemming.txt'):
                os.remove(root.file_save_name + '/posting_with_stemming.txt')
            if os.path.exists(root.file_save_name + '/index.txt'):
                os.remove(root.file_save_name + '/index.txt')
            if os.path.exists(root.file_save_name + '/index_with_stemming.txt'):
                os.remove(root.file_save_name + '/index_with_stemming.txt')
            if os.path.exists(root.file_save_name + '/cities_index.txt'):
                os.remove(root.file_save_name + '/cities_index.txt')
            if os.path.exists(root.file_save_name + '/cities_posting.txt'):
                os.remove(root.file_save_name + '/cities_posting.txt')
            # print("restarting")

    @staticmethod
    def show_dictionary():
        # print("Show Dictionary")
        global main_dictionary
        if len(main_dictionary.keys()) == 0:
            tkinter.messagebox.showerror("Error", "There is no dictionary loaded")
        else:
            window = Toplevel(root)
            window_width = 300
            window_height = 275
            position_right = int(root.winfo_screenwidth() / 2 - window_width / 2)
            position_down = int(root.winfo_screenheight() / 2 - window_height / 2)
            window.geometry("300x275+{}+{}".format(position_right, position_down))
            index_list = Listbox(window, width=window.winfo_width(), height=window.winfo_height())
            index_list.delete(0, END)
            index_list.pack(side="left", fill="both", expand=1)
            scrollbar = Scrollbar(window, orient="vertical")
            scrollbar.config(command=index_list.yview)
            scrollbar.pack(side="right", fill="y")
            index_list.config(yscrollcommand=scrollbar.set)
            # index_lines = open(self.entry_Save_Path.get() + ('/index%s.txt' % ending), 'r').readlines()
            index_list.insert(END, "Term     ->     TF")
            for key in sorted(main_dictionary.keys(), key=str.lower):
                index_list.insert(END, key + '     ->     ' + main_dictionary[key]['tf'])

    def load_dictionary(self):
        # print("Load Dictionary")
        global main_dictionary
        global docs_dictionary
        global avgdl
        ending = ''
        if self.entry_Stemming_Bool.get():
            ending = '_with_stemming'
        if not os.path.exists(self.entry_Save_Path.get() + ('/index%s.txt' % ending)):
            tkinter.messagebox.showerror("Error", "There is no dictionary in the specified Save Path")
        elif not os.path.exists(self.entry_Save_Path.get() + '/parser_docs.txt'):
            tkinter.messagebox.showerror("Error", "There is no documents dictionary in the specified Save Path")
        elif not os.path.exists(self.entry_Save_Path.get() + '/languages.txt'):
            tkinter.messagebox.showerror("Error", "There is no languages dictionary in the specified Save Path")
        else:
            self.status_text_string.set("Loading...")
            self.text_status.config(fg="Red")
            main_dictionary = {}
            loaded_file = open(self.entry_Save_Path.get() + ('/index%s.txt' % ending), 'r').readlines()
            for line in loaded_file:
                if not line.__contains__('@'):
                    line_split = line.split('~')
                    term = line_split[0]
                    term_index = line_split[1]
                    term_tf = line_split[2]
                    main_dictionary[term] = {'post_index': term_index,
                                             'tf': term_tf}
            if os.path.exists(self.entry_Save_Path.get() + '/parser_docs.txt'):
                docs_dictionary = {}
                doc_len_sum = 0
                doc_count = 0
                loaded_file = open(self.entry_Save_Path.get() + '/parser_docs.txt', 'r').readlines()
                for line in loaded_file:
                    if not line.__contains__('@'):
                        line = line.replace('<', '').replace('>', '')
                        line_split = line.split('~')
                        doc = line_split[0]
                        max_tf = line_split[1]
                        max_term = line_split[2]
                        num_of_terms = line_split[3]
                        doc_city = line_split[4]
                        doc_length = line_split[5]
                        doc_entities = line_split[6]
                        docs_dictionary[doc] = {'max_tf': max_tf,
                                                'max_term': max_term,
                                                'num_of_terms': num_of_terms,
                                                'doc_city': doc_city,
                                                'doc_length': doc_length,
                                                'entities': doc_entities}
                        doc_len_sum += int(doc_length)
                        doc_count += 1
                avgdl = float(doc_len_sum) / doc_count
            if os.path.exists(self.entry_Save_Path.get() + '/languages.txt'):
                self.language_list.delete(0, END)
                loaded_languages_file = open(self.entry_Save_Path.get() + '/languages.txt', 'r').readlines()
                for language in loaded_languages_file:
                    if language != '':
                        self.language_list.insert(END, language.replace('<', '').replace('>', ''))

            self.status_text_string.set("Dictionary Loaded!")
            self.text_status.config(fg="Blue")

    def city_filter(self):
        if not os.path.exists(self.entry_Save_Path.get() + '/cities_index.txt'):
            tkinter.messagebox.showerror("Error", "There is no cities dictionary in the specified Save Path")
        else:
            self.status_text_string.set("Loading...")
            self.text_status.config(fg="Red")
            loaded_file = open(self.entry_Save_Path.get() + '/cities_index.txt', 'r').readlines()
            for line in loaded_file:
                if not line == '':
                    line_split = line.split('~')
                    city = line_split[0]
                    self.list_cities.add(city[1:len(city)])
            city_window = Toplevel(root)
            window_width = 200
            window_height = 300
            position_right = int(city_window.winfo_screenwidth() / 2 - window_width / 2)
            position_down = int(city_window.winfo_screenheight() / 2 - window_height / 2)
            city_window.geometry("200x300+{}+{}".format(position_right, position_down))
            self.status_text_string.set("Working on cities...")
            self.text_status.config(fg="Red")
            ok_button = Button(city_window, text="Save", width="8", command=lambda: self.close_city_window(city_window,
                                                                                                           checkboxes))
            ok_button.pack()
            scroll = Scrollbar(city_window, orient="vertical")
            scroll.pack(side=RIGHT, fill=Y)
            city_list = Text(city_window, width=30, height=17, yscrollcommand=scroll.set)
            checkboxes = {}
            checkbox_list = []
            checkbox_var_list = []
            city_list.pack(side=LEFT)
            scroll.config(command=city_list.yview)

            for city in sorted(self.list_cities):
                var_city = IntVar()
                cb = Checkbutton(city_window, text="%s" % city, variable=var_city, name=city.lower())
                checkboxes[city] = var_city
                checkbox_list.append(cb)
                checkbox_var_list.append(var_city)
                city_list.window_create("end", window=cb)
                city_list.insert("end", "\n")

    def close_city_window(self, city_window, checkboxes):
        self.city_into_query = ""
        city_dictionary = {}
        city_selected = False

        for city in sorted(self.list_cities):
            if checkboxes[city].get() == 1:
                city_selected = True
                city_dictionary[city] = 1

                self.city_into_query += (city + " ")
        if not city_selected:
            for city in sorted(self.list_cities):
                city_dictionary[city] = 1
        self.status_text_string.set("Waiting for query...")
        self.text_status.config(fg="Blue")
        city_window.destroy()

    # this method return the dictionary that contain the query number and the information of every query
    def get_queries_from_doc(self):
        queries_texts = {}
        queries_file = open(self.entry_Queries_Path.get(), "r").read()
        for query_contents in queries_file.split("</top>")[:-1]:
            if query_contents != '\n':
                query_number = query_contents.split('<title>')[0].split('Number: ')[1].replace(' ', '').replace('\n', '')
            if '<title>' in query_contents:
                query_text = query_contents.split('<title>')[1].split('<desc>')[0].replace('\n', ' ')
            queries_texts[query_number] = {'query_number': query_number, 'query_text': query_text}
        return queries_texts

    # this method saved all queries results to one file
    def save_query_results(self, query_number, docs):
        queries_file_name = open(self.entry_Save_Path.get() + '/results.txt', "ab")
        query_id = query_number.split(": ")[1]
        # i = 1
        # float_number = 1.0
        for doc in docs:
            queries_file_name.write(query_id + " 0 " + str(doc[0]) + ' 1 1.0 test\n')
        tkinter.messagebox.showinfo("Done", "Query results saved!")

    def save_queries_results(self, queries_dic):
        queries_file_name = open(self.entry_Save_Path.get() + '/results.txt', "ab")
        for key in sorted(queries_dic.iterkeys()):
            query_id = key
            docs = queries_dic[key]
            for doc in docs:
                queries_file_name.write(query_id + " 0 " + str(doc) + ' 1 1.0 test\n')

    @staticmethod
    def doc_entities(doc_name):
        global docs_dictionary
        text_window = Toplevel(root)
        window_width = 200
        window_height = 200
        position_right = int(text_window.winfo_screenwidth() / 2 - window_width / 2)
        position_down = int(text_window.winfo_screenheight() / 2 - window_height / 2)
        text_window.geometry("200x200+{}+{}".format(position_right, position_down))
        exit_button = Button(text_window, text="Exit", command=lambda: text_window.destroy())
        exit_button.pack()
        doc_label = Label(text_window, text=("Doc Name: " + doc_name))
        doc_label.pack(side="top", fill="both")
        entities_label = Label(text_window, text='Top 5 Entities:')
        entities_label.pack(side="top", fill="both")
        entities = docs_dictionary[doc_name]['entities'].split(',')
        for i in range(len(entities)):
            label_text = str(i + 1) + ". " + (str(entities[i]).replace('\'', '').replace('[', '').replace(']', ''))
            label_entity = Label(text_window, text=label_text)
            label_entity.pack(side="top", fill="both")


class ReadFile:
    # docs_texts = {}
    # docs_properties = {}
    cities = set()
    language_dictionary = set()
    resources_path = ''
    file_names = []
    number_of_files_per_iteration = 50
    file_names_split = []
    file_names_split_index = 0
    cities_properties = {}

    def __init__(self, folder_path):
        self.resources_path = folder_path + '/corpus/'
        self.file_names = os.listdir(self.resources_path)
        self.file_names_split = []
        indexes = range(0, self.file_names.__len__(), min(self.file_names.__len__(),
                                                          self.number_of_files_per_iteration))[1:]
        prev = 0
        for index in indexes:
            self.file_names_split.append(self.file_names[prev:index])
            prev = index
        self.file_names_split.append(self.file_names[prev:len(self.file_names)])
        pass

    def read(self):
        docs_texts = {}
        docs_properties = {}
        current_file_names = self.file_names_split[self.file_names_split_index]
        for file_name in current_file_names:
            # file = open(self.root_folder_path + file_name + "/" + file_name, "r").read()
            file = open(self.resources_path + "/" + file_name + "/" + file_name.split(' ')[0], "r").read()
            # for doc_contents in file.split("</DOC>\n\n<DOC>"):
            for doc_contents in file.split("</DOC>")[:-1]:
                doc_language = ''
                doc_city = ''
                doc_text = ''
                if doc_contents != '\n':
                    doc_name = doc_contents.split('</DOCNO>')[0].split('<DOCNO>')[1].replace(' ', '')
                if '<F P=105>' in doc_contents:
                    i = 0
                    while doc_contents.split('<F P=105>')[1].split('</F>')[0].split(' ')[i] == '':
                        i += 1
                    doc_language = doc_contents.split('<F P=105>')[1].split('</F>')[0].split(' ')[i]
                if '<F P=104>' in doc_contents:
                    i = 0
                    while len(doc_contents.split('<F P=104>')[1].split('</F>')[0]) > 0\
                            and doc_contents.split('<F P=104>')[1].split('</F>')[0].split(' ')[i] == '':
                        i += 1
                    doc_city = doc_contents.split('<F P=104>')[1].split('</F>')[0].split(' ')[i]
                if '</TEXT>' in doc_contents:
                    doc_text = doc_contents.split('<TEXT>')[1].split('</TEXT>')[0].replace('\n', ' ') \
                        .replace(':', '').replace('"', '').replace('!', '').replace('?', '').replace('~', '') \
                        .replace("'", '').replace('*', '').replace('(', '').replace(')', '').replace('[', '') \
                        .replace('|', '').replace(']', '').replace('{', '').replace('}', '').replace(';', '') \
                        .replace('&', '').replace('#', '').replace(',.', '').replace('.-', '').replace('\ ', '') \
                        .replace('+', '').replace('_', '').replace('=', '').replace('\r', '').replace('<', '') \
                        .replace('--', ' ').replace('\t', '').replace('-,', ' ').replace('..', '') \
                        .replace('^', '').replace('\ ', '').replace('//', '').replace('@', '').replace('>', '') \
                        .replace('   ', ' ').replace('  ', ' ')
                docs_properties[doc_name] = {'language': doc_language, 'city': doc_city.upper()}
                docs_texts[doc_name] = {'text': doc_text}
        self.file_names_split_index += 1
        return docs_texts, docs_properties

    def read_city_language(self, save_path):
        api_dictionary = self.read_api()
        for file_name in self.file_names:
            # file = open(self.root_folder_path + file_name + "/" + file_name, "r").read()
            file = open(self.resources_path + file_name + "/" + file_name.split(' ')[0], "r").read()
            # for doc_contents in file.split("</DOC>"):
            for doc_contents in file.split("</DOC>\n\n<DOC>"):
                doc_language = ''
                doc_city = ''
                doc_text = ''
                if doc_contents != '\n':
                    doc_name = doc_contents.split('</DOCNO>')[0].split('<DOCNO>')[1].replace(' ', '')
                if '<F P=105>' in doc_contents:
                    i = 0
                    while doc_contents.split('<F P=105>')[1].split('</F>')[0].split(' ')[i] == '':
                        i += 1
                    doc_language = doc_contents.split('<F P=105>')[1].split('</F>')[0].split(' ')[i]
                    if len(doc_language) < 1:
                        pass
                    else:
                        if not doc_language.isalpha() and doc_language[len(doc_language) - 1] \
                                in [',', '.', ':', ';', ']', '-']:
                            doc_language = doc_language[:-1]
                        if (not doc_language[0].isupper()) or doc_language.upper() in self.language_dictionary:
                            pass
                        else:
                            self.language_dictionary.add(doc_language.upper())
                if '<F P=104>' in doc_contents:
                    i = 0
                    while len(doc_contents.split('<F P=104>')[1].split('</F>')[0]) > 0 \
                            and doc_contents.split('<F P=104>')[1].split('</F>')[0].split(' ')[i] == '':
                        i += 1
                    doc_city = doc_contents.split('<F P=104>')[1].split('</F>')[0].split(' ')[i]
                    if len(doc_city) < 1:
                        pass
                    else:
                        if not doc_city.isalpha() and doc_city[len(doc_city) - 1] \
                                in [',', '.', ':', ';', ']', '-']:
                            doc_city = doc_city[:-1]
                        if (not doc_city[0].isupper()) or doc_city.upper() in self.cities:
                            pass
                        else:
                            self.cities.add(doc_city.upper())

        city_file_name = '/cities_index.txt'
        city_properties_file_name = '/cities_properties.txt'
        language_file_name = '/languages.txt'
        open(save_path + city_file_name, "w")
        city_file = open(save_path + city_file_name, "ab")
        open(save_path + language_file_name, "w")
        language_file = open(save_path + language_file_name, "ab")
        open(save_path + city_properties_file_name, "w")
        city_properties_file = open(save_path + city_properties_file_name, "ab")

        for key in sorted(self.language_dictionary):
            # str_language = str(self.language_dictionary[key])
            language_file.write("<" + key + ">\n")
        i = 0
        for key in sorted(self.cities):
            # str_city = str(self.city_dictionary[key])
            if key in api_dictionary.keys():
                city_properties_file.write("<" + api_dictionary[key]["name"] + "~" +
                                           api_dictionary[key]["population"] + "~" +
                                           api_dictionary[key]["currencies"] + ">\n")
            else:
                city_properties_file.write("<~~~>\n")
            city_file.write("<" + key + "~" + str(i) + ">\n")
            i += 1

    def read_api(self):
        # {capital, {vbbnvn, jhfjh, vjhgvgh}}
        response = requests.get("https://restcountries.eu/rest/v2/all")
        json_content = json.loads(response.text)
        for term in json_content:
            currency = term["currencies"][0]["code"]
            temp_population = term["population"]
            if temp_population < 1000:
                population = str(temp_population)
            elif 1000 <= temp_population < 1000000:
                population = str(temp_population / 1000.0) + "K"
            elif 1000000 <= temp_population < 1000000000:
                population = str(temp_population / 1000000.0) + "M"
            else:
                population = str(temp_population / 1000000000.0) + "B"

            capital = (term["capital"]).upper()
            state = term["name"]
            self.cities_properties[capital] = {}
            self.cities_properties[capital]["name"] = state
            self.cities_properties[capital]["population"] = population
            self.cities_properties[capital]["currencies"] = currency
        return self.cities_properties


class Parse:
    parser_index = 0
    stop_words = set()
    stemmer = Stemmer.Stemmer('english')
    global number_of_docs
    global total_length_of_docs

    # id:
    #   term
    # values:
    #   (num of docs) = size(list of docs)              number
    #   tf_per_doc (num of appearances in each doc)     {key:doc_name, value:number}
    #   list of docs                                    [doc1, doc2, ...]
    terms_dictionary = {}
    # id:
    #   doc_name
    # values:
    #   max_tf of term                                  number
    #   num of terms                                    number
    #   doc_city                                        string
    global docs_dictionary
    cities = {}
    global cities_posting

    # Lists for parser:
    price_number_names = {'thousand', 'million', 'billion', 'trillion', 'Thousand', 'Million',
                          'Billion', 'Trillion', 'k', 'm', 'bn', 'tr'}
    dollar_names = {'Dollars', 'dollars', 'Dollars,', 'dollars,', 'Dollars.', 'dollars.'}
    regular_number_names = {'Thousand', 'Million', 'Billion', 'Trillion', 'Thousand.', 'Million.', 'Billion.',
                            'Trillion.', 'thousand', 'million', 'billion', 'trillion', 'thousand.', 'million.',
                            'billion.', 'trillion.', 'Thousand,', 'Million,', 'Billion,', 'Trillion,', 'thousand,',
                            'million,', 'billion,', 'trillion,'}
    percentage_labels = {'%', 'percent', 'percentage', 'percent.', 'percentage.', 'percent,', 'percentage,', 'Percent',
                         'Percentage', 'Percent.', 'Percentage.', 'Percent,', 'Percentage,'}
    months_names = {'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'January',
                    'February', 'March', 'April', 'June', 'July', 'August', 'September', 'October', 'November',
                    'December', 'JANUARY', 'FEBRUARY', 'MARCH', 'APRIL', 'MAY', 'JUNE', 'JULY', 'AUGUST', 'SEPTEMBER',
                    'OCTOBER', 'NOVEMBER', 'DECEMBER', 'Jan.', 'Feb.', 'Mar.', 'Apr.', 'May.', 'Jun.', 'Jul.', 'Aug.',
                    'Sep.', 'Oct.', 'Nov.', 'Dec.', 'January.', 'February.', 'March.', 'April.', 'June.', 'July.',
                    'August.', 'September.', 'October.', 'November.', 'December.', 'JANUARY.', 'FEBRUARY.', 'MARCH.',
                    'APRIL.', 'MAY.', 'JUNE.', 'JULY.', 'AUGUST.', 'SEPTEMBER.', 'OCTOBER.', 'NOVEMBER.', 'DECEMBER.',
                    'Jan,', 'Feb,', 'Mar,', 'Apr,', 'May,', 'Jun,', 'Jul,', 'Aug,',
                    'Sep,', 'Oct,', 'Nov,', 'Dec,', 'January,', 'February,', 'March,', 'April,', 'June,', 'July,',
                    'August,', 'September,', 'October,', 'November,', 'December,', 'JANUARY,', 'FEBRUARY,', 'MARCH,',
                    'APRIL,', 'MAY,', 'JUNE,', 'JULY,', 'AUGUST,', 'SEPTEMBER,', 'OCTOBER,', 'NOVEMBER,', 'DECEMBER,'}
    months_in_number = {'.01.', '.02.', '.03.', '.04.', '.05.', '.06.', '.07.', '.08.', '.09.', '.10.', '.11.', '.12.',
                        '.1.', '.2.', '.3.', '.4.', '.5.', '.6.', '.7.', '.8.', '.9.'}

    def __init__(self, index, sw_path, stem_bool, cities):
        self.parser_index = index
        self.stop_words = set(open(sw_path).read().split())
        self.terms_dictionary = {}
        self.stem_bool = stem_bool
        self.cities = cities
        global docs_dictionary
        # docs_dictionary = {}

    def parse(self, docs_texts, docs_properties):
        # print("Start Parsing")
        global number_of_docs
        global total_length_of_docs
        for doc_name in docs_texts:
            tokens = self.get_tokens(docs_texts[doc_name]['text'])
            (doc_terms, max_tf, max_term, doc_total_length) = self.parse_document(doc_name, tokens)
            self.save_doc_data(doc_name, doc_terms, docs_properties[doc_name], max_tf, max_term, doc_total_length)
            number_of_docs += 1
            total_length_of_docs += doc_total_length
        self.save_parser_data()

    @staticmethod
    def get_tokens(doc_text):
        tokens = doc_text.split(' ')
        return [value for value in tokens if value != '']

    def parse_document(self, doc_name, tokens):
        index = 0
        doc_length = 0
        term_index = 0
        doc_terms = {}
        max_tf = 1
        max_term = ''
        terms_to_add = []
        terms_to_query = []

        while index < len(tokens):
            doc_length += len(terms_to_add)
            terms_to_add = []
            token = str(tokens[index])

            if (token in self.stop_words or token.lower() in self.stop_words
                    and (token != 'between' and token != 'Between')):
                index += 1

            else:
                # If token ends with "." or "," delete last char
                if (len(token) > 1 and
                        (token[len(token) - 1] == "." or token[len(token) - 1] == "," or token[len(token) - 1] == "-")):
                    token = token[:-1]

                if token.count('.') > 1 or token.count('-') > 1:
                    terms_to_add.append(token)
                    index += 1

                elif token[0].isalpha():
                    (terms_to_add, index) = self.word_parser(tokens, token, index)
                elif token[0].isdigit():
                    (terms_to_add, index) = self.number_parser(tokens, token, index)
                elif token[0] == "$" and len(token) > 1:
                    (terms_to_add, index) = self.money_parser(tokens, token, index)
                elif token[0] == "%" and len(token) > 1:
                    (terms_to_add, index) = self.percent_parser(token, index)
                else:
                    terms_to_add.append(token)
                    index += 1
                if not doc_name.__contains__("quer"):
                    (doc_terms, term_index, max_tf, max_term) =\
                        self.add_to_dictionaries(terms_to_add, doc_terms, doc_name, term_index, max_tf, max_term)
                else:
                    for word in terms_to_add:
                        terms_to_query.append(word)
        if doc_name.__contains__("quer"):
            return terms_to_query
        else:
            return doc_terms, max_tf, max_term, doc_length

    def add_to_dictionaries(self, terms_to_add, doc_terms, doc_name, term_index, max_tf, max_term):

        #   df (num of docs) = size(list of docs)

        for new_term in terms_to_add:
            new_term = str(new_term)
            if self.stem_bool and new_term.isalpha():
                new_term = self.stemmer.stemWord(new_term)

            if new_term != '':
                # numbers
                if new_term[0].isdigit():
                    new_term = new_term.lower()
                    if new_term not in self.terms_dictionary:
                        self.terms_dictionary[new_term] = {'docs': [doc_name], 'df': 1}
                        doc_terms[new_term] = {'tf': 1, 'indexes': [term_index]}

                    else:
                        if new_term in doc_terms:
                            doc_terms[new_term]['tf'] += 1
                            if max_tf < doc_terms[new_term]['tf']:
                                max_tf = doc_terms[new_term]['tf']
                                max_term = new_term
                            doc_terms[new_term]['indexes'].extend([term_index])
                        else:
                            self.terms_dictionary[new_term]['docs'].extend([doc_name])
                            self.terms_dictionary[new_term]['df'] = len(self.terms_dictionary[new_term]['docs'])
                            doc_terms[new_term] = {'tf': 1, 'indexes': [term_index]}

                # words
                else:

                    term_lower = new_term.lower()
                    term_upper = new_term.upper()

                    if new_term[0].isupper():
                        if term_lower in self.terms_dictionary:
                            if doc_name not in self.terms_dictionary[term_lower]['docs']:
                                self.terms_dictionary[term_lower]['docs'].append(doc_name)
                                self.terms_dictionary[term_lower]['df'] = len(self.terms_dictionary[term_lower]
                                                                              ['docs']) + 1
                            if term_lower not in doc_terms:
                                doc_terms[term_lower] = {'tf': 1, 'indexes': [term_index]}
                            else:
                                doc_terms[term_lower]['tf'] += 1
                                if max_tf < doc_terms[term_lower]['tf']:
                                    max_tf = doc_terms[term_lower]['tf']
                                    max_term = new_term
                                doc_terms[term_lower]['indexes'].append(term_index)
                        else:
                            if term_upper in self.terms_dictionary:
                                if term_upper in doc_terms:
                                    doc_terms[term_upper]['tf'] += 1
                                    if max_tf < doc_terms[term_upper]['tf']:
                                        max_tf = doc_terms[term_upper]['tf']
                                        max_term = new_term
                                    doc_terms[term_upper]['indexes'].append(term_index)
                                else:
                                    self.terms_dictionary[term_upper]['docs'].extend([doc_name])
                                    self.terms_dictionary[term_upper]['df'] = len(self.terms_dictionary
                                                                                  [term_upper]['docs'])
                                    doc_terms[term_upper] = {'tf': 1, 'indexes': [term_index]}
                            else:
                                self.terms_dictionary[term_upper] = {'docs': [doc_name], 'df': 1}
                                doc_terms[term_upper] = {'tf': 1, 'indexes': [term_index]}
                    elif new_term[0].islower():
                        if term_lower not in self.terms_dictionary:
                            if term_upper in self.terms_dictionary:
                                temp_docs = self.terms_dictionary[term_upper]['docs']
                                temp_df = self.terms_dictionary[term_upper]['df']
                                tmp_tf_per_doc = 'none'
                                if 'tf_per_doc' in self.terms_dictionary[term_upper].keys():
                                    tmp_tf_per_doc = self.terms_dictionary[term_upper]['tf_per_doc']
                                self.terms_dictionary.pop(term_upper)
                                if tmp_tf_per_doc != 'none':
                                    self.terms_dictionary[term_lower] = {'docs': temp_docs,
                                                                         'df': temp_df + 1,
                                                                         'tf_per_doc': tmp_tf_per_doc}
                                else:
                                    self.terms_dictionary[term_lower] = {'docs': temp_docs, 'df': temp_df}
                                if doc_name not in self.terms_dictionary[term_lower]['docs']:
                                    self.terms_dictionary[term_lower]['docs'].extend([doc_name])
                                    self.terms_dictionary[term_lower]['tf'] = len(self.terms_dictionary
                                                                                  [term_lower]['docs'])
                                if term_upper in doc_terms:
                                    temp_tf = doc_terms[term_upper]['tf'] + 1
                                    if max_tf < temp_tf:
                                        max_tf = temp_tf
                                        max_term = new_term
                                    temp_indexes = doc_terms[term_upper]['indexes']
                                    doc_terms.pop(term_upper)
                                    temp_indexes.append(term_index)
                                    doc_terms[term_lower] = {'tf': temp_tf, 'indexes': temp_indexes}
                                else:
                                    doc_terms[term_lower] = {'tf': 1, 'indexes': [term_index]}
                            else:
                                self.terms_dictionary[term_lower] = {'docs': [doc_name], 'df': 1}
                                doc_terms[term_lower] = {'tf': 1, 'indexes': [term_index]}
                        else:
                            if term_lower in doc_terms:
                                doc_terms[term_lower]['tf'] += 1
                                if max_tf < doc_terms[term_lower]['tf']:
                                    max_tf = doc_terms[term_lower]['tf']
                                    max_term = new_term
                                doc_terms[term_lower]['indexes'].extend([term_index])
                            else:
                                self.terms_dictionary[term_lower]['docs'].extend([doc_name])
                                self.terms_dictionary[term_lower]['df'] = len(self.terms_dictionary[term_lower]['docs'])
                                doc_terms[term_lower] = {'tf': 1, 'indexes': [term_index]}

            term_index += 1
        return doc_terms, term_index, max_tf, max_term

    def number_parser(self, tokens, token, index):
        new_terms = []

        # If token is not in good format, simply add it as is
        if token.count('.') > 1 or token.count('-') > 1 or not self.legal_number(token):
            new_terms.append(token)
            index += 1

        # Range:
        elif token.__contains__('-'):
            (new_terms, index) = self.number_parser_range(tokens, token, index)

        # Percentage:
        elif (index < len(tokens) - 1
              and self.percentage_labels.__contains__(tokens[index + 1])):
            (new_terms, index) = self.number_parser_percentage(tokens, token, index)

        # Date:
        elif ((index < len(tokens) - 1 and
               self.months_names.__contains__(tokens[index + 1]))
              or (index > 0 and self.months_names.__contains__(tokens[index - 1]))):
            (new_terms, index) = self.number_parser_date(tokens, token, index)

        # Price:
        elif ((index < len(tokens) - 1 and tokens[index + 1] in self.dollar_names)
              or (index < len(tokens) - 2 and tokens[index + 1] in self.price_number_names
                  and (tokens[index + 2] in self.dollar_names))
              or (index < len(tokens) - 3 and tokens[index + 1] in self.price_number_names
                  and tokens[index + 2] == "U.S." and (tokens[index + 3] in self.dollar_names))):
            (new_terms, index) = self.number_parser_price(tokens, token, index)

        # Regular Number:
        elif (self.contains_only_numbers(token) or
              (type(token) is str and (token.__contains__(',') or token.__contains__('.')))):
            (new_terms, index) = self.number_parser_regular(tokens, token, index)
        else:
            new_terms.append(tokens[index])
            index += 1
        return new_terms, index

    @staticmethod
    def legal_number(token):
        for char in token:
            if not char.isdigit() and char not in ['-', '.', ',']:
                return False
        return True

    @staticmethod
    def legal_money(token):
        for char in token:
            if not char.isdigit() and char not in ['.', ',']:
                return False
        return True

    def number_parser_range(self, tokens, token, index):
        new_terms = []

        month = ""
        flags = dict.fromkeys(["date", "percent", "money"], False)
        range_parts = token.split('-')

        if self.range_parts_are_numeric(range_parts):
            if index > 0:
                if tokens[index - 1] in self.months_names:
                    flags["date"] = True
                    month = tokens[index - 1]
            if index + 1 < len(tokens):
                if tokens[index + 1] in self.months_names:
                    flags["date"] = True
                    month = tokens[index + 1]
                    index += 1
                elif tokens[index + 1] in self.percentage_labels:
                    flags["percent"] = True
                    index += 1
                elif (tokens[index + 1] == "dollar" or tokens[index + 1] == "dollar."
                      or tokens[index + 1] == "Dollar" or tokens[index + 1] == "Dollar."):
                    flags["money"] = True
                    index += 1
                elif (tokens[index + 1] == "U.S." and index + 2 < len(tokens)
                      and tokens[index + 2] in self.price_number_names):
                    flags["money"] = True
                    index += 2

        final_new_terms = []
        part_index = 0

        for part in range_parts:
            new_terms.append(part)
            if flags["date"]:
                new_terms.append(month)
                (new_final_term, part_index) = self.number_parser_date(new_terms, part, part_index)
                final_new_terms.extend(new_final_term)
            elif flags["percent"]:
                new_terms.append("percent")
                (new_final_term, part_index) = self.number_parser_percentage(new_terms, part, part_index)
                final_new_terms.extend(new_final_term)
            elif flags["money"]:
                new_terms.append("dollars")
                (new_final_term, part_index) = self.number_parser_price(new_terms, part, part_index)
                final_new_terms.extend(new_final_term)
            final_new_terms.append(part)
        final_new_terms.append(token)
        return final_new_terms, index + 1

    @staticmethod
    def contains_letter(a):
        for char in a:
            if char.isalpha():
                return True
        return False

    @staticmethod
    def contains_only_numbers(a):
        for char in a:
            if not char.isdigit():
                return False
        return True

    @staticmethod
    def range_parts_are_numeric(range_parts):
        for part in range_parts:
            if type(part) is not int:
                return False
        return True

    def number_parser_percentage(self, tokens, token, index):
        # 30% % ... / 30 percent ... / 30 percentage ...
        new_terms = []
        if tokens[index + 1] in self.percentage_labels:
            index += 1
            token += "%"
        new_terms.append(token)
        # return the new list terms and the index after the percent word
        return new_terms, index + 1

    def number_parser_date(self, tokens, token, index):
        # 14 May, June 12
        new_terms = []
        month_change = ""
        month_position = 0
        pass_over = False
        # delete those delimiters
        if token[0].isdigit():
            # April 18,September 21
            if index - 1 >= 0 and self.months_names.__contains__(tokens[index - 1]):
                month_change = self.change_month(tokens[index - 1])
                month_position = index - 1
            # 14 June,18 July
            elif index + 1 < len(tokens) and self.months_names.__contains__(tokens[index + 1]):
                month_change = self.change_month(tokens[index + 1])
                month_position = index + 1
        if type(token) is str and (token.__contains__("-") or token.__contains__('.') or not token.isdigit()):
            pass_over = True
        # check if this is legal year
        elif type(token) is str and token.__contains__(','):
            temp_term = token.replace("'", '')
            if 0 < temp_term <= 2018:
                token = temp_term
            else:
                pass_over = True
        else:
            pass
        # check if the token is year or day
        if pass_over:
            new_terms.append(token)
            pass
        elif 3000 >= int(token) > 31:
            new_term = token + "-" + month_change
            new_terms.append(new_term)
        elif 0 < int(token) <= 31:
            if int(token) < 10:
                token = '0' + token
            new_term = month_change + "-" + token
            new_terms.append(new_term)
        else:
            pass
        if month_position >= index:
            index += 1
        return new_terms, index + 1

    def number_parser_price(self, tokens, token, index):
        new_terms = []
        if ',' in token:
            num = float(token.replace(',', ''))
            if 1000000 > num >= 1000 and num % 1000 == 0:
                num = int(num)
            elif 1000000000 > num >= 1000000 and num % 1000000 == 0:
                num = int(num)
            elif 1000000000000 > num >= 1000000000 and num % 1000000000 == 0:
                num = int(num)
        elif type(token) is float:
            num = float(token)
        elif type(token) is str and '.' in token:
            num = float(token)
        elif float(token) % 1000 != 0 and float(token) > 1000:
            num = float(token)
        else:
            num = int(token)
        if index + 1 < len(tokens):
            if tokens[index + 1] in self.dollar_names:
                index += 1
            else:
                if tokens[index + 1] in ['k', 'thousand', 'Thousand']:
                    num *= 1000
                elif tokens[index + 1] in ['m', 'million', 'Million']:
                    num *= 1000000
                elif tokens[index + 1] in ['bn', 'billion', 'Billion']:
                    num *= 1000000000
                elif tokens[index + 1] in ['tr', 'trillion', 'Trillion']:
                    num *= 1000000000000
                if tokens[index + 2] == 'U.S.':
                    index += 1
                index += 2
        if num >= 1000000:
            if num % 1000000 == 0:
                num = int(num)
            if type(num) is int:
                new_terms.append(str(int(num / 1000000)) + ' M Dollars')
            else:
                new_terms.append(str(num / 1000000) + ' M Dollars')

        else:
            new_terms.append(token + ' Dollars')
        return new_terms, index + 1

    def number_parser_regular(self, tokens, token, index):
        new_terms = []
        if index < len(tokens) - 1 and tokens[index + 1] in self.regular_number_names:
            new_terms.append(self.term_word(tokens, token, index))
            index += 1
        elif token.count('.') > 1 or token.count('-') > 1 \
                or (not self.contains_only_numbers(token) and (not token.__contains__('-'))):
            new_terms.append(token)
        else:
            new_terms.append(self.term_number(token))
        return new_terms, index + 1

    @staticmethod
    def change_month(month):
        month_in_number = ''
        if month in ['Jan', 'January', 'JANUARY', 'Jan.', 'January.', 'JANUARY.']:
            month_in_number = '01'
        elif month in ['Feb', 'February', 'FEBRUARY', 'Feb.', 'February.', 'FEBRUARY.']:
            month_in_number = '02'
        elif month in ['Mar', 'March', 'MARCH', 'Mar.', 'March.', 'MARCH.']:
            month_in_number = '03'
        elif month in ['Apr', 'April', 'APRIL', 'Apr.', 'April.', 'APRIL.']:
            month_in_number = '04'
        elif month in ['May', 'MAY', 'May.', 'MAY.']:
            month_in_number = '05'
        elif month in ['Jun', 'June', 'JUNE', 'Jun.', 'June.', 'JUNE.']:
            month_in_number = '06'
        elif month in ['Jul', 'July', 'JULY', 'Jul.', 'July.', 'JULY.']:
            month_in_number = '07'
        elif month in ['Aug', 'August', 'AUGUST', 'Aug.', 'August.', 'AUGUST.']:
            month_in_number = '08'
        elif month in ['Sep', 'September', 'SEPTEMBER', 'Sep.', 'September.', 'SEPTEMBER.']:
            month_in_number = '09'
        elif month in ['Oct', 'October', 'OCTOBER', 'Oct.', 'October.', 'OCTOBER.']:
            month_in_number = '10'
        elif month in ['Nov', 'November', 'NOVEMBER', 'Nov.', 'November.', 'NOVEMBER.']:
            month_in_number = '11'
        elif month in ['Dec', 'December', 'DECEMBER', 'Dec.', 'December.', 'DECEMBER.']:
            month_in_number = '12'
        return month_in_number

    @staticmethod
    def term_number(term):
        if ',' in term:
            num = float(term.replace(',', ''))
            if 1000000 > num >= 1000 and num % 1000 == 0:
                num = int(num)
            elif 1000000000 > num >= 1000000 and num % 1000000 == 0:
                num = int(num)
            elif 1000000000000 > num >= 1000000000 and num % 1000000000 == 0:
                num = int(num)
        elif type(term) is float:
            num = float(term)
        elif type(term) is str and '.' in term:
            num = float(term)
        elif float(term) % 1000 != 0 and float(term) > 1000:
            num = float(term)
        else:
            num = int(term)
        if 1000 <= num < 1000000:
            if type(num) is int:
                new_term = int(num / 1000)
            else:
                new_term = (num / 1000)
            new_term_str = new_term.__str__()
            new_term_str += 'K'
        elif 1000000 <= num < 1000000000:
            if type(num) is int:
                new_term = int(num / 1000000)
            else:
                new_term = num / 1000000
            new_term_str = new_term.__str__()
            new_term_str += 'M'
        elif 1000000000 <= num:
            if type(num) is int:
                new_term = int(num / 1000000000)
            else:
                new_term = num / 1000000000
            new_term_str = new_term.__str__()
            new_term_str += 'B'
        else:
            new_term_str = num.__str__()
        return new_term_str

    # handle price of format $10,000 or $10 million
    def money_parser(self, tokens, token, index):
        new_temp_terms = []
        token = token[1:len(token)]
        if not self.legal_money(token):
            return [token], index + 1
        # num = token.replace(',', '')
        new_temp_terms.append(token)
        if index + 1 < len(tokens) and tokens[index + 1] in self.regular_number_names:
            new_temp_terms.append(self.clean_number_name(tokens[index + 1]))
        new_temp_terms.append("Dollars")
        (new_terms, new_index) = self.number_parser_price(new_temp_terms, token, 0)
        return new_terms, index + len(new_temp_terms) - 1

    @staticmethod
    def clean_number_name(token):
        while token[-1:] == '.' or token[-1:] == ',' or token[-1:] == '-':
            token = token[:-1]
        return token

    @staticmethod
    def percent_parser(token, index):
        new_terms = []
        temp_token = token
        token = token[1:len(token)]
        if type(token) is str and (token.count('%') > 1 or token.__contains__('$') or token.count('.') > 1
                                   or token.count('-') >= 1 or token.__contains__('/')):
            return [temp_token], index + 1
        if token.isdigit():
            temp_token = str(token) + "%"
        new_terms.append(temp_token)
        return new_terms, index + 1

    @staticmethod
    def term_word(tokens, token, index):
        temp_str = ""
        temp_num = token
        if type(token) is str and token.__contains__(','):
            temp_num = token.replace(",", '')
        if (tokens[index + 1] == "Thousand" or tokens[index + 1] == "Thousand."
                or tokens[index + 1] == "thousand" or tokens[index + 1] == "thousand."):
            temp_str = temp_num.__str__() + 'K'
        elif (tokens[index + 1] == "Million" or tokens[index + 1] == "Million."
              or tokens[index + 1] == "million" or tokens[index + 1] == "million."):
            temp_str = temp_num.__str__() + 'M'
        elif (tokens[index + 1] == "Billion" or tokens[index + 1] == "Billion."
              or tokens[index + 1] == "billion" or tokens[index + 1] == "billion."):
            temp_str = temp_num.__str__() + 'B'
        elif (tokens[index + 1] == "Trillion" or tokens[index + 1] == "Trillion."
              or tokens[index + 1] == "trillion" or tokens[index + 1] == "trillion."):
            num = token.replace(',', '')
            temp_num = float(num) * 1000
            temp_str = temp_num.__str__() + 'B'
        return temp_str

    def word_parser(self, tokens, token, index):
        new_terms = []
        if token == 'between' or token == 'Between':
            if (index < len(tokens) - 1 and index < len(tokens) - 2 and tokens[index + 1][0].isdigit()
                    and index < len(tokens) - 3 and tokens[index + 2] == 'and'
                    and index < len(tokens) - 4 and tokens[index + 3][0].isdigit()):
                range_token = tokens[index + 1] + '-' + tokens[index + 3]
                (new_terms, temp_index) = self.number_parser_range([range_token], range_token, 0)
                index += temp_index + 2
        elif token.__contains__('-'):
            (new_terms, a) = self.number_parser_range([token], token, 0)
            for j in range(len(new_terms)):
                # added first condition
                if new_terms[j] != '' and new_terms[j][0].isupper():
                    new_terms[j] = new_terms[j].lower()
        elif token in self.months_names and index + 1 < len(tokens)\
                and len(tokens[index + 1]) > 0 and tokens[index + 1][0].isdigit():
            pass
        else:
            new_terms.append(token)
        return new_terms, index + 1

    @staticmethod
    def get_doc_entities(doc_terms):
        i = 0
        entities = []
        for term_tuple in sorted(doc_terms.iteritems(), key=lambda (x, y): y['tf'], reverse=True):
            if term_tuple[0].isupper():
                entities.append(str(term_tuple[0]) + ": tf = " + str(doc_terms[term_tuple[0]]['tf']))
                i += 1
                if i == 5:
                    return entities
        return entities

    def save_doc_data(self, doc_name, doc_terms, doc_properties, max_tf, max_term, doc_length):
        # id:
        #   doc_name
        # values:
        #   max_tf of term
        #   the max term
        #   num of terms
        #   doc_city
        #   doc_length
        global docs_dictionary

        doc_entities = self.get_doc_entities(doc_terms)

        docs_dictionary[doc_name] = {'max_tf': max_tf,
                                     'max_term': max_term,
                                     'num_of_terms': len(doc_terms.keys()),
                                     'doc_city': doc_properties['city'],
                                     'doc_length': doc_length,
                                     'entities': doc_entities}
        for term in doc_terms:

            # { city :                                                           }
            #           { doc_name :                                         }
            #                         { tf : 3 , indexes : [ 2 , 5 , 9 ] }

            if term.upper() in self.cities:
                if term.upper() not in cities_posting:
                    cities_posting[term.upper()] = {doc_name: doc_terms[term]}
                else:
                    cities_posting[term.upper()][doc_name] = doc_terms[term]
            if term.upper() in self.terms_dictionary:
                if 'tf_per_doc' not in self.terms_dictionary[term.upper()].keys():
                    self.terms_dictionary[term.upper()]['tf_per_doc'] = {doc_name: doc_terms[term]['tf']}
                else:
                    tmp_dict = {doc_name: doc_terms[term.upper()]['tf']}
                    self.terms_dictionary[term.upper()]['tf_per_doc'].update(tmp_dict)
            elif term.lower() in self.terms_dictionary:
                if 'tf_per_doc' not in self.terms_dictionary[term.lower()].keys():
                    self.terms_dictionary[term.lower()]['tf_per_doc'] = {doc_name: doc_terms[term]['tf']}
                else:
                    tmp_dict = {doc_name: doc_terms[term.lower()]['tf']}
                    self.terms_dictionary[term.lower()]['tf_per_doc'].update(tmp_dict)
            else:
                if 'tf_per_doc' not in self.terms_dictionary[term.lower()].keys():
                    self.terms_dictionary[term.lower()]['tf_per_doc'] = {doc_name: doc_terms[term]['tf']}
                else:
                    tmp_dict = {doc_name: doc_terms[term]['tf']}
                    self.terms_dictionary[term.lower()]['tf_per_doc'].update(tmp_dict)

    def save_parser_data(self):
        global docs_dictionary
        # -------- terms_dictionary --------
        # id:
        #   term
        # values:
        #   df (num of docs) = size(list of docs)           number
        #   tf_per_doc (num of appearances in each doc)     {key:doc_name, value:number}
        #   list of docs                                    [doc1, doc2, ...]

        # -------- docs_dictionary --------
        # id:
        #   doc_name
        # values:
        #   max_tf of term                                  number
        #   term with max_tf                                string
        #   num of terms                                    number
        #   doc_city                                        string
        #   doc_length                                      number
        ending = ''
        if self.stem_bool:
            ending = '_with_stemming'
        terms_file_name = (('parser_%d_terms' % self.parser_index) + ending + '.txt')
        # docs_file_name = (('parser_%d_docs' % self.parser_index) + ending + '.txt')
        open(terms_file_name, "w")
        terms_file = open(terms_file_name, "ab")
        for key in sorted(self.terms_dictionary.keys(), key=str.lower):
            str_df = str(self.terms_dictionary[key]['df'])
            str_tf_per_doc = str(self.terms_dictionary[key]['tf_per_doc']).replace(' ', '')\
                if 'tf_per_doc' in self.terms_dictionary[key].keys() else ''
            terms_file.write("<" + key + "~" + str_df + "~" + str_tf_per_doc + ">\n")
        terms_file.write("@@@")
        pass


class Index:
    stemmingB = False
    global main_dictionary

    def __init__(self):
        self.stemmingB = False

    def set_stemming_bool(self, bool):
        self.stemmingB = bool

    # Merge two files into one output file
    def merge_two_posting_files(self, file_1_path, file_2_path, index):
        i1 = 1
        i2 = 1
        # output_file_lines = []
        ending = ''
        if self.stemmingB:
            ending = '_with_stemming'
        open((('merge%d' % index) + ending + '.txt'), 'w')
        output_file = open((('merge%d' % index) + ending + '.txt'), 'ab')
        parser1_term_line = linecache.getline(file_1_path, i1)
        parser2_term_line = linecache.getline(file_2_path, i2)
        while not parser1_term_line.__contains__('@') and not parser2_term_line.__contains__('@'):
            parser1_term = parser1_term_line.split('<')[1].split('~')[0]
            parser2_term = parser2_term_line.split('<')[1].split('~')[0]
            if parser1_term.lower() < parser2_term.lower():
                output_file.write(parser1_term_line)
                # output_file_lines.append(parser1_term_line)
                i1 += 1
                parser1_term_line = linecache.getline(file_1_path, i1)
            elif parser1_term.lower() > parser2_term.lower():
                output_file.write(parser2_term_line)
                # output_file_lines.append(parser2_term_line)
                i2 += 1
                parser2_term_line = linecache.getline(file_2_path, i2)
            else:   # are equal
                tmp_term = parser1_term if (parser1_term.isupper()
                                            and parser2_term.isupper()) else parser1_term.lower()
                tmp_df = str(int(parser1_term_line.split('~')[1]) + int(parser2_term_line.split('~')[1]))
                tmp_tf_per_doc = '{' + parser1_term_line.split('{')[1].split('}')[0] + ',' +\
                                 parser2_term_line.split('{')[1].split('}')[0] + '}'
                tmp_output_str = '<' + tmp_term + '~' + tmp_df + '~' + tmp_tf_per_doc + '>\n'
                output_file.write(tmp_output_str)
                # output_file_lines.append(tmp_output_str)
                i1 += 1
                i2 += 1
                parser1_term_line = linecache.getline(file_1_path, i1)
                parser2_term_line = linecache.getline(file_2_path, i2)
        if parser1_term_line.__contains__('@'):
            i2 += 1
            while not parser2_term_line.__contains__('@'):
                output_file.write(parser2_term_line)
                # output_file_lines.append(parser2_term_line)
                parser2_term_line = linecache.getline(file_2_path, i2)
                i2 += 1
        else:
            i1 += 1
            while not parser1_term_line.__contains__('@'):
                output_file.write(parser1_term_line)
                # output_file_lines.append(parser1_term_line)
                parser1_term_line = linecache.getline(file_1_path, i1)
                i1 += 1
        # for line in output_file_lines:
        #     output_file.write(line)
        output_file.write('@@@')
        return ('merge%d' % index) + ending + '.txt'

    # Function will create the indexed dictionary for the posting
    def build_index_dictionary(self, save_path, final_merged_posting_file_path):
        global main_dictionary
        ending = ''
        if self.stemmingB:
            ending = '_with_stemming'
        open(save_path + '/index%s.txt' % ending, 'w')
        index_dictionary_file = open(save_path + '/index%s.txt' % ending, 'ab')
        i = 1
        line = linecache.getline(final_merged_posting_file_path, i)
        while not line.__contains__('@'):
            tmp_corpus_tf = 0
            line_split_tilda = line.split('~')
            tmp_term = line_split_tilda[0].split('<')[1]
            tmp_term_df = int(line_split_tilda[1])
            line_split_colon = line.split(':')[1:]
            for a in range(0, len(line_split_colon) - 1):
                tmp_corpus_tf += int((line_split_colon[a]).split(',')[0])
            tmp_corpus_tf += int((line_split_colon[len(line_split_colon) - 1]).split('}')[0])
            tmp_posting_line_index = i - 1
            index_dictionary_file.write(tmp_term + '~' + str(tmp_posting_line_index) + '~' + str(tmp_corpus_tf) + '\n')
            main_dictionary[tmp_term] = {'post_index': str(tmp_posting_line_index),
                                         'tf': str(tmp_corpus_tf)}
            i += 1
            line = linecache.getline(final_merged_posting_file_path, i)
        index_dictionary_file.write('@@@')


# Both Docs and Terms dictionaries are loaded (global)
class Searcher:
    # Assuming both Docs and Terms dictionaries are loaded (global)

    # 'I love white chocolate'
    query = ''

    # {'I':                        , 'love':             ...
    #       {'doc1': 5, 'doc2': 4}           {'doc2': 3} ...
    query_terms = {}

    # {'doc1', 'doc2', 'doc3', ...}
    docs_containing_current_terms = {}

    semantic = False

    def __init__(self, q, semantic):
        self.query = q
        self.query_terms = {}
        self.semantic = semantic
        for qi in q.split(' '):
            # self.query_terms[qi] = {}
            # if semantic:
                # synonyms = set
                # for syn in wordnet.synsets(qi):
                #     for l in syn.lemmas():
                #         synonym = str(l.name())
                #         if synonym not in synonyms and synonyms.__sizeof__() < 5:
                #             if synonym in main_dictionary.keys():
                #                 print(synonym)
                #                 synonyms[synonym] = 1
                #                 self.query_terms[synonym] = {}
                #
                #
            if semantic:
                # make api call to: "api.datamuse.com/words?ml=" + qi
                response = requests.get("https://api.datamuse.com/words?ml=" + qi)
                words_dict_list = json.loads(response.text)
                synonym_list = []
                word_index = 0
                synonym_index = 0
                while synonym_index < 5 or word_index > len(words_dict_list):
                    word_dict = words_dict_list[word_index]
                    if 'syn' in word_dict["tags"]:
                        synonym = str(word_dict["word"])
                        if synonym in main_dictionary.keys():
                            synonym_list.append(synonym)
                            self.query_terms[synonym.lower()] = {}
                            self.query_terms[synonym.upper()] = {}
                            synonym_index += 1
                    word_index += 1
            qi_upper = str(qi).upper()
            qi_lower = str(qi).lower()
            if qi_upper in main_dictionary.keys():
                self.query_terms[qi_upper] = {}
            if qi_lower in main_dictionary.keys():
                self.query_terms[qi_lower] = {}
        docs_containing_current_terms = {}
        docs_containing_current_terms.clear()

    def find_docs_containing_current_terms(self):
        global main_dictionary
        global docs_dictionary
        global g
        docs_containing_current_terms = {}
        docs_containing_current_terms.clear()
        for term in self.query_terms.keys():
            if term not in main_dictionary.keys():
                continue
            # Get the index of the term in the posting
            term_post_index = int(main_dictionary[term]['post_index']) + 1
            # Get the term line in the posting file
            term_post_line = linecache.getline(g.entry_Save_Path.get() + "/posting.txt", term_post_index)
            # Get the term docs from the posting
            term_docs = ast.literal_eval((term_post_line.split('~')[2])[:-2])
            # Get the term IDF
            term_idf = ast.literal_eval(term_post_line.split('~')[1])
            # Keep the term with and his frequencies in each doc
            self.query_terms[term] = {'idf': term_idf, 'docs': term_docs}
            # Keep all docs that contain terms from the query
            for term_doc in term_docs.keys():
                self.docs_containing_current_terms[term_doc] = ''


class Ranker:
    relevant_docs = {}
    query_terms = {}
    ranked_docs = ()
    k1 = 1.2
    b = 0.75

    def __init__(self, docs, terms):
        self.relevant_docs = docs
        self.query_terms = terms
        self.ranked_docs = ()

    def rank(self):
        global main_dictionary
        global docs_dictionary
        global avgdl
        global number_of_docs
        max_score = 0
        for doc in self.relevant_docs.keys():
            if doc == 'FT941-9999':
                print('FT941-9999')
            score = 0.0
            # Calculate the document score based on BM25
            for term in self.query_terms.keys():
                term_idf = self.query_terms[term]['idf']
                if doc in self.query_terms[term]['docs'].keys():
                    term_doc_tf = self.query_terms[term]['docs'][doc]
                else:
                    term_doc_tf = 0
                len_of_doc = docs_dictionary[doc]['doc_length']
                score += (float(term_idf) *
                          ((float(term_doc_tf) * (self.k1 + 1)) /
                           (float(term_doc_tf) + (self.k1 * (1 - self.b +
                                                             (self.b * float(len_of_doc) / float(avgdl)))))))
            if max_score < score:
                max_score = score
            self.relevant_docs[doc] = score
        for doc in self.relevant_docs.keys():
            self.relevant_docs[doc] = (float(self.relevant_docs[doc]) / max_score)
        self.ranked_docs = sorted(self.relevant_docs.items(), key=operator.itemgetter(1), reverse=True)
        tmp_ranked_docs = []
        if len(self.ranked_docs) > 0:
            i = 0
            minimum_score = 0.5
            current_score = self.ranked_docs[i][1]
            while current_score > minimum_score and i < 50 and i < len(self.ranked_docs):
                tmp_ranked_docs.append(self.ranked_docs[i])
                i += 1
        self.ranked_docs = tmp_ranked_docs


# ---------------- MAIN ---------------- #


# ------ Concurrent Functions ------

# Function for the parsing threads
# def concurrent_parsing(rf, sw_path, index):
#     (docs_texts, docs_properties) = rf.read()
#     parser = Parse(index, sw_path, stemming_bool, read_file.cities)
#     parser.parse(docs_texts, docs_properties)
#     print('Done Parse %d' % index)

# # Function for the indexing threads
# def concurrent_indexing(self):
#     for i in range(0, self.num_of_parser_files, 2):
#         self.merge_two_parser_files('parser_%d_terms.txt' % i, 'parser_%d_terms.txt' % (i + 1), iteration_index)
#         pass
#
# # Main indexing function
# def indexing():
#     for i in range(0, self.num_of_parser_files, 2):
#         .merge_two_parser_files('parser_%d_terms.txt' % i, 'parser_%d_terms.txt' % (i + 1), iteration_index)
#         pass

if __name__ == '__main__':

    print('START!')

    # model = KeyedVectors.load_word2vec_format('GoogleNews-vectors-negative300.bin.gz', binary=True)
    # print(model.most_similar("simple"))

    main_index = Index()
    main_dictionary = {}
    docs_dictionary = {}

    cities_posting = {}
    number_of_docs = 0
    total_length_of_docs = 0
    avgdl = 0

    root = Tk()
    g = GUI(root)
    root.mainloop()


# api.data
