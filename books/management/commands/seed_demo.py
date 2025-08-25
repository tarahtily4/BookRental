from django.core.management.base import BaseCommand
from books.models import Category, Book, BookStock
from books.utils import make_slug


class Command(BaseCommand):
    help = "Заповнює демо-даними: категорії, книги, залишки на складі"

    def handle(self, *args, **options):
        data = {
            "Художня література": [
                {
                    "title": "Тіні забутих предків",
                    "author": "Михайло Коцюбинський",
                    "pages": 240,
                    "cover_url": "https://covers.openlibrary.org/b/id/10523364-L.jpg",
                    "description": "Класична повість про кохання Івана та Марічки.",
                    "stocks": {"NEW": 3, "USED": 5, "FRAGILE": 1},
                },
                {
                    "title": "Місто",
                    "author": "Валер'ян Підмогильний",
                    "pages": 320,
                    "cover_url": "https://covers.openlibrary.org/b/id/12648742-L.jpg",
                    "description": "Становлення Степана Радченка у великому місті.",
                    "stocks": {"NEW": 2, "USED": 4, "FRAGILE": 0},
                },
                {
                    "title": "Кобзар",
                    "author": "Тарас Шевченко",
                    "pages": 416,
                    "cover_url": "https://covers.openlibrary.org/b/id/7222241-L.jpg",
                    "description": "Найвідоміша збірка поезій Шевченка.",
                    "stocks": {"NEW": 4, "USED": 3, "FRAGILE": 0},
                },
                {
                    "title": "Захар Беркут",
                    "author": "Іван Франко",
                    "pages": 232,
                    "cover_url": "https://covers.openlibrary.org/b/id/11053271-L.jpg",
                    "description": "Повість про громаду Тухлі та її боротьбу.",
                    "stocks": {"NEW": 2, "USED": 5, "FRAGILE": 1},
                },
                {
                    "title": "Лісова пісня",
                    "author": "Леся Українка",
                    "pages": 192,
                    "cover_url": "https://covers.openlibrary.org/b/id/11108792-L.jpg",
                    "description": "Драма-феєрія про Мавку і Лукаша.",
                    "stocks": {"NEW": 3, "USED": 3, "FRAGILE": 0},
                },
                {
                    "title": "Три товариші",
                    "author": "Еріх Марія Ремарк",
                    "pages": 496,
                    "cover_url": "https://covers.openlibrary.org/b/id/9874270-L.jpg",
                    "description": "Дружба, кохання і повоєнна Німеччина.",
                    "stocks": {"NEW": 2, "USED": 4, "FRAGILE": 0},
                },
                {
                    "title": "1984",
                    "author": "Джордж Оруелл",
                    "pages": 328,
                    "cover_url": "https://covers.openlibrary.org/b/id/15354102-L.jpg",
                    "description": "Антиутопія про тоталітаризм і контроль.",
                    "stocks": {"NEW": 3, "USED": 3, "FRAGILE": 0},
                },
                {
                    "title": "Маленький принц",
                    "author": "Антуан де Сент-Екзюпері",
                    "pages": 112,
                    "cover_url": "https://covers.openlibrary.org/b/id/9259251-L.jpg",
                    "description": "Притча про дружбу, відповідальність і любов.",
                    "stocks": {"NEW": 5, "USED": 5, "FRAGILE": 0},
                },
                {
                    "title": "Сто років самотності",
                    "author": "Габріель Гарсія Маркес",
                    "pages": 432,
                    "cover_url": "https://covers.openlibrary.org/b/id/8371956-L.jpg",
                    "description": "Сага родини Буендіа і місто Макондо.",
                    "stocks": {"NEW": 2, "USED": 2, "FRAGILE": 0},
                },
                {
                    "title": "Алхімік",
                    "author": "Пауло Коельйо",
                    "pages": 208,
                    "cover_url": "https://covers.openlibrary.org/b/id/240727-L.jpg",
                    "description": "Притча про шлях до своєї Мети.",
                    "stocks": {"NEW": 3, "USED": 4, "FRAGILE": 0},
                },
                {
                    "title": "Атлант розправив плечі",
                    "author": "Айн Ренд",
                    "pages": 1200,
                    "cover_url": "https://covers.openlibrary.org/b/id/8231991-L.jpg",
                    "description": "Масштабний філософський роман.",
                    "stocks": {"NEW": 1, "USED": 2, "FRAGILE": 0},
                },
                {
                    "title": "Пастка-22",
                    "author": "Джозеф Геллер",
                    "pages": 544,
                    "cover_url": "https://covers.openlibrary.org/b/id/8232006-L.jpg",
                    "description": "Сатира на абсурдність війни та бюрократії.",
                    "stocks": {"NEW": 2, "USED": 3, "FRAGILE": 0},
                },
                {
                    "title": "Над прірвою у житі",
                    "author": "Дж. Д. Селінджер",
                    "pages": 288,
                    "cover_url": "https://covers.openlibrary.org/b/id/8226191-L.jpg",
                    "description": "Історія підлітка Голдена Колфілда.",
                    "stocks": {"NEW": 3, "USED": 3, "FRAGILE": 0},
                },
            ],

            "Нехудожня": [
                {
                    "title": "Чому нації занепадають",
                    "author": "Дарон Аджемоґлу; Джеймс Робінсон",
                    "pages": 544,
                    "cover_url": "https://covers.openlibrary.org/b/id/14817678-L.jpg",
                    "description": "Про інститути, владу і процвітання.",
                    "stocks": {"NEW": 1, "USED": 2, "FRAGILE": 0},
                },
                {
                    "title": "Sapiens. Людина розумна",
                    "author": "Юваль Ной Харарі",
                    "pages": 512,
                    "cover_url": "https://covers.openlibrary.org/b/id/8378821-L.jpg",
                    "description": "Коротка історія людства.",
                    "stocks": {"NEW": 3, "USED": 3, "FRAGILE": 0},
                },
                {
                    "title": "Психологія впливу",
                    "author": "Роберт Чалдіні",
                    "pages": 336,
                    "cover_url": "https://covers.openlibrary.org/b/id/240163-L.jpg",
                    "description": "Класика про механізми переконання.",
                    "stocks": {"NEW": 2, "USED": 3, "FRAGILE": 0},
                },
                {
                    "title": "Думай повільно… вирішуй швидко",
                    "author": "Даніель Канеман",
                    "pages": 512,
                    "cover_url": "https://covers.openlibrary.org/b/id/10523360-L.jpg",
                    "description": "Дві системи мислення і наші помилки.",
                    "stocks": {"NEW": 2, "USED": 3, "FRAGILE": 0},
                },
                {
                    "title": "Чорний лебідь",
                    "author": "Насім Ніколас Талеб",
                    "pages": 480,
                    "cover_url": "https://covers.openlibrary.org/b/id/8231642-L.jpg",
                    "description": "Про рідкісні події з великими наслідками.",
                    "stocks": {"NEW": 2, "USED": 2, "FRAGILE": 0},
                },
                {
                    "title": "Атомні звички",
                    "author": "Джеймс Клір",
                    "pages": 320,
                    "cover_url": "https://covers.openlibrary.org/b/id/11122691-L.jpg",
                    "description": "Як маленькі зміни дають великі результати.",
                    "stocks": {"NEW": 3, "USED": 3, "FRAGILE": 0},
                },
            ],

            "Фантастика": [
                {
                    "title": "Пікнік на узбіччі",
                    "author": "Аркадій та Борис Стругацькі",
                    "pages": 224,
                    "cover_url": "https://covers.openlibrary.org/b/id/8232100-L.jpg",
                    "description": "Класика фантастики про Зону і сталкерів.",
                    "stocks": {"NEW": 2, "USED": 4, "FRAGILE": 0},
                },
                {
                    "title": "Дюна",
                    "author": "Френк Герберт",
                    "pages": 688,
                    "cover_url": "https://covers.openlibrary.org/b/id/12886142-L.jpg",
                    "description": "Епопея про пустельну планету Арракіс.",
                    "stocks": {"NEW": 2, "USED": 3, "FRAGILE": 0},
                },
                {
                    "title": "Трилогія про Земномор'я",
                    "author": "Урсула Ле Ґуїн",
                    "pages": 560,
                    "cover_url": "https://covers.openlibrary.org/b/id/9875001-L.jpg",
                    "description": "Маг Гед і світ архіпелагів.",
                    "stocks": {"NEW": 1, "USED": 3, "FRAGILE": 0},
                },
                {
                    "title": "Володар перснів: Братство Персня",
                    "author": "Дж. Р. Р. Толкін",
                    "pages": 576,
                    "cover_url": "https://covers.openlibrary.org/b/id/8232088-L.jpg",
                    "description": "Початок подорожі до Ородруїну.",
                    "stocks": {"NEW": 2, "USED": 2, "FRAGILE": 0},
                },
                {
                    "title": "451° за Фаренгейтом",
                    "author": "Рей Бредбері",
                    "pages": 256,
                    "cover_url": "https://covers.openlibrary.org/b/id/8228694-L.jpg",
                    "description": "Світ, де спалюють книги.",
                    "stocks": {"NEW": 3, "USED": 3, "FRAGILE": 0},
                },
            ],

            "Дитяча література": [
                {
                    "title": "Гаррі Поттер і філософський камінь",
                    "author": "Дж. К. Ролінґ",
                    "pages": 352,
                    "cover_url": "https://covers.openlibrary.org/b/id/7884866-L.jpg",
                    "description": "Початок пригод Гаррі в Гоґвортсі.",
                    "stocks": {"NEW": 4, "USED": 4, "FRAGILE": 0},
                },
                {
                    "title": "Пеппі Довгапанчоха",
                    "author": "Астрід Ліндґрен",
                    "pages": 160,
                    "cover_url": "https://covers.openlibrary.org/b/id/8244158-L.jpg",
                    "description": "Веселі історії про найсильнішу дівчинку.",
                    "stocks": {"NEW": 3, "USED": 3, "FRAGILE": 0},
                },
                {
                    "title": "Хроніки Нарнії: Лев, чаклунка і платтяна шафа",
                    "author": "Клайв Стейплз Льюїс",
                    "pages": 224,
                    "cover_url": "https://covers.openlibrary.org/b/id/6979861-L.jpg",
                    "description": "Дитяча класика про світ Нарнії.",
                    "stocks": {"NEW": 3, "USED": 2, "FRAGILE": 0},
                },
            ],

            "Бізнес": [
                {
                    "title": "Rework. Бізнес без забобонів",
                    "author": "Джейсон Фрайд; Девід Хайнемаєр Хенссон",
                    "pages": 288,
                    "cover_url": "https://covers.openlibrary.org/b/id/8231770-L.jpg",
                    "description": "Практичний погляд на сучасну роботу.",
                    "stocks": {"NEW": 2, "USED": 3, "FRAGILE": 0},
                },
                {
                    "title": "Від нуля до одиниці",
                    "author": "Пітер Тіль",
                    "pages": 224,
                    "cover_url": "https://covers.openlibrary.org/b/id/8231781-L.jpg",
                    "description": "Як створювати майбутнє, а не копіювати.",
                    "stocks": {"NEW": 2, "USED": 2, "FRAGILE": 0},
                },
                {
                    "title": "Доставка щастя",
                    "author": "Тоні Шей",
                    "pages": 272,
                    "cover_url": "https://covers.openlibrary.org/b/id/7600833-L.jpg",
                    "description": "Культура сервісу Zappos і побудова бренду.",
                    "stocks": {"NEW": 2, "USED": 3, "FRAGILE": 0},
                },
            ],

            "Класика світової літератури": [
                {
                    "title": "Злочин і кара",
                    "author": "Федір Достоєвський",
                    "pages": 672,
                    "cover_url": "https://covers.openlibrary.org/b/id/8232050-L.jpg",
                    "description": "Психологічний роман про провину і спокуту.",
                    "stocks": {"NEW": 2, "USED": 3, "FRAGILE": 0},
                },
                {
                    "title": "Анна Кареніна",
                    "author": "Лев Толстой",
                    "pages": 864,
                    "cover_url": "https://covers.openlibrary.org/b/id/8226163-L.jpg",
                    "description": "Трагедія кохання на тлі російського суспільства.",
                    "stocks": {"NEW": 1, "USED": 3, "FRAGILE": 0},
                },
                {
                    "title": "Портрет Доріана Ґрея",
                    "author": "Оскар Вайльд",
                    "pages": 352,
                    "cover_url": "https://covers.openlibrary.org/b/id/8469781-L.jpg",
                    "description": "Класичний роман про красу і мораль.",
                    "stocks": {"NEW": 3, "USED": 2, "FRAGILE": 0},
                },
            ],
        }

        total_books = 0
        for cat_name, books in data.items():
            cat_slug = make_slug(cat_name)
            cat, _ = Category.objects.update_or_create(
                slug=cat_slug,
                defaults={"name": cat_name},
            )

            for b in books:
                book_slug = make_slug(b["title"])
                book, _ = Book.objects.update_or_create(
                    slug=book_slug,
                    defaults=dict(
                        title=b["title"],
                        author=b["author"],
                        pages=b["pages"],
                        description=b.get("description", ""),
                        category=cat,
                        cover_url=b.get("cover_url", ""),
                        in_stock=True,
                    ),
                )
                for cond, qty in b["stocks"].items():
                    BookStock.objects.update_or_create(
                        book=book, condition=cond, defaults={"quantity": qty}
                    )
                total_books += 1

        self.stdout.write(self.style.SUCCESS(f"Демо-дані створено. Книг оновлено/створено: {total_books}"))
