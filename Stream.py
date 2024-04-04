
import streamlit as st
import altair as alt
import plotly.express as px
import os 
import plotly as py
import plotly.graph_objs as go
import pandas as pd
import numpy as np
import math 
import re

def filter_out_of_bounds(player):
    player = player[player['Pitch_x'] >= -52.5]
    player = player[player['Pitch_x'] <= 52.5]
    player = player[player['Pitch_y'] >= -34]
    player = player[player['Pitch_y'] <= 34]
    return player

def Assign_Sprints(player):
    player_temp = player
    current_sprint = [1] * len(player)
    index = 1
    
    for i in range(1, len(player_temp)):
        if player_temp.iloc[i]['Time (s)'] - player_temp.iloc[i-1]['Time (s)'] >= 0.2:
            index += 1
        current_sprint[i] = index
        
        
    player_temp['Sprint'] = current_sprint
    player_temp['Sprint'] = player_temp['Sprint'].astype('object')
        
    return player_temp

def extract_sprint_data(player, N):
    sprints_desired = player['Sprint'].value_counts()[lambda x: x >= N]
    return(player[player['Sprint'].isin(sprints_desired.index)])


def Total_Distance_LeaderBoard(player):
    run = extract_sprint_data(player_data[player], 600)
    dist = 0
    for sprint in run['Sprint'].unique():
        sprint_data = run[run['Sprint'] == sprint]
        for i in range(len(sprint_data)-1):
            dist += math.sqrt((sprint_data.iloc[i+1]["Pitch_x"] - sprint_data.iloc[i]["Pitch_x"])**2 + (sprint_data.iloc[i+1]["Pitch_y"] - sprint_data.iloc[i]["Pitch_y"])**2)
    
    return dist
    
def zone5_count(player):
    run = extract_sprint_data(player_data[player], 10)
    dist_zone5 = 0.0
    for sprint in run['Sprint'].unique():
        sprint_data = run[run['Sprint'] == sprint]
        for i in range(len(sprint_data)-1):
            dist_ms = math.sqrt((sprint_data.iloc[i+1]["Pitch_x"] - sprint_data.iloc[i]["Pitch_x"])**2 + (sprint_data.iloc[i+1]["Pitch_y"] - sprint_data.iloc[i]["Pitch_y"])**2)*10 
            if(dist_ms>= 19.8/3.6 and dist_ms <= 25.1/3.6):
              dist_zone5 += dist_ms
              
    return dist_zone5

def Euclidean_Dist(seg):
    dist = 0
    for i in range(len(seg)-1):
        dist += math.sqrt((seg.iloc[i+1]["Pitch_x"] - seg.iloc[i]["Pitch_x"])**2 + (seg.iloc[i+1]["Pitch_y"] - seg.iloc[i]["Pitch_y"])**2)
        return dist

                   
def Top_Speed_Leaderboard(player):
    run = extract_sprint_data(player_data[player], 600)
    
    speeds = []
    for sprint in run['Sprint'].unique():
        sprint_data = run[run['Sprint'] == sprint]
        for i in range(len(sprint_data)-10):
            speeds.append(Euclidean_Dist(sprint_data.iloc[i:i+10]))
            #     speeds.append(math.sqrt((sprint_data.iloc[j]["Pitch_x"] - sprint_data.iloc[j+1]["Pitch_x"])**2 + (sprint_data.iloc[j]["Pitch_y"] - sprint_data.iloc[j+1]["Pitch_y"])**2))
                
    
    return speeds

def aggregate_data(player, units):
    if(units == 'seconds'):
        player_agg = player[::10]
        max_speed = player['Speed (m/s)'].rolling(window=10, min_periods=1).max()
        player_agg['Max Speed'] = max_speed[::10]
        return player_agg
    
 
def Assign_SetPiece(ball):
    
    current_set_piece = [1] * len(ball)
    index = 1
    for i in range(1, len(ball)):
        if ball.iloc[i]['Time (s)'] - ball.iloc[i-1]['Time (s)'] >= 2:
            index += 1
        current_set_piece[i] = index
        
        
    ball['SetPiece_Id'] = current_set_piece
    ball['SetPiece_Id'] = ball['SetPiece_Id'].astype('object')
        
    return ball






os.chdir("C:\\Users\\abhin\\OneDrive\\Documents\\Technical Task")
data = pd.read_csv("match_data.csv")
data['Time (s)'] = round(data['Time (s)'], 1)

unique_vals = data['participation_id'].unique()
id_list = [id for id in unique_vals if not bool(re.search("ball", id))]

# print("Number of Players represented is: " + str(len(id_list)))

players_list = ["Player" + str(i + 1) for i, id in enumerate(id_list)]

player_id_dict = dict(zip(id_list, players_list))

data['player_id'] =  data['participation_id'].map(player_id_dict)


player_data = {}

