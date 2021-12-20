import sys
import re
import fnmatch
import os

quoted_regex_finder = re.compile('"[^"]*"')
string_in_xml_regex_finder = re.compile('(?<=android:text=).*(?=/>)')
quotes_symbol = '\\"'
quotes_symbol_replacer = '#'

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
def printColored(color, text):
    print(color + text + color)

def showHelp():
    printColored(bcolors.HEADER, "\nScript for generating string resources from hardcoded strings in *.kt source files\nTo generate resource files use command 'codeToRes <path_to_kotlin_source_directory> <path_to_kotlin_layouts_directory>'")

def search_source_files(path_to_dir, pattern):
    kt_files_paths = []
    for root, dirs, files in os.walk(path_to_dir):
        for basename in files:
            if fnmatch.fnmatch(basename, pattern):
                filename = os.path.join(root, basename)
                kt_files_paths.append(filename)
    return kt_files_paths

def build_string_res(string, prefix, index):
    return '    <string name="' + prefix + '_' + str(index) + '">' + string + '</string>\n'

def get_prefix_and_filename_from_source(file_path):
    segmented_path = file_path.split("/")
    prefix = segmented_path[len(segmented_path)-2]
    source_file_name = segmented_path[len(segmented_path)-1]
    return prefix, source_file_name

def build_output_file_for_xml(file_path):
    prefix, source_file_name = get_prefix_and_filename_from_source(file_path)
    input_file = open(file_path, "r")
    file_text = input_file.read()
    text_strings = string_in_xml_regex_finder.findall(file_text)

    printColored(bcolors.OKBLUE, source_file_name + ': Searching harcoded strings in XML file')
    hardcoded_strings = []
    for string in text_strings:
        if "@string" not in string:
            hardcoded_strings.append(string.strip())

    if len(hardcoded_strings) > 0:
        if not os.path.exists("resources"):
            os.makedirs("resources")
        file = open("resources/" + "FROM_LAYOUT_" + prefix + "_" + source_file_name + ".xml", "w+")
        file.write('<resources>\n')
        index = 0
        for string in hardcoded_strings:
            file.write(build_string_res(string, prefix, index))
            index += 1
        
        printColored(bcolors.OKBLUE, source_file_name + ': Created ' + str(len(hardcoded_strings)) + ' string resources')
        file.write('</resources>')
        file.close()
        printColored(bcolors.OKGREEN, source_file_name + ': Resources saved in file: ' + prefix + ".xml")
    else:
        printColored(bcolors.OKBLUE, source_file_name + ': Hardcoded strings not found')


def build_output_file_from_kt(file_path):
    prefix, source_file_name = get_prefix_and_filename_from_source(file_path)

    input_file = open(file_path, "r")
    file_text = input_file.read()

    replaced_source = file_text.replace(quotes_symbol, quotes_symbol_replacer)
    all_hardcoded_strings = quoted_regex_finder.findall(replaced_source)

    printColored(bcolors.OKBLUE, source_file_name + ': Searching harcoded strings in Kotlin file')
    formatted_strings = []
    for string in all_hardcoded_strings:
        formatted_string = string.replace(quotes_symbol_replacer, quotes_symbol).strip()
        if formatted_string != '""':
            formatted_strings.append(formatted_string)
    if len(formatted_strings) > 0:
        if not os.path.exists("resources"):
            os.makedirs("resources")
        file = open("resources/"  + "FROM_SOURCE_" +  prefix + "_" + source_file_name + ".xml", "w+")
        file.write('<resources>\n')
        index = 0
        for string in formatted_strings:
            file.write(build_string_res(string, prefix, index))
            index += 1
        
        printColored(bcolors.OKBLUE, source_file_name + ': Created ' + str(len(formatted_strings)) + ' string resources')
        file.write('</resources>')
        file.close()
        printColored(bcolors.OKGREEN, source_file_name + ': Resources saved in file: ' + prefix + ".xml")
    else:
        printColored(bcolors.OKBLUE, source_file_name + ': Hardcoded strings not found')
    
# MAIN #
if (len(sys.argv) < 3): 
    showHelp()
    exit()

kotlin_source_file_path = sys.argv[1]
layouts_xml_source_file_path = sys.argv[2]
kt_files = search_source_files(kotlin_source_file_path, "*.kt")
xml_files = search_source_files(layouts_xml_source_file_path, "*.xml")
printColored(bcolors.OKGREEN, '----------')
printColored(bcolors.OKGREEN, 'Found ' + str(len(kt_files)) + ' *.kt files')
printColored(bcolors.OKGREEN, 'Found ' + str(len(xml_files)) + ' *.xml files')
printColored(bcolors.OKGREEN, '----------')

printColored(bcolors.OKBLUE, '----------')
for file in kt_files:
    build_output_file_from_kt(file)
printColored(bcolors.OKBLUE, '----------')

printColored(bcolors.OKBLUE, '----------')
for layout_file in xml_files:
    build_output_file_for_xml(layout_file)
printColored(bcolors.OKBLUE, '----------')
