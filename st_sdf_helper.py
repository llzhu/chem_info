import os
import io
import pandas as pd
from rdkit.Chem import PandasTools, Draw
import os.path
from os import path
import streamlit as st
import base64
from io import StringIO


STRUCTURE = 'Molecule'

st.set_page_config(page_title='SDF Viewer', layout='wide')

def get_df_download_csv(df, download_filename, link_label, structure_column):
    if structure_column is not None:
        del df[structure_column]
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    #href = f'<a href="data:file/csv;base64,{b64}">{link_label}</a>'
    href = f'<a href="data:file/txt;base64,{b64}" download="{download_filename}">{link_label}</a>'
    return href

def get_df_download_sdf(df, download_filename, link_label, structure_column):
    f = StringIO()
    PandasTools.WriteSDF(df, f, molColName=structure_column,
                         properties=list(df.columns), allNumeric=False)
    #csv = df.to_csv(index=False)
    data = f.getvalue()
    b64 = base64.b64encode(data.encode()).decode()  # some strings <-> bytes conversions necessary here
    #href = f'<a href="data:file/csv;base64,{b64}">{link_label}</a>'
    href = f'<a href="data:file/txt;base64,{b64}" download="{download_filename}">{link_label}</a>'
    return href

def get_sdf_df(uploaded_file):
    if uploaded_file is not None:
        df_upload = PandasTools.LoadSDF(uploaded_file,smilesName='SMILES',molColName=STRUCTURE)
        return df_upload

def get_rename_dict(header_rename):
    if header_rename:
        rename_list = header_rename.split(',')
        rename_dict = {}
        for rename in rename_list:
            rename_old_new = rename.split('=')
            rename_dict[rename_old_new[0].strip()] = rename_old_new[1].strip()

        return rename_dict


uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:
    df_upload = get_sdf_df(uploaded_file)
    all_headers = list(df_upload.columns.values)
    all_headers.remove('ID')
    all_headers.remove(STRUCTURE)
    all_headers.insert(0, STRUCTURE)
    headers = st.sidebar.multiselect('Select headers', all_headers, all_headers)

    header_rename = st.sidebar.text_area('Rename Headers')
    rename_dict = get_rename_dict(header_rename)

    sort_headers = headers.copy()
    sort_headers.remove(STRUCTURE)
    # st.write(sort_headers)
    sort_by = st.sidebar.selectbox('Sort by:', sort_headers)

    if rename_dict and len(rename_dict) > 0:
        df_upload = df_upload[headers]
        df_upload = df_upload.rename(columns=rename_dict)
    else:
        df_upload = df_upload[headers]

    if sort_by:
        df_upload.sort_values(by=sort_by, inplace=True)

    st.write(df_upload.to_html(escape=False), unsafe_allow_html=True)

    st.sidebar.markdown(get_df_download_sdf(df_upload, 'streamlit_download.sdf', 'Download as Sdf!', STRUCTURE), unsafe_allow_html=True)
    st.sidebar.markdown(get_df_download_csv(df_upload, 'streamlit_download.csv', 'Download as csv!', STRUCTURE), unsafe_allow_html=True)

secret_string =st.secrets["db_password"]
st.sidebar.write("you are not supposed to see this:", secret_string)
