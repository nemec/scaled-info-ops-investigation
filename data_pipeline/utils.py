import re


def pre_process_description(description: str) -> str:
    try:
        idx = description.index('Im Arabic')
        if idx >= 0:
            description = description[:idx]
    except ValueError:
        pass
    subs = [
        (r"Website: http[\w:/%.-]+", ""),
        (r"Facebook: http[\w:/%.-]+", ""),
        (r"Tiwtter: http[\w:/%.-]+", ""),
        (r"Twitter: http[\w:/%.-]+", ""),
        (r"Instagram: http[\w:/%.-]+", ""),
        (r"Youtube: http[\w:/%.-]+", ""),
        (r"-{2,}", ""),
        (r"\s+", " "),
        (r"\n", " "),
    ]
    for sub in subs:
        description = re.sub(sub[0], sub[1], description)
    return description.strip()


def post_process_topic(topic: str) -> str:
    subs = [
        (r"-", ""),
        (r"^\d+\.", ""),
        (r"\*", ""),
    ]
    for sub in subs:
        topic = re.sub(sub[0], sub[1], topic)
    return topic.strip().lower()


# https://stackoverflow.com/questions/6038061/regular-expression-to-find-urls-within-a-string
def find_urls_in_text(text: str) -> list[str]:
    return re.findall(r"""(?:
        (?:https?|ftp|file)://|www\.|ftp\.
    )
    (?:
        \([-A-Z0-9+&@#/%=~_|$?!:,.]*\)|[-A-Z0-9+&@#/%=~_|$?!:,.]
    )*
    (?:
        \([-A-Z0-9+&@#/%=~_|$?!:,.]*\)|[A-Z0-9+&@#/%=~_|$]
    )""", text, flags=re.IGNORECASE | re.VERBOSE)

