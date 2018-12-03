# coding=utf-8
# from multiprocessing.sharedctypes import synchronized
# from threading import Thread
# from multiprocessing import Process
from os import listdir
from tkinter import *
import tkinter.messagebox
from tkinter import filedialog
from nltk import SnowballStemmer


class GUI:

    def __init__(self, root):
        self.topFrame = Frame(root)
        root.title("Boogle")
        root.geometry('300x275+500+150')
        root.resizable(0, 0)
        # self.background_image = \
        #     tkinter.PhotoImage(file="C:/Users/user/PycharmProjects/YankaleProject/resources/background.png")
        # self.background_label = Label(root, image=self.background_image)
        # self.background_label.grid()
        self.text_Resources_Path = Label(root, text="Resources Path:")
        self.text_Save_Path = Label(root, text="Save Path:")
        self.entry_Resources_Path = Entry(root)
        self.entry_Save_Path = Entry(root)
        self.button1 = Button(text="Browse...", fg='black', command=lambda: self.browse_folder())
        self.button2 = Button(text="Browse...", fg='black', command=lambda: self.browse_save_file())
        self.button2.grid(row=1, column=2)
        self.text_Resources_Path.grid(row=0)
        self.text_Save_Path.grid(row=1)
        self.entry_Resources_Path.grid(row=0, column=1)
        self.entry_Save_Path.grid(row=1, column=1)
        self.button1.grid(row=0, column=2)
        self.button2.grid(row=1, column=2)
        self.start_button = Button(text="Start", fg='black', command=lambda: self.start_work())
        self.start_button.grid(row=3, column=1)
        self.var = tkinter.IntVar()
        self.stemmerLabel = Checkbutton(root, text="stemmer", variable=self.var)
        self.stemmerLabel.grid(row=3, column=0)
        self.language = Label(root, text="Language:")
        self.language.grid(row=4, column=0)
        self.language_list = Listbox(root, width=10, height=5)
        self.language_list.insert(1, 'English')
        self.language_list.insert(2, 'Hebrew')
        self.language_list.insert(3, 'Chinese')
        self.language_list.insert(4, 'Arabic')
        self.language_list.grid(row=4, column=1)
        self.reset_button = Button(text="Reset", fg='black', command=lambda: self.reset())
        self.reset_button.grid(row=5, column=1)
        self.dictionary_button = Button(text="Show Dictionary", fg='black', command=lambda: self.show_dictionary())
        self.dictionary_button.grid(row=6, column=1)
        self.load_dictionary_button = Button(text="Load Dictionary", fg='black',
                                             command=lambda: self.load_dictionary())
        self.load_dictionary_button.grid(row=7, column=1)

        # image = Image("C:/Users/user/PycharmProjects/YankaleProject/resources/background.jpg")
        # background_image = root.PhotoImage(image)
        # background_label = root.Label(root, image=background_image)
        # background_label.place(x=0, y=0, relwidth=1, relheight=1)
        # theLabel = Label(root, text="question:")
        # theLabel['fg'] = 'red'
        # entry_Question = Entry(root)
        # theLabel.grid(row=3, column=0)
        # button3 = Button(text="send the question", fg='green')
        # button3.grid(row=3, column=2)
        # entry_Question.grid(row=3, column=1)

    # need to add the paths and the errors
    def start_work(self):
        print("work on it")
        if self.var.get() == 1:
            print("with stemmer")
        else:
            print("without stemmer")
    #     print("ssd")
    #     if self.entry_Save_Path.size() == 0 or self.entry_Resources_Path.size() == 0:
    #         tkinter.messagebox.showerror("Eroor", "You must full the entry lines")
    #         print("ds")
    # root.destroy()

    def browse_save_file(self):
        print("choose a folder")
        root.file_save_name = filedialog.askdirectory()
        self.entry_Save_Path.insert(0, root.file_save_name)
        print(root.file_save_name)

    def browse_folder(self):
        print("choose a folder")
        root.folder_name = filedialog.askdirectory()
        self.entry_Resources_Path.insert(0, root.folder_name)
        print(root.folder_name)

    def reset(self):
        #     need to delete thus label from the label
        if self.entry_Resources_Path is not None:
            self.entry_Resources_Path.delete(0, END)
        if self.entry_Save_Path is not None:
            self.entry_Save_Path.delete(0, END)
        print("restarting")

    def show_dictionary(self):
        print("Show Dictionary")

    def load_dictionary(self):
        print("Load Dictionary")


