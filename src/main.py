import json

from parsers import OtzyvParser


def main():
    reviews = OtzyvParser()._scrape()
    with open('reviews.json', 'w+', encoding='utf8') as jsonfile:
        json.dump(reviews, jsonfile, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    main()