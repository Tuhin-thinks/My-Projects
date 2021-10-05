import re
import sys
from os import link, write
from typing import Any, List, Union

README_FILENAME:Union[None, str] = None
link_regex = "link:(?P<link>.+)\:\:text\:(?P<text>.+)\:\:"
regex = re.compile(link_regex, re.I)

def format_string(string:str):
    # match_obj = regex.search(string)
    or_string = string
    for match_obj in regex.finditer(string):
        if match_obj:
            match_dict = match_obj.groupdict()
            link = match_dict['link']
            text = match_dict['text']
            new_string = f"[{text}]({link})"
            or_string = or_string[:match_obj.start()]+ new_string +or_string[match_obj.end():]
    return or_string

def write_readme(filename, line:str):
    with open(filename, 'a') as writer_obj:
        writer_obj.write(line.strip()+'\n')

def acceptData(headers:tuple, separator:str, write_headers):
    ignoreCount = 0
    writtenCount = 0
    if write_headers:
        write_readme(README_FILENAME, ' | '.join(headers))
        styling = ' | '.join([':---:']*len(headers))
        write_readme(README_FILENAME, styling)

    while True:
        line = input().strip('\n')
        
        if not line:
            break
        
        column_data = format_string(line).split(separator)
        if len(column_data) != len(headers):
            ignoreCount += 1
            continue
        else:
            line_to_write = " | ".join(column_data)
            write_readme(README_FILENAME, line_to_write)
            writtenCount += 1



def askInput()->tuple:
    usrInp = input("Enter headers [comma separated]:")
    if ',' not in usrInp:
        print("Not a comma separated string, please try again.")
        return askInput()
    else:
        headers = tuple(map(lambda x: x.strip(), usrInp.split(',')))
    return headers


if __name__ == "__main__":
    argv = sys.argv
    separator = " > "
    header_labels = None
    write_headers = True
    if len(argv) > 1:
        separator_ = argv[1][0]
        if separator_ not in ('.', '...'):
            separator = separator_
        else:
            print("Using default separator (%s)" % separator)
        print("Using separator (%s)" % separator)
        if len(argv) == 4 and argv[2] != '...':
            header_labels = tuple(argv[2:4])
            print("Header labels :", header_labels)
        elif len(argv) == 4 and argv[2] == '...':
            header_labels = tuple(argv[2:])
            write_headers = False
    else:
        print("Using default separator (%s)" % separator)
    if not header_labels:
        header_labels = askInput()
    README_FILENAME = "DEMO.md"
    acceptData(header_labels, separator, write_headers)