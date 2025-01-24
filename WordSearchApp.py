import tkinter as tk
from tkinter import filedialog, messagebox
import os
import time

# Brute Force Algorithm for pattern search
def BFS(t, pattern, w, c_s): # text, whole word, case sensitive
    
    if not c_s:
        t = t.lower()
        pattern = pattern.lower()

    m = []  # Matches
    t_lines = t.splitlines()

    for l_m, line in enumerate(t_lines, 1):  # line number
        beginning = 0    # beginning position in line
    
        while beginning <= len(line) - len(pattern):
            if line[beginning:beginning + len(pattern)] == pattern:
                if w:
                    if (beginning == 0 or not line[beginning - 1].isalnum()) and \
                       (beginning + len(pattern) == len(line) or not line[beginning + len(pattern)].isalnum()):
                        m.append((l_m, beginning, line))
                else:
                    m.append((l_m, beginning, line))
            beginning += 1
    
    return m

# KMP Algorithm for pattern search
def kmp_search(t, pattern, w, c_s):
    if not c_s:
        t = t.lower()
        pattern = pattern.lower()

    def kmp_preprocess(pattern):
        lps = [0] * len(pattern)
        length = 0  # length of previous longest prefix suffix
        i = 1
        
        while i < len(pattern):
            if pattern[i] == pattern[length]:
                length += 1
                lps[i] = length
                i += 1
            else:
                if length != 0:
                    length = lps[length - 1]
                else:
                    lps[i] = 0
                    i += 1
        return lps

    m = []
    t_lines = t.splitlines()
    lps = kmp_preprocess(pattern)

    for l_m, line in enumerate(t_lines, 1):
        i, j = 0, 0
        
        while i < len(line):
            if pattern[j] == line[i]:
                i += 1
                j += 1

            if j == len(pattern):
                if w:
                    if (i - j == 0 or not line[i - j - 1].isalnum()) and \
                       (i == len(line) or not line[i].isalnum()):
                        m.append((l_m, i - j, line))
                else:
                    m.append((l_m, i - j, line))
                j = lps[j - 1]
            elif i < len(line) and pattern[j] != line[i]:
                if j != 0:
                    j = lps[j - 1]
                else:
                    i += 1
    return m

# GUI for word search

class WordSearchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("RAS Word Search Application")

        self.label = tk.Label(root, text="Enter word to search:")
        self.label.pack()

        self.search_entry = tk.Entry(root, width=40)
        self.search_entry.pack()

        self.w_var = tk.BooleanVar()
        self.c_s_var = tk.BooleanVar()

        self.w_check = tk.Checkbutton(root, text="Whole Word", variable=self.w_var)
        self.w_check.pack()

        self.c_s_check = tk.Checkbutton(root, text="Case Sensitive", variable=self.c_s_var)
        self.c_s_check.pack()

        self.load_button = tk.Button(root, text="Load Files", command=self.load_files)
        self.load_button.pack()

        self.search_button = tk.Button(root, text="Search", command=self.search_word)
        self.search_button.pack()

        self.result_t = tk.Text(root, height=20, width=80)
        self.result_t.pack()

        self.time_label_brute = tk.Label(root, text="Time Taken (Brute Force):")
        self.time_label_brute.pack()

        self.time_label_kmp = tk.Label(root, text="Time Taken (KMP):")
        self.time_label_kmp.pack()

        self.t_data = {}
        self.file_list = []

    def load_files(self):
        f_p = filedialog.askopenfilenames(filetypes=[("Text Files", "*.txt")])  # file paths
        
        if f_p:
            self.file_list = f_p
            self.t_data.clear()
            
            for file_path in f_p:
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        content = file.read()
                except UnicodeDecodeError:
                    with open(file_path, 'r', encoding='ISO-8859-1') as file:
                        content = file.read()

                if content.strip():  # Skip empty files
                    self.t_data[file_path] = content
                else:
                    messagebox.showwarning("Empty File", f"The file '{os.path.basename(file_path)}' is empty.")
            messagebox.showinfo("Files Loaded", "Files loaded successfully!")
        else:
            messagebox.showwarning("No Files", "No file selected.")

    def search_word(self):
        pattern = self.search_entry.get()
        w = self.w_var.get()
        c_s = self.c_s_var.get()

        if not pattern:
            messagebox.showerror("Error", "Please enter a search term.")
            return
            
        if not self.file_list:
            messagebox.showerror("Error", "Please load files to search.")
            return

        # Brute Force Search
        beginning_time = time.perf_counter()
        brute_results = self.search_in_files(BFS, pattern, w, c_s)
        brute_time = time.perf_counter() - beginning_time
        self.time_label_brute.config(text=f"Time Taken (Brute Force): {brute_time:.6f} seconds")

        # KMP Search
        beginning_time = time.perf_counter()
        kmp_results = self.search_in_files(kmp_search, pattern, w, c_s)
        kmp_time = time.perf_counter() - beginning_time
        self.time_label_kmp.config(text=f"Time Taken (KMP): {kmp_time:.6f} seconds")

        if not brute_results and not kmp_results:
            messagebox.showinfo("No Matches", "No matches found for the search term.")
        else:
            self.display_results(brute_results, kmp_results)

    def search_in_files(self, search_function, pattern, w, c_s):
        results = []
        for file_path, t in self.t_data.items():
            file_results = search_function(t, pattern, w, c_s)
            file_name = os.path.basename(file_path)  # Extract only the file name
            for l_m, col_num, line in file_results:
                results.append((file_name, l_m, col_num, line))
        return results

    def display_results(self, brute_results, kmp_results):
        self.result_t.delete(1.0, tk.END)

        self.result_t.insert(tk.END, "==================== Brute Force Results ====================\n", "title")
        for file, l_m, col_num, line in brute_results:
            self.result_t.insert(tk.END, f"\nFile Name: {file}\nLine Number: {l_m}\nRow Number: {l_m}  Column Number: {col_num}\nLine: {line}\n\n")

        self.result_t.insert(tk.END, "\n====================== KMP Results =======================\n", "title")
        for file, l_m, col_num, line in kmp_results:
            self.result_t.insert(tk.END, f"\nFile Name: {file}\nLine Number: {l_m}\nRow Number: {l_m}  Column Number: {col_num}\nLine: {line}\n\n")

        # Styling for title box
        self.result_t.tag_config("title", foreground="blue", font=("Helvetica", 12, "bold"))

# Main application execution
if __name__ == "__main__":
    root = tk.Tk()
    app = WordSearchApp(root)
    root.mainloop()

