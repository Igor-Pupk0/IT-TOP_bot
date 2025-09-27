import telebot

messages_pages = {}

class Pages():
    def __init__(self):
        self.page_list = []
        self.now_page = 1
        self.page_count = 0

    def add_page(self, text: str):
        self.page_list.append(text)
        self.page_count += 1

    def get_page(self):
        if self.now_page == 1:
            return self.page_list[0]
        return self.page_list[self.now_page - 1]
    
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
