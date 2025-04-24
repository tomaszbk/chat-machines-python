import uvicorn
from fastapi import FastAPI

from chatmachine import ChatMachine, SessionState, State

app = FastAPI()


class MENU(State):
    def on_enter(session: SessionState):
        session.add_output("""Welcome! Select an option:                  
                            1. Log in
                            2. Exit""")

    def on_update(session: SessionState):
        if session.input == "1":
            session.change_state(LOGIN)
        elif session.input == "2":
            session.add_output("Thank you for using me")
            session.end()
        else:
            session.add_output("Invalid option. Please try again.")
            return


class LOGIN(State):
    def on_enter(session: SessionState):
        session.add_output("Please enter your token:")

    def on_update(session: SessionState):
        token = session.input
        if token != "1234":
            session.add_output("Invalid token. Please try again.")
            return
        else:
            session.add_output("Logged in successfully.")
            session.change_state(MENU)


chat_machine = ChatMachine(start_state=MENU)


@app.post("/chat")
def get_chatbot_response(user_input: str, session_id: str):
    output = chat_machine.run(user_input, session_id)
    return {"response": output}


if __name__ == "__main__":
    uvicorn.run("fastapi_example:app", host="0.0.0.0", port=8000, reload=True)
