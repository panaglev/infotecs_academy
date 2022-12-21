import re
from flask import Flask, make_response
from flask_restful import Api, Resource

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False # Нужно для корректной работы make_response
api = Api()


class searchByNumber(Resource):
    def get(self, number):
        """
        Принимает идентификационный номер города в качестве аргумента.
        Результатом отдает информацию об этом городе и извещение о том, что нам не известно о таком городе, если такого города нет.
        Usage: 127.0.0.1:8000/number/*geonameid* 
        Example: 127.0.0.1:8000/number/50841
        """
        with open("RU.txt", "r") as f:
            for line in f:
                parsedLine = line.strip().split()
                if int(parsedLine[0]) == number:
                    return make_response(parsedLine)
            else:
                return make_response(str("Нам не известно о таком городе"))


class printPages(Resource):
    def get(self, pagesToDisplay, pageNumber):
        """
        Функция первым аргументом берет количество страниц выводимых на странице, далее идет ключевое слово page
        для демонстрации, что переходим к странице. И последнее сам номер страницы который мы хотим вывести.
        Реализовано криво, как мне кажется, но лучшего, оптимизированного, способа не придумал.
        Usage: 127.0.0.1:8000/*количество страниц на вывод*/page/*номер страницы для вывода*
        Example: 127.0.0.1:8000/10/page/5
        """
        returnedList = []
        with open("RU.txt") as f:
            counter = 0
            for line in f:
                if pagesToDisplay * pageNumber <= counter:
                    if counter < pagesToDisplay * pageNumber + pagesToDisplay:
                        returnedList.append(line.strip().split())
                        counter += 1
                else:
                    counter += 1
        return make_response(returnedList)


