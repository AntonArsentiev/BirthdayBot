from bs4 import BeautifulSoup


class Translator:
    def __init__(self, file="translation.xml"):
        self._languages = {}
        self._translation = {}
        self._read_translation(file)

    def _read_translation(self, file):
        with open(file, "r", encoding="utf-8") as file:
            soup = BeautifulSoup(file.read(), "xml")
            languages = soup.find_all("Language")
            for language in languages:
                attributes = language.attrs
                self._languages[attributes["code"]] = attributes["name"]
            messages = soup.find_all("Message")
            for message in messages:
                attributes = message.attrs
                self._translation[attributes["ru"]] = attributes

    def languages(self):
        return self._languages

    def translate(self, message, language):
        return self._translation[message][language].replace("\\n", "\n")


if __name__ == "__main__":
    translator = Translator()
    print(translator.translate(message="У твоего друга менее чем через неделю день рождения!\\n\\n"
                                       "{fio} исполнится {age}!\\n\\n" 
                                       "Приготовь хороший подарок, надеюсь ты знаешь что бы он хотел! "
                                       "Не забудь поздравить именинника и постарайся "
                                       "сделать его день рождения незабываемым!", language="en"))
    # print(translator.languages())

    # import json
    # dicty_1 = {
    #     'anton': 1,
    #     'egor': [
    #         1, 2, 3
    #     ],
    #     'vitya': {
    #         'name': 'victor',
    #         'familia': 'gordeev'
    #     }
    # }
    # print(dicty_1)
    # js_str = json.dumps(dicty_1)
    # print(js_str)
    # dicty_2 = json.loads(js_str)
    # print(dicty_2)
    # print(dicty_2['vitya'])

