import random


def do_me_a_unique_slug(model_cls, field):
    """
    model_cls: A Django model to enforce uniqueness
    field: The field that stores the unique name
    """
    slug = do_me_a_slug()
    while model_cls.objects.filter(**{'%s__iexact' % field: slug}).exists():
        slug = do_me_a_slug()
    return slug


def do_me_a_slug():
    """
    Generates a random slug using nouns, adjectives and a number
    e.g morning-waterfall-23
    """
    adjectives = [
        "autumn", "hidden", "bitter", "misty", "silent", "empty", "dry",
        "dark", "summer", "icy", "delicate", "quiet", "white", "cool",
        "spring", "winter", "patient", "twilight", "dawn", "crimson", "wispy",
        "weathered", "blue", "billowing", "broken", "cold", "damp", "falling",
        "frosty", "green", "long", "late", "lingering", "bold", "little",
        "morning", "muddy", "old", "red", "rough", "still", "small",
        "sparkling", "throbbing", "shy", "wandering", "withered", "wild",
        "black", "young", "holy", "solitary", "fragrant", "aged", "snowy",
        "proud", "floral", "restless", "divine", "polished", "ancient",
        "purple", "lively", "nameless"
    ]
    nouns = [
        "waterfall", "river", "breeze", "moon", "rain", "wind", "sea",
        "snow", "lake", "sunset", "pine", "shadow", "leaf", "dawn", "glitter",
        "forest", "hill", "cloud", "meadow", "sun", "glade", "bird", "brook",
        "butterfly", "bush", "dew", "dust", "field", "fire", "flower",
        "feather", "grass", "haze", "mountain", "night", "pond", "darkness",
        "snowflake", "silence", "sound", "sky", "shape", "surf", "thunder",
        "violet", "water", "wildflower", "wave", "water", "resonance", "sun",
        "wood", "dream", "cherry", "tree", "fog", "frost", "voice", "paper",
        "frog", "smoke", "star", "morning", "firefly",
    ]
    return "%s-%s-%s" % (
        random.choice(adjectives),
        random.choice(nouns),
        random.randint(1, 1000))
