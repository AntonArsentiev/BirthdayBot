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
        return self._translation[message][language]


if __name__ == "__main__":
    translator = Translator()
    print(translator.translate(message="ФИО", language="en"))
    print(translator.languages())
