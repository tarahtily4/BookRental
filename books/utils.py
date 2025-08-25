from django.utils.text import slugify

_TRANS = {
    "а":"a","б":"b","в":"v","г":"h","ґ":"g","д":"d","е":"e","є":"ie","ж":"zh","з":"z",
    "и":"y","і":"i","ї":"i","й":"i","к":"k","л":"l","м":"m","н":"n","о":"o","п":"p",
    "р":"r","с":"s","т":"t","у":"u","ф":"f","х":"kh","ц":"ts","ч":"ch","ш":"sh",
    "щ":"shch","ь":"","ю":"iu","я":"ia",
    "ё":"e","ы":"y","э":"e",
}
def make_slug(text: str) -> str:
    s = (text or "").strip().lower()
    s = "".join(_TRANS.get(ch, ch) for ch in s)
    return slugify(s)
