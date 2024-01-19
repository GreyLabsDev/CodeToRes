import sys
import re
import fnmatch
import os

exclude_keywords_config_file = "CodeToResExcludeKeywords.txt"
root_module_config_file = "CodeToResRootModuleName.txt"
exclude_files_config_file = "CodeToResExcludeFiles.txt"

has_root_module_name = False
root_module_name = ""

excluse_kyewords = []
excluse_files = []
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
    print(color + text + bcolors.ENDC)

def readExcludeFiles():
    file_lines = open(exclude_files_config_file, "r").readlines()
    for exclude in file_lines:
        excluse_files.append(exclude.strip())

def readExcludeKeywords():
    keywords_file_lines = open(exclude_keywords_config_file, "r").readlines()
    for exclude in keywords_file_lines:
        excluse_kyewords.append(exclude.strip())

def readRootModuleName():
    global has_root_module_name
    global root_module_name
    root_module_name_lines = open(root_module_config_file, "r").readlines()
    has_root_module_name = bool(root_module_name_lines[0])
    root_module_name = root_module_name_lines[1]

def showHelp():
    printColored(bcolors.HEADER, "\nScript for generating string resources from hardcoded strings in *.kt source files\nTo generate resource files use command 'codeToRes <path_to_kotlin_source_directory> <path_to_kotlin_layouts_directory>'")

def search_source_files(path_to_dir, pattern):
    kt_files_paths = []
    for root, dirs, files in os.walk(path_to_dir):
        for basename in files:
            if fnmatch.fnmatch(basename, pattern):
                filename = os.path.join(root, basename)
                if not any(x in filename for x in excluse_files):
                    kt_files_paths.append(filename)
    return kt_files_paths

def build_string_res(string, prefix, index, is_duplicate):
    if is_duplicate:
        return '    <string name="' + prefix + '_' + str(index) + '">' + string + '</string>' + "  <!-- " + "Duplicate string" + " -->\n"
    else:
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

    current_module_name = ""
    if has_root_module_name:
        file_path_split = file_path.split("/")
        if root_module_name in file_path_split:
            root_module_path_index = file_path_split.index(root_module_name)
            current_module_name = file_path_split[root_module_path_index + 1] + "/"

    if len(hardcoded_strings) > 0:
        if not os.path.exists("resources/" + current_module_name + "layout"):
            os.makedirs("resources/" + current_module_name + "layout")
        file = open("resources/" + current_module_name + "layout/" + "" + prefix + "_" + source_file_name + ".xml", "w+")
        file.write('<resources>\n')
        index = 0
        for string in hardcoded_strings:
            file.write(build_string_res(string, prefix, index, False))
            index += 1
        
        printColored(bcolors.OKBLUE, source_file_name + ': Created ' + str(len(hardcoded_strings)) + ' string resources')
        file.write('</resources>')
        file.close()
        printColored(bcolors.OKGREEN, source_file_name + ': Resources saved in file: ' + prefix + ".xml")
    else:
        printColored(bcolors.OKBLUE, source_file_name + ': Hardcoded strings not found')

def has_cyrillic(text):
    return bool(re.search('[\u0400-\u04FF]', text))

def check_string_duplicates(input_string_list):
    unique_set = set(input_string_list)
    return len(unique_set) != len(input_string_list)

def get_duplicates(input_string_list):
    duplicates_list = {x for x in input_string_list if input_string_list.count(x) > 1}
    return duplicates_list

def build_output_file_from_kt(file_path):
    prefix, source_file_name = get_prefix_and_filename_from_source(file_path)

    if "Test.kt" in source_file_name:
        return

    input_file = open(file_path, "r")

    # Exclude commented code lines
    file_text_lines = input_file.readlines()
    rofmatted_text_lines = []

    for line in file_text_lines:
        if not any(x in line for x in excluse_kyewords):
            rofmatted_text_lines.append(line)

    file_text = "".join(rofmatted_text_lines)

    replaced_source = file_text.replace(quotes_symbol, quotes_symbol_replacer)
    all_hardcoded_strings = quoted_regex_finder.findall(replaced_source)

    printColored(bcolors.OKBLUE, source_file_name + ': Searching harcoded strings in Kotlin file')
    formatted_strings = []
    for string in all_hardcoded_strings:
        formatted_string = string.replace(quotes_symbol_replacer, quotes_symbol).strip()
        if formatted_string != '""':
            formatted_strings.append(formatted_string)
    if len(formatted_strings) > 0:

        has_duplicates = check_string_duplicates(formatted_strings)
        is_cyrillic = any(has_cyrillic(st) for st in formatted_strings)

        if not is_cyrillic and not has_duplicates:
            return
        
        duplicates_list = get_duplicates(formatted_strings)

        if has_duplicates:
            resource_open_tag = "<!-- " + "// Original file path:" + " -->\n" + "<!-- " + file_path + " -->\n" + "<!-- " + "Found duplicate strings" + " -->\n" + "<resources>\n"
            name_prefix = ""
        else:
            resource_open_tag = "<!-- " + "// Original file path:" + " -->\n" + "<!-- " + file_path + " -->\n" + "<resources>\n"
            name_prefix = ""

        current_module_name = ""
        if has_root_module_name:
            file_path_split = file_path.split("/")
            if root_module_name in file_path_split:
                root_module_path_index = file_path_split.index(root_module_name)
                current_module_name = file_path_split[root_module_path_index + 1] + "/"

        if not os.path.exists("resources/" + current_module_name + "source/duplicates"):
            os.makedirs("resources/" + current_module_name + "source/duplicates")

        if not os.path.exists("resources/" + current_module_name + "source/strings"):
            os.makedirs("resources/" + current_module_name + "source/strings")

        if has_duplicates:
            file = open("resources/" + current_module_name + "source/duplicates/"  + name_prefix +  prefix + "_" + source_file_name + ".xml", "w+")
        else:
            file = open("resources/" + current_module_name + "source/strings/"  + name_prefix +  prefix + "_" + source_file_name + ".xml", "w+")
        
        file.write(resource_open_tag)
        index = 0

        for string in formatted_strings:
            is_duplicate_string = string in duplicates_list
            file.write(build_string_res(string, prefix, index, is_duplicate_string))
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

readExcludeFiles()
readExcludeKeywords()
readRootModuleName()

printColored(bcolors.OKGREEN, '----------')
printColored(bcolors.OKGREEN, 'Exclude keywords = ' + str(excluse_kyewords))
printColored(bcolors.OKGREEN, 'Exclude file patterns = ' + str(excluse_files))
printColored(bcolors.OKGREEN, 'Has root module name keywords = ' + str(has_root_module_name))
printColored(bcolors.OKGREEN, 'Root module name = ' + str(root_module_name))
printColored(bcolors.OKGREEN, '----------')

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
