# coding=utf-8
from threading import Thread
from os import listdir
from nltk import SnowballStemmer


class ReadFile:
    # This class will read the files from the DB
    resource_path = ''
    stop_words_path = ''
    stop_words = []
    number_of_threads = 50
    threads = []
    file_names = []
    split_file_names = []

    def __init__(self, resource_path, stop_words_path):
        # assuming resource_path is the path to corpus folder
        self.resource_path = resource_path
        self.stop_words = open(stop_words_path, 'r+').read().split('\n')
        self.file_names = listdir(resource_path)
        indexes = range(0, self.file_names.__len__(), 100)[1:]
        prev = 0
        for index in indexes:
            self.split_file_names.append(self.file_names[prev:index])
            prev = index
        # ADDING FOR TESTING:
        if len(indexes) == 0:
            self.split_file_names.append(self.file_names)
        else:
            self.split_file_names.append(self.file_names[indexes[-1]:])
        self.play()
        # self.play_without_threads()

    def play_without_threads(self):
        self.concurrent_function(self.file_names, self.resource_path)

    def play(self):
        for i in range(self.number_of_threads):
            if len(self.split_file_names) > 0:
                process = Thread(target=self.concurrent_function,
                                 args=[self.split_file_names.pop(), self.resource_path])
                print ("############# Thread start: %d\n" % i),
                process.start()
                self.threads.append(process)
        for process in self.threads:
            process.join()

    # Function for the thread
    def concurrent_function(self, current_file_names, resource_path):
        corpus_dictionary = []
        parser = Parse(self.stop_words)
        stemmer = SnowballStemmer("english")
        for file_name in current_file_names:
            # print ('------- Start working on file: %s -------' % file_name)
            current_file = open(resource_path + file_name + "/" + file_name, "r").read()
            for doc in current_file.split("</DOC>\n\n<DOC>"):
                # parsed_doc = Parse(doc, corpus_dictionary)
                doc_num = doc.split('</DOCNO>')[0].split('<DOCNO>')[1].replace(' ', '')
                doc_tokens = parser.get_tokens(doc)
                current_parsed_doc = parser.parse_document(doc_num, doc_tokens)
                current_stemmed_doc = self.stem_document(stemmer, current_parsed_doc)
                pass
            # print(parsed_doc.document_terms)
            print("Parsed File %s\n" % file_name),

        # print current_file_names

    @staticmethod
    def stem_document(stemmer, doc_terms):
        stemmed_doc_terms = []
        for term in doc_terms:
            if type(term) is str and term.isalpha() and term.islower():
                stemmed_doc_terms.append(stemmer.stem(term))
            else:
                stemmed_doc_terms.append(term)
        return stemmed_doc_terms


