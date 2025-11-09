from dataclasses import dataclass


@dataclass
class Track:
    url: str = None
    source: str = None
    title: str = None
    artist: str = None
    duration: int = None
    img_url: str = None
    preview_url: str = None

    @property
    def as_dict(self):
        return {
            'url': self.url,
            'previewUrl': self.preview_url,
            'title': self.title,
            'artist': self.artist,
            'coverUrl': self.img_url,
            'durationSec': self.duration,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)
