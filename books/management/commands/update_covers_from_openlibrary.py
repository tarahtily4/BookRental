import time
import re
import logging
from typing import Any, Dict, List, Optional, Tuple, Iterable
from urllib.parse import urlencode

import requests
from django.core.management.base import BaseCommand
from django.db import transaction

from books.models import Book

log = logging.getLogger(__name__)

OPENLIB_SEARCH = "https://openlibrary.org/search.json"
COVER_BY_ISBN = "https://covers.openlibrary.org/b/isbn/{isbn}-L.jpg?default=false"
COVER_BY_ID = "https://covers.openlibrary.org/b/id/{cover_id}-L.jpg?default=false"

def norm(s: str) -> str:
    if not s:
        return ""
    s = s.lower()
    s = re.sub(r"[^0-9a-zа-яіїєґёыэùáéíóúäöüßç\-'\s]", " ", s, flags=re.I)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def drop_parentheses(s: str) -> str:
    return re.sub(r"\s*\([^)]*\)\s*", " ", s or "").strip()

def drop_subtitle(s: str) -> str:
    return re.split(r"[:–—\-]\s", s or "", maxsplit=1)[0].strip()

def words_set(s: str) -> set:
    return set(norm(s).split())

def jaccard(a: str, b: str) -> float:
    sa, sb = words_set(a), words_set(b)
    if not sa or not sb:
        return 0.0
    inter = len(sa & sb)
    union = len(sa | sb)
    return inter / union if union else 0.0

TRANSLIT = str.maketrans({
    "ї":"i","є":"ie","ґ":"g","і":"i","й":"i","ю":"iu","я":"ia","ш":"sh","щ":"shch","ж":"zh","х":"kh","ч":"ch","ь":"",
    "Ї":"I","Є":"Ie","Ґ":"G","І":"I","Й":"I","Ю":"Iu","Я":"Ia","Ш":"Sh","Щ":"Shch","Ж":"Zh","Х":"Kh","Ч":"Ch","Ь":"",
    "’":"'", "ʼ":"'", "‘":"'", "’":"'", "“":'"', "”":'"'
})

def translit_uk(s: str) -> str:
    return (s or "").translate(TRANSLIT)

TITLE_SYNONYMS: Dict[str, List[str]] = {
    "тіні забутих предків": ["shadows of forgotten ancestors"],
    "захар беркут": ["zakhar berkut"],
    "три товариші": ["three comrades"],
    "маленький принц": ["the little prince", "le petit prince"],
    "сто років самотності": ["one hundred years of solitude", "cien años de soledad"],
    "алхімік": ["the alchemist"],
    "атлант розправив плечі": ["atlas shrugged"],
    "пастка 22": ["catch-22", "catch 22"],
    "над прірвою у житі": ["the catcher in the rye"],
    "sapiens. людина розумна": ["sapiens"],
    "психологія впливу": ["influence", "influence: the psychology of persuasion"],
    "думай повільно вирішуй швидко": ["thinking, fast and slow", "thinking fast and slow"],
    "чорний лебідь": ["the black swan"],
    "атомні звички": ["atomic habits"],
    "пікнік на узбіччі": ["roadside picnic"],
    "трилогія про земномор'я": ["earthsea", "a wizard of earthsea"],
    "володар перснів братство персня": ["the fellowship of the ring"],
    "451° за фаренгейтом": ["fahrenheit 451"],
    "гаррі поттер і філософський камінь": ["harry potter and the philosopher's stone", "harry potter and the sorcerer's stone"],
    "пеппі довгапанчоха": ["pippi longstocking"],
    "хроніки нарнії лев чаклунка і платтяна шафа": ["the lion the witch and the wardrobe"],
    "rework бізнес без забобонів": ["rework"],
    "від нуля до одиниці": ["zero to one"],
    "доставка щастя": ["delivering happiness"],
    "злочин і кара": ["crime and punishment"],
    "анна кареніна": ["anna karenina"],
    "портрет доріана ґрея": ["the picture of dorian gray"],
}