class cityCompare(Resource):
    def get(self, city1, city2):
        """
        Принимает в качестве двух аргументов
        названия городов на русском языке(можно и на английском) в качестве
        результата возвращает информацию об этих городах, строку о том какой город
        находится севернее и совпадают ли временные зоны у этих городов, разницу между временными зонами
        Usage: 127.0.0.1:8000/city/*Название первого города*/*Название второго города*
        Example: 127.0.0.1:8000/city/Медведково/Чупрово
        """
        timezones_dict = {
            # Как это сделать не имея текстовый файл timeZone.txt(который указан в readme.txt) не знаю
            # и дополнительно про это ничего не сказано в ТЗ. Решил эту проблему таким образом. Словарь
            # был сформирон следующим образом: были спаршены все значения, и вручную(благо не так много),
            # составлены пары. Число являющееся значением означает разницу часов между этим городом и Москвой.
            # У некоторых городов не указана временная зона, в таких случаях мы выводим соответствующее сообщение. 
            "Asia/Anadyr": 9,
            "Asia/Kamchatka": 9,
            "Asia/Srednekolymsk": 8,
            "Asia/Sakhalin": 8,
            "Asia/Ust-Nera": 8,
            "Asia/Magadan": 8,
            "Asia/Khandyga": 7,
            "Asia/Vladivostok": 7,
            "Asia/Tokyo": 6,
            "Asia/Chita": 6,
            "Asia/Yakutsk": 6,
            "Asia/Ulaanbaatar": 5,
            "Asia/Shanghai": 5,
            "Asia/Irkutsk": 5,
            "Asia/Hovd": 4,
            "Asia/Novokuznetsk": 4,
            "Asia/Krasnoyarsk": 4,
            "Asia/Barnaul": 4,
            "Asia/Novosibirsk": 4,
            "Asia/Tomsk": 4,
            "Asia/Omsk": 3,
            "Asia/Almaty": 3,
            "Asia/Tashkent": 2,
            "Asia/Yekaterinburg": 2,
            "Asia/Qyzylorda": 2,
            "Europe/Samara": 1,
            "Asia/Baku": 1,
            "Europe/Ulyanovsk": 1,
            "Asia/Tbilisi": 1,
            "Europe/Saratov": 1,
            "Europe/Astrakhan": 1,
            "Europe/Volgograd": 0,
            "Europe/Moscow": 0,
            "Europe/Kirov": 0,
            "Europe/Minsk": 0,
            "Europe/Simferopol": 0,
            "Europe/Kyiv": -1,
            "Europe/Vilnius": -1,
            "Europe/Helsinki": -1,
            "Europe/Riga": -1,
            "Europe/Kaliningrad": -1,
            "Europe/Paris": -2,
            "Europe/Warsaw": -2,
            "Europe/Monaco": -2,
            "Europe/Oslo": -2,
            "Asia/Aqtobe": -2,
            "Asia/Ashgabat": -2,
        }

        reference1 = 0
        reference2 = 0
        parsedCity1 = 0
        parsedCity2 = 0
        timezoneDifference = 0
        cityOnTheNorth = ""
        doesTimezoneEqual = False

        with open("RU.txt", "r") as f:
            for line in f:
                parsedLine = line.strip().split()
                alternativeNames = list(
                    parsedLine[3].split(",")
                )  # Приводим спаршенную строчку к списку с элементами чтобы удобнее с ними работать
                if (city1 in alternativeNames) or (
                    city2 in alternativeNames
                ):  # (city1 or city2) in alternativeNames Вижу такую оптимизацию, но она не работает :(
                    try:
                        population = int(parsedLine[-5])
                    except:
                        population = 0
                    finally:
                        if (
                            city1 in alternativeNames
                        ):  # Находим город к которому относится найденная строчка и находим население чтобы выбрать город из множества
                            if reference1 < population:
                                reference1 = population
                                parsedCity1 = parsedLine
                            elif (reference1 > population) or (
                                reference1 == population
                            ):
                                pass
                        elif city2 in alternativeNames:
                            if reference2 < population:
                                parsedCity2 = parsedLine
                                reference2 = population
                            elif (reference2 > population) or (
                                reference2 == population
                            ):
                                pass
        # Определяем какой город находится севернее
        if float(parsedCity1[4]) > float(parsedCity2[4]):
            cityOnTheNorth = "Первый город находится севернее второго"
        elif float(parsedCity1[4]) < float(parsedCity2[4]):
            cityOnTheNorth = "Второй город находится севернее первого"
        else:
            cityOnTheNorth = "Широты обоих городов равны, ого"

        # Определяем в одной ли часовой зоне находятся города
        if parsedCity1[-2] == parsedCity2[-2]:
            doesTimezoneEqual = True
        else:
            doesTimezoneEqual = False

        # Определяем разницу временных зон
        if parsedCity1[-2].isdigit() or parsedCity2[-2].isdigit():
            timezoneDifference = (
                "У одного из представленных городов не указана временная зона"
            )
        else:
            timezoneDifference = abs(
                timezones_dict[parsedCity2[-2]] - timezones_dict[parsedCity1[-2]]
            )

        return make_response(
            [
                parsedCity1,
                parsedCity2,
                cityOnTheNorth,
                doesTimezoneEqual,
                timezoneDifference,
            ]
        )


class printCities(Resource):
    """
    Данный участок когда который возвращает список городов с возможными продолжениями. 
    re т.к. сокращение от regular expression
    Usage: 127.0.0.1:8000/re/*Неполное название города*
    Example: 127.0.0.1:8000/re/Медведково/Чупрово
    """
    def get(self, template):
        cities = []
        with open("RU.txt", "r") as f:
            for line in f:
                parsedLine = line.strip().split()
                citiesNames = list(parsedLine[3].split(","))
                for city in citiesNames:
                    cities.append(city)
        set(cities)
        r = re.compile(f"{template}*")
        returnedList = list(filter(r.match, cities))
        return make_response((list(set(returnedList))))


api.add_resource(searchByNumber, "/number/<int:number>")
api.add_resource(printPages, "/<int:pagesToDisplay>/page/<int:pageNumber>")
api.add_resource(cityCompare, "/city/<string:city1>/<string:city2>")
api.add_resource(printCities, "/re/<string:template>")
api.init_app(app)

if __name__ == "__main__":
    app.run(debug=True, port=8000, host="127.0.0.1")