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
        if self.now_page + 1 > self.page_count:
            return False
        
        self.now_page += 1
        return self.get_page()
    
    def turn_left_page(self):
        if self.now_page - 1 <= 0:
            return False
        
        self.now_page -= 1
        return self.get_page()