class ReadFile:
    docs_texts = {}
    docs_properties = {}
    root_folder_path = ''
    file_names = []
    number_of_files = 50
    file_names_split = []
    file_names_split_index = 0

    def __init__(self, folder_path):
        self.root_folder_path = folder_path
        self.file_names = listdir(folder_path)
        indexes = range(0, self.file_names.__len__(), min(self.file_names.__len__(),
                                                          self.number_of_files))[1:]
        prev = 0
        for index in indexes:
            self.file_names_split.append(self.file_names[prev:index])
            prev = index
        self.file_names_split.append(self.file_names[prev:len(self.file_names)-1])

    def read(self):
        for file_name in self.file_names_split[self.file_names_split_index]:
            file = open(self.root_folder_path + file_name + "/" + file_name, "r").read()
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
                if '<F P=104>' in doc_contents:
                    i = 0
                    while len(doc_contents.split('<F P=104>')[1].split('</F>')[0]) > 0\
                            and doc_contents.split('<F P=104>')[1].split('</F>')[0].split(' ')[i] == '':
                        i += 1
                    doc_city = doc_contents.split('<F P=104>')[1].split('</F>')[0].split(' ')[i]
                if '</TEXT>' in doc_contents:
                    doc_text = doc_contents.split('<TEXT>')[1].split('</TEXT>')[0].replace('\n', ' ') \
                        .replace(':', '').replace('"', '').replace('!', '').replace('?', '') \
                        .replace("'", '').replace('*', '').replace('(', '').replace(')', '').replace('[', '') \
                        .replace('|', '').replace(']', '').replace('{', '').replace('}', '').replace(';', '') \
                        .replace('&', '').replace('#', '').replace(',.', '').replace('.-', '').replace('\ ', '') \
                        .replace('+', '').replace('_', '').replace('=', '').replace('\r', '') \
                        .replace('--', ' ').replace('\t', '').replace('-,', ' ').replace('..', '') \
                        .replace('^', '').replace('\ ', '').replace('//', '').replace('@', '') \
                        .replace('   ', ' ').replace('  ', ' ')
                self.docs_properties[doc_name] = {'language': doc_language, 'city': doc_city}
                self.docs_texts[doc_name] = {'text': doc_text}
        return self.docs_texts, self.docs_properties


