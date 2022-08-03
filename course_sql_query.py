# Return only query

def fetch_course_id_and_name(text_course_userinput):

    if '니가타' in text_course_userinput:
        text_course_userinput = text_course_userinput.replace('니가타', '니이가타')

    query = f"SELECT [index], [text] FROM text_data " \
            f"WHERE REPLACE([text], ' ', '') LIKE \"%{text_course_userinput.replace(' ','')}%\" " \
            f"AND category IS 31" # cat 31 = stadium

    return query

def fetch_course_name_with_id(course_id):

    query = f"SELECT [text] FROM text_data " \
            f"WHERE text_data.[index] = {course_id} " \
            f"AND category IS 31"

    return query

def fetch_course_param_table_id(text_course_id,
                                text_course_distance,
                                text_course_type_id,
                                text_course_inout_id,
                                text_course_turn_id):

    query = f"SELECT [id] FROM race_course_set " \
            f"WHERE race_track_id IS {text_course_id} " \
            f"AND distance IS {text_course_distance} " \
            f"AND ground IS {text_course_type_id} " \
            f"AND inout IS {text_course_inout_id} " \
            f"AND turn IS {text_course_turn_id}"

    return query

def fetch_course_name(text_course_param_table_id):

    # 타카마츠노미야 기념 cat 32 idx 1002 (text_data)
    # cat 32 = race name
    # index 1xxx = G1, 2xxx = G2 3xxx = G3...
    # 타카마츠노미야 기념
    # course_set 10701 id 1002 (race) -> join text_data

    query = f"SELECT DISTINCT text_data.[text] FROM race INNER JOIN text_data " \
            f"ON race.course_set = {text_course_param_table_id} " \
            f"AND text_data.[index] = race.[id] " \
            f"WHERE text_data.category = 32"

    return query

def fetch_course_index(text_race_userinput):

    # It will be return multiple indexes
    query = f"SELECT text_data.[index] " \
            f"FROM text_data " \
            f"WHERE text_data.category = 32 " \
            f"AND REPLACE(text_data.[text], ' ', '') " \
            f"LIKE \"%{str(text_race_userinput).replace(' ', '')}%\""

    return query

def fetch_course_set(text_race_userinput):

    query = f"SELECT DISTINCT race.course_set " \
            f"FROM race INNER JOIN text_data " \
            f"ON text_data.[index] = race.[id] " \
            f"WHERE REPLACE(text_data.[text], ' ', '') " \
            f"LIKE \"%{str(text_race_userinput).replace(' ', '')}%\" " \
            f"AND text_data.category = 32 " \
            f"AND text_data.[index] = race.[id]"

    return query

def fetch_course_param_table(text_course_set, text_course_index):

    query = f"SELECT * " \
            f"FROM race_course_set INNER JOIN race " \
            f"ON race.course_set = race_course_set.[id] " \
            f"WHERE race_course_set.[id] = {text_course_set} " \
            f"AND race.[id] = {text_course_index}"

    return query

"""
Get races with conditions...

select race.id, text_data.[text] from race
inner join race_course_set on race_course_set.[id] = race.course_set
inner join text_data on text_data.[index] = race.[id]
where race_course_set.ground = 1 and text_data.category = 32 and race_course_set.turn = 2
"""