class Parse:
    corpus_dictionary = {}
    stop_words = []
    uppercase_terms = []

    # Lists for parser:
    price_number_names = ['thousand', 'million', 'billion', 'trillion', 'Thousand', 'Million',
                          'Billion', 'Trillion', 'k', 'm', 'bn', 'tr']
    dollar_names = ['Dollars', 'dollars', 'Dollars,', 'dollars,', 'Dollars.', 'dollars.']
    regular_number_names = ['Thousand', 'Million', 'Billion', 'Trillion', 'Thousand.', 'Million.', 'Billion.',
                            'Trillion.', 'thousand', 'million', 'billion', 'trillion', 'thousand.', 'million.',
                            'billion.', 'trillion.', 'Thousand,', 'Million,', 'Billion,', 'Trillion,', 'thousand,',
                            'million,', 'billion,', 'trillion,']
    percentage_labels = ['%', 'percent', 'percentage', 'percent.', 'percentage.', 'percent,', 'percentage,', 'Percent',
                         'Percentage', 'Percent.', 'Percentage.', 'Percent,', 'Percentage,']
    months_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'January',
                    'February', 'March', 'April', 'June', 'July', 'August', 'September', 'October', 'November',
                    'December', 'JANUARY', 'FEBRUARY', 'MARCH', 'APRIL', 'MAY', 'JUNE', 'JULY', 'AUGUST', 'SEPTEMBER',
                    'OCTOBER', 'NOVEMBER', 'DECEMBER', 'Jan.', 'Feb.', 'Mar.', 'Apr.', 'May.', 'Jun.', 'Jul.', 'Aug.',
                    'Sep.', 'Oct.', 'Nov.', 'Dec.', 'January.', 'February.', 'March.', 'April.', 'June.', 'July.',
                    'August.', 'September.', 'October.', 'November.', 'December.', 'JANUARY.', 'FEBRUARY.', 'MARCH.',
                    'APRIL.', 'MAY.', 'JUNE.', 'JULY.', 'AUGUST.', 'SEPTEMBER.', 'OCTOBER.', 'NOVEMBER.', 'DECEMBER.',
                    'Jan,', 'Feb,', 'Mar,', 'Apr,', 'May,', 'Jun,', 'Jul,', 'Aug,',
                    'Sep,', 'Oct,', 'Nov,', 'Dec,', 'January,', 'February,', 'March,', 'April,', 'June,', 'July,',
                    'August,', 'September,', 'October,', 'November,', 'December,', 'JANUARY,', 'FEBRUARY,', 'MARCH,',
                    'APRIL,', 'MAY,', 'JUNE,', 'JULY,', 'AUGUST,', 'SEPTEMBER,', 'OCTOBER,', 'NOVEMBER,', 'DECEMBER,']
    months_in_number = ['.01.', '.02.', '.03.', '.04.', '.05.', '.06.', '.07.', '.08.', '.09.', '.10.', '.11.', '.12.',
                        '.1.', '.2.', '.3.', '.4.', '.5.', '.6.', '.7.', '.8.', '.9.']

    def __init__(self, stop_words):
        self.stop_words = stop_words
        self.corpus_dictionary = []

    @staticmethod
    def get_tokens(doc):
        text = doc.split('<TEXT>')[1].split('</TEXT>')[0].replace("\n", " ")
        # text = (re.search('<TEXT>(.*)</TEXT>', doc.replace("\n", " "))).group(1)
        split_text = (text.replace(':', '').replace('"', '').replace('!', '').replace('?', '').replace("'", '')
                      .replace('*', '').replace('(', '').replace(')', '').replace('[', '').replace('|', '')
                      .replace(']', '').replace('{', '').replace('}', '').replace(';', '').replace('#', '')
                      .replace(',.', '').replace('.-', '').replace('\ ', '').replace('+', '').replace('_', '')
                      .replace('=', '').replace('\r', '').replace('\n', '').replace('  ', ' ').replace('--', ' ')
                      .replace('\t', '').replace('-,', ' ').replace('..', '').split(' '))
        while split_text.__contains__(''):
            split_text.remove('')
        return split_text

    def parse_document(self, doc_num, tokens):
        terms = []
        doc_terms = {}
        term_index = 0
        index = 0
        while index < len(tokens):
            terms_to_add = []
            token = str(tokens[index])
            # print "%s ->" % token,
            # If token ends with "." or "," delete last char
            if (type(token) is str and len(token) > 1 and
                    (token[len(token) - 1] == "." or token[len(token) - 1] == "," or token[len(token) - 1] == "-")):
                token = token[:-1]

            if token[0].isdigit():
                (terms_to_add, index) = self.number_parser(tokens, token, index)
            elif token[0].isalpha():
                (terms_to_add, index) = self.word_parser(tokens, token, index)
            elif token[0] == "$" and len(token) > 1:
                (terms_to_add, index) = self.money_parser(tokens, token, index)
            elif token[0] == "%" and len(token) > 1:
                (terms_to_add, index) = self.percent_parser(token, index)
            else:
                index += 1

            for new_term in terms_to_add:
                # print ('\'%s\' ' % new_term),
                # terms.append(new_term)

                new_term_str = str(new_term)

                if self.contains_only_numbers(new_term_str):
                    if doc_num not in self.corpus_dictionary[new_term_str]['docs']:
                        self.corpus_dictionary[new_term_str]['docs'].append(doc_num)
                    if new_term_str in doc_terms:
                        doc_terms[new_term_str]['tf'] += 1
                        doc_terms[new_term_str]['indexes'].append(term_index)
                    else:
                        doc_terms[new_term_str] = {'tf': 1, 'indexes': [term_index]}

                else:
                    if new_term_str[0].isupper():
                        if new_term_str.lower() in self.corpus_dictionary:
                            if doc_num not in self.corpus_dictionary[new_term_str.lower()]['docs']:
                                self.corpus_dictionary[new_term_str.lower()]['docs'].append(doc_num)
                            doc_terms[new_term_str.lower()]['tf'] += 1
                            doc_terms[new_term_str.lower()]['indexes'].append(term_index)
                        else:
                            if new_term_str.upper() not in self.corpus_dictionary:
                                self.corpus_dictionary[new_term_str.upper()]['docs'].append(doc_num)
                                doc_terms[new_term_str.upper()] = {'tf': 1, 'indexes': [term_index]}
                            else:
                                doc_terms[new_term_str.lower()]['tf'] += 1
                                doc_terms[new_term_str.lower()]['indexes'].append(term_index)
                    elif new_term_str[0].islower():
                        if new_term_str not in self.corpus_dictionary:
                            if new_term_str.upper() in self.corpus_dictionary:
                                temp_docs = self.corpus_dictionary[new_term_str.upper()]['docs']
                                self.corpus_dictionary.remove([new_term.upper()])
                                self.corpus_dictionary[new_term_str.lower()]['docs'] = temp_docs
                            self.corpus_dictionary[new_term_str.lower()]['docs'].append(doc_num)
                            temp_tf = doc_terms[new_term_str.upper()]['tf'] + 1
                            temp_indexes = doc_terms[new_term_str.upper()]['indexes']
                            temp_indexes.append(term_index)
                            doc_terms[new_term_str] = {'tf': temp_tf, 'indexes': temp_indexes}

                term_index += 1

            # print ("")
        return terms

    def number_parser(self, tokens, token, index):
        new_terms = []

        # If token is not in good format, simply add it as is
        if type(token) is str and (token.__contains__('/') or token.__contains__('%') or token.__contains__('$')
                                   or token.__contains__('^') or token.__contains__('@') or token.__contains__('&')
                                   or token.__contains__('..') or token.__contains__('--') or token.__contains__('\ ')
                                   or token.count('.') > 1 or token.count('-') > 1
                                   or ((not token.__contains__('-')) and self.contains_letter(token))):
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
        new_terms = []
        new_temp_terms = []
        if token.__contains__('-') or self.contains_letter(token) or token.__contains__('/') or token.count('.') > 1:
            return [token], index + 1
        token = token[1:len(token)]
        num = token.replace(',', '')
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
        if token[1].isdigit():
            temp_token = str(token[1:len(token)]) + "%"
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
            for i in range(0, len(new_terms)):
                if new_terms[i][0].isupper():
                    new_terms[i] = new_terms[i].lower()
        elif token in self.months_names and index + 1 < len(tokens) and tokens[index + 1][0].isdigit():
            pass
        elif token in self.stop_words or token.lower() in self.stop_words:
            return new_terms, index + 1
        else:
            new_terms.append(token)
        return new_terms, index + 1


