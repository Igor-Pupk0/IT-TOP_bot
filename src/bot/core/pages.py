import telebot
messages_pages = {}

class Pages():
    def __init__(self):
        self.page_list = []
        self.now_page = 1
        self.page_count = 0

    def add_page(self, text: str, metadata = None):
        self.page_list.append({"text": text, "metadata": metadata})
        self.page_count += 1

    def get_page(self):
        if self.now_page == 1:
            return self.page_list[0]["text"]
        return self.page_list[self.now_page - 1]["text"]
    
    def get_page_metadata(self):
        if self.now_page == 1:
            return self.page_list[0]["metadata"]
        return self.page_list[self.now_page - 1]["metadata"]
    
    def turn_right_page(self):
        
        if 'debug_page' == self.get_next_page():
            debug_page_index = self.now_page
            self.now_page += 1
            debug_page = self.get_debug_page()
            dp_func: function = debug_page['metadata']['invoke_function']
            dp_func_args = debug_page['metadata']['invoke_function_args']
            dp_func(*dp_func_args)
            self.delete_page(debug_page_index)
            return self.get_page()

        if self.now_page + 1 > self.page_count:
            return False

        else:
            self.now_page += 1

        return self.get_page()
    
    def turn_left_page(self):
        if self.now_page - 1 <= 0:
            return False

        self.now_page -= 1
        return self.get_page()
    
    def add_debug_page(self, metadata = None):

        self.page_list.append({"text": 'debug_page', "metadata": metadata})

    def get_debug_page(self):
        if 'debug_page' not in self.get_page():
            raise Exception("Not debug page")
        if self.now_page == 1:
            return self.page_list[0]
        return self.page_list[self.now_page - 1]
    
    def delete_page(self, page_index):
        self.page_list.pop(page_index)

    def get_next_page(self):
        try:
            return self.page_list[self.now_page]["text"]
        except IndexError:
            pass


class Keyboard_pages(Pages):
    def add_page(self, keyboard: telebot.types.InlineKeyboardMarkup, metadata = None):
        self.page_list.append({"keyboard": keyboard, "metadata": metadata})
        self.page_count += 1

    def get_page(self):
        if self.now_page == 1:
            return self.page_list[0]["keyboard"]
        return self.page_list[self.now_page - 1]["keyboard"]
    
    def get_page_metadata(self):
        if self.now_page == 1:
            return self.page_list[0]["metadata"]
        return self.page_list[self.now_page - 1]["metadata"]
    
    def turn_right_page(self):
        if self.now_page + 1 > self.page_count:
            return False
        
        self.now_page += 1
        return self.get_page()
        
    def turn_left_page(self):
        if self.now_page - 1 <= 0:
            return False
        
        self.now_page -= 1
        return self.get_page()

