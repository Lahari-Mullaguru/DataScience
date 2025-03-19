import streamlit as st
import requests

# Set the title of the app
st.title("News Summarization and Sentiment Analysis")

# Input for company name
company_name = st.text_input("Enter the company name (e.g., Tesla):")

# Button to trigger the analysis
if st.button("Analyze News"):
    if company_name:
        # Call the FastAPI backend
        response = requests.get(f"http://127.0.0.1:8000/analyze-news?company_name={company_name}")
        
        if response.status_code == 200:
            result = response.json()
            
            if "error" in result:
                st.error(result["error"])
            else:
                # Display the results
                st.subheader(f"Analysis for {company_name}")

                # Display articles
                st.write("### Articles")
                for i, article in enumerate(result["Articles"], 1):
                    st.write(f"**Title:** {article['Title']}")
                    st.write(f"**Summary:** {article['Summary']}")
                    st.write(f"**Sentiment:** {article['Sentiment']}")
                    st.write(f"**Topics:** {', '.join(article['Topics'])}")
                    st.write("---")

                # Display Sentiment Distribution as plain text
                sentiment_distribution = result["Comparative Sentiment Score"]["Sentiment Distribution"]
                st.write(f"### Sentiment Distribution: {sentiment_distribution}")

                # Display Coverage Differences as plain text
                st.write("### Coverage Differences")
                for coverage in result["Comparative Sentiment Score"]["Coverage Differences"]:
                    st.write(f"{coverage['Comparison']}")
                    st.write(f"{coverage['Impact']}")
                    st.write("---")

                # Display Topic Overlap as plain text
                st.write("### Topic Overlap")
                topic_overlap = result["Comparative Sentiment Score"]["Topic Overlap"]
                
                topic_text = f"**Common Topics:** {', '.join(topic_overlap.get('Common Topics', []))}"
                unique_topics = {k: v for k, v in topic_overlap.items() if k.startswith("Unique Topics")}
                
                for key, value in unique_topics.items():
                    topic_text += f"\n**{key}:** {', '.join(value)}"
                
                st.write(topic_text)

                # Display final sentiment analysis
                st.subheader("Final Sentiment Analysis")
                st.write(result["Final Sentiment Analysis"])

                # Display audio player
                st.subheader("Hindi Text-to-Speech Summary")
                st.audio(result["Audio"])
        else:
            st.error("Failed to fetch news. Please try again.")
    else:
        st.warning("Please enter a company name.")
