from pyngrok import ngrok
public_url = ngrok.connect(8501)
print("Streamlit app is running at:", public_url)
!streamlit run app.py
