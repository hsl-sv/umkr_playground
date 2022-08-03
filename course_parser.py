import numpy as np
import sqlite3
import json
import glob
import os

import warnings
warnings.filterwarnings('ignore')

from vispy import scene, app
from vispy.util.transforms import rotate
from vispy.io import imsave

from course_dict import course_dict
from course_sql_query import *

MDB_PATH = os.path.join('MDB', 'master.mdb')

def course_drawer(text_course_userinput,
                  text_course_distance_userinput,
                  text_course_type_userinput,
                  text_course_turn_userinput,
                  text_course_inout_userinput='',
                  **kwargs
                  ):

    # Fetch data
    # Fetch from sqlite
    mdb = sqlite3.connect(MDB_PATH)
    mdb_cursor = mdb.cursor()

    query = fetch_course_id_and_name(text_course_userinput)

    mdb_cursor.execute(query)
    mdb_result_all = mdb_cursor.fetchall()

    if len(mdb_result_all) < 1:
        print(f'Cannot find course named {text_course_userinput}')
        mdb.close()
        return

    mdb_result = mdb_result_all[0]

    text_course_id = mdb_result[0]
    text_course_name = mdb_result[1]

    course_info = course_dict()

    if text_course_type_userinput in course_info.type.keys():
        text_course_type_id = course_info.type[text_course_type_userinput]
        text_course_type_name = text_course_type_userinput
    else:
        text_course_type_id = course_info.type['잔디']
        text_course_type_name = '잔디'

    if text_course_inout_userinput in course_info.inout.keys():
        text_course_inout_id = course_info.inout[text_course_inout_userinput]
        text_course_inout_name = text_course_inout_userinput
    else:
        text_course_inout_id = course_info.inout['구분없음']
        text_course_inout_name = ''

    if text_course_turn_userinput in course_info.turn.keys():
        text_course_turn_id = course_info.turn[text_course_turn_userinput]
        text_course_turn_name = text_course_turn_userinput
    else:
        text_course_turn_id = course_info.turn['우']
        text_course_turn_name = '우'

    text_course_distance = int(text_course_distance_userinput) if isinstance(text_course_distance_userinput, int) else None
    if text_course_distance is not None and text_course_distance > 3600:
        text_course_distance = 3600
    elif text_course_distance is not None and text_course_distance < 1000:
        text_course_distance = 1000
    elif text_course_distance is None:
        print('Cannot parse course distance')
        mdb.close()
        return
    else:
        text_course_distance = int(np.round(text_course_distance / 100) * 100)

    # Fetch CourseParamTable id
    query = fetch_course_param_table_id(text_course_id, text_course_distance,
                                        text_course_type_id, text_course_inout_id,
                                        text_course_turn_id)

    mdb_cursor.execute(query)
    mdb_result = mdb_cursor.fetchone()

    if not mdb_result:
        print('Course not found')
        mdb.close()
        return

    text_course_param_table_id = mdb_result[0]

    query = fetch_course_name(text_course_param_table_id)

    mdb_cursor.execute(query)
    mdb_result = mdb_cursor.fetchall()

    text_course_used_race = mdb_result # tuples

    mdb.close()

    # Require : Course name + Meter for select RacePosition json
    _path_dist = f'*_{text_course_distance}_*.json'
    for k, v in kwargs.items():
        # course_spec='01_0_0'...
        if 'course_spec' in kwargs.keys():
            _path_dist = f'*_{text_course_distance}_{v}*.json' # TODO: _00_ vs _01_ ?

    # 나카야마 RacePosition\\10005\\pos\\an_pos_race10005_00_2500_01_0_0.json -> 회전 중간에 스타트
    # 나카야마 RacePosition\\10005\\pos\\an_pos_race10005_00_2500_00_1_0~1.json -> 실제 스타트
    file = glob.glob(os.path.join('RacePosition', str(text_course_id), 'pos', _path_dist))

    if len(file) > 1:
        file = [file[0]]

    # Require : master.mdb data for select CourseParamTable json
    # 나카야마 CourseParamTable 10506
    param = glob.glob(os.path.join('CourseParamTable', str(text_course_param_table_id), 'CourseParamTable.json'))

    # Prepare data
    fid = open(file[0], 'r', encoding='utf-8')
    fid_p = open(param[0], 'r', encoding='utf-8')
    jparse = json.load(fid)
    courseparam = json.load(fid_p)
    fid.close()
    fid_p.close()

    xx = jparse['key']['valueX']
    zz = jparse['key']['valueZ']
    yy = jparse['key']['valueY']
    tt = list(dict.fromkeys(np.array(yy).astype(int)))
    race_distance = jparse['Distance']
    print(f'Highest : {max(yy)}, Distance : {race_distance}')
    tt = np.hstack(tt)

    turnparam = courseparam['courseParams']
    param_straight = [item for i, item in enumerate(turnparam) if item['_paramType'] == 2]
    param_turn = [item for i, item in enumerate(turnparam) if item['_paramType'] == 0]
    race_course_sub = []
    race_course_sub_orig = []
    race_course_turn_sub = []
    race_course_turn_sub_orig = []

    for i, item in enumerate(param_straight):
        dist_resample = int(item['_distance'] / race_distance * len(yy))
        if dist_resample < 0:
            dist_resample = 0
        elif dist_resample >= len(yy):
            dist_resample = len(yy) - 1
        race_course_sub.extend([dist_resample])
        race_course_sub_orig.extend([item['_distance']])

    for i, item in enumerate(param_turn):
        dist_resample = int(item['_distance'] / race_distance * len(yy))
        if dist_resample < 0:
            dist_resample = 0
        elif dist_resample >= len(yy):
            dist_resample = len(yy) - 1
        dist_sect_resample = int(item['_values'][1] / race_distance * len(yy))
        if dist_sect_resample < 0:
            dist_sect_resample = 0
        elif dist_sect_resample >= len(yy):
            dist_sect_resample = len(yy) - 1
        race_course_turn_sub.append([[item['_values'][0], dist_sect_resample], dist_resample])
        race_course_turn_sub_orig.append([item['_values'], item['_distance']])

    # Drawing part
    canvas = scene.SceneCanvas(keys='interactive')
    canvas.size = 1600, 900
    canvas.show()
    # Add grid
    grid = canvas.central_widget.add_grid(bgcolor='w', border_color='k')

    # Add 4 ViewBoxes to the grid
    # Top-Down
    b1 = grid.add_view(row=0, col=0, col_span=2)
    b1.border_color = (0.5, 0.5, 0.5, 1)
    td_longest = max(max(map(abs, xx)), max(map(abs, zz)))
    td_pad = td_longest + 100
    td_center = ((min(xx) + max(xx)) / 2, (min(zz) + max(zz)) / 2)
    print(min(zz))
    print(max(zz))
    # rect= (LEFT, TOP, WIDTH (from LEFT), HEIGHT (from TOP))
    b1.camera = scene.PanZoomCamera(rect=(-td_pad, -td_pad, td_pad * 2, td_pad * 2), aspect=1)
    b1.camera.center = td_center
    b1.camera.zoom(0.5)

    # Text description
    b2 = grid.add_view(row=0, col=2)
    b2.camera = scene.PanZoomCamera(rect=(0, 0, 20, 20))
    b2.border_color = (0.5, 0.5, 0.5, 1)

    # Height + Course Separations
    b3 = grid.add_view(row=1, col=0, col_span=2)
    b3.border_color = (0.5, 0.5, 0.5, 1)

    ch_xax_size = min(race_distance / 100 * 8, 100)
    ch_xax_margin = min(race_distance / 100 * 10, 150)

    ch_yax_margin_lower = 0.3
    ch_yax_start = np.floor(min(yy)) - ch_yax_margin_lower
    ch_yax_margin_upper = 0.5
    ch_yax_end = np.abs(ch_yax_start) + np.ceil(max(yy)) + ch_yax_margin_upper
    b3.camera = scene.PanZoomCamera(rect=(-ch_xax_size, ch_yax_start,
                                          len(yy)+ch_xax_margin, ch_yax_end))

    # Rotating course
    b4 = grid.add_view(row=1, col=2)
    b4.border_color = (0.5, 0.5, 0.5, 1)
    cam_3d_center = (0, 0)
    cam_3d = scene.TurntableCamera(scale_factor=1000, center=cam_3d_center, elevation=20, azimuth=120)
    b4.camera = cam_3d

    # Generate vertex
    # Top-down
    N = len(xx)
    NSub = len(race_course_sub)
    NTurnSub = len(race_course_turn_sub)
    pos = np.empty((N, 2), dtype=float)
    pos[:, 0] = xx
    pos[:, 1] = zz

    pos_sub = np.empty((NSub, 2), dtype=float)
    pos_sub[:] = pos[race_course_sub[:],:]

    if text_course_turn_id != 4:
        pos_turns = np.empty((NTurnSub, 2), dtype=float)
        _rctmp = np.array(race_course_turn_sub)
        _rctmp = _rctmp[:,1].tolist()
        pos_turns[:] = pos[_rctmp, :]

    # Colormap
    color = np.ones((N, 4), dtype=float)
    color[:, 0] = np.linspace(0, 1, N)
    color[:, 1] = np.linspace(1, 0, N)
    color[:, 2] = np.linspace(0.2, 0.2, N)

    # Height
    pos_height = np.empty((N, 2), dtype=float)
    pos_height[:, 0] = np.linspace(0, len(yy), len(yy), endpoint=True)
    pos_height[:, 1] = yy

    # 3D Scatter
    pos_3d = np.zeros((N, 3), dtype=float)
    for i in range(N):
        pos_3d[i] = xx[i], zz[i], (yy[i] * 25) # scale height

    pos_3d_sub = np.empty((NSub, 3), dtype=float)
    pos_3d_sub[:] = pos_3d[race_course_sub[:],:]

    # Racecourse
    gridcontents_course = scene.visuals.Line(pos=pos, color=color, antialias=False, width=3, method='gl', parent=b1.scene)
    gridcontents_course.update_gl_state(depth_test=False)
    gridcontents_course_sub = scene.visuals.Markers(parent=b1.scene)
    gridcontents_course_sub.set_data(pos_sub, size=15, symbol='vbar', face_color='k', edge_width=0,)
    gridcontents_course_sub.update_gl_state(depth_test=False)

    if text_course_turn_id != 4:
        gridcontents_course_turn_sub = scene.visuals.Markers(parent=b1.scene)
        gridcontents_course_turn_sub.set_data(pos_turns, size=15, symbol='x', face_color='r', edge_width=0)
        gridcontents_course_turn_sub.update_gl_state(depth_test=False)

    #race_course_turn_sub_idx = [str(item[0][0]) for i, item in enumerate(race_course_turn_sub)]
    sub_wp = np.copy(pos[-1])
    sub_wp[1] -= 40
    scene.visuals.Text(text='WP', pos=sub_wp, rotation=90.0, color='k', parent=b1.scene)
    sub_start = np.copy(pos[0])
    sub_start[1] -= 40
    scene.visuals.Text(text='START', pos=sub_start, rotation=90.0, color='k', parent=b1.scene)

    #scene.visuals.Text(text=race_course_turn_sub_idx, pos=pos_turns, rotation=90.0, color='r', parent=b1.scene)

    # Text description - [0, 0, 20, 20]
    _str_builder = f'<코스 일반 정보>\n\n'
    _str_course = f'코스명 : {text_course_name}\n' \
                    f'코스길이 : {text_course_distance}\n' \
                    f'코스타입 : {text_course_type_name}\n' \
                    f'코스정보 : {text_course_turn_name} / {text_course_inout_name}\n' \
                    f'최고/최저높이 : {max(yy):.1f}m / {min(yy):.1f}m\n' \
                    f'(ID {text_course_id}, ParamID {text_course_param_table_id})\n\n'

    _str_builder += _str_course

    scene.visuals.Text(text=_str_builder, pos=[5, 10], parent=b2.scene, face='맑은 고딕', font_size=15)

    _str_builder = f'<개최 레이스 목록>\n\n'
    for i in range(len(text_course_used_race)):
        _str_builder += f'{text_course_used_race[i][0]}\n'

    scene.visuals.Text(text=_str_builder, pos=[15, 10], parent=b2.scene, face='맑은 고딕', font_size=15)


    # Course Height
    gridcontents_courseheight = scene.visuals.Line(pos=pos_height, color=color, antialias=True, width=3, method='gl', parent=b3.scene)
    gridcontents_courseheight.update_gl_state(depth_test=False)
    scene.Axis(pos=[[0, 0], [N, 0]], tick_direction=(0,-1), domain=(0, race_distance), axis_color='k',
               tick_color='k', text_color='k', axis_font_size=12, tick_font_size=12,
               axis_label_margin=30, tick_label_margin=8, parent=b3.scene)
    scene.Axis(pos=[[0, np.floor(min(yy))], [0, np.ceil(max(yy))]], tick_direction=(-1, 0),
               domain=(np.floor(min(yy)), np.ceil(max(yy))), axis_label='meter',
               axis_color='k', axis_font_size=12, tick_font_size=12,
               tick_color='k', text_color='k',
               axis_label_margin=30, tick_label_margin=8, parent=b3.scene)

    for i in range(len(race_course_sub)):
        scene.visuals.InfiniteLine(race_course_sub[i], [0.5,0.5,0.5,0.5], parent=b3.scene)

        if i % 2 == 1:
            continue

        if i == len(race_course_sub) - 1:
            pass
        else:
            scene.visuals.Text(text=str(f'{race_course_sub_orig[i + 1] - race_course_sub_orig[i]:.0f}'),
                               pos=[race_course_sub[i + 1] - 30, max(yy)+0.2],
                               font_size=12, parent=b3.scene)

    if text_course_turn_id != 4:
        _rctmp = np.array(race_course_turn_sub)
        _rcotmp = np.array(race_course_turn_sub_orig)
        _cmtmp = [[1, 0.27, 0, 0.2],
                  [0.27, 1, 0, 0.2],
                  [0, 0.27, 1, 0.2],
                  [0.58, 0, 0.82, 0.2],]

        for i in range(len(_rctmp)):
            scene.visuals.LinearRegion([_rctmp[i,1], _rctmp[i,1] + _rctmp[i,0][1]], _cmtmp[int(i % 4)], parent=b3.scene)

            scene.visuals.Text(text=str(f'#{_rctmp[i,0][0]} {_rcotmp[i,0][1]:.0f}'),
                               pos=[_rctmp[i,1] + _rctmp[i,0][1] - 40, max(yy)+0.2],
                               font_size=12, parent=b3.scene, color=(0.545, 0, 0, 0.75))

    # 3D Rotating
    gridcontents_3d = scene.visuals.Markers(parent=b4.scene)
    gridcontents_3d.set_data(pos_3d, size=2, symbol='o', face_color=color, edge_width=0)
    gridcontents_3d.update_gl_state(depth_test=False)
    gridcontents_3d_sub = scene.visuals.Markers(parent=b4.scene)
    gridcontents_3d_sub.set_data(pos_3d_sub, size=10, symbol='vbar', face_color='black', edge_width=0)
    gridcontents_3d_sub.update_gl_state(depth_test=False)

    def camera_rotate(event):
        rotmat = rotate(1.0, (0,0,1)) #.dot(rotate(25, (0,1,0)))
        b4.camera.transform.matrix = np.dot(b4.camera.transform.matrix, rotmat)
        b4.update()

    timer = app.Timer(interval='auto', connect=camera_rotate, start=True)

    app.run()

    imsave('test.png', canvas.render())