class Parse:
    parser_index = 0
    stop_words = set()

    # id:
    #   term
    # values:
    #   df (num of docs) = size(list of docs)           number
    #   tf_per_doc (num of appearances in each doc)     {key:doc_name, value:number}
    #   list of docs                                    [doc1, doc2, ...]
    terms_dictionary = {}

    # id:
    #   doc_name
    # values:
    #   max_tf of term                                  number
    #   num of terms                                    number
    #   doc_city                                        string
    docs_dictionary = {}

    stemmer = SnowballStemmer("english")
    stem_bool = False

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

    def __init__(self, index, sw_path, stem_bool):
        self.parser_index = index
        self.stop_words = set(open(sw_path).read().split())
        self.terms_dictionary = {}
        self.docs_dictionary = {}
        self.stem_bool = stem_bool

    def parse(self, docs_texts, docs_properties):
        print("Start Parsing")
        for doc_name in docs_texts:
            tokens = self.get_tokens(docs_texts[doc_name]['text'])
            (doc_terms, max_tf) = self.parse_document(doc_name, tokens)
            self.save_doc_data(doc_name, doc_terms, docs_properties[doc_name], max_tf)
        self.save_parser_data()

    @staticmethod
    def get_tokens(doc_text):
        tokens = doc_text.split(' ')
        return tokens

    def parse_document(self, doc_name, tokens):
        index = 0
        term_index = 0
        doc_terms = {}
        max_tf = 1

        while index < len(tokens):
            terms_to_add = []
            token = str(tokens[index])

            if token == '' or token.count('.') > 1 or token.count('-') > 1:
                index += 1
            elif (token in self.stop_words or token.lower() in self.stop_words
                    and (token != 'between' and token != 'Between')):
                index += 1
            else:
                # If token ends with "." or "," delete last char
                if (len(token) > 1 and
                        (token[len(token) - 1] == "." or token[len(token) - 1] == "," or token[len(token) - 1] == "-")):
                    token = token[:-1]

                if token[0].isalpha():
                    (terms_to_add, index) = self.word_parser(tokens, token, index)
                elif token[0].isdigit():
                    (terms_to_add, index) = self.number_parser(tokens, token, index)
                elif token[0] == "$" and len(token) > 1:
                    (terms_to_add, index) = self.money_parser(tokens, token, index)
                elif token[0] == "%" and len(token) > 1:
                    (terms_to_add, index) = self.percent_parser(token, index)
                else:
                    index += 1

                (doc_terms, term_index, max_tf) = self.add_to_dictionaries(terms_to_add, doc_terms, doc_name, term_index, max_tf)
        # if 'yogev' in doc_terms:
        #     print(doc_terms['yogev'])
        return doc_terms, max_tf

    def add_to_dictionaries(self, terms_to_add, doc_terms, doc_name, term_index, max_tf):

        #   df (num of docs) = size(list of docs)

        for new_term in terms_to_add:
            new_term = str(new_term)

            if self.stem_bool:
                new_term = stemmer.stem(new_term)

            if new_term != '':
                # numbers
                if new_term[0].isdigit():
                    if new_term not in self.terms_dictionary:
                        self.terms_dictionary[new_term] = {'docs': [doc_name], 'df': 1}
                        doc_terms[new_term] = {'tf': 1, 'indexes': [term_index]}
                    else:
                        if new_term in doc_terms:
                            doc_terms[new_term]['tf'] += 1
                            if max_tf < doc_terms[new_term]['tf']:
                                max_tf = doc_terms[new_term]['tf']
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
                                                                                    ['docs'])
                            if term_lower not in doc_terms:
                                doc_terms[term_lower] = {'tf': 1, 'indexes': [term_index]}
                            else:
                                doc_terms[term_lower]['tf'] += 1
                                if max_tf < doc_terms[term_lower]['tf']:
                                    max_tf = doc_terms[term_lower]['tf']
                                doc_terms[term_lower]['indexes'].append(term_index)
                        else:
                            if term_upper in self.terms_dictionary:
                                if term_upper in doc_terms:
                                    doc_terms[term_upper]['tf'] += 1
                                    if max_tf < doc_terms[term_upper]['tf']:
                                        max_tf = doc_terms[term_upper]['tf']
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
                                self.terms_dictionary.pop(term_upper)
                                self.terms_dictionary[term_lower] = {'docs': temp_docs, 'df': temp_df}
                                if doc_name not in self.terms_dictionary[term_lower]['docs']:
                                    self.terms_dictionary[term_lower]['docs'].extend([doc_name])
                                    self.terms_dictionary[term_lower]['tf'] = len(self.terms_dictionary
                                                                                        [term_lower]['docs'])
                                if term_upper in doc_terms:
                                    temp_tf = doc_terms[term_upper]['tf'] + 1
                                    if max_tf < temp_tf:
                                        max_tf = temp_tf
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
                                doc_terms[term_lower]['indexes'].extend([term_index])
                            else:
                                self.terms_dictionary[term_lower]['docs'].extend([doc_name])
                                self.terms_dictionary[term_lower]['df'] = len(self.terms_dictionary
                                                                                    [term_lower]['docs'])
                                doc_terms[term_lower] = {'tf': 1, 'indexes': [term_index]}
            term_index += 1
        return doc_terms, term_index, max_tf

    def number_parser(self, tokens, token, index):
        new_terms = []

        # If token is not in good format, simply add it as is
        if token.count('.') > 1 or token.count('-') > 1\
                or (not token.__contains__('-') and not self.contains_only_numbers(token)):
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
        # delete thous delimiters
        if token[0].isdigit():
            # April 18,September 21
            if index - 1 >= 0 and self.months_names.__contains__(tokens[index - 1]):
                month_change = self.change_month(tokens[index - 1])
                month_position = index - 1
            # 14 June,18 July
            elif index + 1 < len(tokens) and self.months_names.__contains__(tokens[index + 1]):
                month_change = self.change_month(tokens[index + 1])
                month_position = index + 1
            index += 1
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
        else:
            index -= 1
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
                new_terms.extend([int(num / 1000000), 'M', 'Dollars'])
            else:
                new_terms.extend([num / 1000000, 'M', 'Dollars'])

        else:
            new_terms.extend([token, 'Dollars'])
        return new_terms, index + 1

    def number_parser_regular(self, tokens, token, index):
        new_terms = []
        if index < len(tokens) - 1 and tokens[index + 1] in self.regular_number_names:
            new_terms.append(self.term_word(tokens, token, index))
            index += 1
        elif token.count('.') > 1:
            pass
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
                new_term = int(num / 1000000)
            new_term_str = new_term.__str__()
            new_term_str += 'M'
        elif 1000000000 <= num:
            if type(num) is int:
                new_term = int(num / 1000000000)
            else:
                new_term = int(num / 1000000000)
            new_term_str = new_term.__str__()
            new_term_str += 'B'
        else:
            new_term_str = num.__str__()
        return new_term_str

    # handle price of format $10,000 or $10 million
    def money_parser(self, tokens, token, index):
        new_temp_terms = []
        token = token[1:len(token)]
        if type(token) is str and (token.__contains__('%') or token.count('$') > 1 or token.count('.') > 1
                                   or token.count('-') >= 1 or token.__contains__('/')
                                   or ((not token.__contains__('-')) and self.contains_letter(token))):
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
            if (index < len(tokens) - 1 and tokens[index + 1][0].isdigit()
                    and index < len(tokens) - 2 and tokens[index + 2] == 'and'
                    and index < len(tokens) - 3 and tokens[index + 3][0].isdigit()):
                range_token = tokens[index + 1] + '-' + tokens[index + 3]
                (new_terms, temp_index) = self.number_parser_range([range_token], range_token, 0)
                index += temp_index + 2
        elif token.__contains__('-'):
            (new_terms, a) = self.number_parser_range([token], token, 0)
            for j in range(len(new_terms)):
                if new_terms[j][0].isupper():
                    new_terms[j] = new_terms[j].lower()
        elif token in self.months_names and index + 1 < len(tokens)\
                and len(tokens[index + 1]) > 0 and tokens[index + 1][0].isdigit():
            pass
        else:
            new_terms.append(token)
        return new_terms, index + 1

    def save_doc_data(self, doc_name, doc_terms, doc_properties, max_tf):
        # id:
        #   doc_name
        # values:
        #   max_tf of term
        #   num of terms
        #   doc_city
        self.docs_dictionary[doc_name] = {'max_tf': max_tf,
                                          'num_of_terms': len(doc_terms.keys()),
                                          'doc_city': doc_properties['city']}
        for term in doc_terms:
            if term.upper() in self.terms_dictionary:
                if 'tf_per_doc' not in self.terms_dictionary[term.upper()].keys():
                    self.terms_dictionary[term.upper()]['tf_per_doc'] = {doc_name: doc_terms[term]['tf']}
                else:
                    tmp_dict = {doc_name: doc_terms[term]['tf']}
                    self.terms_dictionary[term.upper()]['tf_per_doc'].update(tmp_dict)
            elif term.lower() in self.terms_dictionary:
                if 'tf_per_doc' not in self.terms_dictionary[term.lower()].keys():
                    self.terms_dictionary[term.lower()]['tf_per_doc'] = {doc_name: doc_terms[term]['tf']}
                else:
                    tmp_dict = {doc_name: doc_terms[term]['tf']}
                    self.terms_dictionary[term.lower()]['tf_per_doc'].update(tmp_dict)

    def save_parser_data(self):

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
        #   num of terms                                    number
        #   doc_city                                        string

        terms_file_name = 'parser_%d_terms.txt' % self.parser_index
        docs_file_name = 'parser_%d_docs.txt' % self.parser_index
        terms_file = open(terms_file_name, "a")
        docs_file = open(docs_file_name, "a")
        # a = sys.getsizeof(self.terms_dictionary)
        for key in sorted(self.terms_dictionary.keys()):
            terms_file.write('<%s,' % key),
            terms_file.write('%d,' % self.terms_dictionary[key]['df']),
            if 'tf_per_doc' in self.terms_dictionary[key].keys():
                terms_file.write('%s,' % str(self.terms_dictionary[key]['tf_per_doc'])),
            terms_file.write('%s>' % str(self.terms_dictionary[key]['docs'])),
        for doc in sorted(self.docs_dictionary.keys()):
            docs_file.write('<%s,' % doc),
            docs_file.write('%d,' % self.docs_dictionary[doc]['max_tf']),
            docs_file.write('%d,' % self.docs_dictionary[doc]['num_of_terms']),
            docs_file.write('%s>' % self.docs_dictionary[doc]['doc_city']),
        pass


