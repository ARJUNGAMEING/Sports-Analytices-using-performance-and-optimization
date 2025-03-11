import streamlit as st
from streamlit_option_menu import option_menu
from database import fetch_user
from pyowm import OWM
import time
import pyowm
import requests
from bs4 import BeautifulSoup
import pandas as pd
import pandas as pd
import pickle
import csv
import altair as alt
import re
from googleapiclient.discovery import build
# api key
api_key = 'AIzaSyBhLe5p8LPhBL35V-RJci5DRq2QhwgsUIg'
def video_comments(video_id):
    # Create CSV file for storing comments and attributes
    with open('video_comments.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Author', 'Comment', 'Likes', 'Timestamp']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Write header row to CSV file
        writer.writeheader()

        # creating youtube resource object
        youtube = build('youtube', 'v3', developerKey=api_key)

        # retrieve youtube video results
        video_response = youtube.commentThreads().list(
            part='snippet,replies',
            videoId=video_id
        ).execute()

        # iterate video response
        while video_response:
            # extracting required info from each result object
            for item in video_response['items']:
                # Extracting comments
                comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
                # Counting number of likes for the comment
                likes = item['snippet']['topLevelComment']['snippet']['likeCount']
                # Timestamp of the comment
                timestamp = item['snippet']['topLevelComment']['snippet']['publishedAt']
                # Author name
                author = item['snippet']['topLevelComment']['snippet']['authorDisplayName']

                # Write data to CSV file
                writer.writerow({'Author': author, 'Comment': comment, 'Likes': likes, 'Timestamp': timestamp})

                # Empty reply list
                replies = []

            # Again repeat
            if 'nextPageToken' in video_response:
                video_response = youtube.commentThreads().list(
                    part='snippet,replies',
                    videoId=video_id,
                    pageToken=video_response['nextPageToken']
                ).execute()
            else:
                break
def navigate_to_page(page_name):
    st.session_state["current_page"] = page_name
    st.experimental_rerun()
all_cities = ['Hyderabad', 'Bangalore', 'Mumbai', 'Indore', 'Kolkata', 'Delhi',
                    'Chandigarh', 'Jaipur', 'Chennai', 'Cape Town', 'Port Elizabeth',
                    'Durban', 'Centurion', 'East London', 'Johannesburg', 'Kimberley',
                    'Bloemfontein', 'Ahmedabad', 'Cuttack', 'Nagpur', 'Dharamsala',
                    'Visakhapatnam', 'Pune', 'Raipur', 'Ranchi', 'Abu Dhabi',
                    'Sharjah', 'Mohali', 'Bengaluru']
all_teams = sorted(['Sunrisers Hyderabad',
                'Mumbai Indians',
                'Royal Challengers Bangalore',
                'Kolkata Knight Riders',
                'Kings XI Punjab',
                'Chennai Super Kings',
                'Rajasthan Royals',
                'Delhi Capitals'])         
