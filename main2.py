

import streamlit as st
from Consumer import Consumer
from Factory import Factory
from Labor_Market import L_M
from Goods_Market import G_M, I_M
import pandas as pd
import matplotlib.pyplot as plt
import random
import math
import sys
import scipy.optimize as opt
import time
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import base64
try:
    import altair as alt
    alt.data_transformers.disable_max_rows()
except:
    pass
# 在 main2.py 文件开头添加
import os
os.environ['ALTAIR_RENDERER'] = 'png'


# 修改 get_base64_of_bin_file 函数
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except Exception as e:
        st.error(f"Error loading background image")
        return ""  # 返回空字符串作为后备方案


# 设置页面配置
st.set_page_config(
    page_title="大经济学家游戏",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 设置背景和样式
def set_page_style():
    bin_str = get_base64_of_bin_file('background.png')
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{bin_str}");
            background-size: cover;
            background-position: center center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        .title-container {{
            background-color: rgba(0,0,0,0.7);
            padding: 2rem;
            border-radius: 10px;
            margin-bottom: 2rem;
        }}
        .game-title {{
            color: gold;
            font-family: 'Press Start 2P', cursive;
            text-align: center;
            font-size: 3rem;
            text-shadow: 3px 3px 5px #000;
        }}
        .policy-card {{
            background-color: rgba(255,255,255,0.9);
            padding: 1rem;
            border-radius: 5px;
            margin: 1rem 0;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# 在页面开始时调用
#set_page_style()

# 游戏标题
st.markdown('<div class="title-container"><h1 class="game-title">大经济学家游戏</h1></div>', unsafe_allow_html=True)



if 'simulation_done' not in st.session_state:
    st.session_state.simulation_done = False
if 'df' not in st.session_state:
    st.session_state.df = None
if 'df_equilibrium' not in st.session_state:
    st.session_state.df_equilibrium = None


# 侧边栏参数设置
st.sidebar.title("模型参数设置")
simulation_steps = st.sidebar.slider("预测长度", min_value=100, max_value=1000, value=400, step=40)
animation_speed = st.sidebar.slider("动画速度", min_value=1, max_value=10, value=5)
# 基础参数
st.sidebar.subheader("基础参数")
n = st.sidebar.number_input("初始人口数量", value=6500, min_value=1000, max_value=10000)
lab = st.sidebar.number_input("初始劳动时间", value=10, min_value=1, max_value=15)
A = st.sidebar.number_input("技术水平", value=3.0, min_value=0.1, max_value=10.0)
K = st.sidebar.number_input("初始资本存量", value=2000, min_value=500, max_value=5000)
w = st.sidebar.number_input("初始工资水平", value=15, min_value=5, max_value=30)
p_fd = st.sidebar.number_input("初始商品价格", value=10, min_value=1, max_value=20)

# 冲击设置
st.sidebar.subheader("经济冲击设置")
shock_type = st.sidebar.selectbox(
    "选择冲击类型",
    ["无", "大萧条", "技术进步", "人口冲击", "政府干预"]
)

shock_start = st.sidebar.number_input("冲击开始时间", value=100, min_value=0, max_value=500)
shock_duration = st.sidebar.number_input("冲击持续时间", value=120, min_value=30, max_value=300)

if shock_type != "无":
    shock_intensity = st.sidebar.slider(
        "冲击强度",
        min_value=0.0,
        max_value=10.0,
        value=4.0,
        step=0.5
    )

# 主要模拟逻辑
# 修改模拟函数的参数和缓存装饰器
@st.cache_data
def run_simulation(n, lab, A, K, w, p_fd, shock_type, shock_start, shock_duration,
                   shock_intensity=1.0, time_length=200,
                   fiscal_policy_1_time=100, fiscal_policy_1=0.0,
                   fiscal_policy_2_time=100, fiscal_policy_2=0.0,
                   monetary_policy_1_time=100, monetary_policy_1=0.0,
                   monetary_policy_2_time=100, monetary_policy_2=0.0):
    # 实例化
    consumer = Consumer(n=n, lab=lab)
    factory = Factory(A=A, K=K, consumer=consumer)
    l_m = L_M(w=w)
    g_m = G_M(p_fd=p_fd)
    i_m = I_M(bop=0)

    # 存储数据
    df = pd.DataFrame(columns=['labor time', 'K', 'N', 'population size', 'p_fd', 'w', "bop"])
    df_equilibrium = pd.DataFrame(columns=['g_m.goods_supply', 'g_m.goods_demand',
                                           'l_m.labor_supply', 'l_m.labor_demand'])

    fd_history = 0

    # 模拟循环
    for i in range(time_length):
        # 基础技术进步
        if i <= 400:
            factory.A += 0.001
        else:
            factory.A += 0.0015

        # 处理政策效果
        if i == fiscal_policy_1_time:
            factory.A *= (1 + fiscal_policy_1 / 100)
        if i == fiscal_policy_2_time:
            consumer.n *= (1 - fiscal_policy_2 / 100)
        if i == monetary_policy_1_time:
            l_m.w *= (1 + monetary_policy_1 / 100)
        if i == monetary_policy_2_time:
            g_m.p_fd *= (1 + monetary_policy_2 / 100)

        # 处理冲击
        if shock_type != "无" and shock_start <= i <= (shock_start + shock_duration):
            if shock_type == "大萧条":
                factory.A -= ((shock_duration - (i - shock_start)) / 1000) * 0.008 * shock_intensity
                l_m.w = l_m.w * (1 - ((i - shock_start) / 70000) * shock_intensity)
                if i >= (shock_start + 30):
                    g_m.p_fd = g_m.p_fd * (1 - ((i - shock_start - 30) / 80000) * shock_intensity)

        # 更新模型状态 (保持原有代码不变)
        fd_history = factory.fd
        l_m.adjust_w(consumer=consumer, factory=factory, g_m=g_m)
        g_m.adjust_p_fd(consumer=consumer, factory=factory, l_m=l_m)
        consumer.update_lab(l_m=l_m, g_m=g_m)
        factory.N = consumer.lab * consumer.n
        factory.Revenue(l_m=l_m, g_m=g_m, consumer=consumer)
        factory.K = factory.K + factory.Import(g_m=g_m)
        factory.Production()
        consumer.Population_growth((factory.fd - fd_history) / fd_history)

        # 更新均衡值 (保持原有代码不变)
        g_m.goods_supply = factory.A * factory.K ** 0.2 * factory.N ** 0.8
        g_m.goods_demand = (l_m.w * consumer.lab / g_m.p_fd) * consumer.n
        l_m.labor_supply = consumer.lab * consumer.n
        l_m.labor_demand = factory.N
        i_m.bop = i_m.bop + (g_m.goods_supply - g_m.goods_demand)

        df.loc[i] = [consumer.lab, factory.K, factory.N, consumer.n, g_m.p_fd, l_m.w, i_m.bop]
        df_equilibrium.loc[i] = [g_m.goods_supply, g_m.goods_demand,
                                 l_m.labor_supply, l_m.labor_demand]

    # 对数转换
    df['p_fd'] = df['p_fd'].apply(math.log)
    df['w'] = df['w'].apply(math.log)

    return df, df_equilibrium


# 可视化函数
def create_advanced_visualizations(df, df_equilibrium):
    # 创建高级图表

    # 1. 综合经济指标热力图
    economic_indicators = df[['labor time', 'K', 'N', 'population size', 'p_fd', 'w']].copy()
    economic_indicators = (economic_indicators - economic_indicators.mean()) / economic_indicators.std()

    fig_heatmap = go.Figure(data=go.Heatmap(
        z=economic_indicators.T,
        x=economic_indicators.index,
        y=economic_indicators.columns,
        colorscale='RdBu'
    ))
    fig_heatmap.update_layout(title='经济指标相对变化热力图')

    # 2. 市场均衡差异图
    goods_market_gap = df_equilibrium['g_m.goods_supply'] - df_equilibrium['g_m.goods_demand']
    labor_market_gap = df_equilibrium['l_m.labor_supply'] - df_equilibrium['l_m.labor_demand']

    fig_gaps = go.Figure()
    fig_gaps.add_trace(go.Scatter(y=goods_market_gap, name='商品市场差额'))
    fig_gaps.add_trace(go.Scatter(y=labor_market_gap, name='劳动力市场差额'))
    fig_gaps.update_layout(title='市场供需差额变化')

    # 3. 经济周期分析
    cycle_data = pd.DataFrame({
        'GDP': df_equilibrium['g_m.goods_supply'],
        'Employment': df_equilibrium['l_m.labor_demand']
    })
    cycle_data = cycle_data.rolling(window=20).mean()

    fig_cycle = px.scatter(cycle_data, x='GDP', y='Employment',
                           title='GDP-就业关系周期图',
                           trendline="ols")

    return fig_heatmap, fig_gaps, fig_cycle


# 开始模拟按钮
# 修改开始模拟按钮的处理代码
if st.button("开始模拟"):
    # 运行模拟，传入所有必要的参数
    df, df_equilibrium = run_simulation(
        n=n, lab=lab, A=A, K=K, w=w, p_fd=p_fd,
        shock_type=shock_type,
        shock_start=shock_start,
        shock_duration=shock_duration,
        shock_intensity=shock_intensity if shock_type != "无" else 1.0,
        time_length=simulation_steps,

    )

    # 存储模拟结果
    st.session_state.simulation_data = df
    st.session_state.equilibrium_data = df_equilibrium

    # 创建可视化展示区域
    st.header("结果可视化呈现")

    # 政策控制面板
    st.markdown("### 经济政策调控展示")
    # 创建两列，分别显示财政政策和货币政策
    col3, col4 = st.columns(2)

    with col3:
        st.markdown('<div class="policy-control">', unsafe_allow_html=True)
        st.subheader("财政政策")

        # 财政政策的两个滑块控件
        fiscal_col1, fiscal_col2 = st.columns(2)
        with fiscal_col1:
            fiscal_policy_1_time = st.slider("政府支出实施时间点", 0, simulation_steps, 180)
            fiscal_policy_2_time = st.slider("税收政策实施时间点", 0, simulation_steps, 80)
        with fiscal_col2:
            fiscal_policy_1 = st.slider("政府支出调节力度", -10.0, 10.0, 1.0, 0.5)
            fiscal_policy_2 = st.slider("税收调节力度", -10.0, 10.0, 2.5, 0.5)

        st.markdown('</div>', unsafe_allow_html=True)

    with col4:
        st.markdown('<div class="policy-control">', unsafe_allow_html=True)
        st.subheader("货币政策")

        # 货币政策的两个滑块控件
        monetary_col1, monetary_col2 = st.columns(2)
        with monetary_col1:
            monetary_policy_1_time = st.slider("利率调节实施时间点", 0, simulation_steps, 110)
            monetary_policy_2_time = st.slider("货币供应量实施时间点", 0, simulation_steps, 60)
        with monetary_col2:
            monetary_policy_1 = st.slider("利率调节力度", -5.0, 5.0, 2.0, 0.25)
            monetary_policy_2 = st.slider("货币供应量调节力度", -10.0, 10.0, -1.5, 0.5)

        st.markdown('</div>', unsafe_allow_html=True)

    # 选项卡设置
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["经济指标", "市场均衡", "高级分析", "政策效果", "危机模拟"])

    with tab1:
        st.subheader("经济指标变化")
        # 为每个指标创建空的图表容器
        plot_containers = {
            column: st.empty() for column in ['labor time', 'K', 'N', 'population size', 'p_fd', 'w', 'bop']
        }

        # 动态更新图表，步长随时间递增
        for i in range(0, len(df_equilibrium), max(20, int( animation_speed/5))):
            current_data = df.iloc[:i + 1]
            for column in plot_containers:
                fig = px.line(current_data, y=column, title=f'{column}随时间的变化')
                fig.update_layout(
                    xaxis_title="时间",
                    yaxis_title=column,
                    hovermode='x unified'
                )
                plot_containers[column].plotly_chart(fig, use_container_width=True)

            time.sleep(0.02 / (animation_speed * (1 + i / len(df))))

    with tab2:
        st.subheader("市场均衡分析")
        goods_market_container = st.empty()
        labor_market_container = st.empty()

        # 动态更新均衡图表
        step_size = 1
        for i in range(0, len(df_equilibrium), max(20, int( animation_speed/5))):
            current_equilibrium = df_equilibrium.iloc[:i + 1]

            # 商品市场均衡
            fig_goods = go.Figure()
            fig_goods.add_trace(go.Scatter(y=current_equilibrium['g_m.goods_supply'], name='供给'))
            fig_goods.add_trace(go.Scatter(y=current_equilibrium['g_m.goods_demand'], name='需求'))
            fig_goods.update_layout(title='商品市场均衡', xaxis_title='时间', yaxis_title='数量')
            goods_market_container.plotly_chart(fig_goods, use_container_width=True)

            # 劳动力市场均衡
            fig_labor = go.Figure()
            fig_labor.add_trace(go.Scatter(y=current_equilibrium['l_m.labor_supply'], name='供给'))
            fig_labor.add_trace(go.Scatter(y=current_equilibrium['l_m.labor_demand'], name='需求'))
            fig_labor.update_layout(title='劳动力市场均衡', xaxis_title='时间', yaxis_title='数量')
            labor_market_container.plotly_chart(fig_labor, use_container_width=True)

            time.sleep(0.02 / (animation_speed * (1 + i / len(df_equilibrium))))

    with tab3:
        st.subheader("高级经济分析")
        fig_heatmap, fig_gaps, fig_cycle = create_advanced_visualizations(df, df_equilibrium)
        st.plotly_chart(fig_heatmap, use_container_width=True)
        st.plotly_chart(fig_gaps, use_container_width=True)
        st.plotly_chart(fig_cycle, use_container_width=True)

    # 在tab4中修改图表部分，使用正确的数据列名
    with tab4:
        st.subheader("💡 政策效果分析")

        col3, col4 = st.columns(2)
        with col3:
            fiscal_effects_fig = go.Figure()
            fiscal_effects_fig.add_trace(go.Scatter(
                x=df.index,
                # 使用实际存在的列名
                y=df_equilibrium['g_m.goods_supply'] * (1 + fiscal_policy_1 / 100),
                name='政府支出效果'
            ))
            fiscal_effects_fig.add_trace(go.Scatter(
                x=df.index,
                y=df_equilibrium['g_m.goods_supply'] * (1 - fiscal_policy_2 / 100),
                name='税收政策效果'
            ))
            fiscal_effects_fig.update_layout(
                title='财政政策实施效果',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white')
            )
            st.plotly_chart(fiscal_effects_fig)

        with col4:
            monetary_effects_fig = go.Figure()
            monetary_effects_fig.add_trace(go.Scatter(
                x=df.index,
                y=df['w'] * (1 + monetary_policy_1 / 100),  # 使用工资率作为货币政策效果指标
                name='利率调节效果'
            ))
            monetary_effects_fig.add_trace(go.Scatter(
                x=df.index,
                y=df['p_fd'] * (1 + monetary_policy_2 / 100),  # 使用价格水平作为货币供应量效果指标
                name='货币供应量效果'
            ))
            monetary_effects_fig.update_layout(
                title='货币政策实施效果',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white')
            )
            st.plotly_chart(monetary_effects_fig)

    # 新增的危机模拟标签页内容
    with tab5:
        st.subheader("🌋 经济危机模拟")

        # 危机类型选择
        crisis_types = st.multiselect(
            "选择要模拟的危机类型",
            ["金融危机", "通货膨胀", "贸易战", "自然灾害"],
            help="可以同时选择多个危机类型观察叠加效果"
        )

        # 危机强度设置
        if crisis_types:
            crisis_intensity = {crisis: st.slider(
                f"{crisis}强度", 0.0, 10.0, 5.0, 0.5,
                key=f"crisis_{crisis}"
            ) for crisis in crisis_types}

            # 创建危机效果图表
            crisis_fig = go.Figure()
            for crisis in crisis_types:
                crisis_fig.add_trace(go.Scatter(
                    x=df.index,
                    y=df['GDP'] * (1 - crisis_intensity[crisis] / 100),
                    name=f'{crisis}影响'
                ))
            crisis_fig.update_layout(title='危机影响模拟')
            st.plotly_chart(crisis_fig)

