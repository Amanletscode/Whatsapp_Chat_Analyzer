import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from collections import Counter
import emoji


def fetch_stats(selected_user, df):
    """
    Fetch statistics for the selected user or overall chat.
    """
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    num_messages = df.shape[0]
    words = sum(len(message.split()) for message in df['message_content'])
    num_media_messages = df[df['message_content'] == '<Media omitted>'].shape[0]
    num_links = sum(df['message_content'].str.contains(r'http[s]?://|www\.', na=False))

    return num_messages, words, num_media_messages, num_links


def get_user_list(df):
    """
    Get a sorted list of unique users for dropdown selection.
    """
    user_list = df['user'].unique().tolist()
    if 'group_notification' in user_list:
        user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0, "Overall")
    return user_list


def plot_most_busy_users_interactive(df):
    """
    Plot the top 5 most busy users as an interactive bar chart.
    """
    user_counts = df['user'].value_counts().head(5).reset_index()
    user_counts.columns = ["User", "Message Count"]

    # Create an interactive bar chart
    fig = px.bar(
        user_counts,
        x="User",
        y="Message Count",
        title="Most Active Users",
        text="Message Count",
        color="Message Count",
        color_continuous_scale="Blues",
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(title_x=0.5, template="plotly_dark")

    return fig, user_counts


def get_user_contribution(df):
    """
    Generate a DataFrame showing user contribution percentages.
    """
    contribution = (df['user'].value_counts(normalize=True) * 100).reset_index()
    contribution.columns = ['User', 'Percentage (%)']
    contribution['Percentage (%)'] = contribution['Percentage (%)'].round(2)
    return contribution


def extract_emojis(message):
    """
    Extract all emojis from a single message.
    """
    return [char for char in message if char in emoji.EMOJI_DATA]


def emoji_analysis(df, selected_user):
    """
    Perform emoji analysis for the selected user or overall chat.
    """
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]

    emojis = []
    for message in df['message_content']:
        emojis.extend(extract_emojis(message))

    emoji_counts = Counter(emojis)
    emoji_df = pd.DataFrame(emoji_counts.items(), columns=['Emoji', 'Count'])
    emoji_df = emoji_df.sort_values(by='Count', ascending=False).reset_index(drop=True)

    return sum(emoji_counts.values()), emoji_df


# Timeline and Activity Analysis
def plot_monthly_timeline(selected_user, df):
    """
    Generate an interactive line chart for messages per month.
    """
    if selected_user != "Overall":
        df = df[df["user"] == selected_user]

    # Group messages by year and month
    df['month_year'] = df['date'].dt.to_period('M').dt.strftime('%Y-%m')
    monthly_counts = df.groupby('month_year').size().reset_index(name='message_count')

    # Create the line chart using Plotly
    fig = px.line(
        monthly_counts,
        x='month_year',
        y='message_count',
        title="Messages Per Month",
        labels={'month_year': 'Month', 'message_count': 'Message Count'},
        markers=True,
    )
    fig.update_traces(line=dict(color='blue', width=2))
    fig.update_layout(title_x=0.5, plot_bgcolor='black', paper_bgcolor='black', font=dict(color='white'))

    return fig, monthly_counts


def plot_daily_timeline(selected_user, df):
    """
    Generate an interactive scatter plot for messages per day, aggregated by date.
    """
    if selected_user != "Overall":
        df = df[df["user"] == selected_user]

    # Group messages by date
    daily_counts = df.groupby(df['date'].dt.date).size().reset_index(name='message_count')

    # Create the scatter plot using Plotly
    fig = px.scatter(
        daily_counts,
        x='date',
        y='message_count',
        title="Messages Per Day",
        labels={'date': 'Date', 'message_count': 'Message Count'},
    )
    fig.update_traces(marker=dict(color='green', size=8))
    fig.update_layout(title_x=0.5, plot_bgcolor='black', paper_bgcolor='black', font=dict(color='white'))

    return fig, daily_counts


def plot_interactive_activity_analysis(df, selected_user):
    """
    Plot interactive bar charts for activity analysis (days and hours).
    """
    if selected_user != "Overall":
        df = df[df["user"] == selected_user]

    # Messages per day of the week
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    df["day_name"] = pd.Categorical(df["date"].dt.day_name(), categories=day_order, ordered=True)
    weekly_activity = df.groupby("day_name").size().reset_index(name="message_count")

    # Messages per hour
    hourly_activity = df.groupby(df["date"].dt.hour).size().reset_index(name="message_count")

    # Interactive bar chart for days
    fig1 = px.bar(
        weekly_activity,
        x="day_name",
        y="message_count",
        title="Messages Per Day of the Week",
        labels={"day_name": "Day", "message_count": "Message Count"},
        color="message_count",
        color_continuous_scale="Blues",  # Use a valid colorscale
    )
    fig1.update_layout(title_x=0.5, template="plotly_dark")

    # Interactive bar chart for hours
    fig2 = px.bar(
        hourly_activity,
        x="date",
        y="message_count",
        title="Messages Per Hour",
        labels={"date": "Hour", "message_count": "Message Count"},
        color="message_count",
        color_continuous_scale="Purples",  # Use a valid colorscale
    )
    fig2.update_layout(title_x=0.5, template="plotly_dark")

    return fig1, fig2


def plot_activity_heatmap_matplotlib(df):
    """
    Create a heatmap showing message activity by day of the week and hour of the day using matplotlib.
    """
    # Extract day of the week and hour of the day
    df["day_of_week"] = df["date"].dt.day_name()
    df["hour"] = df["date"].dt.hour

    # Create a pivot table for heatmap
    heatmap_data = df.pivot_table(
        index="day_of_week", columns="hour", values="message_content", aggfunc="count"
    ).fillna(0)

    # Reorder days of the week
    ordered_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    heatmap_data = heatmap_data.reindex(ordered_days)

    # Create the heatmap
    fig, ax = plt.subplots(figsize=(12, 6))
    cax = ax.matshow(heatmap_data, cmap="coolwarm", aspect="auto")

    # Add color bar
    fig.colorbar(cax)

    # Set axis labels
    ax.set_xticks(range(len(heatmap_data.columns)))
    ax.set_yticks(range(len(heatmap_data.index)))
    ax.set_xticklabels(heatmap_data.columns, rotation=90)
    ax.set_yticklabels(heatmap_data.index)

    # Set title and labels
    ax.set_title("Message Activity Heatmap", pad=20, fontsize=16)
    ax.set_xlabel("Hour of the Day", fontsize=12)
    ax.set_ylabel("Day of the Week", fontsize=12)

    plt.tight_layout()

    return fig
