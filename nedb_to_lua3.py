#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''Convert json db of WhoCallTheFleet to KcWiki lua.
'''
import json
from pprint import pprint


NEDB_SHIPS = './db/ships.nedb'
NEDB_ENTITIES = './db/entities.nedb'
NEDB_SHIP_NAMESUFFIX = './db/ship_namesuffix.nedb'
NEDB_SHIP_CLASSES = './db/ship_classes.nedb'
NEDB_SHIP_SERIES = './db/ship_series.nedb'

MIST_SHIPS = {
    9181: {
        # 伊欧娜
        'kcwiki_id': 'Mist01',
        'modernization': [1, 0, 0, 0],
        'scrap': [0, 1, 0, 0]
    },
    9182: {
        # 高雄
        'kcwiki_id': 'Mist02',
        'modernization': [1, 0, 0, 0],
        'scrap': [0, 1, 0, 0]
    },
    9183: {
        # 榛名
        'kcwiki_id': 'Mist03',
        'modernization': [1, 0, 0, 0],
        'scrap': [0, 1, 0, 0]
    }
}

SHIP_TYPE_MAPPING_TABLE = {
    # WhoCallTheFleet type: Kcwiki type
    1: 2,
    2: 3,
    3: 4,
    4: 5,
    5: 6,
    6: 9,
    7: 8,
    8: 10,
    9: 7,
    10: 11,
    11: 18,
    12: 16,
    13: 13,
    14: 14,
    15: 17,
    16: 19,
    17: 20,
    18: 9,  # 战列巡洋舰 (雷装) -> 战列舰
    19: 2,  # 防空驱逐舰 -> 驱逐舰
    20: 9,  # 大型战列舰 -> 战列舰
    21: 21,
    22: 22,
    23: 5,  # 防空巡洋舰 -> 重巡洋舰
    24: 16, # 飞行艇母舰 -> 水上机母舰
    25: 5,  # 海雾舰队重巡洋舰 -> 重巡洋舰
    26: 9,  # 海雾舰队大战舰 -> 战列舰
    27: 13, # 海雾舰队攻击性潜艇 -> 潜水舰
    28: 3,  # 防空轻巡洋舰 -> 轻巡洋舰
    29: 22, # 舰队油船 -> 补给舰 (神威)
    30: 7,  # 攻击型轻航母 -> 轻航母
    31: 1,
    32: 7   # 特设航空母舰 -> 轻航母
}


def nedb_parser(nedb):
    '''nedb_parser
    '''
    result = {}
    line_num = 1

    print('Get raw data from {}'.format(nedb))
    with open(nedb, 'r', encoding='utf-8') as nedb_f:
        for line in nedb_f:
            python_object = json.loads(line)
            if not isinstance(python_object, dict):
                print('Not a python dict')
                print('{}: line {}'.format(nedb, line_num))
                return

            line_num += 1
            item_id = python_object['id']
            result[item_id] = python_object

    print('Loaded {} datas from {}'.format(len(result), nedb))
    return result


def get_ship_no(ship, nedb_ship):
    '''Get the illustration number of ship
    '''
    ship['no'] = nedb_ship['no']


def get_ship_name(ship, nedb_ship, nedb_ship_namesuffix):
    '''Get ship name from nedb
    include jp, kana, zhcn
    '''
    ship['ja_jp'] = nedb_ship['name']['ja_jp']#.encode('utf-8')
    ship['ja_kana'] = nedb_ship['name']['ja_kana']#.encode('utf-8')
    ship['zh_cn'] = nedb_ship['name']['zh_cn']#.encode('utf-8')
    name_suffix = nedb_ship['name']['suffix']
    ship['ja_jp'] += nedb_ship_namesuffix[name_suffix]['ja_jp']#.encode('utf-8')
    ship['zh_cn'] += nedb_ship_namesuffix[name_suffix]['zh_cn']#.encode('utf-8')


def get_ship_type(ship, nedb_ship):
    '''Convert WhoCallTheFleet ship type to KcWiki type
    '''
    ship['type'] = SHIP_TYPE_MAPPING_TABLE[nedb_ship['type']]


def get_ship_class(ship, nedb_ship, nedb_ship_classes):
    '''Get the class and number
    '''
    ship['class'] = (nedb_ship_classes[nedb_ship['class']]['name']['zh_cn'],
                     nedb_ship['class_no'])


def get_ship_rare(ship, nedb_ship):
    '''Get rare of ship, exclude the mistfleet
    '''
    try:
        ship['rare'] = nedb_ship['rare']
    except KeyError:
        if ship['id'] not in MIST_SHIPS:
            print('Get rare value failed')
            print('Ship: {} with ID: {}'.format(ship['zh_cn'], ship['id']))
            raise


def get_ship_stat(ship, nedb_ship):
    '''To parser the nedb_ships.stat
    '''
    ship['hp'] = (nedb_ship['stat']['hp'],
                  nedb_ship['stat']['hp_max'])
    ship['fire'] = (nedb_ship['stat']['fire'],
                    nedb_ship['stat']['fire_max'])
    ship['torpedo'] = (nedb_ship['stat']['torpedo'],
                       nedb_ship['stat']['torpedo_max'])
    ship['aa'] = (nedb_ship['stat']['aa'],
                  nedb_ship['stat']['aa_max'])
    ship['armor'] = (nedb_ship['stat']['armor'],
                     nedb_ship['stat']['armor_max'])
    ship['asw'] = (nedb_ship['stat']['asw'],
                   nedb_ship['stat']['asw_max'])
    ship['evasion'] = (nedb_ship['stat']['evasion'],
                       nedb_ship['stat']['evasion_max'])
    ship['los'] = (nedb_ship['stat']['los'],
                   nedb_ship['stat']['los_max'])
    ship['luck'] = (nedb_ship['stat']['luck'],
                    nedb_ship['stat']['luck_max'])
    ship['speed'] = nedb_ship['stat']['speed']
    ship['range'] = nedb_ship['stat']['range']
    ship['carry'] = nedb_ship['stat']['carry']


def get_ship_slot(ship, nedb_ship):
    '''Get the ship slot
    '''
    ship['nslots'] = len(nedb_ship['slot'])
    # if slot can't not put plane
    # WhoCallTheFleet set it to 0
    # But Kcwiki set it to -1
    ship['slot'] = [x if x > 0 else -1 for x in nedb_ship['slot']]


def get_ship_equip(ship, nedb_ship):
    '''Get the ship equipment
    '''
    # Some ship's equip in WhoCallTheFleet nedb is []
    # initiate it as -1 according to the slot number
    if not nedb_ship['equip']:
        ship['equip'] = [-1] * len(nedb_ship['slot'])
        return
    # if slot has no equipment
    # WhoCallTheFleet set it to an empty string u''
    # But Kcwiki set it to -1
    ship['equip'] = [x if x else -1 for x in nedb_ship['equip']]


def get_ship_kcwiki_id(ship, nedb_ship, nedb_ships):
    '''Get ship kcwiki id
    '''
    if ship['id'] in MIST_SHIPS:
        ship['kcwiki_id'] = MIST_SHIPS[ship['id']]['kcwiki_id']
        return

    ship['kcwiki_id'] = '{:03}'.format(nedb_ship['no'])

    if nedb_ship['name']['suffix'] is None:
        return

    # Dirty solution
    # WhoCallTheFleet ships.nedb may forget to add "illust_same_as_prev"
    # So if the kcwiki_id > total number of ships, handle it.
    #
    # To pull request to WhoCallTheFleet,
    # update the ships.nedb and ship_series.nedb,
    # may be the better solution.
    if (nedb_ship.get('illust_same_as_prev', False) or
            int(ship['kcwiki_id']) > len(nedb_ships)):
        prev_nedb_ship_id = nedb_ship['remodel']['prev']
        ship['kcwiki_id'] = '{:03}a'.format(nedb_ships[prev_nedb_ship_id]['no'])


def get_ship_consum(ship, nedb_ship):
    '''Get consum
    '''
    # Note:
    # In python2, the key of ship['consum'] is unicode string.
    # May this make something wrong in the future?
    ship['consum'] = nedb_ship['consum']


def get_ship_modernization(ship, nedb_ship):
    '''Get modernization value
    '''
    if ship['id'] in MIST_SHIPS:
        nedb_ship['modernization'] = MIST_SHIPS[ship['id']]['modernization']

    ship['modernization'] = dict(zip(['fire', 'torpedo', 'aa', 'armor'],
                                     nedb_ship['modernization']))


def get_ship_scrap(ship, nedb_ship):
    '''Get scrap
    '''
    if ship['id'] in MIST_SHIPS:
        nedb_ship['scrap'] = MIST_SHIPS[ship['id']]['scrap']

    ship['scrap'] = dict(zip(['fire', 'torpedo', 'aa', 'armor'],
                             nedb_ship['scrap']))

def get_ship_get_method(ship, nedb_ship):
    '''Get the get method
    '''
    ship['get_method'] = dict(zip(['drop', 'remodel', 'build', 'buildtime'],
                                  [-1, -1, -1, -1]))

    if ship['id'] in MIST_SHIPS:
        return

    ship['get_method'] = {
        'drop': -1,
        'remodel': 1 if 'prev' in nedb_ship['remodel'] else -1,
        'build': -1,
        'buildtime': nedb_ship['buildtime']
    }


def get_ship_cv_illustrator(ship, nedb_ship, nedb_entities):
    '''Get CV and illustrator
    '''
    try:
        cv_id = nedb_ship['rels']['cv']
        illustrator_id = nedb_ship['rels']['illustrator']
    except KeyError:
    ship['cv'] = nedb_entities[cv_id]['name']['zh_cn']
    illustrator_id = nedb_entities[illustrator_id]['name']['zh_cn']

def get_ship_remodel(ship, nedb_ship, ship_id_kcwiki_id_table):
    '''Get the remodel information
    '''
    ship['remodel'] = {}
    # Get remodel level
    if 'next' in nedb_ship['remodel']:
        ship['remodel']['level'] = nedb_ship['remodel']['next_lvl']
        ship['remodel']['next_kcwiki_id'] = \
            ship_id_kcwiki_id_table[nedb_ship['remodel']['next']]


def main():
    '''Main process
    '''
    nedb_ships = nedb_parser(NEDB_SHIPS)
    nedb_entities = nedb_parser(NEDB_ENTITIES)
    nedb_ship_namesuffix = nedb_parser(NEDB_SHIP_NAMESUFFIX)
    nedb_ship_classes = nedb_parser(NEDB_SHIP_CLASSES)
    if not all((nedb_ships,
                nedb_entities,
                nedb_ship_namesuffix,
                nedb_ship_classes)):
        print('Failed and exit')
        return

    # None means no suffix, just be easy for programming to generate ship name
    nedb_ship_namesuffix[None] = {
        'ja_jp': '',
        'zh_cn': ''
    }

    ship_id_kcwiki_id_table = {}
    for nedb_ship in nedb_ships.values():
        ship = {'id': nedb_ship['id']}

        get_ship_no(ship, nedb_ship)
        get_ship_name(ship, nedb_ship, nedb_ship_namesuffix)
        get_ship_type(ship, nedb_ship)
        get_ship_class(ship, nedb_ship, nedb_ship_classes)
        get_ship_stat(ship, nedb_ship)
        get_ship_rare(ship, nedb_ship)
        get_ship_slot(ship, nedb_ship)
        get_ship_equip(ship, nedb_ship)
        get_ship_consum(ship, nedb_ship)
        get_ship_modernization(ship, nedb_ship)
        get_ship_scrap(ship, nedb_ship)
        get_ship_kcwiki_id(ship, nedb_ship, nedb_ships)
        get_ship_get_method(ship, nedb_ship)
        get_ship_cv_illustrator(ship, nedb_ship, nedb_entities)

        ship_id_kcwiki_id_table[ship['id']] = ship['kcwiki_id']

        print()
        # print(ship['zh_cn'].encode('utf-8'))
        # pprint(ship)
        pprint(ship)



if __name__ == '__main__':
    main()
