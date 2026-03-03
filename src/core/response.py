from dataclasses import dataclass


@dataclass
class Response:
    date: str
    text: str
    rating: str
    respondent: str