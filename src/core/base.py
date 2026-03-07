from abc import ABC, abstractmethod
from typing import Optional

class NewspaperDownloader(ABC):
    @abstractmethod
    def download(self, date: str) -> None :
        pass


class Email(ABC):
    def __init__(self,username: str):
        self.username = username

    @abstractmethod
    def send(self,reciever: str,
             content: str,
             attachements: Optional[list[str]]=None
             )->None:
        """
        Send an email.

        :param receiver: Email address of the receiver
        :param content: Email body content
        :param attachments: Optional list of file-like objects
        """
        pass