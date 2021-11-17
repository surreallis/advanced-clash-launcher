from os import path

default_district = 'Seltzer Summit'
district_list = {
    'tesla': 'Tesla Tundra',
    'quicksand': 'Quicksand Quarry',
    'seltzer': 'Seltzer Summit',
    'kazoo': 'Kazoo Kanyon',
    'anvil': 'Anvil Acres',
    'hypno': 'Hypno Heights',
    'cupcake': 'Cupcake Cove'
}

multicontroller_path = path.join(path.dirname(__file__), '..', 'ToontownMulticontroller.exe')
account_path = path.join(path.dirname(__file__), '..', 'accounts.yml')
app_path = path.join(path.expandvars('%localappdata%'), 'Corporate Clash')
app_exe = path.join(app_path, 'CorporateClash.exe')
api_path = 'https://corporateclash.net/api/v1/login/'
game_server = 'gs.corporateclash.net'
