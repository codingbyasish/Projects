import os
import json
from win32api import GetFileVersionInfo, LOWORD, HIWORD
import csv
import datetime
import pytz
import tkinter as tk
from tkinter import filedialog
import ctypes
from ctypes import wintypes
import msvcrt
import xml.etree.ElementTree as ET

def xml_parser(folder_path, xml_tags):
   xml_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.xml')]
   tag_values = {}
   for xml_file in xml_files:
       file_path = os.path.join(folder_path, xml_file)
       tree = ET.parse(file_path)
       root = tree.getroot()
       for tag in xml_tags:
           elements = root.findall(tag)
           for element in elements:
               tag_values[element.tag] = element.text
   return tag_values

   

def is_folder_locked(folder_path):
   try:
       folder_handle = open(folder_path, 'r')
       msvcrt.locking(folder_handle.fileno(), msvcrt.LK_NBLCK, 1)
       folder_handle.close()
       return False
   except IOError:
       return True

         
def unlock_folder_with_credentials(folder_path, username, password):
   advapi32 = ctypes.WinDLL('advapi32')
   LPWSTR = ctypes.POINTER(wintypes.WCHAR)
   username_wide = ctypes.create_unicode_buffer(username)
   password_wide = ctypes.create_unicode_buffer(password)
   token = wintypes.HANDLE()
   result = advapi32.LogonUserW(
       username_wide,
       None,
       password_wide,
       ctypes.c_uint(2),  # LOGON32_LOGON_INTERACTIVE
       ctypes.c_uint(0),  # LOGON32_PROVIDER_DEFAULT
       ctypes.byref(token)
   )
   if result == 0:
       print("Failed to log in.")
       return
   result = advapi32.ImpersonateLoggedOnUser(token)
   if result == 0:
       print("Failed to impersonate user.")
       advapi32.CloseHandle(token)
       return
   try:
       # Now you can perform operations on the locked folder as the authenticated user
       # For example, you can now access files within the locked folder
       with open(os.path.join(folder_path, 'r')) as file:
           content = file.read()
           print("Successfully accessed file contents:", content)
   finally:
       advapi32.RevertToSelf()
       advapi32.CloseHandle(token)


def get_version_number(filename):
   try:
       info = GetFileVersionInfo(filename, "\\")
       ms = info['FileVersionMS']
       ls = info['FileVersionLS']
       return HIWORD(ms), LOWORD(ms), HIWORD(ls), LOWORD(ls)
   except:
       return "Unknown version"
    


def get_tag_value_from_json(file_path):
   try:
       # Try opening the file with UTF-8 encoding
       with open(file_path, 'r', encoding='utf-8') as json_file:
           data = json.load(json_file)
           tag_value = data.get('scopeName', 'Tag not found')  # Modify 'SENDINGCOMMAND' accordingly
           return tag_value
   except FileNotFoundError:
       return 'Error: File not found'
   except (IOError, json.JSONDecodeError):
       try:
           # Try opening the file with UTF-8 with BOM encoding
           with open(file_path, 'r', encoding='utf-8-sig') as json_file:
               data = json.load(json_file)
               tag_value = data.get('rscopeName', 'Tag not found')  # Modify 'SENDINGCOMMAND' accordingly
               return tag_value
       except (IOError, json.JSONDecodeError):
           try:
               # Try opening the file with Latin-1 encoding
               with open(file_path, 'r', encoding='latin-1') as json_file:
                   data = json.load(json_file)
                   tag_value = data.get('scopeName', 'Tag not found')  # Modify 'SENDINGCOMMAND' accordingly
                   return tag_value
           except (IOError, json.JSONDecodeError):
               return 'Error: Unable to read or decode JSON file'


##def file_hash(pathname, file_extensions):
##   results = []
##   for (root, dirs, files) in os.walk(pathname):
##       for f in files:
##           if any(f.lower().endswith(ext) for ext in file_extensions):
##               file_name = os.path.basename(f)
##               file_path = os.path.join(pathname, file_name)
##               size = os.path.getsize(file_path)
##               version = ".".join([str(i) for i in get_version_number(file_path)])
##               folder_locked = is_folder_locked(root)
##               if f.lower().endswith('.json'):
##                   tag_value = get_tag_value_from_json(pathname)  # You need to define this function
##               else:
##                   tag_value = 'Not a JSON file'
##               results.append([file_name, size, version, tag_value, folder_locked])
##   return results

def file_hash(pathname, file_extensions, xml_file, xml_tags):
   results = []
   for (root, dirs, files) in os.walk(pathname):
       for f in files:
           if any(f.lower().endswith(ext) for ext in file_extensions):
               file_name = os.path.basename(f)
               file_path = os.path.join(pathname, file_name)
               size = os.path.getsize(file_path)
               version = ".".join([str(i) for i in get_version_number(file_path)])
               folder_locked = is_folder_locked(root)
               # Check if the file is an XML file
               if f.lower().endswith('.xml'):
                   # Call the XML parser function to extract values
                   xml_values = xml_parser(xml_file, xml_tags)
                   # Append XML values to the results
                   for tag, value in xml_values.items():
                       results.append([file_name, size, version, tag, value, folder_locked])
               else:
                   # For other file types, append 'Not an XML file' for tag and value
                   results.append([file_name, size, version, 'Not an XML file', 'Not an XML file', folder_locked])
   return results

   

