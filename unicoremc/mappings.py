PageMapping = {
    'properties': {
        'id': {
            'type': 'string',
            'index': 'not_analyzed',
        },
        'uuid': {
            'type': 'string',
            'index': 'not_analyzed',
        },
        'primary_category': {
            'type': 'string',
            'index': 'not_analyzed',
        },
        'source': {
            'type': 'string',
            'index': 'not_analyzed',
        },
        'language': {
            # needs to be renabled once unicore-cms supports it
            # 'index': 'not_analyzed',
            'type': 'string'
        },
        'slug': {
            'type': 'string',
            'index': 'not_analyzed',
        }
    }
}

CategoryMapping = {
    'properties': {
        'id': {
            'type': 'string',
            'index': 'not_analyzed',
        },
        'uuid': {
            'type': 'string',
            'index': 'not_analyzed',
        },
        'source': {
            'type': 'string',
            'index': 'not_analyzed',
        },
        'language': {
            # needs to be renabled once unicore-cms supports it
            # 'index': 'not_analyzed',
            'type': 'string'
        },
        'slug': {
            'type': 'string',
            'index': 'not_analyzed',
        }
    }
}
