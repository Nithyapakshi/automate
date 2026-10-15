#!/usr/bin/env python3
"""Refresh only public Travel markup from an approved visited-country projection.
No network, tickets, dates, photos, stay records or automatic booking ingestion.
Usage: python3 generate_travel.py --projection /private/reviewed-countries.json
Then: python3 generate_travel.py --check
Input must be only {countries:[country names],count:N}.
A booking is not a visit. Upstream must verify actual travel, exclude future and
cancelled bookings, and never remove earlier verified visits on cancellation.
Default re-check reads the sanitized projection embedded in index.html.
Review and publish through a pull request, then verify the deployed page.
No Gmail watch is connected by this script.
"""
import argparse,html,json,re
from pathlib import Path
COUNTRY_CATALOG = {'Aruba': '533', 'Afghanistan': '004', 'Angola': '024', 'Anguilla': '660', 'Åland Islands': '248', 'Albania': '008', 'Andorra': '020', 'United Arab Emirates': '784', 'Argentina': '032', 'Armenia': '051', 'American Samoa': '016', 'Antarctica': '010', 'French Southern Territories': '260', 'Antigua and Barbuda': '028', 'Australia': '036', 'Austria': '040', 'Azerbaijan': '031', 'Burundi': '108', 'Belgium': '056', 'Benin': '204', 'Bonaire, Sint Eustatius and Saba': '535', 'Burkina Faso': '854', 'Bangladesh': '050', 'Bulgaria': '100', 'Bahrain': '048', 'Bahamas': '044', 'Bosnia and Herzegovina': '070', 'Saint Barthélemy': '652', 'Belarus': '112', 'Belize': '084', 'Bermuda': '060', 'Bolivia, Plurinational State of': '068', 'Brazil': '076', 'Barbados': '052', 'Brunei Darussalam': '096', 'Bhutan': '064', 'Bouvet Island': '074', 'Botswana': '072', 'Central African Republic': '140', 'Canada': '124', 'Cocos (Keeling) Islands': '166', 'Switzerland': '756', 'Chile': '152', 'China': '156', "Côte d'Ivoire": '384', 'Cameroon': '120', 'Congo, The Democratic Republic of the': '180', 'Congo': '178', 'Cook Islands': '184', 'Colombia': '170', 'Comoros': '174', 'Cabo Verde': '132', 'Costa Rica': '188', 'Cuba': '192', 'Curaçao': '531', 'Christmas Island': '162', 'Cayman Islands': '136', 'Cyprus': '196', 'Czechia': '203', 'Germany': '276', 'Djibouti': '262', 'Dominica': '212', 'Denmark': '208', 'Dominican Republic': '214', 'Algeria': '012', 'Ecuador': '218', 'Egypt': '818', 'Eritrea': '232', 'Western Sahara': '732', 'Spain': '724', 'Estonia': '233', 'Ethiopia': '231', 'Finland': '246', 'Fiji': '242', 'Falkland Islands (Malvinas)': '238', 'France': '250', 'Faroe Islands': '234', 'Micronesia, Federated States of': '583', 'Gabon': '266', 'United Kingdom': '826', 'Georgia': '268', 'Guernsey': '831', 'Ghana': '288', 'Gibraltar': '292', 'Guinea': '324', 'Guadeloupe': '312', 'Gambia': '270', 'Guinea-Bissau': '624', 'Equatorial Guinea': '226', 'Greece': '300', 'Grenada': '308', 'Greenland': '304', 'Guatemala': '320', 'French Guiana': '254', 'Guam': '316', 'Guyana': '328', 'Hong Kong': '344', 'Heard Island and McDonald Islands': '334', 'Honduras': '340', 'Croatia': '191', 'Haiti': '332', 'Hungary': '348', 'Indonesia': '360', 'Isle of Man': '833', 'India': '356', 'British Indian Ocean Territory': '086', 'Ireland': '372', 'Iran, Islamic Republic of': '364', 'Iraq': '368', 'Iceland': '352', 'Israel': '376', 'Italy': '380', 'Jamaica': '388', 'Jersey': '832', 'Jordan': '400', 'Japan': '392', 'Kazakhstan': '398', 'Kenya': '404', 'Kyrgyzstan': '417', 'Cambodia': '116', 'Kiribati': '296', 'Saint Kitts and Nevis': '659', 'Korea, Republic of': '410', 'Kuwait': '414', "Lao People's Democratic Republic": '418', 'Lebanon': '422', 'Liberia': '430', 'Libya': '434', 'Saint Lucia': '662', 'Liechtenstein': '438', 'Sri Lanka': '144', 'Lesotho': '426', 'Lithuania': '440', 'Luxembourg': '442', 'Latvia': '428', 'Macao': '446', 'Saint Martin (French part)': '663', 'Morocco': '504', 'Monaco': '492', 'Moldova, Republic of': '498', 'Madagascar': '450', 'Maldives': '462', 'Mexico': '484', 'Marshall Islands': '584', 'North Macedonia': '807', 'Mali': '466', 'Malta': '470', 'Myanmar': '104', 'Montenegro': '499', 'Mongolia': '496', 'Northern Mariana Islands': '580', 'Mozambique': '508', 'Mauritania': '478', 'Montserrat': '500', 'Martinique': '474', 'Mauritius': '480', 'Malawi': '454', 'Malaysia': '458', 'Mayotte': '175', 'Namibia': '516', 'New Caledonia': '540', 'Niger': '562', 'Norfolk Island': '574', 'Nigeria': '566', 'Nicaragua': '558', 'Niue': '570', 'Netherlands': '528', 'Norway': '578', 'Nepal': '524', 'Nauru': '520', 'New Zealand': '554', 'Oman': '512', 'Pakistan': '586', 'Panama': '591', 'Pitcairn': '612', 'Peru': '604', 'Philippines': '608', 'Palau': '585', 'Papua New Guinea': '598', 'Poland': '616', 'Puerto Rico': '630', "Korea, Democratic People's Republic of": '408', 'Portugal': '620', 'Paraguay': '600', 'Palestine, State of': '275', 'French Polynesia': '258', 'Qatar': '634', 'Réunion': '638', 'Romania': '642', 'Russian Federation': '643', 'Rwanda': '646', 'Saudi Arabia': '682', 'Sudan': '729', 'Senegal': '686', 'Singapore': '702', 'South Georgia and the South Sandwich Islands': '239', 'Saint Helena, Ascension and Tristan da Cunha': '654', 'Svalbard and Jan Mayen': '744', 'Solomon Islands': '090', 'Sierra Leone': '694', 'El Salvador': '222', 'San Marino': '674', 'Somalia': '706', 'Saint Pierre and Miquelon': '666', 'Serbia': '688', 'South Sudan': '728', 'Sao Tome and Principe': '678', 'Suriname': '740', 'Slovakia': '703', 'Slovenia': '705', 'Sweden': '752', 'Eswatini': '748', 'Sint Maarten (Dutch part)': '534', 'Seychelles': '690', 'Syrian Arab Republic': '760', 'Turks and Caicos Islands': '796', 'Chad': '148', 'Togo': '768', 'Thailand': '764', 'Tajikistan': '762', 'Tokelau': '772', 'Turkmenistan': '795', 'Timor-Leste': '626', 'Tonga': '776', 'Trinidad and Tobago': '780', 'Tunisia': '788', 'Turkey': '792', 'Tuvalu': '798', 'Taiwan, Province of China': '158', 'Tanzania, United Republic of': '834', 'Uganda': '800', 'Ukraine': '804', 'United States Minor Outlying Islands': '581', 'Uruguay': '858', 'United States': '840', 'Uzbekistan': '860', 'Holy See (Vatican City State)': '336', 'Saint Vincent and the Grenadines': '670', 'Venezuela, Bolivarian Republic of': '862', 'Virgin Islands, British': '092', 'Virgin Islands, U.S.': '850', 'Viet Nam': '704', 'Vanuatu': '548', 'Wallis and Futuna': '876', 'Samoa': '882', 'Yemen': '887', 'South Africa': '710', 'Zambia': '894', 'Zimbabwe': '716', 'Tanzania': '834', 'USA': '840'}

