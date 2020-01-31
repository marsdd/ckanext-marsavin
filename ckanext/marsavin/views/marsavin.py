import ckan.lib.base as base
from ckan.lib.plugins import toolkit


def contact():
    u''' display contact page'''
    return base.render(u'home/contact.html', extra_vars={})


def terms():
    u''' display terms page'''
    return base.render(u'home/terms_conditions.html', extra_vars={})


def privacy():
    u''' display privacy page'''
    return base.render(u'home/privacy.html', extra_vars={})


def faq():
    u''' display faq page'''
    questions = {
        "general": [
            {
                "section": toolkit._("General"),
                "question": toolkit._('Who created the AVIN Data Catalogue?'),
                "answer": toolkit._("This catalogue was built by <a "
                                    "href=\"https://www.marsdd.com/\">MaRS "
                                    "Discovery District</a>(<a "
                                    "href=\"http://www.twitter.com/MaRSDD\">"
                                    "@MaRSDD</a>). MaRS in Toronto is North "
                                    "America's largest urban innovation "
                                    "hub. Our purpose is to help innovators "
                                    "change the world. MaRS supports "
                                    "promising ventures tackling key "
                                    "challenges in the health, "
                                    "cleantech, fintech and enterprise "
                                    "sectors as they start, grow and scale. "
                                    "In addition, the MaRS community fosters "
                                    "cross-disciplinary collaboration to "
                                    "drive breakthrough discoveries and new "
                                    "solutions to be adopted in Canada and "
                                    "beyond, growing our economy and "
                                    "delivering societal impact at scale.")
            },
            {
                "section": toolkit._("General"),
                "question": toolkit._('Why was the catalogue created?'),
                "answer": toolkit._('This catalogue was built as part of '
                                    'MaRS\' commitment to the Autonomous '
                                    'Vehicle Innovation Network (AVIN). '
                                    'Learn more about AVIN '
                                    '<a href="https://www.avinhub.ca/about/">'
                                    'on their website.</a>')
            },
            {
                "section": toolkit._("General"),
                "question": toolkit._('Who is it for?'),
                "answer": toolkit._('This catalogue is for members of the '
                                    'connected and autonomous vehicle '
                                    'community interested in sharing data '
                                    'for the purposes of research and '
                                    'product development. If you need data '
                                    'to develop AI models or products, '
                                    'you should take a look in the catalogue.')
            }
        ],
        "data_owners": [
            {
                "section": toolkit._("For Data Owners"),
                "question": toolkit._('How do I join?'),
                "answer": toolkit._('To upload data to the catalogue, '
                                    'you must have an account approved by '
                                    'an administrator. Please contact '
                                    '<a '
                                    'href="mailto:avindata@marsdd.com?subject=Join AVIN Data catalog as data owner">'
                                    'avindata@marsdd.com</a> to start this '
                                    'process.')
            },
            {
                "section": toolkit._("For Data Owners"),
                "question": toolkit._('What data should I upload?'),
                "answer": toolkit._('This catalogue is for any data related '
                                    'to connected and autonomous vehicles; '
                                    'everything from vehicle collision '
                                    'details, to driving videos, sensor data, '
                                    'and beyond. If you\'re not sure whether '
                                    'your data would be appropriate for the '
                                    'AVIN Data Catalogue, feel free to ask '
                                    'us at '
                                    '<a '
                                    'href="mailto:avindata@marsdd.com?subject=Ask a question about AVIN Data catalog">'
                                    'avindata@marsdd.com.</a>')
            },
            {
                "section": toolkit._("For Data Owners"),
                "question": toolkit._('What will you do with my data?'),
                "answer": toolkit._('The data catalogue does not host '
                                    'any data, it simply acts as an index '
                                    'that will link to your data. Therefore, '
                                    'you will always retain control of your '
                                    'data, keep it on your servers, and '
                                    'are free to take it down at any time.')
            },
            {
                "section": toolkit._("For Data Owners"),
                "question": toolkit._('I host my data for a limited '
                                      'amount of time, will I have to '
                                      'remove my datasets every time '
                                      'they\'re no longer available?'),
                "answer": toolkit._('Datasets can be marked with an expiry '
                                    'date, automatically removing them '
                                    'from the catalogue after the '
                                    'specified expiry.')
            },
            {
                "section": toolkit._("For Data Owners"),
                "question": toolkit._('Is there a way to automate adding '
                                      'data to the catalogue?'),
                "answer": toolkit._('There is an API for the data catalogue. '
                                    'Please contact '
                                    '<a '
                                    'href="mailto:avindata@marsdd.com?Subject=Request API Access">'
                                    'avindata@marsdd.com</a> for API '
                                    'documentation.')
            }
        ],
        "data_seekers": [
            {
                "section": toolkit._("For Data Seekers"),
                "question": toolkit._('Can I access all of this data?'),
                "answer": toolkit._('Most of the data you can see in this '
                                    'catalogue is open.  The data owner has '
                                    'agreed to freely share it with anyone '
                                    'who wants it. Some datasets are '
                                    'restricted-the data owner will approve '
                                    'the request or not before you get '
                                    'access to the data. These datasets '
                                    'are marked with a license type '
                                    'of "Other (Not Open)."')
            },
            {
                "section": toolkit._("For Data Seekers"),
                "question": toolkit._('What am I allowed to do with this '
                                      'data?'),
                "answer": toolkit._('It depends on the dataset. In each '
                                    'one, the data owner has specified a '
                                    'license type. Some will allow you to '
                                    'modify, distribute and use data '
                                    'commercially, while others are more '
                                    'restrictive. More information about the '
                                    'types of licenses can be found at '
                                    '<a '
                                    'href="http://opendefinition.org/licenses/"'
                                    '>Open Definition.</a>')
            },
            {
                "section": toolkit._("For Data Seekers"),
                "question": toolkit._('Do I need an account to access data?'),
                "answer": toolkit._('No, you don\'t need to log in in order '
                                    'to access any of these datasets.')
            },
            {
                "section": toolkit._("For Data Seekers"),
                "question": toolkit._('The catalogue is asking me to '
                                      '"request dataset access." Why can\'t '
                                      'I just download it?'),
                "answer": toolkit._('The dataset owner has specified that '
                                    'they\'d like to approve access to that '
                                    'data on a case-by-case basis. You\'ll '
                                    'have to send them a request in order '
                                    'to get access.')
            }
        ]
    }
    return base.render(u'home/faq.html', extra_vars={
        "general": questions["general"],
        "data_owners": questions["data_owners"],
        "data_seekers": questions["data_seekers"]
    })