def course_drawer_wrapper(text_race_userinput):

    mdb = sqlite3.connect(MDB_PATH)
    mdb_cursor = mdb.cursor()

    query = fetch_course_index(text_race_userinput)
    mdb_cursor.execute(query)
    fetch_result = mdb_cursor.fetchone()

    if not fetch_result:
        print(f'Cannot find race named {text_race_userinput}')
        mdb.close()
        return

    race_index = fetch_result[0]

    query = fetch_course_set(text_race_userinput)
    mdb_cursor.execute(query)
    fetch_result = mdb_cursor.fetchone()
    course_set = fetch_result[0]

    query = fetch_course_param_table(course_set, race_index)
    mdb_cursor.execute(query)
    course_param_table = mdb_cursor.fetchone()

    # course_param_table = id / race_track_id / distance / ground / inout / turn ...
    query = fetch_course_name_with_id(course_param_table[1])
    mdb_cursor.execute(query)
    fetch_result = mdb_cursor.fetchone()
    course_name = fetch_result[0]

    mdb.close()

    course_info = course_dict()

    course_drawer(text_course_userinput=course_name,
                  text_course_distance_userinput=course_param_table[2],
                  text_course_turn_userinput=course_info.turn[course_param_table[5]],
                  text_course_type_userinput=course_info.type[course_param_table[3]],
                  text_course_inout_userinput=course_info.inout[course_param_table[4]],
                  )

if __name__ == '__main__':

    #course_drawer_wrapper(text_race_userinput='부상 직후 트레이닝')
    

    course_drawer(text_course_userinput='한신',
                  text_course_distance_userinput=3200,
                  text_course_type_userinput='잔디',
                  text_course_turn_userinput='우',
                  text_course_inout_userinput='외내',
                  )
