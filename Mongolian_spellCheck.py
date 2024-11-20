from tkinter.scrolledtext import ScrolledText
import hunspell
import tkinter as tk
import re
# ru = hunspell.HunSpell('ru_RU.dic', 'ru_RU.aff')
mn = hunspell.HunSpell('mn_MN.dic', 'mn_MN.aff')
en = hunspell.HunSpell('en_US.dic', 'en_US.aff')


class SpellingChecker:
    def __init__(self):
        # Хэрэглэгчийн ажиллах цонх үүсгэх хэсэг
        self.root = tk.Tk()

        width = self.root.winfo_screenwidth()
        height = self.root.winfo_screenheight()
        self.root.geometry(f"{width}x{height}") # Дэлгэцний хэмжээний дагууд цонхны хэмжээг тохируулна
        self.root.title("Алдаа шалгагч")

        self.text = ScrolledText(self.root, font=("Arial", 14), wrap=tk.WORD)
        self.text.pack(expand=True, fill=tk.BOTH)

        self.bottom_frame = tk.Frame(self.root)
        self.bottom_frame.pack(fill=tk.X, side=tk.BOTTOM)

        self.stats_label = tk.Label(self.bottom_frame, text="Үгийн тоо: 0 | Алдсан үгийн тоо: 0")
        self.stats_label.pack(side=tk.BOTTOM)

        self.root.bind("<F6>", self.check_spelling)
        self.text.bind("<Motion>", self.show_suggestions)

        self.suggestion_menu = tk.Menu(self.text, tearoff=0)

        self.root.mainloop()

    def check_spelling(self, event=None):
        content = self.text.get("1.0", tk.END).strip()
        words = re.findall(r'\b\w+\b', content) #Цонхонд бичигдсэн бичвэрээс үг бүрийг салгаж авч words массивт оруулж байна
        total_words = len(words)
        misspelled_count = 0

        self.text.tag_remove("misspelled", "1.0", tk.END)

        for word in words:
            if not (mn.spell(word) or en.spell(word)): # or ru.spell(word)
                misspelled_count += 1
                start_idx = self.text.search(word, "1.0", tk.END)
                end_idx = f"{start_idx}+{len(word)}c"
                self.text.tag_add("misspelled", start_idx, end_idx)
                self.text.tag_config("misspelled", foreground="red", underline=True)

        self.stats_label.config(text=f"Үгийн тоо: {total_words} | Алдсан үгийн тоо: {misspelled_count}")

    def show_suggestions(self, event): # Буруу бичигдсэн үгэнд санал өөр үг санал болгох функц
        mouse_index = self.text.index(f"@{event.x},{event.y}")

        for tag in self.text.tag_names(mouse_index):
            if tag == "misspelled":
                word_start = self.text.index(f"{mouse_index} wordstart")
                word_end = self.text.index(f"{mouse_index} wordend")
                misspelled_word = self.text.get(word_start, word_end)

                suggestions = mn.suggest(misspelled_word) + en.suggest(misspelled_word) # + ru.suggest(misspelled_word)

                self.suggestion_menu.delete(0, tk.END)
                for suggestion in suggestions:
                    self.suggestion_menu.add_command(label=suggestion, command=lambda s=suggestion: self.replace_word(word_start, word_end, s))

                self.suggestion_menu.post(event.x_root, event.y_root)
                return

        self.suggestion_menu.unpost()

    def replace_word(self, start, end, new_word):
        self.text.delete(start, end)
        self.text.insert(start, new_word)

SpellingChecker()