########################################


# nested_dict = {'ABC': {'tf': 1, 'indexes': [1, 2, 3]}}
# i = 1
# term = 'ABC'
#
# if nested_dict.__contains__(term):
#     nested_dict[term]['tf'] += 1
#     nested_dict[term]['indexes'].append(i)
# else:
#     nested_dict[term] = {'tf': 1, 'indexes': [i]}


root_resource_path = "C:/Users/yogev.s/PycharmProjects/Yankale/resources/corpus/"
stop_words_path = "C:/Users/yogev.s/PycharmProjects/Yankale/resources/stop_words.txt"
ReadFile(root_resource_path, stop_words_path)
print("pass")

# number_of_threads = 50
#
# threads = []
# file_names = listdir(root_resource_path)
#
# indexes = range(0, 1800, 50)[1:]
# split_file_names = []
# prev = 0
# for index in indexes:
#     split_file_names.append(file_names[prev:index])
#     prev = index
# split_file_names.append(file_names[indexes[-1]:])
#
#
# # Function for the thread
# def concurrent_function(current_file_names):
#     read_file = ReadFile(current_file_names)
#     pass
#
#
# for i in range(number_of_threads):
#     process = Thread(target=concurrent_function, args=[split_file_names.pop(i)])
#     process.start()
#     threads.append(process)
#
# for process in threads:
#     process.join()

# test = ReadFile("C:/Users/yogev.s/PycharmProjects/Yankale/resources/test")
# print ("pass")
# foo = Parse(test.documents)
# print(foo.document_terms[0])