AUTHOR_SYNONYMS: Dict[str, List[str]] = {
    "михайло коцюбинський": ["mykhailo kotsiubynsky", "mikhailo kotsyubynsky", "mikhail kotsyubinsky"],
    "валер'ян підмогильний": ["valerian pidmohylny", "valerian pidmogilny"],
    "леся українка": ["lesia ukrayinka", "lesya ukrainka"],
    "ремарк": ["erich maria remarque"],
    "джордж орвелл": ["george orwell"],
    "антуан де сент-екзюпері": ["antoine de saint-exupéry", "antoine de saint exupery"],
    "ґабріель ґарсія маркес": ["gabriel garcia marquez"],
    "пауло коельйо": ["paulo coelho"],
    "айн ренд": ["ayn rand"],
    "джозеф геллер": ["joseph heller"],
    "джером селінджер": ["j d salinger", "jerome david salinger", "j.d. salinger"],
    "юваль харарі": ["yuval noah harari"],
    "роберт чалдині": ["robert cialdini"],
    "даніель канеман": ["daniel kahneman"],
    "насім тале̄б": ["nassim nicholas taleb", "nassim n taleb"],
    "джеймс клір": ["james clear"],
    "стругацькі": ["arkady strugatsky", "boris strugatsky", "arkady and boris strugatsky"],
    "урсула ле ґуїн": ["ursula k le guin", "ursula le guin"],
    "джон рональд руел толкін": ["j r r tolkien", "j.r.r. tolkien"],
    "рей бредбері": ["ray bradbury"],
    "джоан ролінґ": ["j k rowling", "j.k. rowling"],
    "астрід ліндґрен": ["astrid lindgren"],
    "клайв стейплз льюїс": ["c s lewis", "c.s. lewis", "clive staples lewis"],
    "джейсон фрайд": ["jason fried"],
    "петер тієль": ["peter thiel"],
    "тоні шей": ["tony hsieh"],
    "федір достоєвський": ["fyodor dostoevsky"],
    "лев толстой": ["leo tolstoy", "lev tolstoy"],
    "оскар уайльд": ["oscar wilde"],
}

def score_doc(doc: Dict[str, Any], title: str, author: str) -> Tuple[int, Optional[str]]:
    ol_title = doc.get("title") or ""
    ol_author_list = doc.get("author_name") or []
    isbns = doc.get("isbn") or []
    cover_i = doc.get("cover_i")
    year = doc.get("first_publish_year")

    score = 0
    t_norm, t_ol_norm = norm(title), norm(ol_title)
    if not t_norm or not t_ol_norm:
        return 0, None

    if t_norm == t_ol_norm:
        score += 9
    else:
        sim = jaccard(title, ol_title)
        if sim >= 0.85:
            score += 7
        elif sim >= 0.7:
            score += 5
        elif t_norm in t_ol_norm or t_ol_norm in t_norm:
            score += 3

    if author and ol_author_list:
        best_author = max(jaccard(author, a) for a in ol_author_list)
        if best_author >= 0.8:
            score += 5
        elif best_author >= 0.6:
            score += 3
        elif best_author >= 0.4:
            score += 1

    cover_url = None
    if isbns:
        cover_url = COVER_BY_ISBN.format(isbn=isbns[0])
        score += 6
    elif cover_i:
        cover_url = COVER_BY_ID.format(cover_id=cover_i)
        score += 3

    if isinstance(year, int) and 1800 <= year <= 2035:
        score += 1

    return score, cover_url

def pick_best_cover(docs: List[Dict[str, Any]], title: str, author: str) -> Optional[str]:
    best_url = None
    best_score = -1
    for d in docs:
        s, url = score_doc(d, title, author)
        if url and s > best_score:
            best_score = s
            best_url = url
    return best_url if best_score >= 6 else None

def fetch_docs(session: requests.Session, params: Dict[str, Any], timeout: float, headers: Dict[str, str]) -> List[Dict[str, Any]]:
    url = f"{OPENLIB_SEARCH}?{urlencode(params)}"
    resp = session.get(url, timeout=timeout, headers=headers)
    resp.raise_for_status()
    data = resp.json()
    return data.get("docs") or []

def gen_queries(title: str, author: str, max_results: int) -> Iterable[Tuple[Dict[str, Any], str]]:
    t0 = (title or "").strip()
    a0 = (author or "").strip()

    t_no_par = drop_parentheses(t0)
    t_core = drop_subtitle(t_no_par)
    t_norm = norm(t_core)

    a_norm = norm(a0)
    a_trans = translit_uk(a0)
    a_trans_norm = norm(a_trans)

    synonym_titles = TITLE_SYNONYMS.get(t_norm, [])
    synonym_authors = AUTHOR_SYNONYMS.get(a_norm, [])

    yield ({"title": t0, "author": a0, "limit": max_results}, "t+a")
    if t_no_par != t0:
        yield ({"title": t_no_par, "author": a0, "limit": max_results}, "t(no-par)+a")
    if t_core != t_no_par:
        yield ({"title": t_core, "author": a0, "limit": max_results}, "t(core)+a")

    if a_trans and a_trans_norm != a_norm:
        yield ({"title": t_core, "author": a_trans, "limit": max_results}, "t(core)+a(trans)")

    for t_syn in synonym_titles:
        yield ({"title": t_syn, "author": a0, "limit": max_results}, "t(syn)+a")
        if synonym_authors:
            for a_syn in synonym_authors:
                yield ({"title": t_syn, "author": a_syn, "limit": max_results}, "t(syn)+a(syn)")

    yield ({"title": t_core, "limit": max_results}, "t-only")
    for t_syn in synonym_titles:
        yield ({"title": t_syn, "limit": max_results}, "t(syn)-only")

    q1 = f"{t_core} {a0}".strip()
    yield ({"q": q1, "limit": max_results}, "q(title+author)")
    if synonym_titles:
        yield ({"q": f"{synonym_titles[0]} {a0}".strip(), "limit": max_results}, "q(t_syn+author)")
    if synonym_authors:
        yield ({"q": f"{t_core} {synonym_authors[0]}".strip(), "limit": max_results}, "q(title+a_syn)")

