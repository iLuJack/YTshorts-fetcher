import json
import re

def fix_spacing_in_text(text):
    """Fix spacing issues in text by adding spaces between words that should be separated."""
    if not text:
        return text
    
    # Common patterns that need spaces between them
    patterns = [
        (r'([a-z])([A-Z][a-z])', r'\1 \2'),  # camelCase -> camel Case
        (r'([a-z])(\d)', r'\1 \2'),  # word1 -> word 1
        (r'(\d)([a-z])', r'\1 \2'),  # 1word -> 1 word
        
        # Fix specifically identified issues
        (r'groupformed', r'group formed'),
        (r'bandformed', r'band formed'),
        (r'inall', r'in all'),
        (r'formerand', r'former and'),
        (r'boyband', r'boy band'),
        (r'girlgroup', r'girl group'),
        (r'duoformed', r'duo formed'),
        (r'albumtrilogy', r'album trilogy'),
        (r'albumtetralogy', r'album tetralogy'),
        (r'groupis', r'group is'),
        (r'groupconsists', r'group consists'),
        (r'groupcurrently', r'group currently'),
        (r'groupwas', r'group was'),
        (r'bandis', r'band is'),
        (r'bandconsists', r'band consists'),
        (r'withthe', r'with the'),
        (r'andthe', r'and the'),
        (r'fromthe', r'from the'),
        (r'forthe', r'for the'),
        (r'onthe', r'on the'),
        (r'tothe', r'to the'),
        (r'atthe', r'at the'),
        (r'asthe', r'as the'),
        (r'bythe', r'by the'),
        (r'isthe', r'is the'),
        (r'wasthe', r'was the'),
        (r'ofthe', r'of the'),
        (r'inthe', r'in the'),
        (r'throughthe', r'through the'),
        (r'titletrack', r'title track'),
        (r'theireponymous', r'their eponymous'),
        (r'eponymousdebut', r'eponymous debut'),
        (r'thesame', r'the same'),
        (r'leadsingles', r'lead singles'),
        (r'leadsingle', r'lead single'),
        (r'albumand', r'album and'),
        (r'musican', r'music an'),
        (r'albumsold', r'album sold'),
        (r'EPsold', r'EP sold'),
        (r'singlealbum', r'single album'),
        (r'studioalbum', r'studio album'),
        (r'albumwas', r'album was'),
        (r'EPwas', r'EP was'),
        (r'firstalbum', r'first album'),
        (r'debutalbum', r'debut album'),
        (r'firstEP', r'first EP'),
        (r'debutEP', r'debut EP'),
        (r'extendedplay', r'extended play'),
        (r'digitalsingles', r'digital singles'),
        (r'digitalsingle', r'digital single'),
        (r'debutsingle', r'debut single'),
        (r'singlesold', r'single sold'),
        (r'musicvideo', r'music video'),
        (r'theirown', r'their own'),
        (r'bandmember', r'band member'),
        (r'groupmember', r'group member'),
        (r'formermember', r'former member'),
        (r'maxi single', r'maxi single'),
        (r'maxisingle', r'maxi single'),
        (r'andwas', r'and was'),
        (r'andis', r'and is'),
        (r'tobecome', r'to become'),
        (r'albumwith', r'album with'),
        (r'albumin', r'album in'),
        (r'albumat', r'album at'),
        (r'chartfor', r'chart for'),
        (r'chartand', r'chart and'),
        (r'chartat', r'chart at'),
        (r'chartin', r'chart in'),
        (r'BillboardHot', r'Billboard Hot'),
        (r'BillboardGlobal', r'Billboard Global'),
        (r'BillboardWorld', r'Billboard World'),
        (r'BillboardK-pop', r'Billboard K-pop'),
        (r'BillboardTop', r'Billboard Top'),
        (r'Billboard200', r'Billboard 200'),
        (r'K-popHot', r'K-pop Hot'),
        (r'BillboardEmerging', r'Billboard Emerging'),
        (r'Billboard\'s', r'Billboard\'s'),
        (r'K-popgroup', r'K-pop group'),
        (r'K-popacross', r'K-pop across'),
        (r'K-popgirl', r'K-pop girl'),
        (r'K-popboy', r'K-pop boy'),
        (r'K-popmale', r'K-pop male'),
        (r'K-popfemale', r'K-pop female'),
        (r'K-popact', r'K-pop act'),
        (r'K-popscene', r'K-pop scene'),
        (r'K-popartist', r'K-pop artist'),
        (r'ForbesKorea', r'Forbes Korea'),
        (r'CircleDigital', r'Circle Digital'),
        (r'CircleAlbum', r'Circle Album'),
        (r'GoldenDisc', r'Golden Disc'),
        (r'SeoulMusic', r'Seoul Music'),
        (r'MelonMusic', r'Melon Music'),
        (r'MnetAsian', r'Mnet Asian'),
        (r'GaonDigital', r'Gaon Digital'),
        (r'GaonAlbum', r'Gaon Album'),
        (r'OrionAlbums', r'Orion Albums'),
        (r'OrionSingles', r'Orion Singles'),
        (r'UKSingles', r'UK Singles'),
        (r'UKOfficial', r'UK Official'),
        (r'USBillboard', r'US Billboard'),
        (r'inK-pop', r'in K-pop'),
        (r'ofK-pop', r'of K-pop'),
        (r'therecord', r'the record'),
        (r'millioncopies', r'million copies'),
        (r'millionsales', r'million sales'),
        (r'millionunit', r'million unit'),
        (r'milliondigital', r'million digital'),
        (r'worldtour', r'world tour'),
        (r'hometour', r'home tour'),
        (r'KoreanWave', r'Korean Wave'),
        (r'SouthKorean', r'South Korean'),
    ]
    
    # Apply all patterns
    for pattern, replacement in patterns:
        text = re.sub(pattern, replacement, text)
    
    return text

def fix_json_formatting(json_file_path):
    """Read JSON file, fix spacing issues, and write back to the same file."""
    try:
        # Read the JSON file
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Fix spacing issues in each group's info text
        for group_name, group_data in data.items():
            if group_data.get('info'):
                fixed_info = []
                for paragraph in group_data['info']:
                    fixed_paragraph = fix_spacing_in_text(paragraph)
                    fixed_info.append(fixed_paragraph)
                group_data['info'] = fixed_info
        
        # Write the fixed data back to the file
        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return "JSON formatting fixed successfully!"
    
    except Exception as e:
        return f"Error: {str(e)}"

# Path to your JSON file
json_file_path = "wikipedia_data/kpop_group_info.json"

# Run the formatting function
result = fix_json_formatting(json_file_path)
print(result)