for player in players_list:
    player_data[str(player)] = data[data['player_id'] == player]
    


ball_data = data[data['participation_id'].str.contains('ball')]


max_speed_leaderboard = pd.read_csv("max_speed_leaderboard.csv").to_dict()

time_leaderboard = pd.read_csv("time_leaderboard.csv").to_dict()

distance_leaderboard = pd.read_csv("distance_leaderboard.csv").to_dict()

distance_zone5_leaderboard = pd.read_csv("distance_zone5_leaderboard.csv").to_dict()



time_l_plot = px.bar(x = list(time_leaderboard.keys()), y = list(time_leaderboard.values()), labels = {'x': 'Player', 'y': 'Time (s)'}, title = 'Time Leaderboard')

dist_l_plot = px.bar(x = list(distance_leaderboard.keys()), y = list(distance_leaderboard.values()), labels = {'x': 'Player', 'y': 'Distance (m)'}, title = 'Total Distance Leaderboard')

dist_5_lplot = px.bar(x = list(distance_zone5_leaderboard.keys()), y = list(distance_zone5_leaderboard.values()), labels = {'x': 'Player', 'y': 'Distance (m)'}, title = 'Distance in Zone 5 Leaderboard')

max_speed_plot = px.bar(x = list(max_speed_leaderboard.keys()), y = list(max_speed_leaderboard.values()), labels = {'x': 'Player', 'y': 'Speed (m/s)'}, title = 'Max Speed Leaderboard')



st.plotly_chart(time_l_plot)

st.plotly_chart(dist_l_plot)

st.plotly_chart(dist_5_lplot)

st.plotly_chart(max_speed_plot)

# st.plotly_chart(fig_ball)

# st.plotly_chart(fig_setpieces)

ball_agg = aggregate_data(ball_data, 'seconds')
ball_agg_within = filter_out_of_bounds(ball_agg)

ball_agg['Within_Pitch'] = ball_agg.index.isin(ball_agg_within.index)



fig_ball = px.scatter(ball_agg, x="Pitch_x", y="Pitch_y", animation_frame="Time (s)", range_x=[-60, 60], range_y=[-40, 40], color= "Within_Pitch", title="Ball Movement")

fig_ball .add_shape(type="line", x0=-52.5, y0=-34, x1=-52.5, y1=34, line=dict(color="black", width=1))  # Left boundary
fig_ball .add_shape(type="line", x0=52.5, y0=-34, x1=52.5, y1=34, line=dict(color="black", width=1))    # Right boundary
fig_ball .add_shape(type="line", x0=-52.5, y0=-34, x1=52.5, y1=-34, line=dict(color="black", width=1))  # Bottom boundary
fig_ball .add_shape(type="line", x0=-52.5, y0=34, x1=52.5, y1=34, line=dict(color="black", width=1))    # Top boundary
fig_ball .update_layout(showlegend=True)
fig_ball .add_shape(type="circle", x0=-0.5, y0=-0.5, x1=0.5, y1=0.5, line=dict(color="red"), fillcolor="rgba(255, 0, 0, 0.1)")
# fig.show()



set_pieces = ball_agg[(ball_agg['Speed (m/s)'] < 0.1) & (ball_agg['Within_Pitch'] == True)]
set_pieces = Assign_SetPiece(set_pieces)

fig_setpiece = px.scatter(set_pieces, x="Pitch_x", y="Pitch_y", animation_frame="Time (s)", 
                 range_x=[-60, 60], range_y=[-40, 40], color="SetPiece_Id", labels = {"SetPiece_Id": "Set Piece ID"},
                 title="Ball Movement")

fig_setpiece.add_shape(type="line", x0=-52.5, y0=-34, x1=-52.5, y1=34, line=dict(color="black", width=1))  
fig_setpiece.add_shape(type="line", x0=52.5, y0=-34, x1=52.5, y1=34, line=dict(color="black", width=1))    
fig_setpiece.add_shape(type="line", x0=-52.5, y0=-34, x1=52.5, y1=-34, line=dict(color="black", width=1)) 
fig_setpiece.add_shape(type="line", x0=-52.5, y0=34, x1=52.5, y1=34, line=dict(color="black", width=1))    


fig_setpiece.add_shape(type="circle", x0=-0.5, y0=-0.5, x1=0.5, y1=0.5, line=dict(color="red"), fillcolor="rgba(255, 0, 0, 0.1)")


# StreamLit Config: 


player_selected = st.sidebar.multiselect("Select Player to display:", players_list)

if(player_selected):
    df_filtered = player_data[player_selected]
else:
    df_filtered = player_data.copy()




st.plotly_chart(time_l_plot)

st.plotly_chart(dist_5_lplot)

st.plotly_chart(max_speed_plot)

st.plotly_chart(fig_ball)

st.plotly_chart(fig_setpiece)

