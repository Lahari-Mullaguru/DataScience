import streamlit as st
import requests

# Set the title of the app
st.title("News Summarization and Sentiment Analysis")

# Input for company name
company_name = st.text_input("Enter the company name (e.g., Tesla):")

# Button to trigger the analysis
if st.button("Analyze News"):
    if company_name:
        # Call the API to fetch and analyze news
        response = requests.get(f"http://127.0.0.1:8000/analyze-news?company_name={company_name}")
        
        if response.status_code == 200:
            result = response.json()
            
            # Display the results
            st.subheader(f"Analysis for {company_name}")
            
            # Display articles
            st.write("### Articles")
            for article in result["Articles"]:
                st.write(f"**Title:** {article['Title']}")
                st.write(f"**Summary:** {article['Summary']}")
                st.write(f"**Sentiment:** {article['Sentiment']}")
                st.write(f"**Topics:** {', '.join(article['Topics'])}")
                st.write("---")
            
            # Display comparative analysis
            st.write("### Comparative Analysis")
            st.write(f"**Sentiment Distribution:** {result['Comparative Sentiment Score']['Sentiment Distribution']}")
            st.write("### Coverage Differences")
            for coverage in data["Comparative Sentiment Score"]["Coverage Differences"]:
                    st.write(f"{coverage['Comparison']}")
                    st.write(f"{coverage['Impact']}")
                    st.write("---")

            st.write("### Topic Overlap")
            topic_overlap = data["Comparative Sentiment Score"]["Topic Overlap"]
            st.json(topic_overlap)
            
            # Display final sentiment analysis
            st.write("### Final Sentiment Analysis")
            st.write(result["Final Sentiment Analysis"])
            
            # Display audio player
            st.write("### Hindi Text-to-Speech Summary")
            st.audio(result["Audio"])
        else:
            st.error("Failed to fetch news. Please try again.")
    else:
        st.warning("Please enter a company name.")