class Command(BaseCommand):
    help = (
        "Подбирает корректные обложки через OpenLibrary Search API и пишет в cover_url.\n"
        "Делает каскад запросов (title/author/синонимы/транслит), приоритет: ISBN → cover_i.\n"
        "Добавлен фильтр ?default=false для обложек, чтобы не получать пустые заглушки."
    )

    def add_arguments(self, parser):
        parser.add_argument("--force", action="store_true", help="Обновлять даже если cover_url уже заполнен.")
        parser.add_argument("--only-empty", action="store_true", help="Только те книги, где cover_url пустой (по умолчанию так и есть).")
        parser.add_argument("--limit", type=int, default=0, help="Ограничить число обрабатываемых книг.")
        parser.add_argument("--sleep", type=float, default=0.2, help="Пауза между запросами к API (сек).")
        parser.add_argument("--timeout", type=float, default=10.0, help="Timeout HTTP запросов (сек).")
        parser.add_argument("--dry-run", action="store_true", help="Показывать изменения, но не сохранять в БД.")
        parser.add_argument("--max-results", type=int, default=20, help="Сколько документов брать у OpenLibrary (на попытку).")

    def handle(self, *args, **opts):
        force: bool = opts["force"]
        only_empty: bool = opts["only_empty"] or not force
        limit: int = opts["limit"]
        pause: float = opts["sleep"]
        timeout: float = opts["timeout"]
        dry: bool = opts["dry_run"]
        max_results: int = max(5, min(50, opts["max_results"]))

        qs = Book.objects.all().order_by("id")
        if only_empty:
            qs = qs.filter(cover_url="") | qs.filter(cover_url__isnull=True)
        if not force:
            qs = qs.exclude(cover__isnull=False).exclude(cover__exact="")

        if limit > 0:
            qs = qs[:limit]

        total = qs.count()
        updated = 0
        skipped = 0
        failed = 0

        self.stdout.write(self.style.MIGRATE_HEADING(f"Найдено книг для обработки: {total}"))

        session = requests.Session()
        headers = {"User-Agent": "BookRental/2.0 (OpenLibrary covers sync)"}

        for book in qs:
            title = (book.title or "").strip()
            author = (book.author or "").strip()

            if not title:
                skipped += 1
                self.stdout.write(f"↷ {book.id} пропуск: пустой title")
                continue

            if book.cover_url and not force:
                skipped += 1
                self.stdout.write(f"↷ {book.id} пропуск: уже есть cover_url")
                continue

            best_cover: Optional[str] = None
            used_label: str = ""
            last_reason: str = ""

            try:
                for params, label in gen_queries(title, author, max_results):
                    docs = fetch_docs(session, params, timeout, headers)
                    if not docs:
                        last_reason = f"нет результатов [{label}]"
                        time.sleep(pause)
                        continue

                    candidate = pick_best_cover(docs, params.get("title") or params.get("q") or title, params.get("author") or author)
                    if candidate:
                        best_cover = candidate
                        used_label = label
                        break
                    else:
                        last_reason = f"низкий скоринг [{label}]"
                    time.sleep(pause)

                if not best_cover:
                    failed += 1
                    self.stderr.write(self.style.WARNING(f"✖ {book.id} {book.title}: не удалось подобрать ({last_reason or 'не найдено'})"))
                    continue

                if dry:
                    self.stdout.write(f"[DRY] {book.id} {book.title} -> {best_cover} ({used_label})")
                else:
                    with transaction.atomic():
                        Book.objects.filter(pk=book.pk).update(cover_url=best_cover)
                    updated += 1
                    self.stdout.write(f"✔ {book.id} {book.title} -> {best_cover} ({used_label})")

            except requests.HTTPError as e:
                failed += 1
                self.stderr.write(self.style.WARNING(f"HTTP {e.response.status_code} для '{book.title}': {e}"))
            except Exception as e:
                failed += 1
                self.stderr.write(self.style.WARNING(f"Ошибка для '{book.title}': {e}"))

            time.sleep(pause)

        self.stdout.write(self.style.SUCCESS(
            f"Готово. Обработано: {total}, обновлено: {updated}, пропущено: {skipped}, ошибок: {failed}"
        ))