def compare_values(path_info1, path_info2):
   comparison_results = []
   for file_info1, file_info2 in zip(path_info1, path_info2):
       file_name1, size1, version1 = file_info1
       file_name2, size2, version2 = file_info2
       if size1 == size2 and version1 == version2:
           comparison_result = [file_name1, "Files are the same", "Size and Version are similar"]
       else:
           size_diff = size1-size2
           version_diff = f"{version1} vs {version2}"
##           tag_diff = f'{tag_value1} vs {tag_value2}'
           comparison_result = [file_name1, "Files are different", f"Size Diff: {size_diff}, Version Diff: {version_diff}"]
       comparison_results.append(comparison_result)
   return comparison_results

def difference(path_info1, path_info2):
   missing_files_path1 = [file_info for file_info in path_info1 if file_info not in path_info2]
   missing_files_path2 = [file_info for file_info in path_info2 if file_info not in path_info1]
   return missing_files_path1, missing_files_path2

def execute_comparison():
   path1 = entry_path1.get()
   path2 = entry_path2.get()
   output = entry_output.get()
   file_extensions_to_compare = ['.dll', '.json', '.exe','.xml']
   xml_file1= path1
   xml_file2= path2
   xml_tags= ['tag1','tag2','tag3']
   hash1 = file_hash(path1, file_extensions_to_compare, xml_file1, xml_tags)
   hash2 = file_hash(path2, file_extensions_to_compare, xml_file2, xml_tags)
   current_time = datetime.datetime.now()
   with open(output, 'w', newline='', encoding='utf-8') as f:
       writer = csv.writer(f)
       writer.writerow(['Date and Time of Execution:', current_time.strftime('%Y-%m-%d %H:%M:%S')])
       writer.writerow([])
       writer.writerow(['File Name', 'Size (Path 1)', 'Version (Path 1)', 'Size (Path 2)', 'Version (Path 2)','Tag (Path 1)', 'Tag (Path 2)', 'Comparison Result', 'Details'])
       all_file_names = set(file_info[0] for file_info in hash1 + hash2)
       for file_name in all_file_names:
           file_info_path1 = next((info for info in hash1 if info[0] == file_name), [file_name, 'N/A', 'N/A'])
           file_info_path2 = next((info for info in hash2 if info[0] == file_name), [file_name, 'N/A', 'N/A'])
           size1, version1, folder_locked1 = file_info_path1[1], file_info_path1[2],file_info_path1[3]
           size2, version2, folder_locked2= file_info_path2[1], file_info_path2[2],file_info_path2[3] if len(file_info_path2)>= 5 else(None, None, None, False)
           if size1 == 'N/A':
               writer.writerow([file_name, 'N/A', 'N/A', size2, version2, 'File present only in path2', ''])
           elif size2 == 'N/A':
               writer.writerow([file_name, size1, version1, 'N/A', 'N/A', 'File present only in path1', ''])
           else:
               size_diff = int(size1) - int(size2)
               version_diff = f"{version1} vs {version2}"
               comparison_result = 'Files are the same' if size1 == size2 and version1 == version2 else 'Files are different'
               if file_name.lower().endswith('.json'):
                   writer.writerow([file_name, size1, version1,  size2, version2, comparison_result, f"Size Diff: {size_diff}, Version Diff: {version_diff}"])
               else:
                   writer.writerow([file_name, size1, version1, 'Not json file', size2, version2, 'Not json file', comparison_result, f"Size Diff: {size_diff}, Version Diff: {version_diff}"])
               writer.writerow([file_name, size1, version1, size2, version2, comparison_result, f"Size Diff: {size_diff}, Version Diff: {version_diff}"])
       missing_files_path1, missing_files_path2 = difference(hash1, hash2)
       
       if folder_locked1:
             unlock_folder_with_credentials(path1, 'your_username', 'your_password')     
       if folder_locked2:
             unlock_folder_with_credentials(path2, 'your_username', 'your_password')

      
       if missing_files_path1:
           writer.writerow(['Files present in path1 but not in path2'])
           writer.writerow(['File Name', 'Size', 'Version'])
           writer.writerows(missing_files_path1)
       if missing_files_path2:
           writer.writerow(['Files present in path2 but not in path1'])
           writer.writerow(['File Name', 'Size', 'Version'])
           writer.writerows(missing_files_path2)
   result_label.config(text="Comparison completed. Check the output file.")


   
# GUI setup
app = tk.Tk()
app.geometry('300x300')
app.title("File Comparison Tool")
tk.Label(app, text="Path 1:").grid(row=0, column=0)
entry_path1 = tk.Entry(app)
entry_path1.grid(row=0, column=1)
tk.Label(app, text="Path 2:").grid(row=1, column=0)
entry_path2 = tk.Entry(app)
entry_path2.grid(row=1, column=1)
tk.Label(app, text="Output File:").grid(row=2, column=0)
entry_output = tk.Entry(app)
entry_output.grid(row=2, column=1)
compare_button = tk.Button(app, text="Compare", command=execute_comparison)
compare_button.grid(row=3, column=0, columnspan=2, pady=10)
result_label = tk.Label(app, text="")
result_label.grid(row=4, column=0, columnspan=2)

def browse_path(entry_widget):
   path = filedialog.askdirectory()
   entry_widget.delete(0, tk.END)
   entry_widget.insert(tk.END, path)
   
tk.Button(app, text="Browse", command=lambda: browse_path(entry_path1)).grid(row=0, column=2)
tk.Button(app, text="Browse", command=lambda: browse_path(entry_path2)).grid(row=1, column=2)
tk.Button(app, text="Browse", command=lambda: browse_path(entry_output)).grid(row=2, column=2)
app.mainloop()
