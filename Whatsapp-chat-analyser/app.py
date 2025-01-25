import streamlit as st
import matplotlib.pyplot as plt
from preprocessor import preprocess
import helper
from helper import plot_activity_heatmap_matplotlib

# Function to load external CSS for styling
def load_css(css_file_path):
    """
    Load external CSS for styling the Streamlit app.
    """
    try:
        with open(css_file_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"CSS file '{css_file_path}' not found. Please ensure it exists in the correct directory.")


# Load external CSS
load_css("styles.css")

# Sidebar Title
st.sidebar.title("WhatsApp Chat Analyzer")

# Sidebar File Upload Feature
uploaded_file = st.sidebar.file_uploader("Choose a file", type=["txt"])

if uploaded_file is not None:
    # Decode uploaded file and preprocess the data
    data = uploaded_file.getvalue().decode("utf-8")
    df = preprocess(data)

    # Sidebar: User Selection
    user_list = helper.get_user_list(df)
    selected_user = st.sidebar.selectbox("Show analysis wrt", user_list)

    # Sidebar: Toggle to view full chat or filtered chat (only when a specific user is selected)
    if selected_user != "Overall":
        toggle_view = st.sidebar.radio(
            "View chat messages",
            options=["Filtered View", "Full View"]
        )

        # Dynamically filter DataFrame based on selected user
        if toggle_view == "Filtered View":
            filtered_df = df[df["user"] == selected_user]
        else:
            filtered_df = df
    else:
        filtered_df = df

    # Display the DataFrame
    st.dataframe(filtered_df)

    # Sidebar: User-friendly label for frequency threshold
    st.sidebar.markdown("### Filter Common Words")
    exclude_common_words = st.sidebar.slider(
        "Exclude words used by most users (%)",
        min_value=0.01,
        max_value=1.0,
        value=0.1,
        step=0.01
    )

    # Button to trigger analysis
    if st.sidebar.button("Show Analysis"):
        # Fetch overall stats
        num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)

        # **Section: Stats**
        st.markdown('<div class="section-header">Overall Statistics</div>', unsafe_allow_html=True)
        stats = {
            "Total Messages": num_messages,
            "Total Words": words,
            "Media Shared": num_media_messages,
            "Links Shared": num_links,
        }
        cols = st.columns(len(stats))
        for col, (label, value) in zip(cols, stats.items()):
            with col:
                st.markdown(f"<div style='text-align: center; font-size: 16px;'><strong>{label}</strong></div>", unsafe_allow_html=True)
                st.markdown(f"<div style='text-align: center; font-size: 18px; font-weight: bold;'>{value}</div>", unsafe_allow_html=True)

        st.markdown('<div class="horizontal-line"></div>', unsafe_allow_html=True)

        # **Section: Most Busy Users**
        if selected_user == "Overall":
            st.markdown('<div class="section-header">Most Busy Users</div>', unsafe_allow_html=True)
            fig_busy_users, busy_users_df = helper.plot_most_busy_users_interactive(df)

            col1, col2 = st.columns([2, 1])
            with col1:
                st.plotly_chart(fig_busy_users, use_container_width=True)
            with col2:
                if not busy_users_df.empty:
                    st.markdown('<div class="sub-header">User Contribution Table</div>', unsafe_allow_html=True)
                    st.dataframe(busy_users_df)

            st.markdown('<div class="horizontal-line"></div>', unsafe_allow_html=True)

        # **Section: Timeline Analysis**
        st.markdown('<div class="section-header">Timeline Analysis</div>', unsafe_allow_html=True)

        # Monthly Timeline
        st.markdown('<div class="sub-header" style="text-align: left;">Monthly Timeline</div>', unsafe_allow_html=True)
        fig_monthly, monthly_timeline_df = helper.plot_monthly_timeline(selected_user, df)
        col1, col2 = st.columns([3, 1])
        with col1:
            st.plotly_chart(fig_monthly, use_container_width=True)
        with col2:
            if not monthly_timeline_df.empty:
                st.markdown('<div class="sub-header">Monthly Activity</div>', unsafe_allow_html=True)
                st.dataframe(monthly_timeline_df, height=400)

        # Add a partition line
        st.markdown('<div class="horizontal-line"></div>', unsafe_allow_html=True)

        # **Daily Timeline Analysis**
        st.markdown('<div class="sub-header">Daily Timeline</div>', unsafe_allow_html=True)

        fig_daily, daily_timeline_df = helper.plot_daily_timeline(selected_user, df)

        # Display chart and DataFrame side by side
        col1, col2 = st.columns([2, 1])
        with col1:
            st.plotly_chart(fig_daily, use_container_width=True)
        with col2:
            st.markdown('<div class="sub-header">Daily Activity</div>', unsafe_allow_html=True)
            st.dataframe(daily_timeline_df.rename(columns={"date": "Date", "message_count": "Message Count"}))

        # Add a partition line
        st.markdown('<div class="horizontal-line"></div>', unsafe_allow_html=True)

        # **Section: Activity Analysis**
        st.markdown('<div class="section-header">Activity Analysis</div>', unsafe_allow_html=True)

        # Most Active Days
        st.markdown('<div class="sub-header" style="text-align: left;">Most Active Days</div>', unsafe_allow_html=True)
        fig_days, fig_hours = helper.plot_interactive_activity_analysis(df, selected_user)
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(fig_days, use_container_width=True)
        with col2:
            st.markdown('<div class="sub-header" style="text-align: left;">Most Active Hours</div>', unsafe_allow_html=True)
            st.plotly_chart(fig_hours, use_container_width=True)

        # Add a partition line
        st.markdown('<div class="horizontal-line"></div>', unsafe_allow_html=True)

        # **Heatmap Section**
        st.markdown('<div class="section-header">Heatmap Analysis</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-header" style="text-align: left;">Message Activity Heatmap</div>', unsafe_allow_html=True)

        # Generate heatmap figure using helper function
        fig_heatmap = plot_activity_heatmap_matplotlib(df)

        # Display heatmap
        st.pyplot(fig_heatmap)

        # Add a partition line
        st.markdown('<div class="horizontal-line"></div>', unsafe_allow_html=True)

        # **Section: Emoji Analysis**
        st.markdown('<div class="section-header">Emoji Analysis</div>', unsafe_allow_html=True)

        # Perform emoji analysis
        total_emojis, emoji_df = helper.emoji_analysis(df, selected_user)

        if total_emojis == 0:
            st.markdown("No emojis found in the chat.")
        else:
            st.markdown(f"**Total Emojis Used:** {total_emojis}")

            # Create columns to display the pie chart and emoji count DataFrame side by side
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown('<div class="sub-header">Top 5 Emojis (Pie Chart)</div>', unsafe_allow_html=True)

                # Pie chart for top 5 emojis
                top_emojis = emoji_df.head(5)
                plt.rcParams['font.family'] = 'Segoe UI Emoji'

                fig, ax = plt.subplots()
                ax.pie(
                    top_emojis['Count'],
                    labels=top_emojis['Emoji'],
                    autopct='%1.1f%%',
                    startangle=90,
                    textprops={'fontsize': 12}
                )
                ax.axis('equal')
                st.pyplot(fig)
            with col2:
                st.markdown('<div class="sub-header">Emoji Usage Details</div>', unsafe_allow_html=True)
                st.dataframe(emoji_df, height=400)

            st.markdown('<div class="horizontal-line"></div>', unsafe_allow_html=True)

else:
    st.sidebar.write("Please upload a WhatsApp chat file.")