# class Index:
#     doc_terms_indexer = {}
#     corpus = {}
#     docs_texts = {}
#     indexer_index = 0
#
#     def __init__(self, indexer, corpus_dictionary, doc_terms, documents_text):
#         self.doc_terms_indexer = doc_terms
#         self.corpus = corpus_dictionary
#         self.docs_texts = documents_text
#         self.indexer_index = indexer
#
#     def index(self):
#         print("Start Indexer")
#         data_file_name = 'parser%d.txt' % self.indexer_index
#         data_file = open(data_file_name, "rw+").read()
#         for key in self.doc_terms_indexer:
#             number_of_shows = len(self.doc_terms_indexer[key])
#             data_file.write(str(self.doc_terms_indexer[key][number_of_shows]))
#
#             # data_file.read('%s>' % key),
#             # data_file.write('%d' % self.doc_terms_indexer[key]['tf']),
#             # data_file.write(str(self.doc_terms_indexer[key]['indexes'])),
#         filenames = ['file1.txt', 'file2.txt', ...]
#         with open('path/to/output/file', 'w') as outfile:
#             for doc_name in docs_texts:
#                 with open(fname) as infile:
#                     outfile.write(infile.read())
#     #
#     # writed_doc = []
#     # for doc_name in docs_texts:
#     #     tokens = self.get_tokens(docs_texts[doc_name]['text'])
#     #     doc_terms = self.parse_document(doc_name, tokens)
#     #     writed_doc.append(sorted(doc_terms))
#     # # writed_doc = sorted(writed_doc)
#     # self.save_doc_data(writed_doc)
#     #


