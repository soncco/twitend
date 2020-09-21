def change_col_name(col_name):
    col_name = col_name.replace("('", '')
    col_name = col_name.replace("', 'tweets_counter')", '')
    return col_name
