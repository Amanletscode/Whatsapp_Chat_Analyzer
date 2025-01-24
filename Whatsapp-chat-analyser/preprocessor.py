import re
import pandas as pd

def preprocess(data):
    """
    Preprocess the WhatsApp chat data to create a structured DataFrame.
    Handles user messages, dates, and metadata extraction.
    """
    # Regex pattern for date and time extraction
    pattern = r"\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s-\s"

    # Split the data into messages and dates
    messages = re.split(pattern, data)[1:]  # Skip the first split as it's empty
    dates = re.findall(pattern, data)

    # Strip unwanted characters from dates
    dates = [date.strip(" - ") for date in dates]

    # Create the DataFrame
    df = pd.DataFrame({"raw_message": messages, "date": dates})

    # Clean up messages
    df["raw_message"] = df["raw_message"].str.strip()

    # Convert 'date' to datetime format, with error handling
    try:
        df["date"] = pd.to_datetime(df["date"], format="%m/%d/%y, %H:%M")
    except ValueError:
        try:
            df["date"] = pd.to_datetime(df["date"], format="%d/%m/%y, %H:%M")
        except ValueError:
            raise ValueError("Date format not recognized. Please ensure the chat export is in a standard format.")

    # Extract user and message content
    users = []
    messages = []
    for message in df["raw_message"]:
        entry = re.split(r"([\w\W]+?):\s", message, maxsplit=1)  # Maxsplit for better handling
        if entry[1:]:  # If user and message exist
            users.append(entry[1])
            messages.append(entry[2])
        else:
            users.append("group_notification")  # Mark as group notification
            messages.append(entry[0])

    # Add extracted data to the DataFrame
    df["user"] = users
    df["message_content"] = messages

    # Drop the raw message column
    df.drop(columns=["raw_message"], inplace=True)

    # Flag media messages (e.g., <Media omitted>)
    df["is_media"] = df["message_content"].str.contains(r"<Media omitted>", na=False)

    # Extract additional time-based metadata
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month_name()
    df["day"] = df["date"].dt.day
    df["hour"] = df["date"].dt.hour
    df["minute"] = df["date"].dt.minute
    df["day_of_week"] = df["date"].dt.day_name()

    return df