def user_home_page():
    user = fetch_user(st.session_state["current_user"])
    with st.sidebar:
        st.markdown(f"<h1 style='text-align: center;'>𝐖𝐄𝐋𝐂𝐎𝐌𝐄 👋 {user[1]}</h1>", unsafe_allow_html=True)
        st.image('https://png.pngtree.com/png-clipart/20240901/original/pngtree-cricket-player-at-bat-in-round-circle-vector-png-image_15901661.png', use_column_width=True)
        select = option_menu(
            "",
            ['Home',"Recent Matches",'Winning Prediction', 'Player Performance',"Sentiment Analysis","Weather Forecasting","Logout"],
            icons=['house-door','calendar-day','gift','graph-up','chat-left-heart','cloud-sun','shield-lock'],
            menu_icon="cast",
            default_index=0,
            orientation="vertical",
            styles={
                "container": {"padding": "0", "background-color": "#d8ed93"}, 
                "icon": {"color": "black", "font-size": "20px"},    
                "nav-link": {
                    "font-size": "16px",
                    "margin": "0px",
                    "color": "black",                                          
                },   
                "nav-link-selected": {
                    "background-color": "#6b8a07", 
                    "color": "white",                           
                },
            },
        )
    if select == 'Home':
        st.markdown(
        """
        <style>
        /* Apply background image to the main content area */
        .main {
            background-image: url('https://files.oaiusercontent.com/file-2Co5v3RU5JPDGH9UnLe1Hi?se=2025-03-07T07%3A31%3A12Z&sp=r&sv=2024-08-04&sr=b&rscc=max-age%3D604800%2C%20immutable%2C%20private&rscd=attachment%3B%20filename%3D6746a396-e350-4e21-8b8c-30c65166f677.webp&sig=hDWWv7nTjGthLdpoJ3irgsH0DnPTSdNdk5AoDaEnYzk%3D');
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }
        </style>
        """,
        unsafe_allow_html=True
        )
        video_url = "https://www.youtube.com/embed/3yiWqnKl7lQ?autoplay=1"
        st.markdown(f'<iframe width="800" height="500" src="{video_url}" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>', unsafe_allow_html=True)
    elif select == 'Recent Matches':
        st.title("Recent Cricket Matches")
        # Apply background styling

        # Fetch recent matches data
        url = "http://static.cricinfo.com/rss/livescores.xml"
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "lxml")

        # Initialize match data lists
        playing_matches = []  # Matches with scores
        future_matches = []   # Matches without scores

        # Parse match details
        for item in soup.findAll("item"):
            description = item.find("description").text.strip()
            teams_score = description.split(" v ")

            if len(teams_score) == 2:
                team1 = teams_score[0].strip()
                team2 = teams_score[1].strip()
            else:
                continue  # Skip invalid entries

            def extract_scores(team):
                """ Extract all score components from a team's description. """
                parts = team.split(" ")
                scores = [part for part in parts if "/" in part or part.isdigit()]
                return " & ".join(scores) if scores else None  # Return None for future matches

            team1_parts = team1.rsplit(" ", 1)  # Split into name and score
            team2_parts = team2.rsplit(" ", 1) if " " in team2 else [team2, None]

            team1_name = team1_parts[0]
            team1_score = extract_scores(team1)

            team2_name = team2_parts[0]
            team2_score = extract_scores(team2)

            if team1_score and team2_score:  # If both teams have scores, it's a playing match
                playing_matches.append([team1_name, team1_score, team2_name, team2_score])
            else:  # Otherwise, it's a future match
                future_matches.append([team1_name, team2_name])

        # Display matches in two columns
        col1, col2 = st.columns(2)

        # Column 1: Ongoing Matches (with scores)
        with col1:
            st.subheader("🏏 Completed Matches")
            if playing_matches:
                for match in playing_matches:
                    st.markdown(f"""
                        <div style="border: 2px solid #008000; padding: 10px; border-radius: 10px; background-image: url('https://www.shutterstock.com/image-illustration/generic-seated-cricket-stadium-showing-600nw-2477634413.jpg'); background-size: cover; background-position: center; background-repeat: no-repeat; background-color: rgba(255, 255, 255, 0.5); background-blend-mode: overlay;">
                            <h4>{match[0]} ({match[1]})</h4>
                            <h5>vs</h5>
                            <h4>{match[2]} ({match[3]})</h4>
                        </div>
                        <br>
                    """, unsafe_allow_html=True)
            else:
                st.write("No live matches currently.")

        # Column 2: Future Matches (without scores)
        with col2:
            st.subheader("📅 Ongoing Matches")
            if future_matches:
                for match in future_matches:
                    st.markdown(f"""
                        <div style="border: 2px solid #ffa500; padding: 10px; border-radius: 10px; background-image: url('https://img.freepik.com/premium-photo/image-cricketer-batting-match-plain-white-background-poster-promoting-cricket-tournament_117038-44632.jpg?w=360'); background-size: cover; background-position: center; background-repeat: no-repeat; background-color: rgba(255, 255, 255, 0.7); background-blend-mode: overlay;">
                            <h4>{match[0]}</h4>
                            <h5>vs</h5>
                            <h4>{match[1]}</h4>
                        </div>
                        <br>
                    """, unsafe_allow_html=True)
            else:
                st.write("No upcoming matches.")
    elif select == 'Winning Prediction':
        match=option_menu(
            "",
            ['IPL','T20'],
            menu_icon="cast",
            default_index=0,
            orientation="horizontal",
            styles={
                "container": {"padding": "0", "background-color": "#d8ed93"}, 
                "icon": {"color": "black", "font-size": "20px"},    
                "nav-link": {
                    "font-size": "16px",
                    "margin": "0px",
                    "color": "black",
                    "background-color": "#f5f073",                                          
                },   
                "nav-link-selected": {
                    "background-color": "#ab7e03", 
                    "color": "white",                           
                },
            },
        )
        if match == 'IPL':
            with st.form(key='my_form'):
                st.markdown(
                """
                <style>
                /* Apply background image to the main content area */
                .main {
                    background-image: url("https://img.freepik.com/premium-photo/icc-world-cup-cricket-stadium-background-vector-wallpaper-design-illustration-social-media_1309136-6669.jpg?ga=GA1.1.804213449.1741408783&semt=ais_hybrid.jpg");
                    background-size: cover;
                    background-position: center;
                    background-repeat: no-repeat;
                }
                </style>
                """,
                unsafe_allow_html=True
                )
                st.markdown(f"<h1 style='text-align: center; color:maroon;'>IPL Winning Prediction</h1>", unsafe_allow_html=True)
                pipe = pickle.load(open('pipe.pkl','rb'))
                teams = sorted(['Sunrisers Hyderabad',
                'Mumbai Indians',
                'Royal Challengers Bangalore',
                'Kolkata Knight Riders',
                'Kings XI Punjab',
                'Chennai Super Kings',
                'Rajasthan Royals',
                'Delhi Capitals'])

                col1,col2 = st.columns(2)

                with col1:
                    batting_team =st.selectbox('Select the batting team',teams)
                with col2:
                    bowling_team = st.selectbox('Select the bowling team',teams)
                col1,col2 = st.columns(2)
                cities = ['Hyderabad', 'Bangalore', 'Mumbai', 'Indore', 'Kolkata', 'Delhi',
                    'Chandigarh', 'Jaipur', 'Chennai', 'Cape Town', 'Port Elizabeth',
                    'Durban', 'Centurion', 'East London', 'Johannesburg', 'Kimberley',
                    'Bloemfontein', 'Ahmedabad', 'Cuttack', 'Nagpur', 'Dharamsala',
                    'Visakhapatnam', 'Pune', 'Raipur', 'Ranchi', 'Abu Dhabi',
                    'Sharjah', 'Mohali', 'Bengaluru']

                selected_city = col1.selectbox('Match Venue',cities)

                target = col2.number_input('Target to chase',min_value=0,value=180)

                col3,col4,col5 = st.columns(3)
                with col3 :
                    score =st.number_input('Present Score',min_value=0,value=90)
                with col4 :
                    wickets =st.number_input('Wickets fallen',min_value=0,max_value=9,value=0)
                with col5 :
                    overs = st.number_input('Overs bowled',min_value=0,max_value=20,value=1)
                try:
                    col1,col2,col3=st.columns([2,3,1])
                    if col2.form_submit_button('Predict Probability',type='primary'):
                        runs_left = target-score
                        balls_left = 120 - overs*6
                        wickets = 10-wickets
                        crr = score/overs
                        rrr = runs_left*6/balls_left
                        df =pd.DataFrame({'batting_team':[batting_team],'bowling_team':[bowling_team],'city':[selected_city],'runs_left':[runs_left],'balls_left':[balls_left],'wickets':[wickets],'total_runs_x':[target],'crr':[crr],'rrr':[rrr]})    
                        result = pipe.predict_proba(df)
                        r_2 = result[0][0]*100
                        r_1 = result[0][1]*100
                        if batting_team == bowling_team:
                            st.markdown(f"<h2 style='text-align: center; color:red;'>Both teams are same</h2>", unsafe_allow_html=True)
                        elif target == 0:
                            st.markdown(f"<h2 style='text-align: center; color:red;'>Target should be greater than 0</h2>", unsafe_allow_html=True)
                        elif target<=score:
                            #ALREADY WON
                            st.markdown(f"<h2 style='text-align: center; color:green;'>{batting_team} has already won</h2>", unsafe_allow_html=True)
                        elif balls_left<=0:
                            #ALREADY WON
                            st.markdown(f"<h2 style='text-align: center; color:green;'>{batting_team} has already won</h2>", unsafe_allow_html=True)
                        elif wickets<=0:
                            #ALREADY WON
                            st.markdown(f"<h2 style='text-align: center; color:green;'>{batting_team} has already won</h2>", unsafe_allow_html=True)
                        elif r_1>r_2:
                            st.markdown(f"<h2 style='text-align: center; color:green;'>{batting_team} has {r_1:.2f}% chances of winning</h2>", unsafe_allow_html=True)
                            st.markdown(f"<h2 style='text-align: center; color:red;'>{bowling_team} has {r_2:.2f}% chances of winning</hhtml>", unsafe_allow_html=True)
                        elif r_1<r_2:
                            st.markdown(f"<h2 style='text-align: center; color:green;'>{batting_team} has {r_1:.2f}% chances of winning</h2>", unsafe_allow_html=True)
                            st.markdown(f"<h2 style='text-align: center; color:red;'>{bowling_team} has {r_2:.2f}% chances of winning</hhtml>", unsafe_allow_html=True)
                        else:
                            pass
                except Exception as e:
                    st.error('Please fill all the details')
        else:
            with st.form(key='my_form'):
                st.markdown(
                """
                <style>
                /* Apply background image to the main content area */
                .main {
                    background-image: url("https://thefederal.com/file/2022/10/t20-world-cup-captains-selfie.webp");
                    background-size: cover;
                    background-position: center;
                    background-repeat: no-repeat;
                }
                </style>
                """,
                unsafe_allow_html=True
                )
                st.markdown(f"<h1 style='text-align: center; color:maroon;'>T20 Winning Prediction</h1>", unsafe_allow_html=True)
                pipe = pickle.load(open('pipe.pkl','rb'))
                teams = sorted(["India", "Australia", "England", "Pakistan", "South Africa", "New Zealand", "West Indies", "Sri Lanka", "Bangladesh", "Afghanistan", "Netherlands", "Ireland", "Zimbabwe", "Scotland", "UAE", "Oman", "Nepal", "USA", "Papua New Guinea", "Namibia"])

                col1,col2 = st.columns(2)

                with col1:
                    batting_team =st.selectbox('Select the batting team',teams)
                with col2:
                    bowling_team = st.selectbox('Select the bowling team',teams)
                col1,col2 = st.columns(2)
                cities = ["Melbourne Cricket Ground", "Sydney Cricket Ground", "Adelaide Oval", "The Gabba", "Perth Stadium", "Wankhede Stadium", "Eden Gardens", "Arun Jaitley Stadium", "M. Chinnaswamy Stadium", "MA Chidambaram Stadium", "Narendra Modi Stadium", "Gaddafi Stadium", "National Stadium Karachi", "Sharjah Cricket Stadium", "Dubai International Cricket Stadium", "Sheikh Zayed Stadium", "Kensington Oval", "Queen's Park Oval", "SuperSport Park", "Newlands", "Wanderers Stadium", "Hagley Oval", "Bay Oval", "Basin Reserve", "Edgbaston", "Old Trafford", "Lord’s", "The Oval", "Trent Bridge", "Headingley", "Sophia Gardens"]

                selected_city = col1.selectbox('Match Venue',cities)

                target = col2.number_input('Target to chase',min_value=0,value=180)

                col3,col4,col5 = st.columns(3)
                with col3 :
                    score =st.number_input('Present Score',min_value=0,value=90)
                with col4 :
                    wickets =st.number_input('Wickets fallen',min_value=0,max_value=9,value=0)
                with col5 :
                    overs = st.number_input('Overs bowled',min_value=0,max_value=20,value=1)
                try:
                    col1,col2,col3=st.columns([2,3,1])
                    if col2.form_submit_button('Predict Probability',type='primary'):
                        runs_left = target-score
                        balls_left = 120 - overs*6
                        wickets = 10-wickets
                        crr = score/overs
                        rrr = runs_left*6/balls_left
                        #select random teamsn and city from cities and teams
                        import random
                        batting = random.choice(all_teams)
                        bowling_ = random.choice(all_teams)
                        selected = random.choice(all_cities)
                        df =pd.DataFrame({'batting_team':[batting],'bowling_team':[bowling_],'city':[selected],'runs_left':[runs_left],'balls_left':[balls_left],'wickets':[wickets],'total_runs_x':[target],'crr':[crr],'rrr':[rrr]})    
                        result = pipe.predict_proba(df)
                        r_2 = result[0][0]*100
                        r_1 = result[0][1]*100
                        if batting_team == bowling_team:
                            st.markdown(f"<h2 style='text-align: center; color:red;'>Both teams are same</h2>", unsafe_allow_html=True)
                        elif target == 0:
                            st.markdown(f"<h2 style='text-align: center; color:red;'>Target should be greater than 0</h2>", unsafe_allow_html=True)
                        elif target<=score:
                            #ALREADY WON
                            st.markdown(f"<h2 style='text-align: center; color:green;'>{batting_team} has already won</h2>", unsafe_allow_html=True)
                        elif balls_left<=0:
                            #ALREADY WON
                            st.markdown(f"<h2 style='text-align: center; color:green;'>{batting_team} has already won</h2>", unsafe_allow_html=True)
                        elif wickets<=0:
                            #ALREADY WON
                            st.markdown(f"<h2 style='text-align: center; color:green;'>{batting_team} has already won</h2>", unsafe_allow_html=True)
                        elif r_1>r_2:
                            st.markdown(f"<h2 style='text-align: center; color:green;'>{batting_team} has {r_1:.2f}% chances of winning</h2>", unsafe_allow_html=True)
                            st.markdown(f"<h2 style='text-align: center; color:red;'>{bowling_team} has {r_2:.2f}% chances of winning</hhtml>", unsafe_allow_html=True)
                        elif r_1<r_2:
                            st.markdown(f"<h2 style='text-align: center; color:green;'>{batting_team} has {r_1:.2f}% chances of winning</h2>", unsafe_allow_html=True)
                            st.markdown(f"<h2 style='text-align: center; color:red;'>{bowling_team} has {r_2:.2f}% chances of winning</hhtml>", unsafe_allow_html=True)
                        else:
                            pass
                except Exception as e:
                    st.error('Please fill all the details')
                
    elif select == 'Player Performance':
        st.markdown(
        """
        <style>
        /* Apply background image to the main content area */
        .main {
            background-image: url("https://files.oaiusercontent.com/file-Td8Gq2HBFNKEuUkuweispH?se=2025-03-07T07%3A23%3A36Z&sp=r&sv=2024-08-04&sr=b&rscc=max-age%3D604800%2C%20immutable%2C%20private&rscd=attachment%3B%20filename%3D8a988676-7dc2-4cf7-9c8f-86453444ec0f.webp&sig=3hLtjS6SlS72sBDNpJLotMLRTiTkx3HVuZc%2BjvwQCJg%3D");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }
        </style>
        """,
        unsafe_allow_html=True
        )
    elif select == 'Sentiment Analysis':
        st.markdown(
        """
        <style>
        /* Apply background image to the main content area */
        .main {
            background-image: url("https://i.pinimg.com/736x/85/f6/67/85f667a6929c54b75dad12a334796b99.jpg");
            background-size: cover;
            background-position: center;
        }
        </style>
        """,
        unsafe_allow_html=True
        )
        st.markdown(f"<h1 style='text-align: center; color:green;'>Sentiment Analysis</h1>", unsafe_allow_html=True)
        url=st.text_input('Enter the URL of the video',value='https://www.youtube.com/watch?v=f8wteRu5eac')
        try:
            col1,col2,col3=st.columns([2.5,3,1])
            if col2.button('Submit',type='primary'):
                video_id = url.split('=')[1]
                video_comments(video_id)
                df=pd.read_csv('video_comments.csv')
                data = []
                with open('video_comments.csv', 'r', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile)
                    for row in reader:
                        # Check if 'Likes', 'Timestamp', and 'Author' are not null
                        if row['Likes'] and row['Timestamp'] and row['Author']:
                            data.append(row)

                # Remove duplicates based on 'Author', 'Comment', and 'Timestamp'
                unique_data = [dict(tupleized) for tupleized in set(tuple(item.items()) for item in data)]

                # Save the cleaned data to a new CSV file
                fieldnames = ['Author', 'Comment', 'Likes', 'Timestamp']
                with open('cleaned_video_comments.csv', 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(unique_data)
                data = pd.read_csv("cleaned_video_comments.csv")
                cleaned_data = []
                with open('cleaned_video_comments.csv', 'r', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile)
                    for row in reader:
                        cleaned_data.append(row['Comment'])

                # Remove links from each comment
                cleaned_data_no_links = []

                for comment in cleaned_data:
                    cleaned_comment = re.sub(r'http\S+', '', comment)  # Remove URLs
                    cleaned_data_no_links.append(cleaned_comment)
                import emoji
                import string
                # Remove emojis from each comment in the list
                cleaned_data_no_emojis = []

                for comment in cleaned_data_no_links:
                    cleaned_comment = emoji.demojize(comment)
                    cleaned_data_no_emojis.append(cleaned_comment)
                combined_text = ' '.join(cleaned_data_no_emojis + cleaned_data_no_emojis)
                from textblob import TextBlob
                import matplotlib.pyplot as plt
                df = pd.read_csv('cleaned_video_comments.csv')
                def get_sentiment(comment):
                    analysis = TextBlob(comment)
                    # Sentiment polarity lies in the range of [-1,1]
                    if analysis.sentiment.polarity > 0:
                        return 'Positive'
                    elif analysis.sentiment.polarity == 0:
                        return 'Neutral'
                    else:
                        return 'Negative'
                df['Sentiment'] = df['Comment'].apply(get_sentiment)
                df[['Comment', 'Sentiment']].to_csv('comments_with_sentiments.csv', index=False)
                sentiment_counts = df['Sentiment'].value_counts(normalize=True) * 100
                positive_comments = df[df['Sentiment'] == 'Positive']['Comment'].tolist()
                negative_comments = df[df['Sentiment'] == 'Negative']['Comment'].tolist()
                neutral_comments = df[df['Sentiment'] == 'Neutral']['Comment'].tolist()
                #disaply the dataset by adding the sentiment column and based on the seentine the comments are displayed are sorted and 
                #sentinments is posstive dissplay the comments with green color and if the sentiment is negative display the comments with red color in the dataframe only
                #add the sentiment column to the dataframe
                df['Sentiment'] = df['Comment'].apply(get_sentiment)
                #display the dataset only Comments and Sentiments
                st.write(df[['Comment','Sentiment','Likes','Author','Timestamp']])
                #show plots
                col1,col2=st.columns(2)
                with col1:
                    chart = alt.Chart(df).mark_bar().encode(
                        x='Sentiment',
                        y='count()',
                        color='Sentiment'
                    ).properties(
                        title='Sentiment Analysis'
                    )
                    st.altair_chart(chart, use_container_width=True)
                with col2:
                    # Convert categorical sentiment to numeric for better variance visualization
                    sentiment_mapping = {"Negative": -1, "Neutral": 0, "Positive": 1}
                    df["Sentiment_Score"] = df["Sentiment"].map(sentiment_mapping)

                    # Create the Altair line chart
                    chart = alt.Chart(df).mark_line(point=True).encode(
                        x=alt.X("Likes:Q", title="Number of Likes"),
                        y=alt.Y("Sentiment_Score:Q", title="Sentiment Score (-1: Negative, 0: Neutral, 1: Positive)"),
                        color=alt.Color("Sentiment:N", scale=alt.Scale(domain=["Positive", "Neutral", "Negative"],
                                                                    range=["green", "blue", "red"])),
                        tooltip=["Likes", "Sentiment"]
                    ).properties(
                        title="Variance of Sentiment Based on Likes"
                    )

                    # Display the chart in Streamlit
                    st.altair_chart(chart, use_container_width=True)

                col1,col2=st.columns(2)
                with col1:
                    df['Year'] = df['Timestamp'].apply(lambda x: x[:4])
                    # Calculate percentage of each sentiment for each year
                    sentiment_counts_per_year = df.groupby(['Year', 'Sentiment']).size().unstack().fillna(0)
                    sentiment_counts_per_year['Total'] = sentiment_counts_per_year.sum(axis=1)
                    sentiment_counts_per_year['Positive (%)'] = sentiment_counts_per_year['Positive'] / sentiment_counts_per_year['Total'] * 100
                    sentiment_counts_per_year['Negative (%)'] = sentiment_counts_per_year['Negative'] / sentiment_counts_per_year['Total'] * 100
                    sentiment_counts_per_year['Neutral (%)'] = sentiment_counts_per_year['Neutral'] / sentiment_counts_per_year['Total'] * 100
                    sentiment_counts_per_year[['Positive (%)', 'Negative (%)', 'Neutral (%)']].plot(kind='bar', stacked=True, figsize=(12, 8))

                    plt.title('Sentiment Analysis Over the Years')
                    plt.xlabel('Year')
                    plt.ylabel('Percentage (%)')
                    plt.xticks(rotation=0)
                    plt.legend(title='Sentiment')
                    st.pyplot(fig=plt)
                with col2:
                    df['Month'] = df['Timestamp'].apply(lambda x: x[5:7])
                    # Calculate percentage of each sentiment for each month
                    sentiment_counts_per_month = df.groupby(['Month', 'Sentiment']).size().unstack().fillna(0)
                    sentiment_counts_per_month['Total'] = sentiment_counts_per_month.sum(axis=1)
                    sentiment_counts_per_month['Positive (%)'] = sentiment_counts_per_month['Positive'] / sentiment_counts_per_month['Total'] * 100
                    sentiment_counts_per_month['Negative (%)'] = sentiment_counts_per_month['Negative'] / sentiment_counts_per_month['Total'] * 100
                    sentiment_counts_per_month['Neutral (%)'] = sentiment_counts_per_month['Neutral'] / sentiment_counts_per_month['Total'] * 100

                    # Plotting the graph
                    sentiment_counts_per_month[['Positive (%)', 'Negative (%)', 'Neutral (%)']].plot(kind='bar', stacked=True, figsize=(12, 8))
                    plt.xlabel('Month')
                    plt.ylabel('Percentage')
                    plt.title('Percentage of Sentiments Over the Months')
                    plt.xticks(rotation=0)
                    plt.legend(title='Sentiment')
                    st.pyplot(fig=plt)
                from wordcloud import WordCloud

                # Combine all comments into a single string
                combined_text = ' '.join(cleaned_data_no_emojis)

                # Create a WordCloud object
                wordcloud = WordCloud(width=800, height=400, background_color='black').generate(combined_text)

                # Display the WordCloud
                plt.figure(figsize=(10, 6))
                plt.imshow(wordcloud, interpolation='bilinear')
                plt.axis('off')
                plt.title('Word Cloud of Comments')
                st.pyplot(fig=plt)
        except Exception as e:
            st.write(e)
            st.markdown(
            """
            <style>
            /* Apply background image to the main content area */
            .main {
                background-color: Black;
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
            }
            </style>
            """,
            unsafe_allow_html=True
            )
            st.image('https://img.freepik.com/free-vector/no-data-concept-illustration_114360-626.jpg',use_column_width=True)

    elif select == 'Weather Forecasting':
        st.markdown(f"<h1 style='text-align: center; color:black;'>Weather Forecasting</h1>", unsafe_allow_html=True)
        st.markdown(
            """
            <style>
            /* Apply background image to the main content area with transparency */
            .main {
                background-image: url('https://files.oaiusercontent.com/file-R68GDtS15zdP9VNGJEiidK?se=2025-03-10T05%3A50%3A55Z&sp=r&sv=2024-08-04&sr=b&rscc=max-age%3D604800%2C%20immutable%2C%20private&rscd=attachment%3B%20filename%3D68877588-ca2e-43fe-89cc-920f7aa8b9bf.webp&sig=qNokJs8LFnym61f%2BNpeY6I0PHDgxhXG%2B929bQLOZbRM%3D');
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
              
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        col1,col2,col3 = st.columns([1,6,1])
        cricket_stadiums = {
            # Stadiums in India
            "Narendra Modi Stadium": "Ahmedabad, India",
            "Eden Gardens": "Kolkata, India",
            "Rajiv Gandhi International Cricket Stadium": "Hyderabad, India",
            "M. A. Chidambaram Stadium": "Chennai, India",
            "Maharaja Yadavindra Singh International Cricket Stadium": "Mullanpur, India",
            "Arun Jaitley Stadium": "New Delhi, India",
            "Wankhede Stadium": "Mumbai, India",
            "Green Park Stadium": "Kanpur, India",
            "Ispat Stadium": "Rourkela, India",
            "Chandigarh Cricket Stadium": "Chandigarh, India",
            "Holkar Cricket Stadium": "Indore, India",
            "PCA-IS Bindra Stadium": "Mohali, India",
            "Saurashtra Cricket Association Stadium": "Rajkot, India",
            "Dr. YS Rajasekhara Reddy ACA-VDCA Cricket Stadium": "Visakhapatnam, India",
            "Sawai Mansingh Stadium": "Jaipur, India",
            "HPCA Stadium": "Dharamsala, India",
            "Greenfield International Stadium": "Thiruvananthapuram, India",
            "JSCA International Stadium Complex": "Ranchi, India",
            "MCA Stadium": "Pune, India",
            "Barabati Stadium": "Cuttack, India",
            "M. Chinnaswamy Stadium": "Bengaluru, India",
            "DY Patil Stadium": "Navi Mumbai, India",
            "Niranjan Shah Stadium": "Rajkot, India",
            "Greater Noida Sports Complex Ground": "Greater Noida, India",
            "ACA Stadium": "Guwahati, India",
            "Rajiv Gandhi International Cricket Stadium": "Dehradun, India",
            "BRSABV Ekana Cricket Stadium": "Lucknow, India",
            "Lalabhai Contractor Stadium": "Surat, India",
            "Veer Narayan Singh International Stadium": "Raipur, India",
            "Madhavrao Scindia Cricket Stadium": "Gwalior, India",
            "Kotambi Stadium": "Vadodara, India",
            # Stadiums outside India
            "Melbourne Cricket Ground": "Melbourne, Australia",
            "Sydney Cricket Ground": "Sydney, Australia",
            "Adelaide Oval": "Adelaide, Australia",
            "The Gabba": "Brisbane, Australia",
            "Lord's": "London, England",
            "The Oval": "London, England",
            "Old Trafford": "Manchester, England",
            "Edgbaston Cricket Ground": "Birmingham, England",
            "Trent Bridge": "Nottingham, England",
            "Headingley": "Leeds, England",
            "Gaddafi Stadium": "Lahore, Pakistan",
            "National Stadium": "Karachi, Pakistan",
            "Pallekele International Cricket Stadium": "Pallekele, Sri Lanka",
            "R. Premadasa Stadium": "Colombo, Sri Lanka",
            "Galle International Stadium": "Galle, Sri Lanka",
            "Sher-e-Bangla National Cricket Stadium": "Dhaka, Bangladesh",
            "Zahur Ahmed Chowdhury Stadium": "Chittagong, Bangladesh",
            "Newlands Cricket Ground": "Cape Town, South Africa",
            "Wanderers Stadium": "Johannesburg, South Africa",
            "Centurion Park": "Centurion, South Africa",
            "Basin Reserve": "Wellington, New Zealand",
            "Eden Park": "Auckland, New Zealand",
            "Sabina Park": "Kingston, Jamaica",
            "Queen's Park Oval": "Port of Spain, Trinidad and Tobago",
            "Kensington Oval": "Bridgetown, Barbados",
            "Dubai International Cricket Stadium": "Dubai, UAE",
            "Sheikh Zayed Cricket Stadium": "Abu Dhabi, UAE"
        }
        stadium = col2.selectbox("Select Stadium", list(cricket_stadiums.keys()))
        id = cricket_stadiums[stadium]
        col1,col2,col3 = st.columns([3,3,2])
        if col2.button('Submit',type='primary'):
            owm = pyowm.OWM('11081b639d8ada3e97fc695bcf6ddb20')
            mgr = owm.weather_manager()
            observation = mgr.weather_at_place(id)
            weather = observation.weather
            t1 = weather.temperature('celsius')['temp']
            h1 = weather.humidity
            w1 = weather.wind()
            p1=weather.pressure['press']
            num_weekdays = 5
            count_weekdays = 0
            weekday_names = []
            now = time.time()
            now1 = time.localtime()
            us_date = time.strftime("%m/%d/%Y", now1)
            while count_weekdays < num_weekdays:
                now += 86400
                local_time = time.localtime(now)
                weekday = local_time.tm_wday
                wn = time.strftime("%a", local_time)
                if count_weekdays!=5:
                    count_weekdays += 1
                    weekday_names.append(time.strftime("%a", local_time))
            col1, col2,col3,col4,col5= st.columns([4,4,4,4,4])
            forecaster = mgr.forecast_at_place(id, '3h', limit=40)

            c=0
            l=[]
            
            for weather in forecaster.forecast:
                temperature = weather.temperature('celsius')['temp']
                c+=1
                if c==8 or c==16 or c==24 or c==32 or c==40:
                    l.append(temperature)
            st.markdown(
                f"""
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 15px; background-color: #f0f0f0; border-radius: 15px; border: 1.5px solid black; margin-bottom: 20px;">
                    <!-- Left Section (Date and Temperature) -->
                    <div style="text-align: left;">
                        <h5 style="margin: 5px 0;">Date: {us_date}</h5>
                        <h4 style="color:red; margin: 5px 0;">{t1}°C</h4>
                    </div>
                    <!-- Right Section (Cloud Image) -->
                    <div style="text-align: right;">
                        <p style="margin: 5px 0;">{id}</p> 
                        <img src="https://static.vecteezy.com/system/resources/thumbnails/022/287/830/small_2x/3d-rendering-sun-ahead-of-the-clouds-icon-3d-render-weather-sun-cloud-icon-sun-ahead-of-the-clouds-png.png" alt="Cloud" style="width: 150px; height: 150px;">
                    </div>
                </div>
                <div style="text-align: center; padding: 15px; background-color: #e5f2ae; border-radius: 15px; border: 1.5px solid black; margin-bottom: 20px;">
                    <!-- Additional Info -->
                    <p style="margin: 5px 0;"><b>Humidity:</b> {h1}%</p>
                    <p style="margin: 5px 0;"><b>Pressure:</b> {p1} hPa</p>
                    <p style="margin: 5px 0;"><b>Wind Speed:</b> {w1['speed']} hPa</p>
                    <hr style="border: 1px solid #ccc; margin: 10px 0;" />
                    <!-- Forecast Columns -->
                    <div style="display: flex; justify-content: space-between; text-align: center;">
                        <div style="flex: 1; margin: 5px;">
                            <h4 style="color:#EE82EE;">{weekday_names[0]}</h4>
                            <p>{l[0]}°C</p>
                        </div>
                        <div style="flex: 1; margin: 5px;">
                            <h4 style="color:blue;">{weekday_names[1]}</h4>
                            <p>{l[1]}°C</p>
                        </div>
                        <div style="flex: 1; margin: 5px;">
                            <h4 style="color:green;">{weekday_names[2]}</h4>
                            <p>{l[2]}°C</p>
                        </div>
                        <div style="flex: 1; margin: 5px;">
                            <h4 style="color:orange;">{weekday_names[3]}</h4>
                            <p>{l[3]}°C</p>
                        </div>
                        <div style="flex: 1; margin: 5px;">
                            <h4 style="color:red;">{weekday_names[4]}</h4>
                            <p>{l[4]}°C</p>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    elif select == 'Logout':
        st.session_state["logged_in"] = False
        st.session_state["current_user"] = None
        navigate_to_page("home")
