from mjc import Client
from mjc.helpers import Term, Subject


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    client = Client()
    client.get_courses(Term.spring_2021)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
