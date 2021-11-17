import numpy as np
from flask import request, jsonify
from numpy import genfromtxt

from server import app, knn
from server.models import Picture


@app.route('/get_similar', methods=['POST'])
def get_similar():
    data = request.get_json().get('nameValuePairs')
    vector = data.get('vector')
    k_neighbors = data.get('k_neighbors')

    result_pictures_list = find_similar(vector, k_neighbors)
    # print('Result: ', result_pictures_list)

    resp = jsonify(result_pictures_list)
    resp.status_code = 200
    return resp


def find_similar(vector_list, k_neighbors_str=5):
    k_neighbors = int(k_neighbors_str)
    if k_neighbors <= 0:
        k_neighbors = 5

    vector = np.asarray([vector_list])
    # np.savetxt('./file.csv', vector, delimiter='|', fmt='%s')

    limit = 0.45
    dist, indices = knn.kneighbors(vector.reshape(1, -1), n_neighbors=k_neighbors)
    dist, indices = dist.flatten(), indices.flatten()

    dist_limited = dist[dist <= limit]
    indices_limited = indices[:len(dist_limited)]

    pics = get_pics_from_db((indices_limited + 1).tolist())
    return pics


def get_pics_from_db(ids):
    pictures_db = []
    for id in ids:
        pictures_db.append(Picture.query.filter(Picture.id==id).first())

    pictures_list = []
    for picture in pictures_db:
        new_pic = {'id': picture.id, 'title': picture.title,
                   'painter': picture.painter, 'image': picture.image}
        pictures_list.append(new_pic)
    return pictures_list




def process(pipeline, text='Строка', keep_pos=True, keep_punct=False):
    entities = {'PROPN'}
    named = False  # переменная для запоминания того, что нам встретилось имя собственное
    memory = []
    mem_case = None
    mem_number = None
    tagged_propn = []

    # обрабатываем текст, получаем результат в формате conllu:
    processed = pipeline.process(text)
    # пропускаем строки со служебной информацией:
    content = [l for l in processed.split('\n') if not l.startswith('#')]
    # извлекаем из обработанного текста леммы, тэги и морфологические характеристики
    tagged = [w.split('\t') for w in content if w]

    for t in tagged:
        if len(t) != 10: # если список короткий — строчка не содержит разбора, пропускаем
            continue
        (word_id,token,lemma,pos,xpos,feats,head,deprel,deps,misc) = t
        if not lemma or not token: # если слово пустое — пропускаем
            continue
        if pos in entities: # здесь отдельно обрабатываем имена собственные — они требуют особого обращения
            if '|' not in feats:
                tagged_propn.append('%s_%s' % (lemma, pos))
                continue
            morph = {el.split('=')[0]: el.split('=')[1] for el in feats.split('|')}
            if 'Case' not in morph or 'Number' not in morph:
                tagged_propn.append('%s_%s' % (lemma, pos))
                continue
            if not named:
                named = True
                mem_case = morph['Case']
                mem_number = morph['Number']
            if morph['Case'] == mem_case and morph['Number'] == mem_number:
                memory.append(lemma)
                if 'SpacesAfter=\\n' in misc or 'SpacesAfter=\s\\n' in misc:
                    named = False
                    past_lemma = '::'.join(memory)
                    memory = []
                    tagged_propn.append(past_lemma + '_PROPN ')
            else:
                named = False
                past_lemma = '::'.join(memory)
                memory = []
                tagged_propn.append(past_lemma + '_PROPN ')
                tagged_propn.append('%s_%s' % (lemma, pos))
        else:
            if not named:
                if pos == 'NUM' and token.isdigit():  # Заменяем числа на xxxxx той же длины
                    lemma = num_replace(token)
                tagged_propn.append('%s_%s' % (lemma, pos))
            else:
                named = False
                past_lemma = '::'.join(memory)
                memory = []
                tagged_propn.append(past_lemma + '_PROPN ')
                tagged_propn.append('%s_%s' % (lemma, pos))

    if not keep_punct: # обрабатываем случай, когда пользователь попросил не сохранять пунктуацию (по умолчанию она сохраняется)
        tagged_propn = [word for word in tagged_propn if word.split('_')[1] != 'PUNCT']
    if not keep_pos:
        tagged_propn = [word.split('_')[0] for word in tagged_propn]
    return tagged_propn