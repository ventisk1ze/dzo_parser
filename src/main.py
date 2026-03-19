import sys
import json

from parsers import OtzyvParser


def main():
    if sys.argv[1] == 'json':
        reviews = OtzyvParser(('2024-01-01', '2026-03-04'), True)._scrape()
        with open('reviews.json', 'w+', encoding='utf8') as jsonfile:
            json.dump(reviews, jsonfile, ensure_ascii=False, indent=4)
    elif sys.argv[1] == 'pd':
        reviews = OtzyvParser(('2024-01-01', '2026-03-04'), True).parse()
        reviews.to_csv('reviews.csv')


if __name__ == '__main__':
    main()