# ---------------- MAIN FUNCTION ---------------- #

root_folder_path = "C:/Users/yogev.s/PycharmProjects/Yankale/resources/corpus/"
stop_words_path = "C:/Users/yogev.s/PycharmProjects/Yankale/resources/stop_words.txt"

root = Tk()
g = GUI(root)
root.mainloop()

processes = []
number_of_threads = 37
stemming = False
read_file = ReadFile(root_folder_path)

if stemming:
    stemmer = SnowballStemmer("english")


# Function for the threads
def concurrent_function(rf, sw_path, index):
    (docs_texts, docs_properties) = read_file.read()
    parser = Parse(index, sw_path, stemming)
    parser.parse(docs_texts, docs_properties)
    # indexer = Index(parser.get_doc_terms())
    print("done")


# Without threads
for index1 in range(number_of_threads):
    (docs_texts, docs_properties) = read_file.read()
    parser = Parse(index1, stop_words_path, False)
    parser.parse(docs_texts, docs_properties)
    # if stemming:
    #     indexer = Index(stemmer)
    # indexer = Index(index1, parser.get_corpus(), parser.get_doc_terms(), docs_texts)
    # indexer.index()
    print("Done with 50 files")

# With threads
# if __name__ == '__main__':
#     for thread_index in range(number_of_threads):
#         process = Process(target=concurrent_function, args=[read_file, stop_words_path, thread_index])
#         process.start()
#         processes.append(process)
#
# # Finish threads
# for process in processes:
#     process.join()


print("pass")


