# Python Chat Machines

[![CI](https://img.shields.io/github/actions/workflow/status/pydantic/pydantic/ci.yml?branch=main&logo=github&label=CI)](https://github.com/tomaszbk/chat-machines-python/actions)
[![Coverage](https://coverage-badge.samuelcolvin.workers.dev/pydantic/pydantic.svg)](https://coverage-badge.samuelcolvin.workers.dev/redirect/pydantic/pydantic)
[![pypi](https://img.shields.io/pypi/v/pydantic.svg)](https://pypi.org/manage/project/chatmachine)
[![versions](https://img.shields.io/pypi/pyversions/pydantic.svg)](https://github.com/tomaszbk/chat-machines-python)
[![license](https://img.shields.io/github/license/pydantic/pydantic.svg)](https://github.com/tomaszbk/chat-machines-python/blob/master/LICENSE)

Small, simple, and typed Python library for building chatbots using state machines, that can be integrated with REST APIs, discord, whatsapp, telegram, etc.

## Installation

Install using `pip install chatmachine` or `uv add chatmachine`.

## Usage

```python
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
```

## Explanation

The first State defined will automatically be selected as the initial state. The `on_enter` method is called when the state is entered, and the `on_exit` method is called when the state is exited. The `on_update` method is called on every input received in the state after it has been entered once.

The `SessionState` object is passed to the state methods, which contains the input and output attributes. The `input` attribute contains the user input. The `add_output` method is used to append a message to the output. A custom data pydantic object can be set to `session.data` to store any data you want to keep through states.

The `change_state` method is used to change the state of the session. It will automatically trigger the new state's `on_enter` method. The `end` method is used to end the session.

## Planned
- Database integrations for storing sessions.
- More examples for different platforms.
- More personalization options.

## License
This project is licensed under the terms of the MIT license. See the [LICENSE](LICENSE) file for details.