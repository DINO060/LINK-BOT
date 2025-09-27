from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class VideoLink:
    url: str
    quality: Optional[str] = None
    format: Optional[str] = None
    size: Optional[int] = None
    
@dataclass
class ExtractResult:
    success: bool
    links: List[VideoLink]
    title: Optional[str] = None
    error: Optional[str] = None
    source: str = "unknown"

class BaseExtractor(ABC):
    """Classe de base pour tous les extracteurs"""
    
    def __init__(self):
        self.name = self.__class__.__name__
    
    @abstractmethod
    async def extract(self, url: str, query: str, lang: str = "vostfr") -> ExtractResult:
        """Méthode principale d'extraction"""
        pass
    
    @abstractmethod
    def can_handle(self, domain: str) -> bool:
        """Vérifie si l'extracteur peut gérer ce domaine"""
        pass