def validate_projection(p,catalog):
    if not isinstance(p,dict) or set(p)!={'countries','count'}:
        raise ValueError('Projection must contain only countries and count')
    names=p['countries']
    if not isinstance(names,list) or not all(isinstance(n,str) for n in names):
        raise ValueError('countries must be country names only')
    if len(set(names))!=len(names) or type(p['count']) is not int or p['count']!=len(names):
        raise ValueError('Count mismatch or duplicate country')
    if any(n not in catalog for n in names):
        raise ValueError('Unknown country name; verify an ISO mapping before continuing')
    return sorted(names)

def generate(page,projection,catalog):
    names=validate_projection(projection,catalog);count=len(names);visited={catalog[n] for n in names}
    match=re.search(r'<div\b[^>]*\bid="travel"[^>]*>',page)
    if not match:raise ValueError('Missing Travel view')
    start=match.start()
    # Public route ends before the next data-view, with its exact current structure.
    end=page.find('<div',match.end())
    # Use balanced div tags, not a greedy full-document replacement.
    depth=1;end=None
    for tag in re.finditer(r'</?div\b[^>]*>',page[match.end():]):
        depth+=-1 if tag.group().startswith('</') else 1
        if depth==0:end=match.end()+tag.end();break
    if end is None:raise ValueError('Unbalanced Travel container')
    travel=page[start:end]
    seen=set()
    def path_replace(m):
        tag=m.group();iso=re.search(r'data-country-iso="([0-9-]+)"',tag)
        if not iso:raise ValueError('Path missing verified ISO mapping')
        iso=iso.group(1);seen.add(iso)
        fill='#73a89a' if iso in visited else '#eeeae7'
        return re.sub(r'\bfill="[^"]*"',f'fill="{fill}"',tag)
    travel=re.sub(r'<path\b[^>]*>',path_replace,travel)
    if len(seen)!=173:raise ValueError('Expected all173 mapped geometry paths')
    travel=re.sub(r'aria-label="World map with \d+ visited countries highlighted"',f'aria-label="World map with {count} visited countries highlighted"',travel)
    travel=re.sub(r'<strong>\d+</strong>',f'<strong>{count}</strong>',travel)
    travel=re.sub(r'Explore the \d+ countries',f'Explore the {count} countries',travel)
    stamps=''.join(f'<div class="stamp s{i%4}"><span>EXPLORED</span><strong>{html.escape(n)}</strong><small>PAKSHIRAJ / TRAVEL</small></div>' for i,n in enumerate(names))
    travel,n=re.subn(r'<div class="stamps">.*?</div>(?=<footer>)',f'<div class="stamps">{stamps}</div>',travel,flags=re.S)
    if n!=1:raise ValueError('Missing unique stamp grid')
    return page[:start]+travel+page[end:]

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--projection',type=Path);ap.add_argument('--page',type=Path,default=Path('index.html'));ap.add_argument('--check',action='store_true');args=ap.parse_args()
    before=args.page.read_text();current=re.search(r'<script id="visited-country-projection" type="application/json">(.*?)</script>',before,re.S)
    if args.projection:projection=json.loads(args.projection.read_text())
    elif current:projection=json.loads(current.group(1))
    else:raise ValueError('No sanitized projection supplied')
    result=generate(before,projection,COUNTRY_CATALOG)
    encoded=json.dumps(projection,separators=(',',':')).replace('<','\\u003c')
    if current: result=re.sub(r'<script id="visited-country-projection" type="application/json">.*?</script>',lambda _: '<script id="visited-country-projection" type="application/json">'+encoded+'</script>',result,flags=re.S)
    else: result=result.replace('</head>','<script id="visited-country-projection" type="application/json">'+encoded+'</script></head>',1)
    if args.check:
        if result!=before:raise SystemExit('Travel output needs regeneration')
        print('Travel output matches approved projection')
    else:args.page.write_text(result);print('Updated public Travel country count,stamps and highlights only')
if __name__=='__main__':main()
