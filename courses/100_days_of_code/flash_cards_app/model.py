from datetime import datetime
import os
import os.path as osp
from typing import Union
from dataclasses import dataclass, field, asdict
from pathlib import Path
from json import load, dump
from string import ascii_letters, digits



ROOT = osp.dirname(__file__)
PROJECTS_DIR = Path(osp.join(ROOT, '.projects'))
try: os.mkdir(PROJECTS_DIR)
except FileExistsError: pass
DATE_FMT = '%m-%d-%Y %H:%M:%S.%f'
VALID_CHARS = frozenset(''.join((ascii_letters, digits, ' -_')))
TODAY = datetime.now().date()



def datetime_from_str(date: str) -> datetime:
    return datetime.strptime(date, DATE_FMT)

def str_from_datetime(date: datetime) -> str:
    return date.strftime(DATE_FMT)

@dataclass
class Card:

    name: str
    fimg: str
    ftxt: str
    bimg: str
    btxt: str
    creation: datetime = field(default_factory=datetime.now)
    num_revisions: int = 0
    last_revision: datetime = None
    learned: bool = False

    @staticmethod
    def parse_card_dict(card_dict: dict[str, object]) -> dict[str, object]:
        card_dict['creation'] = datetime_from_str(card_dict['creation'])
        if card_dict['last_revisition'] is not None:
            card_dict['last_revisition'] = datetime_from_str(
                card_dict['last_revisition'])

    @classmethod
    def from_dict(cls, card_dict: dict[str, object]) -> 'Card':
        cls.parse_card_dict(card_dict)
        return Card(**card_dict)



def dump_default(obj: object) -> str:
    if isinstance(obj, Path):
        return str(obj.resolve())
    elif isinstance(obj, datetime):
        return str_from_datetime(obj)
    else:
        raise TypeError(
            'Object of type %s is not JSON serializable' %type(obj).__name__)

@dataclass
class Project:

    name: str
    creation: datetime = field(default_factory=datetime.now)
    cards: dict[str, Card] = field(default_factory=dict)
    save_dir: str = None
    imgs_dir: str = None

    def __post_init__(self):
        if not self.save_dir:
            self.save_dir = PROJECTS_DIR / self.name.replace(' ', '-')
            self.imgs_dir = self.save_dir / 'imgs'
        elif not self.imgs_dir:
            self.save_dir = Path(self.save_dir)
            self.imgs_dir = self.save_dir / 'imgs'
        else:
            self.save_dir = Path(self.save_dir)
            self.imgs_dir = Path(self.imgs_dir)
        self.imgs_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def parse_project_dict(
            project_dict: dict[str, object]) -> dict[str, object]:
        project_dict['creation'] = datetime_from_str(project_dict['creation'])
        project_dict['cards'] = {
            name: Card.from_dict(card)
            for name, card in project_dict['cards'].items()}

    @classmethod
    def from_dict(cls, project_dict: dict[str, object]) -> 'Project':
        cls.parse_project_dict(project_dict)
        return Project(**project_dict)

    @classmethod
    def from_file(cls, project_json: Union[str, Path]) -> 'Project':
        with open(str(project_json), mode='br') as json_file:
            return cls.from_dict(load(json_file))

    def save(self):
        with open(self.save_dir / 'project.json', mode='w') as proj_file:
            dump(asdict(self), proj_file, default=dump_default, indent=4)

    def delete(self):
        os.rename(
            self.save_dir,
            self.save_dir.parent / 'trash' / self.save_dir.name)



def get_project_files() -> list[str]:
    projects_files = []
    for item in os.listdir(PROJECTS_DIR):
        project = osp.join(PROJECTS_DIR, item, 'project.json')
        if osp.isfile(project):
            projects_files.append(project)
    return projects_files

def load_projects() -> list[Project]:
    return [Project.from_file(f) for f in get_project_files()]

def is_valid_name(name: str) -> bool:
    return not (frozenset(name) - VALID_CHARS)

def card_score(card: Card) -> int:
    score = 0 if card.learned else 100  # starting score
    # number of days since last revision complement
    if card.num_revisions:
        # number of revisions penalty
        score = score * 0.98 ** card.num_revisions
        days_since_revision = max(0, (TODAY - card.last_revision.date()).days)
    else:
        days_since_revision = 0
    # polygonal function complement:
    # from 0 to 14 days (2 weeks), each day increments the score by 2
    # past 14 days, each day increments the score by 0.5
    if days_since_revision > 14:
        score += 100 + (days_since_revision - 14) * 2
    else:
        score += (100 / 14) * days_since_revision
    return round(score)

def project_progress(project: Project):
    last_studied = None
    learned_total = 0
    reviewed_today = 0
    learned_today = 0
    for card in project.cards.values():
        learned_total += card.learned
        try:
            if card.last_revision > last_studied:
                last_studied = card.last_revision
        except TypeError:
            pass
        if card.last_revision.date() == TODAY:
            reviewed_today += 1
            if card.learned:
                learned_today += 1
    progress = 100 * learned_total / len(project.cards)
    return {'last_studied': last_studied,
            'reviewed_today': reviewed_today,
            'learned_today': learned_today,
            'progress': progress}

def get_revision_groups(cards: list[Card]) -> tuple[list[tuple[Card, int]]]:
    learned = []
    reviewed = []
    to_review = []
    for card in cards:
        score = card_score(card)
        if card.learned:
            learned.append((card, score))
        elif card.last_revision.date() == TODAY:
            reviewed.append((card, score))
        else:
            to_review.append((card, score))
    learned.sort(key=lambda pair: pair[1], reverse=True)
    reviewed.sort(key=lambda pair: pair[1], reverse=True)
    to_review.sort(key=lambda pair: pair[1], reverse=True)
    return to_review, reviewed, learned

def add_to_revision_group(
        card: Card, revision_group: list[tuple[Card, int]]) -> int:
    score = card_score(card)
    for i, (_, gcard_score) in enumerate(revision_group):
        if gcard_score < score:
            revision_group.insert(i, card)
            return i
    revision_group.append(card)
    return len(revision_group) - 1
