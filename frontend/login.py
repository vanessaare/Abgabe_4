import streamlit as st
import streamlit_authenticator as stauth
import yaml 

def load_authenticator():

    with open("data/config.yaml", "r") as file:
        config = yaml.safe_load(file)

    authenticator = stauth.Authenticate(
        config["credentials"],
        config["cookie"]["name"],
        config["cookie"]["key"],
        config["cookie"]["expiry_days"]
    )

    return authenticator


def login(authenticator):

    authenticator.login()

    if st.session_state["authentication_status"]:
        st.success("Login erfolgreich")
        return True

    elif st.session_state["authentication_status"] is False:
        st.error("Falscher Benutzer oder Passwort")

    else:
        st.warning("Bitte einloggen")

    return False