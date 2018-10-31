import re
from os import listdir


class ReadFile:
    # This class will read the files from the DB
    documents = []

    def __init__(self, resource_path):
        # assuming resource_path is the path to corpus folder
        resource_path += "/"
        folder_names = listdir(resource_path)
        for folder in folder_names:
            current_file_path = resource_path + folder + "/" + folder
            current_file = open(current_file_path, "r").read()
            for doc in current_file.split("</DOC>\n\n<DOC>"):
                self.documents.append(doc)

    # divides the documents by files
    # def __init__(self, resource_path):
    #     # assuming resource_path is the path to corpus folder
    #     resource_path += "/"
    #     folder_names = listdir(resource_path)
    #     for folder in folder_names:
    #         current_file_path = resource_path + folder + "/" + folder
    #         current_file = open(current_file_path, "r").read()
    #         documents_of_current_file = current_file.split("</DOC>")
    #         self.documents.append(documents_of_current_file)


class Parse:
    # This class will parse each document from the DB
    document_texts = []
    document_terms = []

    def __init__(self, documents):
        for doc in documents:
            # text.replace("a", "b") Replaces a with b
            text = (re.search('<TEXT>(.*)</TEXT>', doc.replace("\n", "\t"))).group(1)
            self.document_texts.append(text)
            self.document_terms.append(text.split(" "))


test = ReadFile("C:/Users/yogev.s/PycharmProjects/Yankale/resources/test")
foo = Parse(test.documents)
print(foo.document_terms[0])
