##-0 Library導入-##
import streamlit as st # UI画面
import streamlit_shadcn_ui as ui
import numpy as np # データ処理
import polars as pl
import pandas as pd
from modules.data_loader import load_data
from modules.data_processor import get_most_syuyaku, get_sorted_unique_values, filter_data_sequentially
from modules.visualizer import create_dashboard_figure
from modules.data_transformer import prepare_visualization_data
from modules.auth_utils import setup_page_config, initialize_authentication

# Setup page configuration
setup_page_config()

# Initialize authentication
authenticator, auth_status = initialize_authentication()

# Main application logic
if auth_status:
    # Load and filter data
    raw, dateInfo, rate, metricTable, itemInfoTable, skuSummary, AccuracySummary, ProblemSummary = load_data()
    most_syuyaku_Brand, most_syuyaku_Region, most_syuyaku_Department, most_syuyaku_SubCategory, most_syuyaku = get_most_syuyaku(raw)
    
    # Your filtering code now uses the imported functions
    sorted_Brand = get_sorted_unique_values(raw, 'Brand')
    selected_Brand = st.sidebar.selectbox("グローバル事業", sorted_Brand, index = sorted_Brand.index(most_syuyaku_Brand))
    raw_filtered = filter_data_sequentially(raw, selected_Brand=selected_Brand)

    # フィルタ1: 事業を選択
    sorted_Brand = get_sorted_unique_values(raw, 'Brand')
    selected_Brand = st.sidebar.selectbox("グローバル事業", sorted_Brand, index = sorted_Brand.index(most_syuyaku_Brand))
    raw_filtered = filter_data_sequentially(raw, selected_Brand=selected_Brand)

    # フィルタ2: 事業を選択した上で、国を選択
    sorted_Region = get_sorted_unique_values(raw_filtered, 'Region')
    selected_Region = st.sidebar.selectbox("事業国", sorted_Region, index = sorted_Region.index(most_syuyaku_Region))
    raw_filtered = filter_data_sequentially(raw_filtered, selected_Region=selected_Region)

    # フィルタ3: 事業と国選択した上で、部門を選択
    sorted_Department = get_sorted_unique_values(raw_filtered, 'Department')
    selected_Department = st.sidebar.selectbox("部門", sorted_Department, index = sorted_Department.index(most_syuyaku_Department))
    raw_filtered = filter_data_sequentially(raw_filtered, selected_Department=selected_Department)

    # フィルタ4: 事業、国、部門を選択した上で、サブカテゴリを選択
    sorted_SubCategory = get_sorted_unique_values(raw_filtered, 'SubCategory')
    selected_SubCategory = st.sidebar.selectbox("サブカテゴリ", sorted_SubCategory, index = sorted_SubCategory.index(most_syuyaku_SubCategory))
    raw_filtered = filter_data_sequentially(raw_filtered, selected_SubCategory=selected_SubCategory)

    # フィルタ5: すべての以前の選択に基づいた集約の選択
    sorted_Syuyaku = get_sorted_unique_values(raw_filtered, 'Syuyaku')
    selected_Syuyaku = st.sidebar.selectbox("販売集約", sorted_Syuyaku)
    raw_filtered = filter_data_sequentially(raw_filtered, selected_Syuyaku=selected_Syuyaku)

    # フィルタ6: 選択された集約のうち、サイズを選択(ディフォルト設定は全表示[S, M, L])
    sorted_Size = get_sorted_unique_values(raw_filtered, 'Size')
    selected_Size = st.sidebar.multiselect("サイズ", sorted_Size, placeholder = "未入力の場合、全選択される")
    raw_filtered = filter_data_sequentially(raw_filtered, selected_Size=selected_Size)

    # フィルタ7: 選択された集約のうち、色を選択(ディフォルト設定は全表示[Color1, Color2])
    sorted_Color = get_sorted_unique_values(raw_filtered, 'Color')
    selected_Color = st.sidebar.multiselect("カラー", sorted_Color, placeholder = "未入力の場合、全選択される")    
    raw_filtered = filter_data_sequentially(raw_filtered, selected_Color=selected_Color)

    # フィルタ8: 選択された集約のうち、SKUを選択(ディフォルト設定は全表示[S, M, L] * [Color1, Color2])
    sorted_SKU = get_sorted_unique_values(raw_filtered, 'SKU')
    selected_SKU = st.sidebar.multiselect("SKU", sorted_SKU, placeholder = "未入力の場合、全選択される")
    raw_filtered = filter_data_sequentially(raw_filtered, selected_SKU=selected_SKU)

    # 日付範囲の選択
    start_date = st.sidebar.date_input("開始日", raw.select(pl.col("Date")).min().to_series()[0])
    end_date = st.sidebar.date_input("終了日", raw.select(pl.col("Date")).max().to_series()[0])

    # ユーザ操作によって、フィルタされたデータ
    raw_filtered = filter_data_sequentially(raw_filtered, start_date=start_date, end_date=end_date)

    # Prepare data for visualization
    df_disp, df_real, df_pred = prepare_visualization_data(
        raw_filtered, dateInfo, rate, selected_Region, selected_Syuyaku
    )

    # Get column names for visualization
    size_cols = raw_filtered.select(pl.col("Size")).unique().to_series().to_list()
    color_cols = raw_filtered.select(pl.col("Color")).unique().to_series().to_list()
    
    # Create and display visualization
    fig = create_dashboard_figure(df_disp, df_real, df_pred, color_cols, size_cols)
    st.pyplot(fig)
