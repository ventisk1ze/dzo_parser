from typing import List
from dataclasses import dataclass


from .response import Response

@dataclass
class Review:
    id: str # уникальный номер 
    created_date: str # время публикации
    title: str # заголовок
    url: str # ссылка
    source: str # наименование ресурса
    text: str # текст отзыва
    download_date: str # дата загрузки
    author: str # автор
    address: str # адрес (если есть)
    rating: str # рейтинг
    response: List[Response] # ответ
    company_name: str # наименование ДЗО
    tags: str # тэги