# CodeToRes
Fast and easy extract hardcoded strings and string duplicates from your *.kt and *.xml files and pack to structured string resources

## How to use exclude rules

- CodeToResExcludeFiles.txt Add here file names you want to exclude from parsing
- CodeToResExcludeKeywords.txt Add here keywords you want to exclude from line parsing in source code
- CodeToResRootModuleName.txt For multi-module projest. First line - set to TRUE, if you want to sort all results by different directories named by module names. Second line - main module name, to resolve child module name for each file

Use example:
```python CodeToRes.py /path/to/source/code/kotlin/files /path/to/res/layout```
